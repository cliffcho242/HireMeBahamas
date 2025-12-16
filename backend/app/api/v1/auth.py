"""Authentication API v1 - Re-exports router from parent API module."""
from app.api.auth import router

__all__ = ["router"]
