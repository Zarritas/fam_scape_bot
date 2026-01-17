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

            # Determinar el formato de la tabla
            header = table[0] if table[0] else []
            header_text = " ".join(str(cell).strip() for cell in header if cell).upper()

            # Formato 1: Headers de sección ("CARRERAS", "CONCURSOS")
            if "CARRERAS" in header_text:
                event_type = EventType.CARRERA
                # Procesar filas de datos
                for row in table[1:]:
                    if not row or len(row) < 3:
                        continue
                    try:
                        event = self._parse_event_row(row, event_type)
                        if event:
                            events.append(event)
                    except Exception as e:
                        logger.warning(f"Error procesando fila de evento: {e}")
                        continue

            elif "CONCURSOS" in header_text:
                event_type = EventType.CONCURSO
                # Procesar filas de datos
                for row in table[1:]:
                    if not row or len(row) < 3:
                        continue
                    try:
                        event = self._parse_event_row(row, event_type)
                        if event:
                            events.append(event)
                    except Exception as e:
                        logger.warning(f"Error procesando fila de evento: {e}")
                        continue

            # Formato 2: Tabla de test con header ["Prueba", "Sexo", "Hora", "Categoría"]
            elif "PRUEBA" in header_text and "SEXO" in header_text:
                # Tabla de test unitario - procesar todas las filas como datos
                for row in table[1:]:  # Skip header
                    if not row or len(row) < 4:
                        continue
                    try:
                        # Auto-detectar tipo por disciplina en primera columna
                        discipline = str(row[0]).strip() if row[0] else ""
                        if any(keyword in discipline.upper() for keyword in [
                            "60", "100", "200", "400", "800", "1500", "3000", "5000", "10000",
                            "110", "400V", "3000S", "3000O"
                        ]):
                            event_type = EventType.CARRERA
                        elif any(keyword in discipline.upper() for keyword in [
                            "ALTURA", "PÉRTIGA", "PESO", "DISCO", "MARTILLO", "JABALINA",
                            "LONGITUD", "TRIPLE"
                        ]):
                            event_type = EventType.CONCURSO
                        else:
                            continue

                        event = self._parse_event_row(row, event_type)
                        if event:
                            events.append(event)
                    except Exception as e:
                        logger.warning(f"Error procesando fila de test: {e}")
                        continue

            # Formato 3: Eventos individuales (PDFs reales con formato horario)
            else:
                # Intentar diferentes estrategias
                # Estrategia 1: Cada tabla es un evento individual
                try:
                    event = self._parse_event_header(header)
                    if event:
                        events.append(event)
                        # Procesar filas adicionales si existen
                        for row in table[1:]:
                            if not row or len(row) < 3:
                                continue
                            try:
                                additional_event = self._parse_event_row(row, event.event_type)
                                if additional_event:
                                    events.append(additional_event)
                            except Exception as e:
                                logger.warning(f"Error procesando fila adicional: {e}")
                                continue
                        continue  # Si se procesó como header, no continuar con otras estrategias
                except Exception as e:
                    logger.warning(f"Error procesando tabla como evento único: {e}")

                # Estrategia 2: Procesar todas las filas como datos individuales
                for row in table:
                    if not row or len(row) < 3:
                        continue
                    try:
                        # Auto-detectar tipo por contenido de la fila
                        row_text = " ".join(str(cell) for cell in row if cell).upper()
                        if any(keyword in row_text for keyword in [
                            "SERIE", "CARRERA", "METROS", "60M", "100M", "200M", "400M"
                        ]):
                            event_type = EventType.CARRERA
                        elif any(keyword in row_text for keyword in [
                            "ALTURA", "PESO", "DISCO", "PÉRTIGA", "LONGITUD", "TRIPLE", "MARTILLO", "JABALINA"
                        ]):
                            event_type = EventType.CONCURSO
                        else:
                            continue

                        event = self._parse_event_row(row, event_type)
                        if event:
                            events.append(event)
                    except Exception as e:
                        logger.warning(f"Error procesando fila con auto-detección: {e}")
                        continue

        return events

    def _parse_event_header(self, header: list) -> Event | None:
        """Parsea un header de tabla que contiene información de evento."""
        if len(header) < 3:
            return None

        # Headers típicos: ["hora1", "hora2", "hora3", "hora4", "disciplina", "sexo", "serie"]
        # Ejemplo: ['14:50', '15:20', '15:25', '15:30', '60 Heptatlón', 'M', 'SERIE 1']

        header_text = [str(cell).strip() for cell in header if cell and str(cell).strip()]

        if len(header_text) < 3:
            return None

        # El penúltimo campo suele ser el sexo
        sex_str = header_text[-2] if len(header_text) >= 2 else ""
        if sex_str.upper() == "M":
            sex = Sex.MASCULINO
        elif sex_str.upper() == "F":
            sex = Sex.FEMENINO
        else:
            sex = Sex.MASCULINO  # default

        # El antepenúltimo campo suele ser la disciplina
        discipline_str = header_text[-3] if len(header_text) >= 3 else ""
        discipline = normalize_discipline(discipline_str)

        if not discipline:
            return None

        # Determinar tipo de evento
        if any(keyword in discipline.upper() for keyword in [
            "60", "100", "200", "400", "800", "1500", "3000", "5000", "10000",
            "110", "400V", "3000S", "3000O"
        ]):
            event_type = EventType.CARRERA
        elif any(keyword in discipline.upper() for keyword in [
            "ALTURA", "PÉRTIGA", "PESO", "DISCO", "MARTILLO", "JABALINA",
            "LONGITUD", "TRIPLE"
        ]):
            event_type = EventType.CONCURSO
        else:
            # No se pudo determinar el tipo
            return None

        # Extraer hora del primer campo si existe
        scheduled_time = None
        first_cell = header_text[0]
        time_match = re.search(r"(\d{1,2}):(\d{2})", first_cell)
        if time_match:
            hour, minute = time_match.groups()
            with contextlib.suppress(ValueError):
                scheduled_time = time(int(hour), int(minute))

        # Extraer categoría del último campo si contiene "SERIE" o similar
        category = "Absoluto"
        last_cell = header_text[-1]
        if "SERIE" in last_cell.upper() or any(word in last_cell.upper() for word in ["SUB", "MASTER", "JUVENIL", "CADETE"]):
            category = last_cell

        return Event(
            discipline=discipline,
            event_type=event_type,
            sex=sex,
            scheduled_time=scheduled_time,
            category=category,
        )

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

        # Extraer disciplina, sexo y categoría de los campos restantes
        remaining_cells = [cell for cell in row_text if cell and not re.search(r"(\d{1,2}):(\d{2})", cell)]

        for cell in remaining_cells:
            # Buscar patrón de disciplina (ej: "60m", "Altura", "Peso")
            if not discipline:
                # Normalizar disciplina
                discipline = normalize_discipline(cell)

            # Buscar sexo
            if "M" in cell.upper() and sex == Sex.MASCULINO:
                sex = Sex.MASCULINO
            elif "F" in cell.upper():
                sex = Sex.FEMENINO

            # Buscar categoría (última parte)
            if not category and len(cell.split()) > 1:
                parts = cell.split()
                if len(parts) > 1:
                    category = " ".join(parts[1:])  # Todo después del primer espacio

        # Si no se encontró disciplina válida, intentar con el primer campo
        if not discipline and remaining_cells:
            discipline = normalize_discipline(remaining_cells[0])

        if not discipline:
            return None

        return Event(
            discipline=discipline,
            event_type=event_type,
            sex=sex,
            scheduled_time=scheduled_time,
            category=category or "Absoluto",
        )
