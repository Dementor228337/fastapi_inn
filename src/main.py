from contextlib import asynccontextmanager
from typing import AsyncGenerator
from src.core.database import Base, async_engine
from fastapi import FastAPI
from src.routers.url_router import inn_router
from src.routers.task_router import task_router
from src.logger_core.logging_config import logger
from src.kafka.producer import KafkaProducerService
from src.core.pool import pool

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Контекстный менеджер жизненного цикла приложения FastAPI, выполняющий инициализацию базы данных при старте приложения.

    Что делает
    - При старте приложения открывает асинхронную транзакцию через async_engine и:
      - создаёт все таблицы, описанные в Base.metadata (эквивалент CREATE TABLE IF NOT EXISTS),
    - Передаёт управление приложению (yield) — в этот момент приложение принимает и обрабатывает запросы.
    - Открывает пул браузеров (максимум 3)
    - Запускает продюсер кафки
    :param app: Экземпляр класса FastAPI.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info("Starting application lifespan")

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception:
        logger.critical("Failed to create database tables", exc_info=True)
        raise


    await pool.start()
    logger.info("Browser pool started")

    producer = KafkaProducerService()
    await producer.start()
    app.state.kafka_producer = producer
    logger.info("kafka producer started")

    try:
        yield
    finally:
        await producer.stop()
        logger.info("kafka producer stopped")

        await pool.stop()
        logger.info("Browser pool stopped")

        await async_engine.dispose()
        logger.info("Database engine disposed")


app = FastAPI(title="API для парсинга Росстата", lifespan=lifespan)

app.include_router(inn_router)
logger.info("Included router: router for inn forms")

app.include_router(task_router)
logger.info("Included router: router for results")
