"""
HireMeBahamas API - Main Application Entry Point

This is the main FastAPI application with OpenAPI documentation enabled.
Documentation is automatically organized by tags.

Pattern from problem statement:
    from fastapi import FastAPI
    from app.api.v1 import router as v1_router
    from app.errors import register_error_handlers
    from app.logging import setup_logging

    setup_logging()

    app = FastAPI(
        title="HireMeBahamas API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    register_error_handlers(app)

    app.include_router(v1_router)
    
    Docs now live at:
        •	/docs
        •	/redoc

    Organized by tags automatically.

This module re-exports the fully configured backend application which already
implements this exact pattern. The actual implementation is in api/backend_app/main.py
which has:
- FastAPI app with docs_url="/docs" and redoc_url="/redoc"
- All API routers included with proper tags (analytics, auth, jobs, users, etc.)
- Error handlers registered
- Logging configured
"""
from app.errors import register_error_handlers
from app.logging import setup_logging

# Set up logging
setup_logging()

# Import the fully configured backend app
# api/backend_app/main.py already implements the pattern from the problem statement:
# - FastAPI app with docs_url="/docs" and redoc_url="/redoc"  
# - All routers included with tags (analytics, auth, debug, feed, health, hireme, jobs, messages, notifications, posts, profile_pictures, reviews, upload, users)
# - Documentation automatically organized by tags
from api.backend_app.main import app

# Register error handlers
register_error_handlers(app)

# Export the app
__all__ = ['app']
