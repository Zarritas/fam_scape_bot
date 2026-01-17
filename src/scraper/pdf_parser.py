"""
Parser de PDFs de competiciones de la FAM.

Extrae información estructurada de los PDFs de convocatorias:
- Fecha de la competición
- Lugar
- Tablas de pruebas (carreras y concursos)
"""

import contextlib
import re
from datetime import date, time
from io import BytesIO

import pdfplumber

from src.scraper.models import (
    Competition,
    Event,
    EventType,
    Sex,
    normalize_discipline,
)
from src.utils.hash import calculate_pdf_hash
from src.utils.logging import get_logger

logger = get_logger(__name__)


class PDFParserError(Exception):
    """Error durante el parsing de PDF."""

    pass


class PDFParser:
    """
    Parser para PDFs de convocatorias de competiciones FAM.
    """

    # Meses en español
    MONTHS_ES = {
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

    def parse(
        self,
        pdf_content: bytes,
        name: str = "",
        pdf_url: str = "",
        enrollment_url: str | None = None,
        has_modifications: bool = False,
        competition_type: str | None = None,
    ) -> Competition:
        """
        Parsea un PDF de convocatoria FAM y extrae toda la información.

        Estructura típica de PDFs FAM:
        - Página 1: Información básica (lugar, fecha, organizador)
        - Páginas siguientes: Sección HORARIO con tablas de CARRERAS y CONCURSOS
        - Tablas con columnas: tiempos, pruebas, sexo, series, etc.

        Args:
            pdf_content: Contenido binario del PDF
            name: Nombre de la competición (opcional)
            pdf_url: URL del PDF (para referencia)
            has_modifications: Si tiene marcador de modificaciones
            competition_type: Tipo de competición (PC, AL, etc.)

        Returns:
            Competition con todos los datos extraídos

        Raises:
            PDFParserError: Si hay error en el parsing
        """
        pdf_hash = calculate_pdf_hash(pdf_content)
        logger.info(f"Parseando PDF FAM: {name or pdf_url} (hash: {pdf_hash[:8]}...)")

        try:
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                # Extraer texto completo de todas las páginas
                full_text = ""
                all_tables = []

                for page in pdf.pages:
                    # Extraer texto con manejo de encoding
                    try:
                        text = page.extract_text() or ""
                        full_text += text + "\n"
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        logger.warning("Error de encoding en página, continuando...")
                        continue

                    # Extraer tablas
                    try:
                        tables = page.extract_tables() or []
                        all_tables.extend(tables)
                    except Exception as e:
                        logger.warning(f"Error extrayendo tablas de página: {e}")
                        continue

                # Extraer información básica
                location = self._extract_location(full_text)
                competition_date = self._extract_date(full_text)

                # Si no se pudo extraer fecha, usar fecha por defecto
                if not competition_date:
                    competition_date = date.today()
                    logger.warning("No se pudo extraer fecha, usando fecha actual")

                # Extraer eventos de las tablas
                events = self._extract_events_from_tables(all_tables)

                # Extraer nombre si no se proporcionó
                if not name:
                    name = self._extract_competition_name(full_text) or "Competición sin nombre"

                # Crear objeto Competition
                competition = Competition(
                    name=name,
                    competition_date=competition_date,
                    location=location or "Madrid",
                    pdf_url=pdf_url,
                    enrollment_url=enrollment_url,
                    pdf_hash=pdf_hash,
                    has_modifications=has_modifications,
                    competition_type=competition_type,
                    events=events,
                )

                logger.info(f"PDF parseado exitosamente: {len(events)} eventos encontrados")
                return competition

        except Exception as e:
            logger.error(f"Error parseando PDF: {e}")
            raise PDFParserError(f"Error parseando PDF: {e}") from e

    def _extract_competition_name(self, text: str) -> str | None:
        """Extrae el nombre de la competición del texto."""
        # Buscar patrones comunes de nombres de competiciones
        patterns = [
            r"FEDERACIÓN DE ATLETISMO DE MADRID\s*\n\s*(.+?)\s*\n",
            r"(.+?)\s*\n\s*LUGAR:",
            r"(.+?)\s*\n\s*DIA:",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name) > 5:  # Evitar matches demasiado cortos
                    return name

        return None

    def _extract_location(self, text: str) -> str | None:
        """Extrae el lugar de la competición."""
        # Buscar patrón "LUGAR:" seguido del nombre del lugar
        match = re.search(r"LUGAR:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # También buscar lugares conocidos en el texto
        known_venues = [
            "Vallehermoso",
            "Gallur",
            "Alcorcón",
            "Alcobendas",
            "Pista Cubierta",
            "Polideportivo",
        ]

        for venue in known_venues:
            if venue.lower() in text.lower():
                return venue

        return None

    def _extract_date(self, text: str) -> date | None:
        """Extrae la fecha de la competición."""
        # Buscar diferentes patrones de fecha
        patterns = [
            r"DIA:\s*(.+?)(?:\n|$)",  # DIA: formato
            r"Fecha:\s*(.+?)(?:\n|$)",  # Fecha: formato
            r"Fecha de la competición:\s*(.+?)(?:\n|$)",  # Fecha de la competición: formato
        ]

        date_str = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                break

        if not date_str:
            return None

        # Intentar diferentes formatos de fecha
        # Formato: 03/01/2026
        date_match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", date_str)
        if date_match:
            day, month, year = date_match.groups()
            try:
                return date(int(year), int(month), int(day))
            except ValueError:
                pass

        # Formato: 17 y 18/01/2026
        date_match = re.search(r"(\d{1,2})\s*y\s*(\d{1,2})[/-](\d{1,2})[/-](\d{4})", date_str)
        if date_match:
            # Para fechas múltiples, usar la primera fecha
            day1, day2, month, year = date_match.groups()
            try:
                return date(int(year), int(month), int(day1))
            except ValueError:
                pass

        # Formato: 11 de enero de 2026
        date_match = re.search(r"(\d{1,2})\s*de\s+(\w+)\s*de\s+(\d{4})", date_str, re.IGNORECASE)
        if date_match:
            day, month_name, year = date_match.groups()
            month = self.MONTHS_ES.get(month_name.lower())
            if month:
                try:
                    return date(int(year), month, int(day))
                except ValueError:
                    pass

        return None

    def _extract_events_from_tables(self, tables: list) -> list[Event]:
        """Extrae eventos de las tablas del PDF."""
        events = []

        for table in tables:
            if not table or len(table) < 2:
                continue

            # Determinar si es tabla de CARRERAS o CONCURSOS
            header = table[0] if table[0] else []
            header_text = " ".join(str(cell) for cell in header if cell).upper()

            if "CARRERAS" in header_text:
                event_type = EventType.CARRERA
            elif "CONCURSOS" in header_text:
                event_type = EventType.CONCURSO
            else:
                # Para tablas mixtas, determinar el tipo por fila individual
                event_type = None

            # Procesar filas de datos (saltar header)
            for row in table[1:]:
                if not row or len(row) < 3:
                    continue

                try:
                    # Si no hay tipo determinado, intentar detectar por disciplina
                    current_event_type = event_type
                    if current_event_type is None:
                        # Intentar detectar tipo por nombre de disciplina
                        discipline = str(row[0]).strip() if row[0] else ""
                        if any(
                            keyword in discipline.upper()
                            for keyword in [
                                "60",
                                "100",
                                "200",
                                "400",
                                "800",
                                "1500",
                                "3000",
                                "5000",
                                "10000",
                                "110",
                                "400V",
                                "3000S",
                                "3000O",
                            ]
                        ):
                            current_event_type = EventType.CARRERA
                        elif any(
                            keyword in discipline.upper()
                            for keyword in [
                                "ALTURA",
                                "PÉRTIGA",
                                "PESO",
                                "DISCO",
                                "MARTILLO",
                                "JABALINA",
                                "LONGITUD",
                                "TRIPLE",
                            ]
                        ):
                            current_event_type = EventType.CONCURSO
                        else:
                            continue

                    event = self._parse_event_row(row, current_event_type)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.warning(f"Error procesando fila de evento: {e}")
                    continue

        return events

    def _parse_event_row(self, row: list, event_type: EventType) -> Event | None:
        """Parsea una fila de tabla para extraer información de evento."""
        if len(row) < 4:
            return None

        # Unir celdas que puedan estar divididas
        row_text = [str(cell).strip() for cell in row if cell and str(cell).strip()]

        if len(row_text) < 3:
            return None

        # Extraer hora (primer campo que contenga hora)
        scheduled_time = None
        discipline = ""
        sex = Sex.MASCULINO  # default
        category = ""

        for cell in row_text:
            # Buscar hora (HH:MM)
            time_match = re.search(r"(\d{1,2}):(\d{2})", cell)
            if time_match and not scheduled_time:
                hour, minute = time_match.groups()
                with contextlib.suppress(ValueError):
                    scheduled_time = time(int(hour), int(minute))

            # Buscar disciplina (metros, saltos, lanzamientos)
            if not discipline:
                # Buscar patrones de disciplina
                disc_match = re.search(r"(\d+)\s*(?:ml|m\.?|metros?)", cell, re.IGNORECASE)
                if disc_match:
                    discipline = f"{disc_match.group(1)}m"
                elif "ALTURA" in cell.upper():
                    discipline = "altura"
                elif "LONGITUD" in cell.upper():
                    discipline = "longitud"
                elif "TRIPLE" in cell.upper():
                    discipline = "triple"
                elif "PESO" in cell.upper():
                    discipline = "peso"
                elif "DISCO" in cell.upper():
                    discipline = "disco"
                elif "MARTILLO" in cell.upper():
                    discipline = "martillo"
                elif "JABALINA" in cell.upper():
                    discipline = "jabalina"
                elif "PÉRTIGA" in cell.upper() or "PERTIGA" in cell.upper():
                    discipline = "pértiga"

            # Determinar sexo
            if "F" in cell.upper() or "FEMENINO" in cell.upper():
                sex = Sex.FEMENINO
            elif "M" in cell.upper() or "MASCULINO" in cell.upper():
                sex = Sex.MASCULINO

        if not discipline:
            return None

        # Normalizar disciplina
        normalized_discipline = normalize_discipline(discipline)
        if not normalized_discipline:
            return None

        return Event(
            discipline=normalized_discipline,
            event_type=event_type,
            sex=sex,
            scheduled_time=scheduled_time,
            category=category or "",
        )
