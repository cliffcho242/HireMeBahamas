# Database Module Migration Guide

## Overview

HireMeBahamas now has a **single source of truth** for all database configuration: `app/database.py`

This consolidation eliminates confusion, reduces maintenance burden, and ensures consistent database behavior across the entire application.

## What Changed?

### Before (Multiple Database Modules) ❌

Previously, there were multiple database configuration modules scattered across the codebase:

- `api/database.py` - Vercel serverless variant
- `api/backend_app/database.py` - Main backend variant
- `backend/app/database.py` - Duplicate backend variant
- `app/database.py` - Wrapper that delegated to backend_app

This led to:
- Confusion about which module to import
- Inconsistent configuration
- Difficult maintenance
- Potential for bugs

### After (Single Source of Truth) ✅

Now there is **ONE** database module:

- `app/database.py` - **SINGLE SOURCE OF TRUTH**

All other database modules are deprecated and will be removed in a future version.

## Migration Instructions

### For New Code

Always import from `app.database`:

```python
# ✅ CORRECT - Use single source of truth
from app.database import get_engine, get_db, init_db, close_db
from app.database import Base, AsyncSessionLocal
from app.database import test_db_connection, get_db_status
```

### For Existing Code

Update your imports gradually:

```python
# ❌ OLD - Deprecated
from api.database import get_engine
from api.backend_app.database import get_db
from backend.app.database import init_db

# ✅ NEW - Single source of truth
from app.database import get_engine, get_db, init_db
```

### Module Alias System

The application uses a module alias system where `sys.modules['app']` points to `backend_app`. This means:

```python
# These are equivalent due to module aliasing:
from app.database import get_engine
from backend_app.database import get_engine  # (via alias)

# However, always prefer explicit app.database imports
# as they clearly indicate use of the single source of truth
```

## Available Functions

The `app.database` module provides all necessary database functionality:

### Core Engine Management
- `get_engine()` - Get or create the database engine (lazy initialization)
- `engine` - LazyEngine wrapper for backward compatibility

### Session Management
- `get_db()` - Primary FastAPI dependency for database sessions
- `get_async_session()` - Alternative async session getter
- `AsyncSessionLocal` - Session factory for manual session creation
- `async_session` - Alias for AsyncSessionLocal

### Lifecycle Management
- `init_db()` - Initialize database tables with retry logic
- `close_db()` - Close database connections gracefully
- `close_engine()` - Legacy alias for close_db()

### Health & Monitoring
- `test_db_connection()` - Test database connectivity (returns tuple)
- `test_connection()` - Legacy alias (returns boolean)
- `warmup_db()` - Warm up connection pool
- `get_db_status()` - Get initialization status
- `get_pool_status()` - Get connection pool metrics

### ORM Base
- `Base` - SQLAlchemy declarative base for models

### Configuration Constants
- `DATABASE_URL` - Configured database URL
- `DB_PLACEHOLDER_URL` - Placeholder for invalid config
- `POOL_SIZE`, `MAX_OVERFLOW`, `POOL_TIMEOUT`, `POOL_RECYCLE`
- `CONNECT_TIMEOUT`, `COMMAND_TIMEOUT`, `STATEMENT_TIMEOUT_MS`

## Configuration

Database configuration is controlled via environment variables:

### Required
- `DATABASE_URL` - PostgreSQL connection string
  - Format: `postgresql://user:pass@host:5432/dbname?sslmode=require`
  - For asyncpg: `postgresql+asyncpg://user:pass@host:5432/dbname?sslmode=require`

### Optional
- `ENVIRONMENT` or `ENV` - Set to "production" to enforce DATABASE_URL
- `DB_POOL_SIZE` - Connection pool size (default: 5)
- `DB_MAX_OVERFLOW` - Pool burst capacity (default: 10)
- `DB_POOL_TIMEOUT` - Max wait time for connection (default: 30s)
- `DB_POOL_RECYCLE` - Connection recycle time (default: 300s)
- `DB_CONNECT_TIMEOUT` - Connection timeout (default: 5s)
- `DB_COMMAND_TIMEOUT` - Query timeout (default: 30s)
- `DB_STATEMENT_TIMEOUT_MS` - Statement timeout (default: 30000ms)
- `DB_ECHO` - Enable SQL logging (default: false)

## Production Safety Features

The new `app.database` module includes several production-safety features:

1. **Lazy Initialization** - Connections are created on first use, not at import time
2. **Graceful Degradation** - App starts even if DATABASE_URL is invalid
3. **Production Warnings** - Logs clear warnings if DATABASE_URL is missing in production
4. **SSL Enforcement** - Automatically adds `?sslmode=require` for cloud databases
5. **Connection Pooling** - Optimized pool settings for serverless environments
6. **Health Check Support** - Functions return status tuples for monitoring

## Testing

A comprehensive test suite verifies the single database path:

```bash
python test_single_database_path.py
```

This test verifies:
- ✅ `app.database` module exists with all required functions
- ✅ Old database modules have deprecation notices
- ✅ No code creates duplicate database engines
- ✅ Health endpoints don't require database access

## Backward Compatibility

Old database modules remain functional for backward compatibility:

- `api/database.py` - ⚠️ DEPRECATED (will be removed)
- `api/backend_app/database.py` - ⚠️ DEPRECATED (will be removed)
- `backend/app/database.py` - ⚠️ DEPRECATED (will be removed)

These modules include deprecation notices and will be removed in a future version.

## Example Usage

### FastAPI Endpoint with Database

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all users"""
    from app.models import User
    from sqlalchemy import select
    
    result = await db.execute(select(User))
    users = result.scalars().all()
    return {"users": [u.dict() for u in users]}
```

### Application Startup

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from app.database import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup: initialize database in background
    asyncio.create_task(init_db())
    
    yield
    
    # Shutdown: close connections
    await close_db()

app = FastAPI(lifespan=lifespan)
```

### Manual Session Management

```python
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models import User

async def get_user_count():
    """Get total user count"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return len(users)
```

## Benefits

The single source of truth approach provides:

1. **Clarity** - Developers know exactly where to import from
2. **Consistency** - Same configuration used throughout the app
3. **Maintainability** - Changes only need to be made in one place
4. **Testability** - Easier to test and mock database access
5. **Documentation** - Single, comprehensive documentation source
6. **Performance** - No duplicate engines or connections

## Questions?

If you have questions about the migration:

1. Check the deprecation notices in old database modules
2. Review the `app.database` module docstrings
3. Run the test suite: `python test_single_database_path.py`
4. Check existing code examples in `api/backend_app/api/*.py`

## Timeline

- **Now**: New code MUST use `app.database`
- **Soon**: Update existing imports to `app.database`
- **Future**: Remove deprecated database modules

Start migrating your imports today to avoid breaking changes in future versions!
