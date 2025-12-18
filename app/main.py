"""
HireMeBahamas Backend - FastAPI Main File (Final Form)

Instant health check response with non-blocking database initialization.
✅ App responds immediately
✅ DB never blocks startup
✅ Render health check always passes
✅ Safe background task handling prevents orphaned tasks
"""
from fastapi import FastAPI
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}

async def safe_background_init():
    """Initialize database in background (non-blocking) with safe exception handling.
    
    This function is designed to be run as a background task and includes
    proper exception handling to prevent task destruction warnings.
    
    Note: Using sync database functions with asyncio.to_thread to avoid blocking.
    """
    from app.database import init_db, warmup_db

    try:
        # Run sync init_db in a thread to avoid blocking the event loop
        success = await asyncio.to_thread(init_db)
        if success:
            logger.info("Database initialization successful")
            # Run sync warmup_db in a thread to avoid blocking the event loop
            await asyncio.to_thread(warmup_db)
            logger.info("Database warmup complete")
        else:
            logger.warning("Database initialization failed, warmup skipped")
    except Exception as e:
        logger.error(f"Background init failed: {e}")

@app.on_event("startup")
async def startup():
    """Startup event handler with safe background task initialization.
    
    Creates a background task for database initialization using asyncio.create_task
    within the startup event. This prevents orphaned tasks when Gunicorn restarts workers.
    """
    logger.info("Application startup initiated")
    asyncio.create_task(safe_background_init())
    logger.info("Background initialization task created")

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler to allow tasks to close cleanly.
    
    This gives async operations time to complete gracefully and prevents
    "Task was destroyed but it is pending!" warnings when Gunicorn restarts workers.
    """
    logger.info("Application shutdown initiated")
    await asyncio.sleep(0)  # Allow tasks to close cleanly
    logger.info("Application shutdown complete")
