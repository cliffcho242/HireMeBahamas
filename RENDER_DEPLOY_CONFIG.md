# RENDER DEPLOYMENT CONFIG - TIMEOUT FIX

## DATABASE_URL (Environment Variable)

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@dpg-XXXXX-a.oregon-postgres.render.com/yourdb_XXXX?sslmode=require&connect_timeout=30&options=-c%20jit=off
```

## Engine Code (backend/app/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import os

engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    pool_size=3,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "connect_timeout": 30,
        "server_settings": {"jit": "off"},
        "ssl": "require"
    }
)
```

## Render Settings

1. **Instance Memory**: 1 GB minimum
2. **Start Command**: `gunicorn main:app -k uvicorn.workers.UvicornWorker --workers 1 --preload`
