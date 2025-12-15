"""
HireMeBahamas Backend Application Main Entry Point

This module provides the 'app' variable for uvicorn deployment.
Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

The actual FastAPI application is implemented in api/backend_app/main.py
This file serves as a clean entry point for deployment platforms.
"""

from api.backend_app.main import app

__all__ = ['app']
