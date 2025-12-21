"""
Authentication module for HireMeBahamas API.

Provides JWT-based authentication with secure token handling.
"""

from app.auth.dependencies import get_current_user, get_current_user_optional
from app.auth.jwt import create_access_token, decode_access_token

__all__ = [
    "get_current_user",
    "get_current_user_optional",
    "create_access_token",
    "decode_access_token",
]
