import pytest
import pytest_asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import ASGITransport
from app.main import app
from app.database import get_async_session, settings
from app.models import Base

# Укажите действительные учетные данные
#TEST_DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@localhost:5432/mydb"
engine = create_async_engine(settings.TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False
)

async def override_get_async_session():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

@pytest_asyncio.fixture(scope="function")
async def async_client():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    await client.aclose()

@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

    async with TestingSessionLocal() as session:
        async with session.begin() as transaction:
            yield session
            await transaction.rollback()
        await session.close()

    await engine.dispose()

@pytest.mark.asyncio
async def test_create_table(async_client: httpx.AsyncClient, db_session: AsyncSession):
    response = await async_client.post("/tables/", json={
        "name": "Test Table",
        "seats": 4,
        "location": "зал у окна"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Table"
    assert data["seats"] == 4
    assert data["location"] == "зал у окна"

@pytest.mark.asyncio
async def test_create_reservation(async_client: httpx.AsyncClient, db_session: AsyncSession):
    table_response = await async_client.post("/tables/", json={
        "name": "Table with Reservation",
        "seats": 2,
        "location": "терраса"
    })
    assert table_response.status_code == 201
    table = table_response.json()

    reservation_data = {
        "table_id": table["id"],
        "customer_name": "Alice",
        "reservation_time": "2025-04-10T18:00:00",
        "duration_minutes": 60
    }
    reservation_response = await async_client.post("/reservations/", json=reservation_data)
    assert reservation_response.status_code == 201
    reservation = reservation_response.json()
    assert reservation["customer_name"] == "Alice"
    assert reservation["table_id"] == table["id"]
    assert reservation["duration_minutes"] == 60

@pytest.mark.asyncio
async def test_delete_table_without_reservations_success(async_client: httpx.AsyncClient, db_session: AsyncSession):
    table_response = await async_client.post("/tables/", json={
        "name": "Free Table",
        "seats": 4,
        "location": "зал у окна"
    })
    assert table_response.status_code == 201
    table = table_response.json()

    response = await async_client.delete(f"/tables/{table['id']}")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_table_with_reservation_fails(async_client: httpx.AsyncClient, db_session: AsyncSession):
    table_response = await async_client.post("/tables/", json={
        "name": "Busy Table",
        "seats": 2,
        "location": "зал у окна"
    })
    assert table_response.status_code == 201
    table = table_response.json()

    reservation_response = await async_client.post("/reservations/", json={
        "table_id": table["id"],
        "customer_name": "Bob",
        "reservation_time": "2025-04-10T19:00:00",
        "duration_minutes": 60
    })
    assert reservation_response.status_code == 201

    response = await async_client.delete(f"/tables/{table['id']}")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_create_overlapping_reservation_fails(async_client: httpx.AsyncClient, db_session: AsyncSession):
    # Создаем стол
    table_response = await async_client.post("/tables/", json={
        "name": "Busy Table",
        "seats": 2,
        "location": "зал у окна"
    })
    assert table_response.status_code == 201
    table = table_response.json()

    # Создаем первую бронь
    first_reservation = {
        "table_id": table["id"],
        "customer_name": "Alice",
        "reservation_time": "2025-04-10T18:00:00",
        "duration_minutes": 60  # с 18:00 до 19:00
    }
    response = await async_client.post("/reservations/", json=first_reservation)
    assert response.status_code == 201

    # Пытаемся создать вторую бронь, пересекающуюся с первой
    second_reservation = {
        "table_id": table["id"],
        "customer_name": "Bob",
        "reservation_time": "2025-04-10T18:30:00",  # Пересекается с 18:00-19:00
        "duration_minutes": 60
    }
    response = await async_client.post("/reservations/", json=second_reservation)
    assert response.status_code == 400  # Ожидаем ошибку
    assert "table is already reserved for the selected time" in response.text.lower()  # Проверяем сообщение об ошибке

@pytest.mark.asyncio
async def test_delete_reservation_success(async_client: httpx.AsyncClient, db_session: AsyncSession):
    # Создаем стол
    table_response = await async_client.post("/tables/", json={
        "name": "Table for Deletion",
        "seats": 2,
        "location": "зал у окна"
    })
    assert table_response.status_code == 201
    table = table_response.json()

    # Создаем резервацию
    reservation_data = {
        "table_id": table["id"],
        "customer_name": "Charlie",
        "reservation_time": "2025-04-10T20:00:00",
        "duration_minutes": 60
    }
    reservation_response = await async_client.post("/reservations/", json=reservation_data)
    assert reservation_response.status_code == 201
    reservation = reservation_response.json()

    # Удаляем резервацию
    response = await async_client.delete(f"/reservations/{reservation['id']}")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_get_tables_success(async_client: httpx.AsyncClient, db_session: AsyncSession):
    # Создаем стол
    table_response = await async_client.get("/tables/")
    assert table_response.status_code == 200

@pytest.mark.asyncio
async def test_get_reservations_success(async_client: httpx.AsyncClient, db_session: AsyncSession):
    # Создаем резервацию
    table_response = await async_client.get("/reservations/")
    assert table_response.status_code == 200

@pytest.mark.asyncio
async def test_create_reservation_invalid_duration(async_client: httpx.AsyncClient, db_session: AsyncSession):
    table_response = await async_client.post("/tables/", json={
        "name": "Test Table",
        "seats": 4,
        "location": "зал у окна"
    })
    assert table_response.status_code == 201
    table = table_response.json()

    invalid_reservation = {
        "table_id": table["id"],
        "customer_name": "Alice",
        "reservation_time": "2025-04-10T18:00:00",
        "duration_minutes": -5
    }
    response = await async_client.post("/reservations/", json=invalid_reservation)
    assert response.status_code == 422
    assert "Duration must be positive" in response.text