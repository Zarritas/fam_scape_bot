"""
Repositorio para eventos/pruebas.
"""

from collections.abc import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Event
from src.database.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    """
    Repositorio para operaciones con eventos/pruebas.
    """

    model = Event

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_competition(
        self,
        competition_id: int,
    ) -> Sequence[Event]:
        """Obtiene todos los eventos de una competición."""
        result = await self.session.execute(
            select(Event)
            .where(Event.competition_id == competition_id)
            .order_by(Event.scheduled_time)
        )
        return result.scalars().all()

    async def get_by_discipline_and_sex(
        self,
        discipline: str,
        sex: str,
    ) -> Sequence[Event]:
        """
        Obtiene eventos por disciplina y sexo.

        La búsqueda de disciplina es case-insensitive.
        """
        result = await self.session.execute(
            select(Event).where(
                and_(
                    Event.discipline.ilike(discipline),
                    Event.sex == sex.upper(),
                )
            )
        )
        return result.scalars().all()

    async def get_matching_subscriptions(
        self,
        discipline: str,
        sex: str,
    ) -> Sequence[Event]:
        """
        Obtiene eventos que coinciden con una suscripción.

        Busca eventos donde la disciplina contenga el texto buscado.
        """
        from datetime import date

        from src.database.models import Competition

        result = await self.session.execute(
            select(Event)
            .join(Competition)
            .where(
                and_(
                    Event.discipline.ilike(f"%{discipline}%"),
                    Event.sex == sex.upper(),
                    Competition.competition_date >= date.today(),
                )
            )
        )
        return result.scalars().all()
