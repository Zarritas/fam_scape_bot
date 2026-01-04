"""
Tests unitarios para el PDF parser.
"""

import pytest
from datetime import date, time

from src.scraper.pdf_parser import PDFParser, PDFParserError
from src.scraper.models import (
    Event,
    EventType,
    Sex,
    Competition,
    normalize_discipline,
    detect_event_type,
)


class TestPDFParser:
    """Tests para la clase PDFParser."""
    
    def test_extract_date_spanish_format(self):
        """Test extracción de fecha en formato español."""
        parser = PDFParser()
        text = "Fecha: 11 de enero de 2026"
        
        result = parser._extract_date(text)
        
        assert result is not None
        assert result.day == 11
        assert result.month == 1
        assert result.year == 2026
        
    def test_extract_date_numeric_format(self):
        """Test extracción de fecha en formato numérico."""
        parser = PDFParser()
        text = "Fecha de la competición: 15/03/2026"
        
        result = parser._extract_date(text)
        
        assert result is not None
        assert result.day == 15
        assert result.month == 3
        assert result.year == 2026
        
    def test_extract_location(self):
        """Test extracción de lugar."""
        parser = PDFParser()
        text = "Lugar: Polideportivo Municipal de Gallur"
        
        result = parser._extract_location(text)
        
        assert result is not None
        assert "Gallur" in result
        
    def test_extract_location_from_known_venue(self):
        """Test que detecta lugares conocidos."""
        parser = PDFParser()
        text = "Pruebas en la pista de Vallehermoso"
        
        result = parser._extract_location(text)
        
        assert result is not None
        assert "Vallehermoso" in result
        
    def test_parse_events_table(self, sample_events_table: list[list[str]]):
        """Test parsing de tabla de pruebas."""
        parser = PDFParser()
        
        events = parser._parse_events_table(sample_events_table)
        
        assert len(events) >= 4
        
        # Verificar que hay carreras y concursos
        carreras = [e for e in events if e.event_type == EventType.CARRERA]
        concursos = [e for e in events if e.event_type == EventType.CONCURSO]
        
        assert len(carreras) > 0
        assert len(concursos) > 0
        
    def test_parse_event_row_with_columns(self):
        """Test parsing de fila con columnas identificadas."""
        parser = PDFParser()
        row = ["60m", "M", "10:00", "Senior"]
        
        event = parser._parse_event_row(
            row,
            discipline_col=0,
            sex_col=1,
            time_col=2,
            category_col=3,
        )
        
        assert event is not None
        assert "60" in event.discipline
        assert event.sex == Sex.MASCULINO
        assert event.scheduled_time == time(10, 0)
        assert event.category == "Senior"
        
    def test_parse_time_valid(self):
        """Test parsing de hora válida."""
        parser = PDFParser()
        
        result = parser._parse_time("10:30")
        
        assert result == time(10, 30)
        
    def test_parse_time_invalid(self):
        """Test parsing de hora inválida."""
        parser = PDFParser()
        
        result = parser._parse_time("invalid")
        
        assert result is None
        
    def test_parse_time_empty(self):
        """Test que retorna None para hora vacía."""
        parser = PDFParser()
        
        result = parser._parse_time("")
        
        assert result is None
        
    def test_extract_events_from_text(self, sample_pdf_text: str):
        """Test extracción de pruebas del texto."""
        parser = PDFParser()
        
        events = parser._extract_events_from_text(sample_pdf_text)
        
        # Debería encontrar varias pruebas
        assert len(events) >= 4
        
        # Verificar que hay variedad
        disciplines = set(e.discipline for e in events)
        assert len(disciplines) >= 3
        
    def test_extract_sex_masculine(self):
        """Test detección de sexo masculino."""
        parser = PDFParser()
        row = ["60m", "Masculino", "10:00"]
        
        sex = parser._extract_sex_from_row(row, sex_col=1)
        
        assert sex == Sex.MASCULINO
        
    def test_extract_sex_feminine(self):
        """Test detección de sexo femenino."""
        parser = PDFParser()
        row = ["60m", "Femenino", "10:00"]
        
        sex = parser._extract_sex_from_row(row, sex_col=1)
        
        assert sex == Sex.FEMENINO


