"""
Application entry point for Render deployment.

This module provides the 'app' variable that Render's default gunicorn
command expects (gunicorn app:app).
"""

from final_backend_postgresql import app, application  # noqa: F401
