"""Posts API v1 - Re-exports router from parent API module."""
from app.api.posts import router

__all__ = ["router"]
