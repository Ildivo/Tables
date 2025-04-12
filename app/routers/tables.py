from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_session
from app.schemas import TableCreate, TableResponse
from app.services import table_service

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/", response_model=list[TableResponse])
async def get_tables(db: AsyncSession = Depends(get_async_session)):
    return await table_service.get(db)

@router.post("/", response_model=TableResponse, status_code=201)
async def create_table(table: TableCreate, db: AsyncSession = Depends(get_async_session)):
    return await table_service.create(table, db)

@router.delete("/{table_id}", status_code=204)
async def delete_table(table_id: int, db: AsyncSession = Depends(get_async_session)):
    await table_service.delete(table_id, db)
    return {"message": "Table deleted"}
