from fastapi import APIRouter
from app.routers.tables import router as tables_router
from app.routers.reservations import router as reservations_router

router = APIRouter()
router.include_router(tables_router, prefix="/tables", tags=["Tables"])
router.include_router(reservations_router, prefix="/reservations", tags=["Reservations"])
