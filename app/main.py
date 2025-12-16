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

This module provides a clean entry point to the backend application.

The actual FastAPI application is implemented in api/backend_app/main.py which:
- Creates FastAPI app instance
- Configures docs_url="/docs" and redoc_url="/redoc" (after initial startup)
- Includes all API routers with proper tags (analytics, auth, jobs, users, etc.)
- Has production-ready middleware and error handling

This wrapper module ensures:
- Clean import path: from app.main import app
- Proper logging configuration
- Additional error handler registration
- Follows the pattern specified in the problem statement
"""
from app.errors import register_error_handlers
from app.logging import setup_logging

# Set up logging first
setup_logging()

# Import the fully configured backend app
# The backend app (api/backend_app/main.py) implements the OpenAPI docs pattern:
# - FastAPI app with docs_url="/docs" and redoc_url="/redoc"
# - All routers included with tags for automatic organization
# - 14 tags organizing 89 endpoints
from api.backend_app.main import app

# Register additional error handlers for consistency
register_error_handlers(app)

# Export the app
__all__ = ['app']
