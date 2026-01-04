"""
Repositorio para suscripciones.
"""

from typing import Sequence, Optional

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Subscription, User
from src.database.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    """
    Repositorio para operaciones con suscripciones.
    """
    
    model = Subscription
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def get_by_user(self, user_id: int) -> Sequence[Subscription]:
        """Obtiene todas las suscripciones de un usuario."""
        result = await self.session.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.discipline)
        )
        return result.scalars().all()
    
    async def get_by_user_telegram_id(
        self,
        telegram_id: int,
    ) -> Sequence[Subscription]:
        """Obtiene suscripciones por ID de Telegram."""
        result = await self.session.execute(
            select(Subscription)
            .join(User)
            .where(User.telegram_id == telegram_id)
            .order_by(Subscription.discipline)
        )
        return result.scalars().all()
    
    async def get_users_for_event(
        self,
        discipline: str,
        sex: str,
    ) -> Sequence[int]:
        """
        Obtiene IDs de usuarios suscritos a una prueba específica.
        
        Búsqueda case-insensitive de disciplina.
        
        Returns:
            Lista de user_ids suscritos
        """
        result = await self.session.execute(
            select(Subscription.user_id)
            .join(User)
            .where(
                and_(
                    Subscription.discipline.ilike(discipline),
                    Subscription.sex == sex.upper(),
                    User.is_active == True,
                )
            )
        )
        return list(result.scalars().all())
    
    async def subscribe(
        self,
        user_id: int,
        discipline: str,
        sex: str,
    ) -> tuple[Subscription, bool]:
        """
        Suscribe un usuario a una prueba.
        
        Si ya está suscrito, retorna la suscripción existente.
        
        Returns:
            Tupla (Subscription, is_new)
        """
        # Verificar si ya existe
        existing = await self.get_subscription(user_id, discipline, sex)
        if existing:
            return existing, False
        
        # Crear nueva suscripción
        subscription = await self.create(
            user_id=user_id,
            discipline=discipline,
            sex=sex.upper(),
        )
        return subscription, True
    
    async def get_subscription(
        self,
        user_id: int,
        discipline: str,
        sex: str,
    ) -> Optional[Subscription]:
        """Obtiene una suscripción específica."""
        result = await self.session.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.discipline.ilike(discipline),
                    Subscription.sex == sex.upper(),
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def unsubscribe(
        self,
        user_id: int,
        discipline: str,
        sex: str,
    ) -> bool:
        """
        Elimina la suscripción de un usuario.
        
        Returns:
            True si se eliminó, False si no existía
        """
        result = await self.session.execute(
            delete(Subscription).where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.discipline.ilike(discipline),
                    Subscription.sex == sex.upper(),
                )
            )
        )
        await self.session.flush()
        return result.rowcount > 0
    
    async def unsubscribe_all(self, user_id: int) -> int:
        """
        Elimina todas las suscripciones de un usuario.
        
        Returns:
            Número de suscripciones eliminadas
        """
        result = await self.session.execute(
            delete(Subscription).where(Subscription.user_id == user_id)
        )
        await self.session.flush()
        return result.rowcount
