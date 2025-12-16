"""
JWT token creation and validation logic.

This module handles JWT token operations including creation, decoding,
and validation for access and refresh tokens.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from decouple import config
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = config("SECRET_KEY", default="your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT access token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


def create_reset_token(email: str) -> str:
    """Create a password reset token.
    
    Args:
        email: User email for password reset
        
    Returns:
        Encoded JWT token for password reset
    """
    expire = datetime.utcnow() + timedelta(minutes=15)  # 15 minutes
    to_encode = {"email": email, "exp": expire, "type": "reset"}

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token and return email.
    
    Args:
        token: Password reset token to verify
        
    Returns:
        Email if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        token_type: str = payload.get("type")

        if email is None or token_type != "reset":
            return None

        return email
    except JWTError:
        return None
