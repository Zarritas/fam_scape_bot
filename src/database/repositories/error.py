"""
Repositorio para logs de errores.
"""

import traceback
from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.database.models import ErrorLog
from src.database.repositories.base import BaseRepository


class ErrorRepository(BaseRepository[ErrorLog]):
    """
    Repositorio para operaciones con logs de errores.
    """
    
    model = ErrorLog
    
    def __init__(self, session: AsyncSession):
        super().__init__(session)
    
    async def log_error(
        self,
        component: str,
        error: Exception,
        message: str = "",
    ) -> ErrorLog:
        """
        Registra un error en la base de datos.
        
        Args:
            component: Componente donde ocurrió (ej: "scraper", "bot", "scheduler")
            error: Excepción capturada
            message: Mensaje adicional opcional
        """
        # Obtener stack trace completo
        stack = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        
        return await self.create(
            component=component,
            error_type=type(error).__name__,
            message=message or str(error),
            stack_trace=stack,
        )
    
    async def get_recent(
        self,
        limit: int = 10,
        hours: int = 24,
    ) -> Sequence[ErrorLog]:
        """
        Obtiene errores recientes.
        
        Args:
            limit: Número máximo de errores a retornar
            hours: Ventana de tiempo en horas
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(ErrorLog)
            .where(ErrorLog.timestamp >= cutoff)
            .order_by(ErrorLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_component(
        self,
        component: str,
        limit: int = 10,
    ) -> Sequence[ErrorLog]:
        """Obtiene errores de un componente específico."""
        result = await self.session.execute(
            select(ErrorLog)
            .where(ErrorLog.component == component)
            .order_by(ErrorLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def count_recent(self, hours: int = 24) -> int:
        """Cuenta errores en las últimas N horas."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        result = await self.session.execute(
            select(func.count(ErrorLog.id))
            .where(ErrorLog.timestamp >= cutoff)
        )
        return result.scalar_one()
    
    async def cleanup_old(self, days: int = 7) -> int:
        """
        Elimina logs antiguos.
        
        Returns:
            Número de registros eliminados
        """
        from sqlalchemy import delete
        
        cutoff = datetime.now() - timedelta(days=days)
        result = await self.session.execute(
            delete(ErrorLog).where(ErrorLog.timestamp < cutoff)
        )
        await self.session.flush()
        return result.rowcount
