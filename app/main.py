"""
HireMeBahamas Backend Application Main Entry Point

This module provides the 'app' variable for uvicorn deployment.
Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

The actual FastAPI application is implemented in api/backend_app/main.py
This file serves as a clean entry point for deployment platforms.

Note: Both 'app' (FastAPI) and 'socket_app' (with Socket.IO) are exported.
When Socket.IO is not available, socket_app falls back to the regular app.
Use 'app.main:app' for standard deployment (recommended for most platforms).
Use 'app.main:socket_app' if you specifically need Socket.IO support.
"""

try:
    from api.backend_app.main import app, socket_app
except ImportError as e:
    # Fallback: If import fails, try creating a minimal app
    import sys
    print(f"Warning: Failed to import from api.backend_app.main: {e}", file=sys.stderr)
    print("Creating minimal fallback application", file=sys.stderr)
    from fastapi import FastAPI
    app = FastAPI(title="HireMeBahamas API (Fallback)")
    socket_app = app

# Export app for standard ASGI deployment (Railway, Render, Heroku)
# socket_app is available and includes Socket.IO support when python-socketio is installed
__all__ = ['app', 'socket_app']
