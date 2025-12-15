# HireMeBahamas Backend - Project Structure

## ✅ Correct FastAPI Project Structure

The backend follows a clean, modular FastAPI structure with proper separation of concerns:

```
backend/
└── app/
    ├── main.py                 # Application entry point - wires routers together
    ├── core/                   # Core functionality (config, database, security, etc.)
    │   ├── __init__.py
    │   ├── config.py           # ✅ Configuration & environment variables
    │   ├── database.py         # ✅ Database connection & session management
    │   ├── security.py         # Authentication & security utilities
    │   ├── metrics.py          # Monitoring & metrics
    │   ├── redis_cache.py      # Caching layer
    │   └── ...
    ├── api/                    # API route handlers (routers)
    │   ├── __init__.py
    │   ├── auth.py             # ✅ Authentication endpoints
    │   ├── users.py            # ✅ User management endpoints
    │   ├── jobs.py             # ✅ Job posting endpoints
    │   └── ...
    ├── models/                 # Database models (SQLAlchemy)
    │   ├── __init__.py
    │   └── ...
    ├── schemas/                # Pydantic schemas for request/response validation
    │   ├── __init__.py
    │   ├── auth.py
    │   ├── job.py
    │   └── ...
    └── database.py             # Re-exports from core.database (backward compatibility)
```

## 📋 Module Responsibilities

### 1. `main.py` - Application Wiring
**Primary Responsibility:** Wire routers together and configure the FastAPI app.

**Ideal Structure** (see `main_simple_example.py`):
```python
from fastapi import FastAPI
from app.api import auth, users, jobs

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(jobs.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Current Structure:** The production `main.py` includes additional complexity for:
- Pydantic forward reference resolution (required for the codebase)
- CORS middleware configuration
- Startup/shutdown event handlers
- Request logging middleware
- Health check endpoints with database connectivity
- Socket.IO integration for real-time messaging

### 2. `core/config.py` - Configuration Management
**Responsibility:** Centralize all environment variable reads and configuration logic.

**Key Features:**
- `Settings` class with all configuration parameters
- Database connection settings
- CORS origins
- No direct environment variable reads elsewhere in the code

### 3. `core/database.py` - Database Layer
**Responsibility:** Database connection, session management, and initialization.

**Key Features:**
- Async SQLAlchemy engine configuration
- Connection pooling with Railway/Vercel optimization
- SSL/TLS configuration for PostgreSQL
- Session factory (`get_db()` dependency)
- Database initialization with retry logic
- Connection health checks

**No database logic in:** `main.py`, `api/` routers (they just use `get_db()`)

### 4. `api/` - API Routers
**Responsibility:** Define API endpoints and route handlers.

**Key Features:**
- Each file exports a `router` object (FastAPI APIRouter)
- Business logic lives here
- Use `Depends(get_db)` for database access
- Use `Depends(get_current_user)` for authentication

**Example:**
```python
from fastapi import APIRouter, Depends
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
async def list_resources(db: AsyncSession = Depends(get_db)):
    # Route logic here
    pass
```

### 5. `schemas/` - Pydantic Models
**Responsibility:** Request/response validation and serialization.

**Key Features:**
- Pydantic BaseModel subclasses
- Input validation
- Response serialization
- Type safety

## 🔑 Key Principles

### ✅ DO:
- **Separate concerns:** Configuration in `core/config.py`, database in `core/database.py`, routes in `api/`
- **Use dependency injection:** `Depends(get_db)`, `Depends(get_current_user)`
- **Import from core:** `from app.core.database import get_db`
- **Keep routers focused:** One resource per file (users, jobs, auth)

### ❌ DON'T:
- **Don't read env vars** in `main.py` or route handlers (use `core/config.py`)
- **Don't create DB connections** in route handlers (use `Depends(get_db)`)
- **Don't put business logic** in `main.py` (belongs in `api/` routers)
- **Don't mix concerns:** Keep auth logic in `api/auth.py`, not scattered

## 🚀 Running the Application

```bash
# From backend directory
uvicorn app.main:app --reload

# Or using the entry point
python -m app.main
```

## 📝 Adding a New Feature

1. **Add configuration** (if needed): `core/config.py`
2. **Add database model** (if needed): `models/`
3. **Add Pydantic schemas**: `schemas/your_feature.py`
4. **Create API router**: `api/your_feature.py`
5. **Register router** in `main.py`:
   ```python
   from app.api import your_feature
   app.include_router(your_feature.router)
   ```

## 🔧 Maintenance Notes

- **Database changes:** Modify `core/database.py`
- **Configuration changes:** Modify `core/config.py`
- **API changes:** Modify files in `api/`
- **Schema changes:** Modify files in `schemas/`

The goal is to maintain clear separation of concerns and make the codebase easy to navigate and maintain.
