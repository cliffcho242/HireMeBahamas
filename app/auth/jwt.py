"""
JWT Token Generation Module - STEP 13
Simple and secure JWT token creation for access and refresh tokens
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from jose import jwt
from app.config import JWT_SECRET, JWT_ALGORITHM


def create_access_token(user_id: str, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token for a user.
    
    Args:
        user_id: User identifier to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=15)  # 15 minutes default
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str, expires_delta: timedelta = None) -> str:
    """
    Create a JWT refresh token for long-lived authentication.
    
    Args:
        user_id: User identifier to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT refresh token string
    """
    if expires_delta is None:
        expires_delta = timedelta(days=7)  # 7 days default
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload
