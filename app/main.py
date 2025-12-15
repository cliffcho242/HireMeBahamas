"""
HireMeBahamas Backend - Simplified Entry Point

This module provides a simplified import path for the FastAPI application.
Instead of: uvicorn api.backend_app.main:app
Use: uvicorn app.main:app

This makes deployment configuration cleaner and more standard.

The backend exports both 'app' (FastAPI) and 'socket_app' (Socket.IO wrapper).
- socket_app = Socket.IO wrapped app (when Socket.IO is available)
- app = Standard FastAPI app (always available)

For deployment, use 'app' as the standard entry point. The backend will
automatically use socket_app internally when Socket.IO features are enabled.
"""

# Import the FastAPI app from the actual backend location
from api.backend_app.main import app, socket_app

# Export both for flexibility
# Most deployments should use 'app' which works with or without Socket.IO
__all__ = ['app', 'socket_app']
