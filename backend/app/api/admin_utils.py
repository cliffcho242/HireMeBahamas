"""
Shared utilities for admin-only endpoints.
"""
from fastapi import Depends, HTTPException, status
from app.models import User
from app.api.auth import get_current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin authentication
    
    Args:
        current_user: Current authenticated user from get_current_user dependency
        
    Returns:
        User object if user is admin
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
