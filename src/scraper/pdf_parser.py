"""
Parser de PDFs de competiciones de la FAM.

Extrae información estructurada de los PDFs de convocatorias:
- Fecha de la competición
- Lugar
- Tablas de pruebas (carreras y concursos)
"""

import re
from datetime import date, time
from io import BytesIO

import pdfplumber

from src.scraper.models import (
    Competition,
    Event,
    EventType,
    Sex,
    detect_event_type,
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
    Parser para PDFs de convocatorias de competiciones.
    """

    # Disciplinas comunes para detección por contenido
    COMMON_DISCIPLINES = [
        "60",
        "100",
        "200",
        "300",
        "400",
        "500",
        "600",
        "800",
        "1.000",
        "1500",
        "3000",
        "60m",
        "100m",
        "200m",
        "300m",
        "400m",
        "500m",
        "600m",
        "800m",
        "1000m",
        "1500m",
        "vallas",
        "mv",
        "Altura",
        "Longitud",
        "Pértiga",
        "Triple",
        "Peso",
        "Disco",
        "Jabalina",
        "Martillo",
        "Marcha",
        "Cross",
        "Relevo",
        "Combinada",
    ]

    # Patrones para extraer información
    DATE_PATTERNS = [
        # "11 de enero de 2026"
        r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})",
        # "11/01/2026" o "11-01-2026"
        r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
        # "Fecha: 11 de enero"
        r"[Ff]echa[:\s]+(\d{1,2})\s+(?:de\s+)?(\w+)",
    ]

    LOCATION_PATTERNS = [
        r"[Ll]ugar[:\s]+(?:de\s+|del\s+)?([A-Za-záéíóúñÁÉÍÓÚÑ\.\s,]+)",
        r"[Ii]nstalaci[oó]n[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ\.\s,]+)",
        r"[Ss]ede[:\s]+([A-Za-záéíóúñÁÉÍÓÚÑ\.\s,]+)",
        # Pista conocidas
        r"(Gallur|Vallehermoso|Moratalaz|Getafe|Polideportivo[^,\n\.]+)",
    ]

    # Keywords para identificar secciones de pruebas
    TRACK_KEYWORDS = [
        "carreras",
        "pruebas de pista",
        "velocidad",
        "fondo",
        "vallas",
        "relevos",
        "obstáculos",
    ]

    FIELD_KEYWORDS = [
        "concursos",
        "saltos",
        "lanzamientos",
        "pruebas de campo",
    ]

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

    def __init__(self):
        pass

    def parse(
        self,
        pdf_content: bytes,
        name: str = "",
        pdf_url: str = "",
        has_modifications: bool = False,
        competition_type: str | None = None,
    ) -> Competition:
        """
        Parsea un PDF de convocatoria y extrae toda la información.

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
        logger.info(f"Parseando PDF: {name or pdf_url} (hash: {pdf_hash[:8]}...)")

        try:
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                # Extraer todo el texto
                full_text = ""
                all_tables: list[list[list[str]]] = []

                for page in pdf.pages:
                    text = page.extract_text() or ""
                    full_text += text + "\n"

                    # Extraer tablas de cada página
                    tables = page.extract_tables() or []
                    all_tables.extend(tables)

                # Extraer fecha
                competition_date = self._extract_date(full_text)
                if not competition_date:
                    logger.warning("No se pudo extraer fecha del PDF")
                    competition_date = date.today()

                # Extraer lugar
                location = self._extract_location(full_text)
                if not location:
                    location = "Lugar no especificado"

                # Extraer pruebas de las tablas
                events = self._extract_events_from_tables(all_tables)

                # Si no hay tablas, intentar extraer del texto
                if not events:
                    events = self._extract_events_from_text(full_text)

                logger.info(
                    f"Extraídos: fecha={competition_date}, lugar={location}, pruebas={len(events)}"
                )

                return Competition(
                    name=name or self._extract_name(full_text),
                    competition_date=competition_date,
                    location=location,
                    pdf_url=pdf_url,
                    pdf_hash=pdf_hash,
                    has_modifications=has_modifications,
                    competition_type=competition_type,
                    events=events,
                )

        except Exception as e:
            logger.error(f"Error parseando PDF: {e}")
            raise PDFParserError(f"Error parseando PDF: {e}") from e

    def _extract_date(self, text: str) -> date | None:
        """
        Extrae la fecha de la competición del texto.
        """
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()

                if len(groups) == 3:
                    day = int(groups[0])

                    # Segundo grupo puede ser mes texto o número
                    if groups[1].isdigit():
                        month = int(groups[1])
                    else:
                        month = self.MONTHS_ES.get(groups[1].lower(), 0)

                    # Tercer grupo es el año (o puede no existir)
                    year = int(groups[2]) if len(groups) >= 3 and groups[2] else date.today().year

                    if month and 1 <= day <= 31:
                        try:
                            return date(year, month, day)
                        except ValueError:
                            continue

                elif len(groups) == 2:
                    # Patrón sin año
                    day = int(groups[0])
                    month_str = groups[1].lower()
                    month = self.MONTHS_ES.get(month_str, 0)
                    year = date.today().year

                    if month:
                        try:
                            return date(year, month, day)
                        except ValueError:
                            continue

        return None

    def _extract_location(self, text: str) -> str | None:
        """
        Extrae el lugar de la competición del texto.
        """
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                # Limpiar y limitar longitud
                location = re.sub(r"\s+", " ", location)
                if len(location) > 100:
                    location = location[:100]
                return location

        return None

    def _extract_name(self, text: str) -> str:
        """
        Intenta extraer el nombre de la competición del texto.
        """
        # Buscar en las primeras líneas
        lines = text.split("\n")[:10]

        keywords = [
            "campeonato",
            "copa",
            "trophy",
            "trofeo",
            "memorial",
            "meeting",
            "control",
            "pruebas",
            "jornada",
        ]

        for line in lines:
            line_lower = line.lower()
            for keyword in keywords:
                if keyword in line_lower:
                    # Limpiar el nombre
                    name = line.strip()
                    name = re.sub(r"\s+", " ", name)
                    if len(name) > 150:
                        name = name[:150]
                    return name

        return "Competición"

    def _extract_events_from_tables(
        self,
        tables: list[list[list[str]]],
    ) -> list[Event]:
        """
        Extrae pruebas de las tablas del PDF.
        """
        events: list[Event] = []
        last_time = None

        for table in tables:
            if not table:
                continue

            table_events = self._parse_events_table(table, initial_time=last_time)
            events.extend(table_events)

            # Actualizar last_time con el último tiempo válido encontrado en la tabla
            for e in reversed(table_events):
                if e.scheduled_time:
                    last_time = e.scheduled_time
                    break

        return events

    def _parse_events_table(
        self,
        table: list[list[str]],
        initial_time: time | None = None,
    ) -> list[Event]:
        """
        Parsea una tabla individual de pruebas.
        """
        events: list[Event] = []

        # 1. Intentar detectar columnas por cabecera
        header_row = table[0] if table else []
        discipline_col = None
        sex_col = None
        time_col = None
        category_col = None

        for i, cell in enumerate(header_row):
            if not cell:
                continue
            cell_lower = str(cell).lower()

            if any(kw in cell_lower for kw in ["prueba", "disciplina", "evento"]):
                discipline_col = i
            elif any(kw in cell_lower for kw in ["sexo", "género", "cat"]):
                sex_col = i
            elif any(
                kw in cell_lower for kw in ["hora", "tiempo", "horario", "inicio", "comienzo"]
            ):
                time_col = i
            elif any(kw in cell_lower for kw in ["categoría", "categoria"]):
                category_col = i

        start_index = 1

        # 2. Si no se detectaron columnas clave, intentar detectar por contenido de las primeras filas
        if discipline_col is None or (time_col is None and sex_col is None):
            # Probar en las primeras 3 filas para detectar columnas (heurística)
            for row in table[:3]:
                for i, cell in enumerate(row):
                    if not cell:
                        continue
                    val = str(cell).strip()
                    # Si detectamos una hora en esta columna
                    if time_col is None and re.search(r"\d{1,2}[:\.]\d{2}", val):
                        time_col = i
                    # Si detectamos sexo M o F
                    if sex_col is None and val.upper() in ["M", "F", "M-F", "H", "M ASC", "FEM"]:
                        sex_col = i
                    # Si detectamos una disciplina conocida d
                    if discipline_col is None:  # noqa: SIM102
                        if any(d.lower() in val.lower() for d in self.COMMON_DISCIPLINES):
                            discipline_col = i

            # Si detectamos algo, es una tabla sin cabecera o la cabecera era de datos
            if discipline_col is not None:
                start_index = 0

        # 3. Procesar filas de datos
        last_time = initial_time
        for row in table[start_index:]:
            if not row or all(not cell for cell in row):
                continue

            event = self._parse_event_row(
                row,
                discipline_col=discipline_col,
                sex_col=sex_col,
                time_col=time_col,
                category_col=category_col,
            )

            if event:
                # Si no tiene hora pero el anterior sí, heredarla (común en bloques de pruebas)
                if not event.scheduled_time and last_time:
                    event.scheduled_time = last_time
                elif event.scheduled_time:
                    last_time = event.scheduled_time

                events.append(event)

        return events

    def _parse_event_row(
        self,
        row: list[str],
        discipline_col: int | None,
        sex_col: int | None,
        time_col: int | None,
        category_col: int | None,
    ) -> Event | None:
        """
        Parsea una fila de la tabla de pruebas.
        """
        # Limpiar celdas
        row = [str(c or "").strip() for c in row]
        if all(not c for c in row):
            return None

        # 1. Obtener hora (prioridad alta)
        scheduled_time = None
        if time_col is not None and time_col < len(row):
            scheduled_time = self._parse_time(row[time_col])

        # Fallback: buscar hora en toda la fila si no se encontró
        if not scheduled_time:
            for cell in row:
                st = self._parse_time(cell)
                if st:
                    scheduled_time = st
                    break

        # 2. Obtener disciplina
        discipline = ""
        if discipline_col is not None and discipline_col < len(row):
            discipline = row[discipline_col]
        else:
            discipline = self._find_discipline_in_row(row)

        if not discipline:
            return None

        # Limpiar disciplina de horas (HH:MM o HH.MM) y palabras extra
        if discipline:
            # Normalizar espacios y saltos de línea
            discipline = str(discipline).replace("\n", " ")
            # Eliminar todos los patrones de hora (HH:MM o HH.MM)
            discipline = re.sub(r"\d{1,2}[:\.]\d{2}", "", discipline).strip()
            # Eliminar múltiples espacios
            discipline = re.sub(r"\s+", " ", discipline).strip()
            # Eliminar "serie X" si estorba
            discipline = re.sub(r"[Ss]erie\s*\d+", "", discipline).strip()

        # Normalizar disciplina
        discipline = normalize_discipline(discipline)

        # Detectar tipo de evento
        event_type = detect_event_type(discipline)

        # 3. Obtener sexo
        sex = self._extract_sex_from_row(row, sex_col)

        # 4. Obtener categoría
        category = ""
        if category_col is not None and category_col < len(row):
            category = row[category_col]

        return Event(
            discipline=discipline,
            event_type=event_type,
            sex=sex,
            category=category,
            scheduled_time=scheduled_time,
        )

    def _find_discipline_in_row(self, row: list[str]) -> str:
        """
        Busca una disciplina válida en cualquier celda de la fila.
        """
        discipline_patterns = [
            r"\d{2,5}\s*m",  # 100m, 1500m, etc.
            r"\d+\s*(?:metros?|m\.?)",
            r"vallas?",
            r"obstáculos",
            r"relevos?",
            r"altura",
            r"longitud",
            r"triple",
            r"pértiga",
            r"pertiga",
            r"peso",
            r"disco",
            r"martillo",
            r"jabalina",
            r"marcha",
        ]

        for cell in row:
            if not cell:
                continue
            cell_str = str(cell).lower()

            for pattern in discipline_patterns:
                if re.search(pattern, cell_str):
                    # Retornar la celda completa como disciplina
                    return str(cell).strip()

        return ""

    def _extract_sex_from_row(
        self,
        row: list[str],
        sex_col: int | None,
    ) -> Sex:
        """
        Extrae el sexo de una fila de pruebas.
        """
        # Buscar en columna específica
        if sex_col is not None and sex_col < len(row):
            cell = str(row[sex_col] or "").lower()
            if "f" in cell or "fem" in cell or "muj" in cell:
                return Sex.FEMENINO
            elif "m" in cell or "mas" in cell or "hom" in cell:
                return Sex.MASCULINO

        # Buscar en toda la fila
        row_text = " ".join(str(c or "") for c in row).lower()

        if any(kw in row_text for kw in ["femenino", "fem.", "mujeres", " f "]):
            return Sex.FEMENINO
        elif any(kw in row_text for kw in ["masculino", "mas.", "hombres", " m "]):
            return Sex.MASCULINO

        # Por defecto masculino (más común en los PDFs históricos)
        return Sex.MASCULINO

    def _parse_time(self, time_str: str) -> time | None:
        """
        Parsea una hora en formato HH:MM.
        """
        if not time_str:
            return None

        # Patrón HH:MM o HH.MM
        match = re.search(r"(\d{1,2})[:\.](\d{2})", time_str)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return time(hour, minute)

        return None

    def _extract_events_from_text(self, text: str) -> list[Event]:
        """
        Fallback: extrae pruebas del texto cuando no hay tablas.
        """
        events: list[Event] = []

        # Patrones para pruebas comunes
        discipline_patterns = [
            (r"(\d{2,5})\s*m(?:etros?)?", EventType.CARRERA),
            (r"(\d+)\s*(?:metros? )?vallas?", EventType.CARRERA),
            (r"(\d+)\s*(?:metros? )?obstáculos?", EventType.CARRERA),
            (r"(altura)", EventType.CONCURSO),
            (r"(longitud)", EventType.CONCURSO),
            (r"(triple\s+salto?)", EventType.CONCURSO),
            (r"(pértiga|pertiga)", EventType.CONCURSO),
            (r"(peso)", EventType.CONCURSO),
            (r"(disco)", EventType.CONCURSO),
            (r"(martillo)", EventType.CONCURSO),
            (r"(jabalina)", EventType.CONCURSO),
        ]

        for pattern, event_type in discipline_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                discipline = match.group(1)
                if event_type == EventType.CARRERA and discipline.isdigit():
                    discipline = f"{discipline}m"

                discipline = normalize_discipline(discipline)

                # Buscar contexto para determinar sexo
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end].lower()

                sex = Sex.FEMENINO if "femen" in context or "mujer" in context else Sex.MASCULINO

                # Evitar duplicados
                existing = any(e.discipline == discipline and e.sex == sex for e in events)
                if not existing:
                    events.append(
                        Event(
                            discipline=discipline,
                            event_type=event_type,
                            sex=sex,
                        )
                    )

        return events
