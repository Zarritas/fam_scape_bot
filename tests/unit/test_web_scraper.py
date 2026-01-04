"""
Tests unitarios para el web scraper.
"""

import pytest
from datetime import date

from src.scraper.web_scraper import (
    WebScraper,
    get_current_and_next_months,
    parse_date_string,
)
from src.scraper.models import RawCompetition


class TestWebScraper:
    """Tests para la clase WebScraper."""
    
    def test_parse_calendar_html(self, sample_calendar_html: str):
        """Test que parsea correctamente el HTML del calendario."""
        scraper = WebScraper()
        competitions = scraper._parse_calendar_html(sample_calendar_html, 2026)
        
        assert len(competitions) == 3
        
        # Verificar primera competición
        comp1 = competitions[0]
        assert "Control" in comp1.name or "control" in comp1.name.lower()
        assert "pdf" in comp1.pdf_url.lower()
        assert comp1.has_modifications is False
        
    def test_detect_yellow_background(self, sample_calendar_html: str):
        """Test que detecta el fondo amarillo (modificaciones)."""
        scraper = WebScraper()
        competitions = scraper._parse_calendar_html(sample_calendar_html, 2026)
        
        # La segunda competición tiene fondo amarillo
        modified_comps = [c for c in competitions if c.has_modifications]
        assert len(modified_comps) >= 1
        
    def test_extract_date_from_row(self):
        """Test de extracción de fechas de filas."""
        from bs4 import BeautifulSoup
        
        scraper = WebScraper()
        
        # Crear fila de prueba
        html = "<tr><td>11 de enero</td><td>Competición</td></tr>"
        soup = BeautifulSoup(html, "lxml")
        row = soup.find("tr")
        
        date_str = scraper._extract_date_from_row(row)
        assert "11" in date_str
        assert "enero" in date_str
        
    def test_build_calendar_url(self):
        """Test construcción de URL con parámetros."""
        scraper = WebScraper(
            base_url="https://test.com",
            calendar_path="/calendario?id=1"
        )
        
        url = scraper._build_calendar_url(1, 2026)
        
        assert "mes=1" in url
        assert "ano=2026" in url
        assert "https://test.com" in url
        
    def test_extract_location_from_row(self):
        """Test de extracción de ubicación."""
        from bs4 import BeautifulSoup
        
        scraper = WebScraper()
        
        html = "<tr><td>Prueba en Gallur</td></tr>"
        soup = BeautifulSoup(html, "lxml")
        row = soup.find("tr")
        
        location = scraper._extract_location_from_row(row)
        assert location == "Gallur"


class TestGetCurrentAndNextMonths:
    """Tests para la función get_current_and_next_months."""
    
    def test_returns_two_months(self):
        """Debe retornar exactamente dos meses."""
        months = get_current_and_next_months()
        assert len(months) == 2
        
    def test_returns_correct_format(self):
        """Cada elemento debe ser tupla (mes, año)."""
        months = get_current_and_next_months()
        
        for month, year in months:
            assert 1 <= month <= 12
            assert year >= 2024
            
    def test_december_to_january(self, monkeypatch):
        """Test del cambio de año diciembre -> enero."""
        # Simular que estamos en diciembre 2025
        from datetime import date
        monkeypatch.setattr(
            "src.scraper.web_scraper.date",
            type("MockDate", (), {
                "today": staticmethod(lambda: date(2025, 12, 15))
            })
        )
        
        # Re-importar para aplicar mock
        from src.scraper import web_scraper
        months = web_scraper.get_current_and_next_months()
        
        # Debería tener diciembre 2025 y enero 2026
        assert (12, 2025) in months
        assert (1, 2026) in months


class TestParseDateString:
    """Tests para la función parse_date_string."""
    
    def test_parse_spanish_date(self):
        """Test parsing de fecha en español."""
        result = parse_date_string("11 de enero", 2026)
        
        assert result is not None
        assert result.day == 11
        assert result.month == 1
        assert result.year == 2026
        
    def test_parse_numeric_date(self):
        """Test parsing de fecha numérica."""
        result = parse_date_string("11/01", 2026)
        
        assert result is not None
        assert result.day == 11
        assert result.month == 1
        
    def test_parse_invalid_date(self):
        """Test que retorna None para fechas inválidas."""
        result = parse_date_string("invalid date", 2026)
        assert result is None
        
    def test_parse_empty_string(self):
        """Test que retorna None para string vacío."""
        result = parse_date_string("", 2026)
        assert result is None


class TestRawCompetition:
    """Tests para el modelo RawCompetition."""
    
    def test_absolute_url(self):
        """Test que convierte URLs relativas a absolutas."""
        comp = RawCompetition(
            name="Test",
            date_str="11 de enero",
            pdf_url="/files/test.pdf",
        )
        
        assert comp.pdf_url.startswith("http")
        
    def test_keeps_absolute_url(self):
        """Test que mantiene URLs absolutas sin cambios."""
        comp = RawCompetition(
            name="Test",
            date_str="11 de enero",
            pdf_url="https://example.com/test.pdf",
        )
        
        assert comp.pdf_url == "https://example.com/test.pdf"
