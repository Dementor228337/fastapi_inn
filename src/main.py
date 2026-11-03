from fastapi import FastAPI
from src.routers.url_router import inn_router
from src.logger_core.logging_config import logger


logger.info("Started")

app = FastAPI(title="API для парсинга Росстата")

app.include_router(inn_router)
logger.info("Included router: router for inn forms")
