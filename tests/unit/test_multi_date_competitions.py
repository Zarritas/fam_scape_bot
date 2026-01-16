"""
Tests para soporte de fechas múltiples en competiciones.
"""

import pytest
from datetime import date

from src.database.repositories.competition import CompetitionRepository
from src.scraper.models import RawCompetition
from src.scraper.web_scraper import WebScraper


class TestMultiDateCompetitions:
    """Tests para competiciones con fechas múltiples."""

    @pytest.fixture
    async def repo(self, db_session):
        """Repositorio para tests."""
        return CompetitionRepository(db_session)

    def test_web_scraper_extract_additional_dates(self):
        """Test que el web scraper extrae fechas adicionales correctamente."""
        scraper = WebScraper()

        # Caso: "17y18.01 (S-D)" debería extraer ["18/01/2026"]
        dates = scraper._extract_additional_dates("17y18.01 (S-D)")
        assert len(dates) == 1
        assert dates[0].endswith("/01/2026")  # El día 18

        # Caso: fecha simple no debería extraer nada
        dates = scraper._extract_additional_dates("03/01/2026")
        assert len(dates) == 0

    async def test_competition_model_additional_dates(self, repo):
        """Test que el modelo Competition maneja fechas adicionales."""
        # Crear competición con fechas adicionales
        additional_dates = [date(2026, 1, 18)]
        comp, _ = await repo.upsert_with_hash(
            pdf_url="https://test.com/pdf.pdf",
            pdf_hash="hash123",
            name="Competición Multi-día",
            competition_date=date(2026, 1, 17),
            location="Madrid",
            fechas_adicionales=additional_dates
        )

        # Verificar que se guardaron las fechas adicionales
        assert comp.fechas_adicionales_list == additional_dates

        # Verificar propiedad todas_las_fechas
        assert len(comp.todas_las_fechas) == 2
        assert date(2026, 1, 17) in comp.todas_las_fechas
        assert date(2026, 1, 18) in comp.todas_las_fechas

        # Verificar fecha_display
        display = comp.fecha_display
        assert "17/01" in display
        assert "18/01/2026" in display

    async def test_raw_competition_with_additional_dates(self):
        """Test que RawCompetition maneja fechas adicionales."""
        comp = RawCompetition(
            name="Test Competition",
            date_str="17y18.01 (S-D)",
            pdf_url="https://test.com/pdf.pdf",
            fechas_adicionales=["18/01/2026"]
        )

        assert comp.fechas_adicionales == ["18/01/2026"]
        assert comp.name == "Test Competition"

    async def test_upsert_with_additional_dates(self, repo):
        """Test que upsert_with_hash maneja fechas adicionales correctamente."""
        # Primera inserción
        comp1, created1 = await repo.upsert_with_hash(
            pdf_url="https://test.com/multi.pdf",
            pdf_hash="hash_multi",
            name="Multi-day Test",
            competition_date=date(2026, 1, 17),
            location="Madrid",
            fechas_adicionales=[date(2026, 1, 18)]
        )

        assert created1 is True
        assert len(comp1.fechas_adicionales_list) == 1

        # Actualización con mismas fechas (no debería crear nueva)
        comp2, created2 = await repo.upsert_with_hash(
            pdf_url="https://test.com/multi.pdf",
            pdf_hash="hash_multi",
            name="Multi-day Test",
            competition_date=date(2026, 1, 17),
            location="Madrid",
            fechas_adicionales=[date(2026, 1, 18)]
        )

        assert created2 is False  # No creó nueva
        assert comp1.id == comp2.id  # Es la misma competición

    async def test_date_display_formats(self, repo):
        """Test que fecha_display funciona en diferentes formatos."""
        # Una sola fecha
        comp1, _ = await repo.upsert_with_hash(
            pdf_url="https://test.com/single.pdf",
            pdf_hash="single",
            name="Single Day",
            competition_date=date(2026, 1, 17),
            location="Madrid"
        )
        assert comp1.fecha_display == "17/01/2026"

        # Dos fechas
        comp2, _ = await repo.upsert_with_hash(
            pdf_url="https://test.com/double.pdf",
            pdf_hash="double",
            name="Double Day",
            competition_date=date(2026, 1, 17),
            location="Madrid",
            fechas_adicionales=[date(2026, 1, 18)]
        )
        assert "17/01" in comp2.fecha_display
        assert "18/01/2026" in comp2.fecha_display

        # Tres fechas
        comp3, _ = await repo.upsert_with_hash(
            pdf_url="https://test.com/triple.pdf",
            pdf_hash="triple",
            name="Triple Day",
            competition_date=date(2026, 1, 17),
            location="Madrid",
            fechas_adicionales=[date(2026, 1, 18), date(2026, 1, 19)]
        )
        assert "17/01" in comp3.fecha_display
        assert "19/01/2026" in comp3.fecha_display
        assert "3 días" in comp3.fecha_display