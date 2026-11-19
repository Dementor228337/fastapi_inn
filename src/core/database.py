from typing import Any, AsyncGenerator
from src.logger_core.logging_config import logger
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings

class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Используется для объявления таблиц базы данных.
    """

    pass


async_engine = create_async_engine(settings.DATABASE_URL)
logger.info("Database engine successfully initialized")


async_session = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    """
    Функция для получения асинхронной сессии базы данных.

    Эта функция создает асинхронную сессию, начинает транзакцию и предоставляет ее
    в качестве генератора.  Это позволяет использовать сессию в блоке async with.
    После выхода из блока async with, сессия автоматически закрывается и транзакция откатывается,
    если не было явно закоммичено.

    Yields:
        AsyncSession: Асинхронная сессия базы данных.
    """
    logger.debug("Creating new database session...")
    async with async_session() as session:
        async with session.begin():
            yield session