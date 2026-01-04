"""
SQLAlchemy engine factory y configuración de sesión.

Soporta SQLite (desarrollo) y PostgreSQL (producción).
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings

# Engine global (lazy initialization)
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Obtiene o crea el engine de SQLAlchemy.
    
    Usa lazy initialization para permitir configuración
    antes de la primera conexión.
    """
    global _engine
    
    if _engine is None:
        # Configuración específica según el tipo de BD
        if settings.is_sqlite:
            # SQLite necesita check_same_thread=False para async
            connect_args = {"check_same_thread": False}
            _engine = create_async_engine(
                settings.database_url,
                connect_args=connect_args,
                echo=settings.log_level == "DEBUG",
            )
        else:
            # PostgreSQL
            _engine = create_async_engine(
                settings.database_url,
                echo=settings.log_level == "DEBUG",
                pool_size=5,
                max_overflow=10,
            )
    
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Obtiene la factoría de sesiones.
    """
    global _session_factory
    
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    
    return _session_factory

from contextlib import asynccontextmanager

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener una sesión de base de datos.
    
    Uso:
        async with get_session() as session:
            # usar session
    
    O como dependency en handlers.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.
    
    Debe llamarse al inicio de la aplicación.
    """
    from src.database.models import Base
    
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Cierra las conexiones a la base de datos.
    
    Debe llamarse al cerrar la aplicación.
    """
    global _engine, _session_factory
    
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
