"""
Repositorio para usuarios.
"""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models import User
from src.database.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repositorio para operaciones con usuarios.
    """

    model = User

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_by_telegram_id(
        self,
        telegram_id: int,
    ) -> User | None:
        """Obtiene un usuario por su ID de Telegram."""
        result = await self.session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
            .options(selectinload(User.subscriptions))
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        first_name: str = "",
        username: str | None = None,
    ) -> tuple[User, bool]:
        """
        Obtiene un usuario existente o crea uno nuevo.

        Returns:
            Tupla (User, is_new) donde is_new es True si se creó
        """
        existing = await self.get_by_telegram_id(telegram_id)

        if existing:
            return existing, False

        user = await self.create(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
        )
        return user, True

    async def get_active_users(self) -> Sequence[User]:
        """Obtiene todos los usuarios activos."""
        result = await self.session.execute(
            select(User).where(User.is_active).options(selectinload(User.subscriptions))
        )
        return result.scalars().all()

    async def count_active(self) -> int:
        """Cuenta usuarios activos."""
        result = await self.session.execute(select(func.count(User.id)).where(User.is_active))
        return result.scalar_one()

    async def deactivate(self, user: User) -> User:
        """Marca un usuario como inactivo."""
        return await self.update(user, is_active=False)

    async def activate(self, user: User) -> User:
        """Marca un usuario como activo."""
        return await self.update(user, is_active=True)
