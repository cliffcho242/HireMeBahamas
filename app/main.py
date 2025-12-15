"""
HireMeBahamas Backend Application Main Entry Point

This module provides the 'app' variable for uvicorn deployment.
Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

The actual FastAPI application is implemented in api/backend_app/main.py
This file serves as a clean entry point for deployment platforms.

Note: For Socket.IO support, the backend uses socket_app internally, but
deployment platforms should use 'app' which is the ASGI-compatible application.
"""

from api.backend_app.main import app, socket_app

# Export app for standard ASGI deployment (Railway, Render, Heroku)
# socket_app is available but should only be used when explicitly needed
__all__ = ['app', 'socket_app']
