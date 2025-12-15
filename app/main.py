"""
HireMeBahamas Backend - Simplified Entry Point

This module provides a simplified import path for the FastAPI application.
Instead of: uvicorn api.backend_app.main:app
Use: uvicorn app.main:app

This makes deployment configuration cleaner and more standard.
"""

# Import the FastAPI app from the actual backend location
from api.backend_app.main import app

# Export app for uvicorn
__all__ = ['app']
