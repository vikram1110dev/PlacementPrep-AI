# PlacementPrep AI Backend

This is the production-ready FastAPI backend for PlacementPrep AI. It is built strictly following Clean Architecture, Repository Pattern, and Service Layers.

## 🏗 Tech Stack
- **Python 3.13+**
- **FastAPI** (Web Framework)
- **SQLAlchemy 2.0** (ORM)
- **Alembic** (Migrations)
- **MySQL 8.0** (Database)
- **Pydantic v2** (Data Validation)
- **Loguru** (Logging)

## 📁 Folder Structure (Clean Architecture)

- `app/api/`: API router definitions for each module.
- `app/core/`: Configuration, security, and global constants.
- `app/database/`: Database connection and SQLAlchemy base.
- `app/models/`: SQLAlchemy ORM definitions.
- `app/schemas/`: Pydantic definitions for standard request/response payloads.
- `app/repositories/`: Database abstraction layer (SQL queries go here).
- `app/services/`: Business logic layer (Calls repositories).
- `app/middleware/`: Global error handlers and request performance tracking.
- `main.py`: The Application Factory.

## 🚀 Installation & Setup

### Option 1: Native Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   cp .env.example .env
   ```
   *Update your `.env` with actual MySQL credentials.*
4. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

### Option 2: Docker Setup (Recommended)

To spin up the API, MySQL database, and Redis cache automatically:
```bash
docker-compose up --build
```
*The database schema (`database/schema.sql`) will automatically execute on the first boot of the MySQL container.*

## 🛣 Standard Response Format

All APIs return a standard format powered by Pydantic:
```json
{
    "success": true,
    "message": "Welcome to PlacementPrep AI Backend",
    "data": null,
    "errors": null
}
```

## 📝 Best Practices Used
- **Dependency Injection**: Services and repositories should be injected into FastAPI routes.
- **Loguru**: Standard `logging` is completely replaced by Loguru for colorized, easy-to-read, and file-rotated logs.
- **Standard Exceptions**: Any unhandled `500` or `422 Unprocessable Entity` is automatically intercepted and returned in the Standard Response Format to prevent client-side crashes.
