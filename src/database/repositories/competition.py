"""
Repositorio para competiciones.
"""

from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import Competition, Event
from src.database.repositories.base import BaseRepository


class CompetitionRepository(BaseRepository[Competition]):
    """
    Repositorio para operaciones con competiciones.
    """

    model = Competition

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_pdf_url(self, pdf_url: str) -> Competition | None:
        """Obtiene una competición por su URL de PDF."""
        result = await self.session.execute(
            select(Competition)
            .where(Competition.pdf_url == pdf_url)
            .options(selectinload(Competition.events))
        )
        return result.scalar_one_or_none()

    async def get_by_pdf_url_and_name(self, pdf_url: str, name: str) -> Competition | None:
        """Obtiene una competición por su URL de PDF y nombre."""
        result = await self.session.execute(
            select(Competition)
            .where(Competition.pdf_url == pdf_url, Competition.name == name)
            .options(selectinload(Competition.events))
        )
        return result.scalar_one_or_none()

    async def get_by_pdf_hash(self, pdf_hash: str) -> Competition | None:
        """Obtiene una competición por su hash de PDF."""
        result = await self.session.execute(
            select(Competition).where(Competition.pdf_hash == pdf_hash)
        )
        return result.scalar_one_or_none()

    async def get_upcoming(
        self,
        from_date: date | None = None,
    ) -> Sequence[Competition]:
        """
        Obtiene competiciones con fecha >= from_date.

        Si from_date es None, usa la fecha actual.
        """
        if from_date is None:
            from_date = date.today()

        result = await self.session.execute(
            select(Competition)
            .where(Competition.competition_date >= from_date)
            .order_by(Competition.competition_date)
            .options(selectinload(Competition.events))
        )
        return result.scalars().all()

    async def upsert_with_hash(
        self,
        pdf_url: str | None,
        pdf_hash: str | None,
        name: str,
        competition_date: date,
        location: str,
        has_modifications: bool = False,
        competition_type: str | None = None,
        enrollment_url: str | None = None,
        events: list[dict] | None = None,
        fechas_adicionales: list[date] | None = None,
    ) -> tuple[Competition, bool]:
        """
        Inserta o actualiza una competición basándose en el hash del PDF.

        Si el PDF ya existe con el mismo hash, no hace nada.
        Si el PDF existe pero el hash cambió, actualiza.
        Si el PDF no existe, lo crea.

        Args:
            pdf_url: URL del PDF
            pdf_hash: Hash SHA-256 del contenido del PDF
            name: Nombre de la competición
            competition_date: Fecha de la competición
            location: Lugar
            has_modifications: Si tiene marcador de modificaciones
            competition_type: Tipo de competición (PC, AL, etc.)
            enrollment_url: URL de inscripción
            events: Lista opcional de eventos a crear

        Returns:
            Tupla (Competition, is_new_or_updated)
            - is_new_or_updated es True si se creó o actualizó
        """
        existing = await self.get_by_pdf_url_and_name(pdf_url, name) if pdf_url else None

        if existing:
            # Ya existe - verificar si el hash cambió
            # También actualizamos si ha cambiado la URL de inscritos
            # aunque el hash del PDF sea el mismo
            if existing.pdf_hash == pdf_hash and existing.enrollment_url == enrollment_url:
                # Sin cambios
                return existing, False

            # Actualizar
            # Nota: Si solo cambia el enrollment_url, también actualizamos
            await self.update(
                existing,
                pdf_hash=pdf_hash,
                name=name,
                competition_date=competition_date,
                location=location,
                has_modifications=has_modifications,
                competition_type=competition_type,
                enrollment_url=enrollment_url,
            )

            # Actualizar fechas adicionales
            if fechas_adicionales is not None:
                existing.fechas_adicionales_list = fechas_adicionales

            # Eliminar eventos antiguos y crear nuevos
            if events is not None:
                # Eliminar eventos existentes
                for event in list(existing.events):
                    await self.session.delete(event)

                # Crear nuevos eventos
                for event_data in events:
                    event = Event(competition_id=existing.id, **event_data)
                    self.session.add(event)

            await self.session.flush()
            return existing, True

        # No existe - crear nueva
        competition = await self.create(
            pdf_url=pdf_url,
            pdf_hash=pdf_hash,
            name=name,
            competition_date=competition_date,
            location=location,
            has_modifications=has_modifications,
            competition_type=competition_type,
            enrollment_url=enrollment_url,
        )

        # Crear eventos
        if events is not None:
            for event_data in events:
                event = Event(competition_id=competition.id, **event_data)
                self.session.add(event)
            await self.session.flush()

        # Establecer fechas adicionales
        if fechas_adicionales is not None:
            competition.fechas_adicionales_list = fechas_adicionales

        return competition, True

    async def get_with_events(self, competition_id: int) -> Competition | None:
        """Obtiene una competición con sus eventos cargados."""
        result = await self.session.execute(
            select(Competition)
            .where(Competition.id == competition_id)
            .options(selectinload(Competition.events))
        )
        return result.scalar_one_or_none()

    async def count_upcoming(self, from_date: date | None = None) -> int:
        """Cuenta competiciones futuras."""
        if from_date is None:
            from_date = date.today()

        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count(Competition.id)).where(Competition.competition_date >= from_date)
        )
        return result.scalar_one()

    async def get_by_event_type(
        self,
        discipline: str,
        sex: str,
        from_date: date | None = None,
    ) -> Sequence[Competition]:
        """
        Obtiene competiciones que contienen una prueba específica.

        Args:
            discipline: Nombre de la disciplina (ej: "100m")
            sex: Sexo ("M", "F" o "B" para ambos)
            from_date: Fecha inicial (default: hoy)
        """
        if from_date is None:
            from_date = date.today()

        stmt = (
            select(Competition)
            .join(Competition.events)
            .where(
                Competition.competition_date >= from_date,
                Event.discipline == discipline,
            )
            .options(selectinload(Competition.events))
            .distinct()
            .order_by(Competition.competition_date)
        )

        if sex != "B":
            stmt = stmt.where(Event.sex == sex)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_exact_date(self, target_date: date) -> Sequence[Competition]:
        """Obtiene competiciones para una fecha específica."""
        result = await self.session.execute(
            select(Competition)
            .where(Competition.competition_date == target_date)
            .options(selectinload(Competition.events))
        )
        return result.scalars().all()

    async def delete_past_competitions(self, before_date: date) -> int:
        """
        Elimina competiciones con fecha anterior a before_date.

        Returns:
            Número de competiciones eliminadas.
        """
        from sqlalchemy import delete

        # Obtener IDs de competiciones a eliminar
        result = await self.session.execute(
            select(Competition.id).where(Competition.competition_date < before_date)
        )
        competition_ids = result.scalars().all()

        if not competition_ids:
            return 0

        # Eliminar competiciones (los eventos se eliminan automáticamente por cascade)
        delete_stmt = delete(Competition).where(Competition.competition_date < before_date)
        result = await self.session.execute(delete_stmt)

        return result.rowcount
