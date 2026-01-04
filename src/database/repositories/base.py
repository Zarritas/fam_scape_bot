"""
Repositorio base con operaciones CRUD comunes.
"""

from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Repositorio base con operaciones CRUD genéricas.

    Heredar y especificar el tipo de modelo.
    """

    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> ModelT:
        """Crea una nueva instancia y la guarda."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, id: int) -> ModelT | None:
        """Obtiene una instancia por su ID."""
        return await self.session.get(self.model, id)

    async def get_all(self) -> Sequence[ModelT]:
        """Obtiene todas las instancias."""
        result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def update(self, instance: ModelT, **kwargs) -> ModelT:
        """Actualiza una instancia con los valores proporcionados."""
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def delete(self, instance: ModelT) -> None:
        """Elimina una instancia."""
        await self.session.delete(instance)
        await self.session.flush()

    async def delete_by_id(self, id: int) -> bool:
        """Elimina una instancia por su ID. Retorna True si se eliminó."""
        result = await self.session.execute(delete(self.model).where(self.model.id == id))
        await self.session.flush()
        return result.rowcount > 0
