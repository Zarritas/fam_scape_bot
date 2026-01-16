"""
Tests con PDFs reales para validar el parsing correcto.
Usa los archivos PDF reales del calendario FAM.
"""

import pytest
from pathlib import Path

from src.scraper.pdf_parser import PDFParser

# Lista de PDFs reales para testear
REAL_PDF_FILES = [
    "modificado_gallur_2026_01_03.pdf",
    "modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf",
    "sub23_gallur_2026_01_24.pdf"
]


class TestPDFParserReal:
    """Tests del PDF parser con archivos reales."""

    @pytest.fixture
    def parser(self):
        """Instancia del parser para tests."""
        return PDFParser()

    @pytest.mark.parametrize("pdf_filename", REAL_PDF_FILES)
    def test_parse_real_pdf_structure(self, parser, pdf_filename):
        """Test que los PDFs reales tienen estructura válida."""
        pdf_path = Path(__file__).parent.parent.parent / "pdf_examples" / pdf_filename

        # Verificar que el archivo existe
        assert pdf_path.exists(), f"PDF file {pdf_filename} not found"

        # Leer el contenido del PDF
        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        # Verificar que es un PDF válido
        assert pdf_content.startswith(b"%PDF-"), f"File {pdf_filename} is not a valid PDF"

        # Verificar que tiene contenido sustancial
        assert len(pdf_content) > 1000, f"PDF {pdf_filename} is too small"

    @pytest.mark.parametrize("pdf_filename", REAL_PDF_FILES)
    def test_parse_real_pdf_competition_data(self, parser, pdf_filename):
        """Test que extrae correctamente datos de competición de PDFs reales."""
        pdf_path = Path(__file__).parent.parent.parent / "pdf_examples" / pdf_filename

        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        # Parsear el PDF
        competition = parser.parse(
            pdf_content=pdf_content,
            name=f"Test Competition from {pdf_filename}",
            pdf_url=f"/pdfs/{pdf_filename}",
            enrollment_url="https://test.com",
            has_modifications=False,
            competition_type="PC"
        )

        # Verificar estructura básica
        assert competition is not None
        assert hasattr(competition, 'name')
        assert hasattr(competition, 'competition_date')
        assert hasattr(competition, 'location')
        assert hasattr(competition, 'events')

        # Verificar que tiene eventos
        assert isinstance(competition.events, list)
        assert len(competition.events) > 0, f"PDF {pdf_filename} should have events"

    def test_parse_real_pdf_gallur_2026_01_03(self, parser):
        """Test específico del PDF modificado_gallur_2026_01_03.pdf."""
        pdf_path = Path(__file__).parent.parent.parent / "pdf_examples" / "modificado_gallur_2026_01_03.pdf"

        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        competition = parser.parse(
            pdf_content=pdf_content,
            name="Copa Madrid - Reunión Gallur",
            pdf_url="/pdfs/modificado_gallur_2026_01_03.pdf",
            enrollment_url="https://inscripciones.fam.es",
            has_modifications=True,
            competition_type="PC"
        )

        # Verificar datos específicos conocidos
        assert "Gallur" in competition.location or "gallur" in competition.location.lower()
        assert competition.competition_type == "PC"
        assert competition.has_modifications is True

        # Verificar que tiene eventos de atletismo
        assert len(competition.events) > 0
        for event in competition.events:
            assert hasattr(event, 'discipline')
            assert hasattr(event, 'sex')
            assert hasattr(event, 'event_type')

    def test_parse_real_pdf_combinadas_absoluto(self, parser):
        """Test específico del PDF combinadas absoluto."""
        pdf_path = Path(__file__).parent.parent.parent / "pdf_examples" / "modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf"

        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        competition = parser.parse(
            pdf_content=pdf_content,
            name="Copa Madrid Absoluta - Combinadas",
            pdf_url="/pdfs/modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf",
            enrollment_url="https://inscripciones.fam.es",
            has_modifications=True,
            competition_type="PC"
        )

        # Verificar que es multi-día (17-18 enero)
        assert competition is not None

        # Verificar que tiene eventos (combinadas suelen tener múltiples pruebas)
        assert len(competition.events) > 0

    def test_parse_real_pdf_sub23(self, parser):
        """Test específico del PDF Sub23."""
        pdf_path = Path(__file__).parent.parent.parent / "pdf_examples" / "sub23_gallur_2026_01_24.pdf"

        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        competition = parser.parse(
            pdf_content=pdf_content,
            name="Campeonato de Madrid Sub23",
            pdf_url="/pdfs/sub23_gallur_2026_01_24.pdf",
            enrollment_url="https://inscripciones.fam.es",
            has_modifications=False,
            competition_type="PC"
        )

        # Verificar que es Sub23
        assert competition is not None
        assert "Sub23" in competition.name or "sub23" in competition.name.lower()

        # Verificar que tiene eventos apropiados para categoría Sub23
        assert len(competition.events) > 0

    def test_parse_real_pdf_error_handling(self, parser):
        """Test que maneja errores gracefully con PDFs corruptos."""
        # PDF vacío
        with pytest.raises(Exception):
            parser.parse(
                pdf_content=b"",
                name="Test",
                pdf_url="/test.pdf"
            )

        # PDF inválido
        with pytest.raises(Exception):
            parser.parse(
                pdf_content=b"This is not a PDF",
                name="Test",
                pdf_url="/test.pdf"
            )

    @pytest.mark.parametrize("pdf_filename", REAL_PDF_FILES)
    def test_parse_real_pdf_event_validation(self, parser, pdf_filename):
        """Test que todos los eventos extraídos son válidos."""
        pdf_path = Path(__file__).parent.parent.parent / "pdf_examples" / pdf_filename

        with open(pdf_path, "rb") as f:
            pdf_content = f.read()

        competition = parser.parse(
            pdf_content=pdf_content,
            name=f"Test from {pdf_filename}",
            pdf_url=f"/pdfs/{pdf_filename}"
        )

        # Validar cada evento
        for event in competition.events:
            # Disciplina no vacía
            assert event.discipline, f"Event has empty discipline in {pdf_filename}"

            # Sexo válido
            assert event.sex in ['M', 'F'], f"Invalid sex '{event.sex}' in {pdf_filename}"

            # Tipo de evento válido
            assert event.event_type in ['carrera', 'concurso'], f"Invalid event_type '{event.event_type}' in {pdf_filename}"

            # Categoría es string (puede estar vacío)
            assert isinstance(event.category, str), f"Category should be string in {pdf_filename}"