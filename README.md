---

# 🍽️ Tables API: Restaurant Table Reservation Service

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-blue)
![pytest](https://img.shields.io/badge/pytest-tested-brightgreen)

This project is a REST API for managing restaurant table reservations, developed as a test assignment. It allows users to create, view, and delete tables and reservations, ensuring no conflicting bookings occur. The application is built with **FastAPI**, uses **PostgreSQL** for data storage, and is fully containerized with **Docker** and **docker-compose**.

---

## 📌 Overview

The **Tables API** provides a robust solution for restaurant table management, implementing the following functionality:
- **Tables**: Create, list, and delete tables with details like name, seats, and location.
- **Reservations**: Create, list, and delete reservations with validation to prevent overlapping bookings.
- **Business Logic**: Ensures no table is double-booked for the same time slot.

The project follows a modular architecture, includes automated tests, logging, and database migrations for scalability and maintainability.

---

## ✅ Features

### Models
- **Table**:
  - `id`: Unique identifier
  - `name`: Table name (e.g., "Table 1")
  - `seats`: Number of seats
  - `location`: Location in the restaurant (e.g., "Window Hall", "Terrace")
- **Reservation**:
  - `id`: Unique identifier
  - `customer_name`: Name of the customer
  - `table_id`: Foreign key to Table
  - `reservation_time`: Date and time of the reservation
  - `duration_minutes`: Duration of the reservation

### API Endpoints
- **Tables**:
  - `GET /tables/` – List all tables
  - `POST /tables/` – Create a new table
  - `DELETE /tables/{id}` – Delete a table (only if no active reservations)
- **Reservations**:
  - `GET /reservations/` – List all reservations
  - `POST /reservations/` – Create a new reservation
  - `DELETE /reservations/{id}` – Delete a reservation

### Key Logic
- Prevents overlapping reservations by validating `table_id`, `reservation_time`, and `duration_minutes`.
- Returns clear error messages for conflicts (e.g., "Table is already reserved").
- Ensures tables with active reservations cannot be deleted.

---

## ⚙️ Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL with SQLModel for ORM
- **Migrations**: Alembic for database schema management
- **Containerization**: Docker and docker-compose
- **Testing**: pytest with async support for API endpoint tests
- **Logging**: Integrated logging for debugging and monitoring

---

## 📦 Project Structure
```
tables/
├── app/
│   ├── __init__.py                 # Module initialization
│   ├── main.py                     # FastAPI application entry point
│   ├── database.py                 # Database configuration and session management
│   ├── models/                     # SQLModel models (Table, Reservation)
│   │   ├── __init__.py             # Module initialization
│   │   ├── reservations.py         # Model Reservation
│   │   ├── table.py                # Model Table
│   ├── schemas/                    # Pydantic schemas for request/response validation
│   │   ├── __init__.py             # Module initialization
│   │   ├── reservations.py         # Schema Reservation
│   │   ├── table.py                # Schema Table
│   ├── routers/                    # API route handlers
│   │   ├── __init__.py             # Module initialization
│   │   ├── reservations.py         # Router Reservation
│   │   ├── table.py                # Router Table
│   └── services/                   # Business logic for tables and reservations
│   │   ├── __init__.py             # Module initialization
│   │   ├── reservations_service.py # Service Reservation
│   │   ├── table_service.py        # Service Table
├── tests/
│   └── test_api.py                 # pytest tests for API endpoints
├── alembic/                        # Database migrations
├── docker-compose.yml              # Docker services (app, postgres, tests)
├── .gitignore                      # Git ignore rules
├── pytest.ini                      # pytest configuration
└── README.md                       # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Docker and docker-compose installed
- Git

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/ildivo/tables.git
   cd tables
   ```

2. **Start the services**:
   ```bash
   docker-compose up --build
   ```
   This will:
   - Build and run the FastAPI app (`app`) on `http://localhost:8001`
   - Start PostgreSQL (`postgres`) for the app
   - Start a test PostgreSQL instance (`postgres_test`) for tests
   - Run pytest tests (`test`) and exit

3. **Access the API**:
   - API documentation: `http://localhost:8001/docs`
   - Health check: `http://localhost:8001/health`

4. **Run tests manually** (optional):
   ```bash
   docker-compose exec test pytest -v tests/test_api.py
   ```

5. **Stop the services**:
   ```bash
   docker-compose down -v
   ```

---

## 🧪 Testing
The project includes **pytest** tests covering:
- Table creation, listing, and deletion
- Reservation creation, listing, and deletion
- Validation of overlapping reservations
- Edge cases (e.g., deleting a table with active reservations)

Run tests:
```bash
docker-compose run test
```

---

## 🛠️ Database Migrations
Database schema is managed with **Alembic**. To apply migrations:
```bash
docker-compose exec app alembic upgrade head
```

To create a new migration after model changes:
```bash
docker-compose exec app alembic revision --autogenerate -m "Description"
```

---

## 📝 Notes
- **Logging**: Debug-level logs are enabled for development (see `docker-compose.yml`).
- **Extensibility**: The modular structure (`routers/`, `services/`) makes it easy to add new features, such as user authentication or table availability checks.
- **Improvements**: Potential enhancements include rate limiting, advanced reservation filters, or a frontend interface.

---

## 🧠 Implementation Highlights
- **Architecture**: Clean separation of concerns with models, schemas, routers, and services.
- **Business Logic**: Robust validation prevents reservation conflicts using datetime checks.
- **Docker**: Fully containerized setup with isolated databases for app and tests.
- **Tests**: Comprehensive async tests ensure API reliability.
- **Code Quality**: Type hints, Pydantic validation, and consistent error handling.

---

## 📬 Contact
Feel free to reach out for feedback or collaboration:
- GitHub: [ildivo](https://github.com/Ildivo/)
- Email: [evfincom@protonmail.com](evfincom@protonmail.com)

---

*This project was developed as a test assignment to demonstrate proficiency in FastAPI, PostgreSQL, Docker, and testing. Bon appétit! 🍽️*

---
