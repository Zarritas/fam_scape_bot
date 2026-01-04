"""
Web scraper para el calendario de la Federación de Atletismo de Madrid.

Extrae la lista de competiciones del calendario web, incluyendo:
- Nombre de la competición
- Fecha
- URL del PDF
- Indicador de modificaciones (fondo amarillo)
"""

import re
from datetime import date
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

from src.config import settings
from src.scraper.models import RawCompetition
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Meses en español para conversión de fechas
MONTHS_ES: dict[str, int] = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


class WebScraperError(Exception):
    """Error durante el scraping web."""
    pass


class WebScraper:
    """
    Scraper para el calendario de competiciones de la FAM.
    
    Extrae competiciones del calendario web filtrando por mes y año.
    
    Estructura HTML del calendario FAM:
    - Tabla con clase 'calendario' dentro de div#calendario
    - Columnas: Fecha | Límite inscripción | Competición | Lugar | regl. | insc. | | Tipo
    - El enlace al PDF está en la columna 'regl.' (no en el nombre de la competición)
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        calendar_path: Optional[str] = None,
        timeout: int = 30,
    ):
        self.base_url = base_url or settings.fam_base_url
        self.calendar_path = calendar_path or settings.fam_calendar_path
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        })
    
    def _build_calendar_url(self, month: int, year: int) -> str:
        """
        Construye la URL del calendario con filtros de mes y año.
        
        La web FAM usa parámetros en la URL para filtrar:
        - temporada: año (ej: 2026)
        - mes: número de mes (1-12)
        """
        base = f"{self.base_url}{self.calendar_path}"
        # Añadir parámetros de temporada y mes
        separator = "&" if "?" in self.calendar_path else "?"
        return f"{base}{separator}temporada={year}&mes={month}"
    
    def get_competitions(
        self,
        month: int,
        year: int,
    ) -> list[RawCompetition]:
        """
        Obtiene la lista de competiciones para un mes y año específicos.
        
        Args:
            month: Mes (1-12)
            year: Año (ej: 2026)
            
        Returns:
            Lista de RawCompetition con los datos extraídos
            
        Raises:
            WebScraperError: Si hay error en la petición o parsing
        """
        url = self._build_calendar_url(month, year)
        logger.info(f"Scraping calendario: {url}")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error en petición HTTP: {e}")
            raise WebScraperError(f"Error obteniendo calendario: {e}") from e
        
        try:
            return self._parse_calendar_html(response.text, month, year)
        except Exception as e:
            logger.error(f"Error parseando HTML: {e}")
            raise WebScraperError(f"Error parseando calendario: {e}") from e
    
    def _parse_calendar_html(
        self, 
        html: str,
        month: int,
        year: int,
    ) -> list[RawCompetition]:
        """
        Parsea el HTML del calendario y extrae las competiciones.
        
        El calendario tiene una tabla con clase 'calendario':
        - Columna 0: Fecha (ej: "03.01 (S)")
        - Columna 1: Límite inscripción
        - Columna 2: Nombre de la competición (enlace a página de detalle)
        - Columna 3: Lugar
        - Columna 4: Enlace al reglamento PDF ("regl.")
        - Columna 5: Enlace a inscritos
        - Columna 6: vacío
        - Columna 7: Tipo (PC, AL, C, M, R)
        """
        soup = BeautifulSoup(html, "lxml")
        competitions: list[RawCompetition] = []
        
        # Buscar la tabla con clase 'calendario'
        calendar_table = soup.find("table", class_="calendario")
        if not calendar_table:
            # Fallback: buscar cualquier tabla en div#calendario
            calendar_div = soup.find("div", id="calendario")
            if calendar_div:
                calendar_table = calendar_div.find("table")
        
        if not calendar_table:
            logger.warning("No se encontró la tabla del calendario")
            return []
        
        rows = calendar_table.find_all("tr")
        
        for row in rows:
            competition = self._parse_competition_row(row, month, year)
            if competition:
                competitions.append(competition)
        
        logger.info(f"Encontradas {len(competitions)} competiciones")
        return competitions
    
    def _parse_competition_row(
        self,
        row: Tag,
        month: int,
        year: int,
    ) -> Optional[RawCompetition]:
        """
        Parsea una fila de la tabla para extraer datos de competición.
        
        Estructura de columnas:
        0: Fecha | 1: Límite | 2: Competición | 3: Lugar | 4: regl. | 5: insc. | 6: | 7: Tipo
        """
        cells = row.find_all("td")
        if len(cells) < 5:
            # Probablemente es la fila de encabezado (th) o fila incompleta
            return None
        
        # Columna 4: Enlace al reglamento (normalmente PDF, a veces link externo)
        regl_cell = cells[4] if len(cells) > 4 else None
        regl_link = None
        if regl_cell:
            # Buscar enlace que tenga el texto "regl." o que tenga title "Reglamento"
            regl_link = regl_cell.find("a", string=lambda x: x and "regl" in x.lower())
            if not regl_link:
                regl_link = regl_cell.find("a", title=lambda x: x and "Reglamento" in x)
            if not regl_link:
                # Fallback: primer enlace en la celda
                regl_link = regl_cell.find("a")
        
        if not regl_link:
            # También puede estar en un span con clase 'reglamento_circular'
            if regl_cell:
                span = regl_cell.find("span", class_="reglamento_circular")
                if span:
                    regl_link = span.find("a")
        
        if not regl_link:
            # No tiene link de reglamento, saltar esta fila
            return None
        
        pdf_url = regl_link.get("href", "")
        if not pdf_url:
            return None
        
        # Hacer URL absoluta
        pdf_url = urljoin(self.base_url, pdf_url)
        
        # Columna 2: Nombre de la competición
        name_cell = cells[2] if len(cells) > 2 else None
        name = "Competición sin nombre"
        if name_cell:
            # El nombre está en un enlace dentro de la celda
            name_link = name_cell.find("a")
            if name_link:
                name = name_link.get_text(strip=True)
            else:
                name = name_cell.get_text(strip=True)
        
        # Columna 0: Fecha (formato: "03.01 (S)" o "17y18.01 (S-D)")
        date_cell = cells[0] if len(cells) > 0 else None
        date_str = ""
        if date_cell:
            date_str = date_cell.get_text(strip=True)
        
        # Columna 3: Lugar
        location_cell = cells[3] if len(cells) > 3 else None
        location = None
        if location_cell:
            location = location_cell.get_text(strip=True)
            if not location:
                location = None
        
        # Columna 7: Tipo de competición
        type_cell = cells[7] if len(cells) > 7 else None
        comp_type = None
        if type_cell:
            comp_type = type_cell.get_text(strip=True)
        
        # Detectar si tiene modificaciones (fondo verde/amarillo en el style del tr)
        # Las filas con estilo tienen: style='background:#EBFFAA;font-style:italic;'
        has_modifications = self._has_highlight_background(row)
        
        return RawCompetition(
            name=name,
            date_str=self._normalize_date(date_str, month, year),
            pdf_url=pdf_url,
            has_modifications=has_modifications,
            location=location,
            competition_type=comp_type,
        )
    
    def _normalize_date(self, date_str: str, month: int, year: int) -> str:
        """
        Normaliza el formato de fecha del calendario.
        
        Entrada: "03.01 (S)" o "17y18.01 (S-D)"
        Salida: "03/01" o "17-18/01"
        """
        if not date_str:
            return ""
        
        # Limpiar paréntesis con día de la semana
        date_str = re.sub(r'\s*\([^)]*\)', '', date_str).strip()
        
        # Patrón para fechas con rango: "17y18.01"
        range_match = re.match(r'(\d{1,2})y(\d{1,2})\.(\d{2})', date_str)
        if range_match:
            day1, day2, month_num = range_match.groups()
            return f"{day1}-{day2}/{month_num}"
        
        # Patrón para fecha simple: "03.01"
        simple_match = re.match(r'(\d{1,2})\.(\d{2})', date_str)
        if simple_match:
            day, month_num = simple_match.groups()
            return f"{day}/{month_num}"
        
        return date_str
    
    def _has_highlight_background(self, element: Tag) -> bool:
        """
        Detecta si un elemento tiene fondo destacado (amarillo/verde).
        
        Las competiciones externas/especiales tienen:
        style='background:#EBFFAA;font-style:italic;'
        """
        if not element:
            return False
        
        style = element.get("style", "")
        if style:
            style_lower = style.lower()
            # Buscar colores de fondo que indican competición especial
            highlight_colors = [
                "#ebffaa",  # Verde claro usado en la FAM
                "yellow",
                "#ffff",
                "#ff0",
                "#ffc",
                "#ffd",
                "#ffe",
            ]
            for color in highlight_colors:
                if color in style_lower:
                    return True
        
        return False
    
    def _has_yellow_background(self, element: Tag) -> bool:
        """Alias para compatibilidad."""
        return self._has_highlight_background(element)
    
    def download_pdf(self, url: str) -> bytes:
        """
        Descarga el contenido binario de un PDF.
        
        Args:
            url: URL del PDF a descargar
            
        Returns:
            Contenido binario del PDF
            
        Raises:
            WebScraperError: Si hay error en la descarga
        """
        logger.info(f"Descargando PDF: {url}")
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Verificar que es un PDF
            content_type = response.headers.get("Content-Type", "")
            if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
                logger.warning(f"Contenido no parece ser PDF: {content_type}")
            
            return response.content
            
        except requests.RequestException as e:
            logger.error(f"Error descargando PDF: {e}")
            raise WebScraperError(f"Error descargando PDF: {e}") from e
    
    def get_competitions_for_months(
        self,
        months: list[tuple[int, int]],
    ) -> list[RawCompetition]:
        """
        Obtiene competiciones para múltiples meses.
        
        Args:
            months: Lista de tuplas (mes, año)
            
        Returns:
            Lista combinada de competiciones (sin duplicados por URL)
        """
        all_competitions: dict[str, RawCompetition] = {}
        
        for month, year in months:
            try:
                competitions = self.get_competitions(month, year)
                for comp in competitions:
                    # Usar URL como clave para evitar duplicados
                    all_competitions[comp.pdf_url] = comp
            except WebScraperError as e:
                logger.error(f"Error en mes {month}/{year}: {e}")
                # Continuar con otros meses aunque falle uno
        
        return list(all_competitions.values())


def get_current_and_next_months() -> list[tuple[int, int]]:
    """
    Obtiene el mes actual y el siguiente.
    
    Maneja el cambio de año (diciembre → enero).
    
    Returns:
        Lista de tuplas (mes, año) para mes actual y siguiente
    """
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Mes siguiente
    if current_month == 12:
        next_month = 1
        next_year = current_year + 1
    else:
        next_month = current_month + 1
        next_year = current_year
    
    return [
        (current_month, current_year),
        (next_month, next_year),
    ]


def parse_date_string(date_str: str, year: int) -> Optional[date]:
    """
    Convierte una cadena de fecha al objeto date.
    
    Args:
        date_str: Fecha como string (ej: "11 de enero", "11/01")
        year: Año para completar la fecha
        
    Returns:
        Objeto date o None si no se puede parsear
    """
    if not date_str:
        return None
    
    # Patrón: "11 de enero" o "11 enero"
    match = re.search(r"(\d{1,2})\s*(?:de\s+)?(\w+)", date_str, re.IGNORECASE)
    if match:
        day = int(match.group(1))
        month_str = match.group(2).lower()
        month = MONTHS_ES.get(month_str)
        if month:
            try:
                return date(year, month, day)
            except ValueError:
                return None
    
    # Patrón: "11/01"
    match2 = re.search(r"(\d{1,2})[/-](\d{1,2})", date_str)
    if match2:
        day = int(match2.group(1))
        month = int(match2.group(2))
        try:
            return date(year, month, day)
        except ValueError:
            return None
    
    return None
