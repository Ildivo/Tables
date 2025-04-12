from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas import ReservationCreate, ReservationResponse
from app.services import reservation_service

router = APIRouter()

@router.get("/", response_model=list[ReservationResponse])
async def get_reservations(db: AsyncSession = Depends(get_async_session)):
    return await reservation_service.get(db)

@router.post("/", response_model=ReservationResponse, status_code=201)
async def create_reservation(reservation: ReservationCreate, db: AsyncSession = Depends(get_async_session)):
    return await reservation_service.create(reservation, db)

@router.delete("/{reservation_id}", status_code=204)
async def delete_reservation(reservation_id: int, db: AsyncSession = Depends(get_async_session)):
    await reservation_service.delete(reservation_id, db)
    return {"message": "Reservation deleted"}
