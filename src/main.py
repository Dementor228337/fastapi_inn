from fastapi import FastAPI
from src.routers.url_router import inn_router

app = FastAPI(title="API для парсинга Росстата")

app.include_router(inn_router)

