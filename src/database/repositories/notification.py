"""
Repositorio para logs de notificaciones.
"""

from collections.abc import Sequence
from datetime import datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import NotificationLog
from src.database.repositories.base import BaseRepository


class NotificationRepository(BaseRepository[NotificationLog]):
    """
    Repositorio para operaciones con logs de notificaciones.
    """

    model = NotificationLog

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def was_notified(
        self,
        user_id: int,
        event_id: int,
    ) -> bool:
        """
        Verifica si un usuario ya fue notificado de un evento.

        Returns:
            True si ya se envió notificación
        """
        result = await self.session.execute(
            select(NotificationLog.id)
            .where(
                and_(
                    NotificationLog.user_id == user_id,
                    NotificationLog.event_id == event_id,
                )
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def log_notification(
        self,
        user_id: int,
        event_id: int,
        message_hash: str,
    ) -> NotificationLog:
        """
        Registra una notificación enviada.
        """
        return await self.create(
            user_id=user_id,
            event_id=event_id,
            message_hash=message_hash,
        )

    async def get_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> Sequence[NotificationLog]:
        """Obtiene las últimas notificaciones de un usuario."""
        result = await self.session.execute(
            select(NotificationLog)
            .where(NotificationLog.user_id == user_id)
            .order_by(NotificationLog.sent_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def count_sent_today(self) -> int:
        """Cuenta notificaciones enviadas hoy."""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        result = await self.session.execute(
            select(func.count(NotificationLog.id)).where(NotificationLog.sent_at >= today_start)
        )
        return result.scalar_one()

    async def cleanup_old(self, days: int = 30) -> int:
        """
        Elimina logs antiguos.

        Returns:
            Número de registros eliminados
        """
        from sqlalchemy import delete

        cutoff = datetime.now() - timedelta(days=days)
        # Contar registros antes de eliminar
        count_result = await self.session.execute(
            select(func.count(NotificationLog.id)).where(NotificationLog.sent_at < cutoff)
        )
        count_to_delete = count_result.scalar_one()

        # Eliminar registros
        await self.session.execute(delete(NotificationLog).where(NotificationLog.sent_at < cutoff))
        await self.session.flush()

        return count_to_delete
