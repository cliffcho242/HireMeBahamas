"""
Central Error Handling for HireMeBahamas API

This module provides centralized error handling for the FastAPI application.
It registers global exception handlers to catch and log all unhandled exceptions.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

log = logging.getLogger("app")


def register_error_handlers(app):
    """Register global error handlers for the FastAPI application.
    
    This function registers exception handlers that catch all unhandled exceptions
    and return consistent JSON responses to the client while logging the errors.
    
    Args:
        app: The FastAPI application instance
    """
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler to catch all unhandled exceptions.
        
        This handler ensures that:
        1. All exceptions are logged with full context
        2. Clients receive a consistent error response format
        3. Sensitive information is not exposed to clients
        
        Args:
            request: The incoming request that caused the exception
            exc: The unhandled exception
            
        Returns:
            JSONResponse with error details
        """
        log.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
