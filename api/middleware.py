"""
JWT Authentication Middleware for FastAPI + Vercel
Production-ready JWT verification with current_user dependency
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days

# Security scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing user data (email, user_type, etc.)
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Authorization credentials with Bearer token
        
    Returns:
        User data dictionary from token payload
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    # Extract user info from token
    email = payload.get("email")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return user info from token
    return {
        "email": email,
        "user_type": payload.get("user_type"),
        "first_name": payload.get("first_name"),
        "last_name": payload.get("last_name"),
    }


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """
    Optional dependency to get current user if token is provided
    Returns None if no token is provided
    
    Args:
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        User data dictionary or None
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
