"""
Application entry point for Render deployment.

This module provides Flask app entry points for Gunicorn/WSGI deployment.

Available entry points:
- app:application (RECOMMENDED) - WSGI standard name
- app:app - Flask app instance (also works)

Recommended Gunicorn command:
    gunicorn app:application --config gunicorn.conf.py

Or use the direct import:
    gunicorn final_backend_postgresql:application --config gunicorn.conf.py
"""

from final_backend_postgresql import app, application  # noqa: F401
