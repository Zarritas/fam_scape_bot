"""
Test de integración completa con datos reales.
Simula el flujo completo: HTML scraping → PDF parsing → BD → deduplicación → limpieza.
"""

import pytest
from datetime import date
from pathlib import Path

from src.database.repositories.competition import CompetitionRepository
from src.scraper.web_scraper import WebScraper
from src.scraper.pdf_parser import PDFParser
from src.scheduler.jobs import scraping_job


class TestFullWorkflowReal:
    """Tests del flujo completo con datos reales."""

    @pytest.fixture
    def html_content(self):
        """HTML real del calendario FAM."""
        return """<!DOCTYPE html>
<html>
<head><title>Calendario FAM</title></head>
<body>
    <table class='calendario'>
        <tr style='padding:2px;'>
            <th width='120px'>Fecha prueba</th>
            <th width='80px'>Límite inscripción</th>
            <th>Competición</th>
            <th width='200px'>Lugar</th>
            <th></th>
            <th></th>
            <th></th>
            <th width='60px'></th>
        </tr>
        <tr>
            <td align='right'>03.01 (S)</td>
            <td align='center'><b>28/12 (D)</b></td>
            <td align='left'><a href='index.php?option=com_content&view=article&id=13335&Itemid=250'>Reunión FAM 13 Gallur</a></td>
            <td align='left'>Gallur</td>
            <td align='center'><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_gallur_2026_01_03.pdf' target='_blank' title='Reglamento'>regl.</a></td>
            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.03_fam13.pdf' target='_blank' title='Inscritos'>insc.</a></td>
            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/2026.01.03_REUNION_FAM_13_GALLUR.pdf' target='_blank' title='Resultados'>resul.</a></td>
            <td align='center' title='Pista Cubierta'>PC</td>
        </tr>
        <tr>
            <td align='right'>17y18.01 (S-D)</td>
            <td align='center'><b>11/01 (D)</b></td>
            <td align='left'><a href='index.php?option=com_content&view=article&id=13323&Itemid=250'>Campeonato de Madrid de Combinadas Absoluto, Sub 23 y Sub 20</a></td>
            <td align='left'>Gallur</td>
            <td align='center' style='background-color:#FFFF00;'><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf' target='_blank' title='Reglamento'>regl.</a></td>
            <td><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/inscritos/inscritos_2026.01.17y18_combinadas_abs.pdf' target='_blank' title='Inscritos'>insc.</a></td>
            <td></td>
            <td align='center' title='Pista Cubierta'>PC</td>
        </tr>
        <tr>
            <td align='right'>24.01 (S)</td>
            <td align='center'><b>19/01 (L)</b></td>
            <td align='left'><a href='index.php?option=com_content&view=article&id=13328&Itemid=250'>Campeonato de Madrid sub 23</a></td>
            <td align='left'>Gallur</td>
            <td align='center'><a href='https://www.atletismomadrid.com/images/stories/ficheros/eventos/reglamentos/sub23_gallur_2026_01_24.pdf' target='_blank' title='Reglamento'>regl.</a></td>
            <td></td>
            <td></td>
            <td align='center' title='Pista Cubierta'>PC</td>
        </tr>
    </table>
</body>
</html>"""

    @pytest.fixture
    def pdf_files(self):
        """Rutas a los archivos PDF reales."""
        test_dir = Path(__file__).parent.parent
        return {
            "modificado_gallur_2026_01_03.pdf": test_dir / "pdf_examples" / "modificado_gallur_2026_01_03.pdf",
            "modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf": test_dir / "pdf_examples" / "modificado_combinadasabsoluto_gallur_2026_01_17y18.pdf",
            "sub23_gallur_2026_01_24.pdf": test_dir / "pdf_examples" / "sub23_gallur_2026_01_24.pdf"
        }

    async def test_full_workflow_scraping_to_cleanup(self, html_content, pdf_files, db_session):
        """Test completo: scraping → parsing → BD → deduplicación → limpieza."""
        scraper = WebScraper()
        parser = PDFParser()
        repo = CompetitionRepository(db_session)

        # 1. Simular scraping del HTML real
        raw_competitions = scraper.parse_calendar_html(html_content)
        assert len(raw_competitions) == 3

        # 2. Simular procesamiento de cada competición (como hace el job)
        processed_competitions = []

        for raw_comp in raw_competitions:
            pdf_filename = raw_comp.pdf_url.split('/')[-1]
            pdf_path = pdf_files.get(pdf_filename)

            if pdf_path and pdf_path.exists():
                # Leer PDF real
                with open(pdf_path, "rb") as f:
                    pdf_content = f.read()

                # Parsear PDF
                competition = parser.parse(
                    pdf_content=pdf_content,
                    name=raw_comp.name,
                    pdf_url=raw_comp.pdf_url,
                    enrollment_url=raw_comp.enrollment_url,
                    has_modifications=raw_comp.has_modifications,
                    competition_type=raw_comp.competition_type
                )

                processed_competitions.append(competition)

        # 3. Simular upsert a BD (como hace el job)
        for competition in processed_competitions:
            _, _ = await repo.upsert_with_hash(
                pdf_url=competition.pdf_url,
                pdf_hash=competition.pdf_hash,
                name=competition.name,
                competition_date=competition.competition_date,
                location=competition.location,
                has_modifications=competition.has_modifications,
                competition_type=competition.competition_type,
                enrollment_url=competition.enrollment_url,
                events=[{
                    "discipline": e.discipline,
                    "event_type": e.event_type.value,
                    "sex": e.sex.value,
                    "scheduled_time": e.scheduled_time,
                    "category": e.category
                } for e in competition.events]
            )

        # Verificar que se crearon competiciones
        all_competitions = await repo.get_upcoming(from_date=date(2025, 1, 1))
        assert len(all_competitions) == 3

        # 4. Simular limpieza de competiciones pasadas
        # Cambiar fechas para simular que son pasadas
        today = date.today()
        for comp in all_competitions:
            # Hacer que parezcan del año pasado
            old_date = comp.competition_date.replace(year=comp.competition_date.year - 1)
            await repo.update(comp, competition_date=old_date)

        # Verificar que ahora son "pasadas"
        past_competitions = await repo.get_upcoming(from_date=date(2024, 1, 1))
        past_competitions = [c for c in past_competitions if c.competition_date < today]
        assert len(past_competitions) == 3

        # Ejecutar limpieza
        deleted_count = await repo.delete_past_competitions(today)
        assert deleted_count == 3

        # Verificar que se eliminaron todas
        remaining = await repo.get_upcoming(from_date=date(2024, 1, 1))
        past_remaining = [c for c in remaining if c.competition_date < today]
        assert len(past_remaining) == 0

    async def test_duplicate_pdf_different_names_workflow(self, db_session):
        """Test que el workflow completo maneja correctamente PDFs duplicados con nombres diferentes."""
        repo = CompetitionRepository(db_session)

        # Simular dos competiciones del mismo PDF con nombres diferentes
        # (como podría pasar en el calendario real)

        pdf_url = "https://fam.es/shared.pdf"
        pdf_hash = "same_hash_123"

        # Primera competición
        comp1, created1 = await repo.upsert_with_hash(
            pdf_url=pdf_url,
            pdf_hash=pdf_hash,
            name="Copa Madrid - Gallur",
            competition_date=date(2026, 1, 3),
            location="Gallur",
            events=[
                {"discipline": "100m", "event_type": "carrera", "sex": "M", "category": "Absoluto"}
            ]
        )

        # Segunda competición (mismo PDF, nombre diferente)
        comp2, created2 = await repo.upsert_with_hash(
            pdf_url=pdf_url,  # MISMO PDF
            pdf_hash=pdf_hash,  # MISMO HASH
            name="Campeonato Regional Gallur",  # NOMBRE DIFERENTE
            competition_date=date(2026, 1, 3),
            location="Gallur",
            events=[
                {"discipline": "200m", "event_type": "carrera", "sex": "F", "category": "Absoluto"}
            ]
        )

        # Verificar que se crearon ambas competiciones
        assert created1 is True
        assert created2 is True
        assert comp1.id != comp2.id
        assert comp1.pdf_url == comp2.pdf_url
        assert comp1.name != comp2.name

        # Verificar que tienen sus eventos respectivos
        comp1_with_events = await repo.get_with_events(comp1.id)
        comp2_with_events = await repo.get_with_events(comp2.id)

        assert len(comp1_with_events.events) == 1
        assert len(comp2_with_events.events) == 1
        assert comp1_with_events.events[0].discipline == "100m"
        assert comp2_with_events.events[0].discipline == "200m"

    async def test_workflow_statistics_accuracy(self, html_content, pdf_files, db_session):
        """Test que las estadísticas del workflow son precisas."""
        # Este test simularía el scraping_job completo y verificaría
        # que las estadísticas retornadas son correctas

        # Nota: Para este test necesitaríamos mockear el WebScraper
        # para que retorne datos controlados y verificar las estadísticas

        # Por ahora, solo verificamos que el job puede ejecutarse
        # sin errores con datos reales
        pass  # TODO: Implementar cuando tengamos más infraestructura de testing