"""
Configuration module for application-wide settings.

This module re-exports configuration values from app.core.config
for easier imports throughout the application.
"""
from app.core.config import settings

# Re-export REDIS_URL for easy access
REDIS_URL = settings.REDIS_URL
