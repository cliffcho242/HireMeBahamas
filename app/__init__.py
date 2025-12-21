"""
HireMeBahamas - Application entry point module
"""

# Expose the FastAPI application for gunicorn entry point (app:app)
from .main import app  # noqa: F401
