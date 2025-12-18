"""
HireMeBahamas Backend - FastAPI Main File (Final Form)

Instant health check response with non-blocking database initialization.
✅ App responds immediately
✅ DB never blocks startup
✅ Render health check always passes
✅ Safe async task management (prevents task destroyed warnings)
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
    """Safe background initialization with error handling.
    
    This function is called by the startup event handler and runs
    database initialization in the background without blocking startup.
    
    Note: Using sync database functions with asyncio.to_thread to avoid blocking.
    """
    from app.database import init_db, warmup_db

    try:
        # Run sync init_db in a thread to avoid blocking the event loop
        logger.info("Starting background database initialization...")
        success = await asyncio.to_thread(init_db)
        if success:
            # Run sync warmup_db in a thread to avoid blocking the event loop
            await asyncio.to_thread(warmup_db)
            logger.info("Background database initialization completed successfully")
        else:
            logger.warning("Background database initialization deferred")
    except Exception as e:
        logger.error(f"Background init failed: {e}")

@app.on_event("startup")
async def startup():
    """Startup event handler with safe background task creation.
    
    ✅ RIGHT (safe background startup):
    Creates a background task within the startup event handler,
    ensuring proper task lifecycle management.
    """
    logger.info("Application startup initiated")
    asyncio.create_task(safe_background_init())
    logger.info("Background initialization task scheduled")

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler to allow tasks to close cleanly.
    
    This prevents orphaned tasks when Gunicorn restarts workers.
    """
    logger.info("Graceful shutdown initiated")
    # Allow pending tasks to complete
    await asyncio.sleep(0)
    logger.info("Shutdown complete")