class TestNormalizeDiscipline:
    """Tests para la función normalize_discipline."""
    
    @pytest.mark.parametrize("input_val,expected", [
        ("60 m", "60"),
        ("60m", "60"),
        ("100 m", "100"),
        ("100m", "100"),
        ("400 m", "400"),
        ("salto de altura", "Altura"),
        ("altura", "Altura"),
        ("salto con pértiga", "Pértiga"),
        ("pértiga", "Pértiga"),
        ("pertiga", "Pértiga"),  # Sin acento
        ("lanzamiento de peso", "Peso"),
    ])
    def test_normalize_known_disciplines(self, input_val: str, expected: str):
        """Test normalización de disciplinas conocidas."""
        result = normalize_discipline(input_val)
        assert result == expected
        
    def test_normalize_unknown_discipline(self):
        """Test que mantiene disciplinas desconocidas."""
        result = normalize_discipline("Prueba Especial")
        assert result == "Prueba Especial"
        
    def test_normalize_with_whitespace(self):
        """Test que limpia espacios."""
        result = normalize_discipline("  60 m  ")
        assert result == "60"


class TestDetectEventType:
    """Tests para la función detect_event_type."""
    
    @pytest.mark.parametrize("discipline,expected", [
        ("60", EventType.CARRERA),
        ("100m", EventType.CARRERA),
        ("400m vallas", EventType.CARRERA),
        ("Altura", EventType.CONCURSO),
        ("Longitud", EventType.CONCURSO),
        ("Triple Salto", EventType.CONCURSO),
        ("Pértiga", EventType.CONCURSO),
        ("Peso", EventType.CONCURSO),
        ("Disco", EventType.CONCURSO),
        ("Martillo", EventType.CONCURSO),
        ("Jabalina", EventType.CONCURSO),
    ])
    def test_detect_event_type(self, discipline: str, expected: EventType):
        """Test detección de tipo de prueba."""
        result = detect_event_type(discipline)
        assert result == expected


class TestEvent:
    """Tests para el modelo Event."""
    
    def test_display_name(self):
        """Test generación de nombre para mostrar."""
        event = Event(
            discipline="400",
            event_type=EventType.CARRERA,
            sex=Sex.MASCULINO,
        )
        
        assert event.display_name == "400 Masculino"
        
    def test_subscription_key_masculine(self):
        """Test clave de suscripción masculina."""
        event = Event(
            discipline="Pértiga",
            event_type=EventType.CONCURSO,
            sex=Sex.MASCULINO,
        )
        
        assert event.subscription_key == "pértiga_M"
        
    def test_subscription_key_feminine(self):
        """Test clave de suscripción femenina."""
        event = Event(
            discipline="Altura",
            event_type=EventType.CONCURSO,
            sex=Sex.FEMENINO,
        )
        
        assert event.subscription_key == "altura_F"


class TestCompetition:
    """Tests para el modelo Competition."""
    
    @pytest.fixture
    def sample_competition(self) -> Competition:
        """Competición de ejemplo con pruebas."""
        return Competition(
            name="Control de Pista",
            competition_date=date(2026, 1, 11),
            location="Gallur",
            pdf_url="https://example.com/test.pdf",
            pdf_hash="abc123",
            events=[
                Event("60", EventType.CARRERA, Sex.MASCULINO),
                Event("60", EventType.CARRERA, Sex.FEMENINO),
                Event("Altura", EventType.CONCURSO, Sex.FEMENINO),
                Event("Pértiga", EventType.CONCURSO, Sex.MASCULINO),
            ]
        )
    
    def test_get_events_by_type_carreras(self, sample_competition: Competition):
        """Test filtrado por tipo carrera."""
        carreras = sample_competition.get_events_by_type(EventType.CARRERA)
        
        assert len(carreras) == 2
        assert all(e.event_type == EventType.CARRERA for e in carreras)
        
    def test_get_events_by_type_concursos(self, sample_competition: Competition):
        """Test filtrado por tipo concurso."""
        concursos = sample_competition.get_events_by_type(EventType.CONCURSO)
        
        assert len(concursos) == 2
        assert all(e.event_type == EventType.CONCURSO for e in concursos)
        
    def test_get_events_by_sex(self, sample_competition: Competition):
        """Test filtrado por sexo."""
        femenino = sample_competition.get_events_by_sex(Sex.FEMENINO)
        
        assert len(femenino) == 2
        assert all(e.sex == Sex.FEMENINO for e in femenino)
        
    def test_get_events_by_discipline(self, sample_competition: Competition):
        """Test búsqueda por disciplina."""
        events = sample_competition.get_events_by_discipline("60")
        
        assert len(events) == 2
