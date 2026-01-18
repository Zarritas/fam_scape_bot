"""
Tests unitarios para el web scraper.
"""

from src.scraper.models import RawCompetition
from src.scraper.web_scraper import (
    WebScraper,
    clean_pdf_url,
    get_current_and_next_months,
    parse_date_string,
)


class TestWebScraper:
    """Tests para la clase WebScraper."""

    def test_build_calendar_url(self):
        """Test construcción de URL con parámetros."""
        scraper = WebScraper(base_url="https://test.com", calendar_path="/calendario?id=1")

        url = scraper._build_calendar_url(1, 2026)

        assert "mes=1" in url
        assert "temporada=2026" in url
        assert "https://test.com" in url


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
            type("MockDate", (), {"today": staticmethod(lambda: date(2025, 12, 15))}),
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


class TestCleanPdfUrl:
    """Tests para la función clean_pdf_url."""

    def test_clean_url_without_parameters(self):
        """Test que mantiene URLs limpias sin cambios."""
        url = "https://fam.es/pdfs/competition.pdf"
        assert clean_pdf_url(url) == url

    def test_clean_url_with_query_parameters(self):
        """Test que elimina parámetros de query después de .pdf."""
        url = "https://fam.es/pdfs/competition.pdf?param=value&other=123"
        expected = "https://fam.es/pdfs/competition.pdf"
        assert clean_pdf_url(url) == expected

    def test_clean_url_with_fragment(self):
        """Test que elimina fragmentos después de .pdf."""
        url = "https://fam.es/pdfs/competition.pdf#page=1"
        expected = "https://fam.es/pdfs/competition.pdf"
        assert clean_pdf_url(url) == expected

    def test_clean_url_with_both_params_and_fragment(self):
        """Test que elimina tanto parámetros como fragmentos."""
        url = "https://fam.es/pdfs/competition.pdf?download=1#section"
        expected = "https://fam.es/pdfs/competition.pdf"
        assert clean_pdf_url(url) == expected

    def test_clean_url_case_insensitive(self):
        """Test que funciona con .PDF en mayúsculas."""
        url = "https://fam.es/pdfs/competition.PDF?param=value"
        expected = "https://fam.es/pdfs/competition.PDF"
        assert clean_pdf_url(url) == expected

    def test_clean_url_no_pdf_extension(self):
        """Test que mantiene URLs sin extensión .pdf sin cambios."""
        url = "https://fam.es/files/document.docx"
        assert clean_pdf_url(url) == url

    def test_clean_url_empty_string(self):
        """Test que maneja strings vacíos correctamente."""
        assert clean_pdf_url("") == ""

    def test_clean_url_none(self):
        """Test que maneja None correctamente."""
        assert clean_pdf_url(None) is None
