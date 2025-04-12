from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.reservation import Reservation
from app.models.table import Table
from app.schemas.reservation import ReservationCreate
from fastapi import HTTPException, status
from sqlalchemy import and_, delete,  text
from datetime import datetime, timedelta
import sqlalchemy as sa
import logging

logger = logging.getLogger(__name__)

# Функция проверки доступности стола
async def check_table_availability(db: AsyncSession, table_id: int, reservation_time: datetime, duration_minutes: int):
    end_time = reservation_time + timedelta(minutes=duration_minutes)

    # Выполняем запрос для поиска конфликтующих броней
    result = await db.execute(
        select(Reservation).filter(
            Reservation.table_id == table_id,
            and_(
                Reservation.reservation_time < end_time,
                # Используем SQL-выражение для вычисления конца брони
                (Reservation.reservation_time + sa.text("INTERVAL '1 minute' * duration_minutes")) > reservation_time
            )
        )
    )

    conflicting_reservations = result.scalars().all()
    is_available = len(conflicting_reservations) == 0

    if not is_available:
        logger.warning(f"Конфликт брони для стола {table_id} на время {reservation_time}")
    return is_available

class ReservationService:
    async def get(self, db: AsyncSession):
        """Получение списка всех броней."""
        logger.info("Получение списка всех броней")
        result = await db.execute(select(Reservation))
        reservations = result.scalars().all()
        logger.debug(f"Найдено {len(reservations)} броней")
        return reservations

    async def create(self, reservation_data: ReservationCreate, db: AsyncSession):
        """Создание новой брони с проверкой доступности стола."""
        logger.info(f"Создание новой брони: {reservation_data}")
        reservation = Reservation(**reservation_data.model_dump())

        # Проверка существования стола
        result = await db.execute(select(Table).filter(Table.id == reservation.table_id))
        table = result.scalar_one_or_none()

        if table is None:
            logger.error(f"Стол с ID {reservation.table_id} не найден")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table with id {reservation.table_id} not found"
            )

        # Проверка доступности стола
        if not await check_table_availability(
            db, reservation.table_id, reservation.reservation_time, reservation.duration_minutes
        ):
            logger.error(f"Стол {reservation.table_id} уже забронирован на время {reservation.reservation_time}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Table is already reserved for the selected time."
            )

        # Добавление и сохранение брони
        db.add(reservation)
        await db.commit()
        await db.refresh(reservation)
        logger.info(f"Бронь успешно создана: ID={reservation.id}")
        return reservation

    async def delete(self, reservation_id: int, db: AsyncSession):
        """Удаление брони по ID с проверкой существования."""
        logger.info(f"Удаление брони с ID={reservation_id}")
        result = await db.execute(select(Reservation).filter(Reservation.id == reservation_id))
        reservation = result.scalar_one_or_none()

        if reservation is None:
            logger.error(f"Бронь с ID {reservation_id} не найдена")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation with id {reservation_id} not found"
            )

        await db.execute(delete(Reservation).where(Reservation.id == reservation_id))
        await db.commit()
        logger.info(f"Бронь с ID={reservation_id} успешно удалена")
        return {"message": f"Reservation {reservation_id} deleted"}

reservation_service = ReservationService()