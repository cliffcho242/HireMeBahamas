"""Health API v1 - Re-exports router from parent API module."""
from app.api.health import router

__all__ = ["router"]
