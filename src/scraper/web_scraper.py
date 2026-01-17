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

# Diccionario inverso para obtener nombre del mes por número
MONTHS_BY_NUMBER = {v: k for k, v in MONTHS_ES.items()}


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
        base_url: str | None = None,
        calendar_path: str | None = None,
        timeout: int = 30,
    ):
        self.base_url = base_url or settings.fam_base_url
        self.calendar_path = calendar_path or settings.fam_calendar_path
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            }
        )

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
            return self.parse_calendar_html(response.text, month, year)
        except Exception as e:
            logger.error(f"Error parseando HTML: {e}")
            raise WebScraperError(f"Error parseando calendario: {e}") from e

    def parse_calendar_html(
        self, html: str, default_month: int = 1, default_year: int = 2026
    ) -> list[RawCompetition]:
        """
        Parsea el HTML del calendario FAM y extrae las competiciones.

        Estructura HTML real:
        - Tabla con clase "table table-striped table-hover"
        - Columnas: Fecha | Competición | Lugar | Documentos | Inscripciones
        - Los PDFs están en la columna "Documentos" como enlaces
        """
        soup = BeautifulSoup(html, "lxml")
        competitions: list[RawCompetition] = []

        # Buscar tabla del calendario (la estructura real del sitio FAM)
        calendar_table = soup.find("table", class_="table table-striped table-hover")

        if not calendar_table:
            logger.warning("No se encontró la tabla del calendario")
            return []

        # Saltar el header (primera fila)
        rows = calendar_table.find_all("tr")[1:]

        for row in rows:
            competition = self._parse_real_competition_row(row, default_month, default_year)
            if competition:
                competitions.append(competition)

        logger.info(f"Encontradas {len(competitions)} competiciones")
        return competitions

    def _parse_real_competition_row(self, row: Tag, month: int, year: int) -> RawCompetition | None:
        """
        Parsea una fila de la tabla real del calendario FAM.

        Estructura: Fecha | Competición | Lugar | Documentos | Inscripciones
        Maneja fechas múltiples como "17y18.01 (S-D)"
        """
        cells = row.find_all("td")
        if len(cells) < 5:
            return None

        # Columna 0: Fecha (ej: "03/01/2026" o "17y18.01 (S-D)")
        date_cell = cells[0]
        date_str = date_cell.get_text(strip=True)

        # Parsear fechas múltiples
        fechas_adicionales = self._extract_additional_dates(date_str)

        # Columna 1: Competición (nombre)
        name_cell = cells[1]
        name = name_cell.get_text(strip=True)

        # Columna 2: Lugar
        location_cell = cells[2]
        location = location_cell.get_text(strip=True) or None

        # Columna 3: Documentos (contiene el enlace al PDF)
        docs_cell = cells[3]
        pdf_url = None
        pdf_link = docs_cell.find("a")
        if pdf_link:
            pdf_href = pdf_link.get("href")
            if pdf_href:
                pdf_url = urljoin(self.base_url, pdf_href)

        # Columna 4: Inscripciones (contiene el enlace de inscripción)
        enroll_cell = cells[4]
        enrollment_url = None
        enroll_link = enroll_cell.find("a")
        if enroll_link:
            enroll_href = enroll_link.get("href")
            if enroll_href:
                enrollment_url = urljoin(self.base_url, enroll_href)

        # Detectar modificaciones (por ahora no hay indicador visual claro)
        has_modifications = False

        # Tipo de competición (extraer del nombre o dejar como None por ahora)
        competition_type = None

        if not name or not pdf_url:
            return None

        # Normalizar la fecha para display legible
        normalized_date = self._normalize_date(date_str, month, year)

        # Crear RawCompetition con soporte para fechas adicionales
        competition = RawCompetition(
            name=name,
            date_str=normalized_date,  # Usar fecha normalizada
            pdf_url=pdf_url,
            enrollment_url=enrollment_url,
            has_modifications=has_modifications,
            location=location,
            competition_type=competition_type,
        )

        # Agregar fechas adicionales como atributo personalizado
        if fechas_adicionales:
            competition.fechas_adicionales = fechas_adicionales

        return competition

    def _parse_competition_row(
        self,
        row: Tag,
        month: int,
        year: int,
    ) -> RawCompetition | None:
        """
        Parsea una fila de la tabla para extraer datos de competición.

        Usa la celda del reglamento (PDF) como ancla para encontrar:
        - Nombre: ancla - 2
        - Lugar: ancla - 1
        - Inscritos: ancla + 1
        """
        cells = row.find_all("td")
        if not cells:
            return None

        # 1. Encontrar celda ancla (Reglamento/PDF)
        regl_index = -1

        # Búsqueda por contenido (más robusta)
        for i, cell in enumerate(cells):
            # Buscar enlace con "regl" en texto o título
            if (
                cell.find("a", string=lambda x: x and "regl" in x.lower())
                or cell.find("a", title=lambda x: x and "Reglamento" in x)
                or cell.find("span", class_="reglamento_circular")
            ):
                regl_index = i
                break

        # Fallback a posición fija si no se detecta (el calendario suele ser fijo)
        if regl_index == -1:
            if len(cells) > 4 and cells[4].find("a"):
                regl_index = 4
            else:
                return None

        # 2. Extraer URL del PDF (Ancla)
        regl_cell = cells[regl_index]
        regl_link = regl_cell.find("a")
        if not regl_link:
            # Intentar dentro de span
            span = regl_cell.find("span", class_="reglamento_circular")
            if span:
                regl_link = span.find("a")

        if not regl_link:
            return None

        pdf_url = regl_link.get("href", "")
        if not pdf_url:
            return None

        pdf_url = urljoin(self.base_url, pdf_url)

        # 3. Extraer Nombre (Ancla - 2)
        name_index = regl_index - 2
        name = "Competición sin nombre"
        if name_index >= 0 and name_index < len(cells):
            name_cell = cells[name_index]
            name_link = name_cell.find("a")
            name = name_link.get_text(strip=True) if name_link else name_cell.get_text(strip=True)

        # 4. Extraer Lugar (Ancla - 1)
        loc_index = regl_index - 1
        location = None
        if loc_index >= 0 and loc_index < len(cells):
            location = cells[loc_index].get_text(strip=True) or None

        # 5. Extraer Inscritos (Ancla + 1)
        enroll_index = regl_index + 1
        enrollment_url = None
        if enroll_index < len(cells):
            enroll_cell = cells[enroll_index]
            enroll_link = enroll_cell.find("a")
            if enroll_link:
                e_url = enroll_link.get("href", "")
                if e_url:
                    enrollment_url = urljoin(self.base_url, e_url)

        # 6. Extraer Fecha (Siempre columna 0?)
        # Asumimos columna 0 para fecha
        date_str = ""
        if len(cells) > 0:
            date_str = cells[0].get_text(strip=True)

        # 7. Tipo de competición (Última columna o Ancla + 3?)
        # La estructura típica es: ... | Regl | Insc | ? | Tipo
        # Regl=4, Insc=5, ?=6, Tipo=7. Diff = +3
        type_index = regl_index + 3
        comp_type = None
        if type_index < len(cells):
            comp_type = cells[type_index].get_text(strip=True)

        # Detectar modificaciones
        has_modifications = self._has_highlight_background(row)

        return RawCompetition(
            name=name,
            date_str=self._normalize_date(date_str, month, year),
            pdf_url=pdf_url,
            enrollment_url=enrollment_url,
            has_modifications=has_modifications,
            location=location,
            competition_type=comp_type,
        )

    def _extract_enrollment_url(self, cells: list[Tag]) -> str | None:
        """Extrae la URL de inscripción de la celda correspondiente."""
        if len(cells) <= 5:
            return None

        cell = cells[5]
        link = cell.find("a")
        if not link:
            return None

        url = link.get("href", "")
        if not url:
            return None

        return urljoin(self.base_url, url)

    def _extract_additional_dates(self, date_str: str) -> list[str]:
        """
        Extrae fechas adicionales de strings como "17y18.01 (S-D)".

        Returns:
            Lista de fechas adicionales en formato "DD/MM/YYYY"
        """
        additional_dates = []

        try:
            # Caso: "17y18.01 (S-D)" -> ["18/01/2026"]
            range_match = re.match(r"(\d{1,2})y(\d{1,2})\.(\d{2})", date_str)
            if range_match:
                day1, day2, month_num = range_match.groups()
                # Solo agregar días adicionales (el día 1 es la fecha principal)
                if day1 != day2:
                    # Necesitamos el año del contexto. Por ahora asumimos el año actual
                    # En una implementación completa, esto vendría del parámetro year
                    from datetime import date

                    current_year = date.today().year
                    additional_dates.append(f"{int(day2):02d}/{int(month_num):02d}/{current_year}")

            # Caso: "17,18,19/01" -> ["18/01/2026", "19/01/2026"]
            comma_match = re.match(r"(\d{1,2})(?:,(\d{1,2}))(?:,(\d{1,2}))?[/-](\d{1,2})", date_str)
            if comma_match:
                days = [g for g in comma_match.groups()[:-1] if g]
                month_num = comma_match.groups()[-1]

                if len(days) > 1:
                    from datetime import date

                    current_year = date.today().year
                    # El primer día es la fecha principal, agregar los demás
                    for day in days[1:]:
                        additional_dates.append(
                            f"{int(day):02d}/{int(month_num):02d}/{current_year}"
                        )

        except Exception as e:
            logger.warning(f"Error parseando fechas adicionales de '{date_str}': {e}")

        return additional_dates

    def _normalize_date(self, date_str: str, month: int, year: int) -> str:  # noqa: ARG002
        """
        Normaliza el formato de fecha del calendario a formato legible.

        Entrada: "03.01 (S)" o "17y18.01 (S-D)"
        Salida: "3 enero 2026" o "17-18 enero 2026"
        """
        if not date_str:
            return ""

        # Limpiar paréntesis con día de la semana
        date_str = re.sub(r"\s*\([^)]*\)", "", date_str).strip()

        # Patrón para fechas con rango: "17y18.01"
        range_match = re.match(r"(\d{1,2})y(\d{1,2})\.(\d{2})", date_str)
        if range_match:
            day1, day2, month_num = range_match.groups()
            month_name = MONTHS_BY_NUMBER.get(int(month_num), f"mes {month_num}")
            return f"{int(day1)}-{int(day2)} {month_name} {year}"

        # Patrón para fecha simple: "03.01"
        simple_match = re.match(r"(\d{1,2})\.(\d{2})", date_str)
        if simple_match:
            day, month_num = simple_match.groups()
            month_name = MONTHS_BY_NUMBER.get(int(month_num), f"mes {month_num}")
            return f"{int(day)} {month_name} {year}"

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
        Obtiene competiciones para múltiples meses desde el calendario completo.

        Args:
            months: Lista de tuplas (mes, año) - usado para filtrado posterior

        Returns:
            Lista combinada de competiciones
        """
        try:
            # Obtener el calendario completo (sin parámetros de mes/año específicos)
            url = f"{self.base_url}{self.calendar_path}"
            logger.info(f"Obteniendo calendario completo: {url}")

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Parsear todas las competiciones
            all_competitions = self.parse_calendar_html(
                response.text, 1, 2026
            )  # Valores por defecto

            # Filtrar por los meses solicitados
            filtered_competitions = []
            for comp in all_competitions:
                # Intentar parsear la fecha para filtrar
                try:
                    if "/" in comp.date_str:
                        day_month = comp.date_str.split("/")[0:2]
                        if len(day_month) == 2:
                            month = int(day_month[1])
                            # Asumir año actual para filtrado básico
                            current_year = date.today().year
                            if (month, current_year) in months:
                                filtered_competitions.append(comp)
                        else:
                            # Si no se puede parsear, incluirla
                            filtered_competitions.append(comp)
                    else:
                        # Si no tiene formato esperado, incluirla
                        filtered_competitions.append(comp)
                except (ValueError, IndexError):
                    # Si hay error en el parseo, incluirla
                    filtered_competitions.append(comp)

            logger.info(
                f"Filtradas {len(filtered_competitions)} competiciones para los meses solicitados"
            )
            return filtered_competitions

        except Exception as e:
            logger.error(f"Error obteniendo calendario completo: {e}")
            raise WebScraperError(f"Error obteniendo calendario: {e}") from e


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


def parse_date_string(date_str: str, year: int) -> date | None:
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
