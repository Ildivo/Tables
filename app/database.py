import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

# Базовый класс моделей
Base = declarative_base()

# Настройки базы данных
class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://myuser:mypassword@postgres:5432/mydb")
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://myuser:mypassword@postgres_test:5432/mytestdb")
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

# Создаем экземпляр настроек
settings = Settings()

# Выбираем URL: TEST_DATABASE_URL для тестов, DATABASE_URL для приложения
db_url = settings.TEST_DATABASE_URL if os.getenv("PYTEST_CURRENT_TEST") or os.getenv("DATABASE_URL", "").endswith("mytestdb") else settings.DATABASE_URL

# Подключение к базе данных
engine = create_async_engine(db_url, echo=True)

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Зависимость для FastAPI
async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session