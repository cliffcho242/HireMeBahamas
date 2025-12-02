import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import os
import secrets

import anyio
from decouple import config
from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Security configuration
# CRITICAL: SECRET_KEY must be set in production via environment variable
SECRET_KEY = config("SECRET_KEY", default=None)
if not SECRET_KEY:
    # In production, fail fast if SECRET_KEY is not set
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env in ("production", "prod"):
        raise ValueError("SECRET_KEY environment variable must be set in production")
    # For development, generate a temporary key (will change on restart)
    SECRET_KEY = secrets.token_urlsafe(32)
    logger.warning("⚠️  Using temporary SECRET_KEY for development. Set SECRET_KEY env var for production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Bcrypt configuration
# Default of 12 rounds can be slow (200-300ms per operation)
# 10 rounds provides good security while being much faster (~25-30ms per operation)
# See OWASP recommendations: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
BCRYPT_ROUNDS = config("BCRYPT_ROUNDS", default=10, cast=int)

# Password hashing with optimized bcrypt rounds
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=BCRYPT_ROUNDS
)

# Flag to track if bcrypt has been pre-warmed
_bcrypt_warmed = False


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (synchronous version)"""
    return pwd_context.verify(plain_password, hashed_password)


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash asynchronously.
    
    Uses anyio.to_thread.run_sync() to run the CPU-intensive bcrypt
    verification in a thread pool, preventing blocking of the async event loop.
    This provides 2-3x better concurrency in async FastAPI applications.
    """
    return await anyio.to_thread.run_sync(
        pwd_context.verify, plain_password, hashed_password
    )


def get_password_hash(password: str) -> str:
    """Hash a password (synchronous version)"""
    return pwd_context.hash(password)


async def get_password_hash_async(password: str) -> str:
    """Hash a password asynchronously.
    
    Uses anyio.to_thread.run_sync() to run the CPU-intensive bcrypt
    hashing in a thread pool, preventing blocking of the async event loop.
    """
    return await anyio.to_thread.run_sync(pwd_context.hash, password)


def prewarm_bcrypt() -> None:
    """Pre-warm bcrypt by performing a dummy hash operation.
    
    This eliminates cold-start latency on the first login by ensuring
    bcrypt's internal state is initialized before handling real requests.
    Call this during application startup.
    """
    global _bcrypt_warmed
    if _bcrypt_warmed:
        return
    
    # Perform a dummy hash to initialize bcrypt internals
    _ = pwd_context.hash("prewarm-dummy-password")
    _bcrypt_warmed = True
    logger.info(f"Bcrypt pre-warmed with {BCRYPT_ROUNDS} rounds")


async def prewarm_bcrypt_async() -> None:
    """Pre-warm bcrypt asynchronously during application startup.
    
    This eliminates cold-start latency on the first login by ensuring
    bcrypt's internal state is initialized before handling real requests.
    """
    await anyio.to_thread.run_sync(prewarm_bcrypt)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


def create_reset_token(email: str) -> str:
    """Create a password reset token"""
    expire = datetime.utcnow() + timedelta(minutes=15)  # 15 minutes
    to_encode = {"email": email, "exp": expire, "type": "reset"}

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token and return email"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        token_type: str = payload.get("type")

        if email is None or token_type != "reset":
            return None

        return email
    except JWTError:
        return None


def verify_token(token: str) -> Dict[str, Any]:
    """Verify a JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


# FastAPI dependencies
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# Optional bearer token security scheme
optional_bearer = HTTPBearer(auto_error=False)


# Import here to avoid circular imports
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(None),  # Will be injected properly
):
    """Get current authenticated user"""
    try:
        # Import User model here to avoid circular imports
        from database import get_async_session
        from models import User

        if db is None:
            async with get_async_session() as session:
                db = session

        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
):
    """Get current authenticated user optionally (returns None if not authenticated).
    
    This is useful for GraphQL endpoints where some queries may be public
    but can provide additional data when authenticated.
    
    Note: The database session should be obtained from the GraphQL context,
    not from dependency injection here. This function only extracts and validates
    the token to get the user_id.
    """
    if credentials is None:
        return None
    
    try:
        # Import User model here to avoid circular imports
        from database import get_async_session
        from models import User

        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            return None

        # Use a new session to fetch the user
        # This is acceptable because we're just reading user data once
        async with get_async_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            return user

    except (ValueError, Exception):
        return None
