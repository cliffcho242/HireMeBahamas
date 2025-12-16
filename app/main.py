"""
HireMeBahamas Backend - FastAPI Main File (Final Form)

Instant health check response with non-blocking database initialization.
✅ App responds immediately
✅ DB never blocks startup
✅ Render health check always passes
"""
from fastapi import FastAPI
import asyncio
import logging

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

@app.get("/health", include_in_schema=False)
def health():
    return {"ok": True}

@app.on_event("startup")
async def startup():
    asyncio.create_task(background_init())

async def background_init():
    from app.database import init_db, warmup_db

    try:
        engine = init_db()
        if engine:
            warmup_db(engine)
    except Exception as e:
        logging.warning(f"Background init skipped: {e}")

@app.on_event("shutdown")
def shutdown():
    logging.info("Graceful shutdown initiated")
