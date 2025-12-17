"""
HireMeBahamas Backend - FastAPI Main File (Final Form)

Instant health check response with non-blocking database initialization.
✅ App responds immediately
✅ DB never blocks startup
✅ Render health check always passes
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
    """Initialize database in background (non-blocking).
    
    Note: Using sync database functions with asyncio.to_thread to avoid blocking.
    """
    import asyncio
    from app.database import init_db, warmup_db

    try:
        # Run sync init_db in a thread to avoid blocking the event loop
        success = await asyncio.to_thread(init_db)
        if success:
            # Run sync warmup_db in a thread to avoid blocking the event loop
            await asyncio.to_thread(warmup_db)
    except Exception as e:
        logging.warning(f"Background init skipped: {e}")
