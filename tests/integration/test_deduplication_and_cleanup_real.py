"""
Tests de integración con datos reales.
Prueba la lógica de deduplicación y limpieza usando escenarios realistas.
"""

import pytest
from datetime import date, timedelta
from pathlib import Path

from src.database.repositories.competition import CompetitionRepository
from src.scraper.models import RawCompetition, Competition
from src.scraper.pdf_parser import PDFParser


class TestDeduplicationReal:
    """Tests de deduplicación con datos reales."""

    @pytest.fixture
    async def repo(self, db_session):
        """Repositorio para tests."""
        return CompetitionRepository(db_session)

    @pytest.fixture
    def parser(self):
        """Parser de PDF para tests."""
        return PDFParser()

    @pytest.fixture
    def real_pdf_content_1(self):
        """Contenido del primer PDF real."""
        pdf_path = Path(__file__).parent.parent.parent / "pdf_examples" / "modificado_gallur_2026_01_03.pdf"
        with open(pdf_path, "rb") as f:
            return f.read()

    @pytest.fixture
    def real_pdf_content_2(self):
        """Contenido del segundo PDF real."""
        pdf_path = Path(__file__).parent.parent.parent / "pdf_examples" / "modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf"
        with open(pdf_path, "rb") as f:
            return f.read()

    async def test_deduplication_same_pdf_different_names(self, repo, parser, real_pdf_content_1):
        """Test que permite múltiples competiciones del mismo PDF con nombres diferentes."""
        # Simular dos competiciones del mismo PDF con nombres diferentes
        comp1, created1 = await repo.upsert_with_hash(
            pdf_url="https://fam.es/pdf1.pdf",
            pdf_hash="hash123",
            name="Copa Madrid - Gallur",
            competition_date=date(2026, 1, 3),
            location="Gallur",
            has_modifications=False,
            competition_type="PC"
        )

        comp2, created2 = await repo.upsert_with_hash(
            pdf_url="https://fam.es/pdf1.pdf",  # MISMO PDF
            pdf_hash="hash123",               # MISMO HASH
            name="Campeonato Regional Gallur", # NOMBRE DIFERENTE
            competition_date=date(2026, 1, 3),
            location="Gallur",
            has_modifications=False,
            competition_type="PC"
        )

        # Deberían crearse ambas competiciones (no deduplicar por PDF solo)
        assert created1 is True
        assert created2 is True
        assert comp1.id != comp2.id
        assert comp1.pdf_url == comp2.pdf_url  # Mismo PDF
        assert comp1.name != comp2.name        # Nombres diferentes

    async def test_deduplication_same_pdf_same_name_updates(self, repo):
        """Test que actualiza cuando mismo PDF y mismo nombre."""
        # Primera inserción
        comp1, created1 = await repo.upsert_with_hash(
            pdf_url="https://fam.es/same.pdf",
            pdf_hash="hash456",
            name="Misma Competición",
            competition_date=date(2026, 2, 1),
            location="Madrid",
            enrollment_url="https://old.com",
            has_modifications=False,
            competition_type="PC"
        )

        # Segunda inserción con mismo PDF y nombre, pero datos diferentes
        comp2, created2 = await repo.upsert_with_hash(
            pdf_url="https://fam.es/same.pdf",    # MISMO PDF
            pdf_hash="hash456",                  # MISMO HASH
            name="Misma Competición",            # MISMO NOMBRE
            competition_date=date(2026, 2, 1),  # MISMA FECHA
            location="Madrid",
            enrollment_url="https://new.com",   # URL DIFERENTE
            has_modifications=True,             # MARCADOR DIFERENTE
            competition_type="PC"
        )

        # Debería actualizar la existente, no crear nueva
        assert created1 is True
        assert created2 is False  # No creó nueva
        assert comp1.id == comp2.id  # Es la misma competición
        assert comp2.enrollment_url == "https://new.com"  # Se actualizó
        assert comp2.has_modifications is True           # Se actualizó

    async def test_deduplication_different_pdfs_same_name(self, repo):
        """Test que permite competiciones con mismo nombre pero PDFs diferentes."""
        # Dos competiciones con mismo nombre pero PDFs diferentes
        comp1, created1 = await repo.upsert_with_hash(
            pdf_url="https://fam.es/pdf_a.pdf",
            pdf_hash="hash_a",
            name="Copa Madrid",
            competition_date=date(2026, 3, 1),
            location="Gallur"
        )

        comp2, created2 = await repo.upsert_with_hash(
            pdf_url="https://fam.es/pdf_b.pdf",  # PDF DIFERENTE
            pdf_hash="hash_b",                  # HASH DIFERENTE
            name="Copa Madrid",                 # MISMO NOMBRE
            competition_date=date(2026, 3, 1), # MISMA FECHA
            location="Gallur"
        )

        # Deberían crearse ambas (diferentes PDFs)
        assert created1 is True
        assert created2 is True
        assert comp1.id != comp2.id
        assert comp1.pdf_url != comp2.pdf_url
        assert comp1.name == comp2.name


