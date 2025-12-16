"""
STEP 17 — main.py (ENTRYPOINT)

This is the ideal FastAPI application structure where main.py serves as a clean
entrypoint that ONLY wires routers together.

Key principles:
- NO database logic
- NO environment variable reads  
- NO business logic
- ONLY router imports and inclusion

This structure makes the application modular, testable, and easy to maintain.

Note: This is a minimal reference example. In production (see app/main.py), you would
typically add:
- Router prefixes (e.g., prefix="/api/auth")
- Tags for API documentation
- CORS middleware
- Error handlers
- Additional configuration
"""
from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.feed.routes import router as feed_router
from app.health import router as health_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(health_router)
