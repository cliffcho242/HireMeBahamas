"""
Error handling for HireMeBahamas
"""
from fastapi import HTTPException, status


class AppError(Exception):
    """Base application error"""
    pass


class NotFoundError(AppError):
    """Resource not found error"""
    pass


class UnauthorizedError(AppError):
    """Unauthorized access error"""
    pass


class ValidationError(AppError):
    """Validation error"""
    pass