class TestCleanupReal:
    """Tests de limpieza de competiciones pasadas con datos realistas."""

    @pytest.fixture
    async def repo(self, db_session):
        """Repositorio para tests."""
        return CompetitionRepository(db_session)

    async def test_cleanup_past_competitions_real_dates(self, repo):
        """Test limpieza con fechas realistas del calendario."""
        today = date.today()

        # Crear competiciones pasadas (usando fechas del calendario real)
        past_dates = [
            today - timedelta(days=30),  # Hace un mes
            today - timedelta(days=7),   # La semana pasada
            today - timedelta(days=1),   # Ayer
        ]

        created_competitions = []
        for i, past_date in enumerate(past_dates):
            comp, _ = await repo.upsert_with_hash(
                pdf_url=f"https://fam.es/past_{i}.pdf",
                pdf_hash=f"hash_past_{i}",
                name=f"Competición Pasada {i}",
                competition_date=past_date,
                location="Madrid"
            )
            created_competitions.append(comp)

        # Crear competiciones futuras
        future_dates = [
            today + timedelta(days=1),   # Mañana
            today + timedelta(days=7),   # Próxima semana
            today + timedelta(days=30),  # Próximo mes
        ]

        future_competitions = []
        for i, future_date in enumerate(future_dates):
            comp, _ = await repo.upsert_with_hash(
                pdf_url=f"https://fam.es/future_{i}.pdf",
                pdf_hash=f"hash_future_{i}",
                name=f"Competición Futura {i}",
                competition_date=future_date,
                location="Madrid"
            )
            future_competitions.append(comp)

        # Verificar que todas están creadas
        total_before = len(created_competitions) + len(future_competitions)
        all_competitions = await repo.get_upcoming(from_date=today - timedelta(days=60))
        assert len(all_competitions) >= total_before

        # Ejecutar limpieza
        deleted_count = await repo.delete_past_competitions(today)

        # Verificar que se eliminaron las competiciones pasadas
        assert deleted_count == len(past_dates), f"Se eliminaron {deleted_count} pero deberían ser {len(past_dates)}"

        # Verificar que las competiciones futuras siguen existiendo
        remaining_competitions = await repo.get_upcoming(from_date=today - timedelta(days=1))
        future_remaining = [c for c in remaining_competitions if c.competition_date >= today]
        assert len(future_remaining) >= len(future_competitions)

        # Verificar que no quedan competiciones pasadas
        past_remaining = [c for c in remaining_competitions if c.competition_date < today]
        assert len(past_remaining) == 0, f"Todavía quedan {len(past_remaining)} competiciones pasadas"

    async def test_cleanup_competition_with_events(self, repo):
        """Test que elimina competiciones junto con sus eventos."""
        today = date.today()
        past_date = today - timedelta(days=7)

        # Crear competición pasada con eventos
        competition, _ = await repo.upsert_with_hash(
            pdf_url="https://fam.es/with_events.pdf",
            pdf_hash="hash_events",
            name="Competición con Eventos",
            competition_date=past_date,
            location="Gallur",
            events=[
                {"discipline": "100m", "event_type": "carrera", "sex": "M", "category": "Absoluto"},
                {"discipline": "200m", "event_type": "carrera", "sex": "F", "category": "Absoluto"},
                {"discipline": "pértiga", "event_type": "concurso", "sex": "M", "category": "Absoluto"}
            ]
        )

        # Verificar que se crearon eventos
        comp_with_events = await repo.get_with_events(competition.id)
        assert len(comp_with_events.events) == 3

        # Ejecutar limpieza
        deleted_count = await repo.delete_past_competitions(today)

        # Verificar que se eliminó la competición
        assert deleted_count == 1

        # Verificar que ya no existe la competición
        not_found = await repo.get_by_id(competition.id)
        assert not_found is None

    async def test_cleanup_no_past_competitions(self, repo):
        """Test que no hace nada cuando no hay competiciones pasadas."""
        today = date.today()

        # Crear solo competiciones futuras
        future_date = today + timedelta(days=30)
        await repo.upsert_with_hash(
            pdf_url="https://fam.es/future_only.pdf",
            pdf_hash="hash_future",
            name="Solo Futura",
            competition_date=future_date,
            location="Madrid"
        )

        # Ejecutar limpieza
        deleted_count = await repo.delete_past_competitions(today)

        # No debería eliminar nada
        assert deleted_count == 0

        # La competición futura debería seguir existiendo
        future_competitions = await repo.get_upcoming(from_date=today)
        assert len(future_competitions) >= 1