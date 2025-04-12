import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.table import Table
from app.schemas.table import TableCreate

logger = logging.getLogger(__name__)


class TableService:
    async def get(self, db: AsyncSession):
        logger.info("Получение списка всех столиков")
        result = await db.execute(select(Table))
        tables = result.scalars().all()
        logger.debug(f"Найдено {len(tables)} столиков")
        return tables

    async def create(self, table_data: TableCreate, db: AsyncSession):
        logger.info("Создание нового столика")
        table = Table(**table_data.model_dump())
        db.add(table)
        await db.commit()
        await db.refresh(table)
        logger.debug(f"Создан столик: {table}")
        return table

    async def delete(self, table_id: int, db: AsyncSession):
        logger.info(f"Удаление столика с ID={table_id}")
        stmt = delete(Table).where(Table.id == table_id)
        await db.execute(stmt)
        await db.commit()
        logger.debug(f"Удалён столик с ID={table_id}")


table_service = TableService()

