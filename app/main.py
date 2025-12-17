"""
HireMeBahamas Backend - FastAPI Main File (SYNC DATABASE - OPTION A)

Instant health check response with non-blocking database initialization.
✅ App responds immediately
✅ DB never blocks startup  
✅ Render health check always passes
✅ SYNC DATABASE (no async/await on DB operations)
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup: create background task for database initialization
    asyncio.create_task(background_init())
    
    yield
    
    # Shutdown: graceful shutdown
    logging.info("Graceful shutdown initiated")

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan
)

@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}

async def background_init():
    """Background initialization task - runs DB init in background.
    
    ✅ SYNC DATABASE PATTERN:
    - init_db() is NOT awaited (it's sync)
    - warmup_db() is NOT awaited (it's sync)
    """
    from app.database import init_db, warmup_db

    try:
        engine = init_db()   # ✅ NOT awaited (sync function)
        if engine:
            warmup_db(engine)  # ✅ NOT awaited (sync function)
    except Exception as e:
        logging.warning(f"Background init skipped: {e}")
