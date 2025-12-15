"""
HireMeBahamas Backend Application Entry Point

This module provides a clean entry point for uvicorn to start the FastAPI application.
It imports the actual application from api.backend_app.main.
"""

from api.backend_app.main import app

__all__ = ['app']
