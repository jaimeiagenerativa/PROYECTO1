"""
Configuración de la base de datos SQLAlchemy 2.0 con async support.
"""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os

# Variables de entorno para configuración
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./proyecto.db"
)

# Crear engine async
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Mostrar SQL queries en logs
    future=True,
    pool_pre_ping=True,  # Verificar conexiones antes de usar
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base para los modelos
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia para obtener la sesión de base de datos en los endpoints.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """
    Inicializar la base de datos creando todas las tablas.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Cerrar la conexión con la base de datos.
    """
    await engine.dispose()
