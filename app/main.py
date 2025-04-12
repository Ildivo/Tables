# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

from app.database import engine
from app.models import Base
from app.routers import tables, reservations

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Lifespan-событие для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔧 Инициализация базы данных...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ База данных готова.")
    yield
    logger.info("🛑 Завершение работы приложения.")

# Инициализация FastAPI-приложения
app = FastAPI(title="Table Reservation API", lifespan=lifespan)

# Подключение маршрутов
app.include_router(tables.router, prefix="/tables", tags=["Tables"])
app.include_router(reservations.router, prefix="/reservations", tags=["Reservations"])
