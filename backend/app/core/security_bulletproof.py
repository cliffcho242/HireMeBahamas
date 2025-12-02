"""
JWT Security Module — Bulletproof Vercel-Ready 2025
python-jose[cryptography] + passlib[bcrypt]
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import anyio
from jose import JWTError, jwt
from passlib.context import CryptContext
from decouple import config

logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = config("SECRET_KEY", default="your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Bcrypt Configuration (10 rounds = ~60ms per operation)
BCRYPT_ROUNDS = config("BCRYPT_ROUNDS", default=10, cast=int)

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=BCRYPT_ROUNDS
)

# Pre-warm flag
_bcrypt_warmed = False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (synchronous)"""
    return pwd_context.verify(plain_password, hashed_password)


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (async - non-blocking)"""
    return await anyio.to_thread.run_sync(
        pwd_context.verify, plain_password, hashed_password
    )


def get_password_hash(password: str) -> str:
    """Hash a password (synchronous)"""
    return pwd_context.hash(password)


async def get_password_hash_async(password: str) -> str:
    """Hash a password (async - non-blocking)"""
    return await anyio.to_thread.run_sync(pwd_context.hash, password)


def prewarm_bcrypt() -> None:
    """Pre-warm bcrypt by performing a dummy hash operation"""
    global _bcrypt_warmed
    if _bcrypt_warmed:
        return
    
    _ = pwd_context.hash("prewarm-dummy-password")
    _bcrypt_warmed = True
    logger.info(f"Bcrypt pre-warmed with {BCRYPT_ROUNDS} rounds")


async def prewarm_bcrypt_async() -> None:
    """Pre-warm bcrypt asynchronously during application startup"""
    await anyio.to_thread.run_sync(prewarm_bcrypt)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT access token. Raises ValueError on invalid token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


def verify_token(token: str) -> Dict[str, Any]:
    """Alias for decode_access_token"""
    return decode_access_token(token)
