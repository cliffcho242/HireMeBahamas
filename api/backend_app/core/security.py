import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import anyio
from decouple import config
from jose import JWTError, jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Suppress bcrypt version check warning from passlib logger
# bcrypt 4.x removed __about__ attribute, but passlib handles this gracefully
# Setting passlib logger to ERROR level prevents the non-critical warning from appearing
logging.getLogger('passlib').setLevel(logging.ERROR)

# Security configuration
SECRET_KEY = config("SECRET_KEY", default="your-secret-key-change-in-production")
ALGORITHM = "HS256"
# Production-grade token expiration settings
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=15, cast=int)  # 15 minutes
REFRESH_TOKEN_EXPIRE_DAYS = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)  # 7 days

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
    
    Note: bcrypt 4.x compatibility - passlib may log a benign warning about
    bcrypt version detection, but this is handled gracefully internally.
    """
    global _bcrypt_warmed
    if _bcrypt_warmed:
        return
    
    try:
        # Perform a dummy hash to initialize bcrypt internals
        _ = pwd_context.hash("prewarm")
        _bcrypt_warmed = True
        logger.info(f"Bcrypt pre-warmed with {BCRYPT_ROUNDS} rounds")
    except Exception as e:
        # Log the error but don't fail startup - pre-warming is optional
        logger.warning(f"Bcrypt pre-warm encountered an error (non-critical): {type(e).__name__}: {e}")


async def prewarm_bcrypt_async() -> None:
    """Pre-warm bcrypt asynchronously during application startup.
    
    This eliminates cold-start latency on the first login by ensuring
    bcrypt's internal state is initialized before handling real requests.
    
    Note: This function is non-critical and will not raise exceptions.
    If pre-warming fails, authentication will still work but the first
    login may be slightly slower.
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


def create_refresh_token(user_id: int) -> str:
    """Create a refresh token for long-lived authentication
    
    Args:
        user_id: User ID to encode in the token
        
    Returns:
        JWT refresh token string
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a refresh token
    
    Args:
        token: Refresh token string to decode
        
    Returns:
        Payload dict if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        
        # Verify this is a refresh token
        if token_type != "refresh":
            return None
            
        return payload
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """Hash a token for secure storage in database
    
    Uses SHA-256 to create a one-way hash of the token.
    This ensures tokens stored in the database cannot be used
    even if the database is compromised.
    
    Args:
        token: Token string to hash
        
    Returns:
        SHA-256 hex digest of the token
    """
    import hashlib
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token(token: str) -> Dict[str, Any]:
    """Verify a JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")


# Refresh token database operations
async def store_refresh_token(
    db,  # AsyncSession
    user_id: int,
    token: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> None:
    """Store a refresh token in the database
    
    Args:
        db: Database session
        user_id: User ID this token belongs to
        token: The refresh token string
        ip_address: Optional IP address of the client
        user_agent: Optional user agent string
    """
    from app.models import RefreshToken
    
    token_hash_value = hash_token(token)
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    db_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash_value,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(db_token)
    await db.commit()
    
    logger.info(f"Stored refresh token for user_id={user_id}")


async def verify_refresh_token_in_db(db, token: str) -> Optional[int]:
    """Verify a refresh token exists in database and is valid
    
    Args:
        db: Database session
        token: The refresh token string to verify
        
    Returns:
        User ID if token is valid, None otherwise
    """
    from app.models import RefreshToken
    from sqlalchemy import select
    
    # First decode the JWT to check expiration
    payload = decode_refresh_token(token)
    if not payload:
        logger.warning("Invalid refresh token JWT")
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("Refresh token missing user ID")
        return None
    
    # Check if token exists in database and is not revoked
    token_hash_value = hash_token(token)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash_value,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
    )
    db_token = result.scalar_one_or_none()
    
    if not db_token:
        logger.warning(f"Refresh token not found or invalid for user_id={user_id}")
        return None
    
    return int(user_id)


async def revoke_refresh_token(db, token: str) -> bool:
    """Revoke a refresh token
    
    Args:
        db: Database session
        token: The refresh token to revoke
        
    Returns:
        True if token was revoked, False if not found
    """
    from app.models import RefreshToken
    from sqlalchemy import select
    
    token_hash_value = hash_token(token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash_value)
    )
    db_token = result.scalar_one_or_none()
    
    if not db_token:
        logger.warning("Attempted to revoke non-existent refresh token")
        return False
    
    db_token.revoked = True
    db_token.revoked_at = datetime.utcnow()
    await db.commit()
    
    logger.info(f"Revoked refresh token for user_id={db_token.user_id}")
    return True


async def revoke_all_user_tokens(db, user_id: int) -> int:
    """Revoke all refresh tokens for a user
    
    Useful for logout from all devices or security incidents.
    
    Args:
        db: Database session
        user_id: User ID whose tokens to revoke
        
    Returns:
        Number of tokens revoked
    """
    from app.models import RefreshToken
    from sqlalchemy import select, update
    
    result = await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        )
        .values(revoked=True, revoked_at=datetime.utcnow())
    )
    await db.commit()
    
    count = result.rowcount
    logger.info(f"Revoked {count} refresh tokens for user_id={user_id}")
    return count


async def cleanup_expired_tokens(db) -> int:
    """Clean up expired and revoked tokens from database
    
    Should be called periodically (e.g., daily cron job).
    
    Args:
        db: Database session
        
    Returns:
        Number of tokens deleted
    """
    from app.models import RefreshToken
    from sqlalchemy import delete
    
    # Delete tokens that are either:
    # 1. Expired for more than 30 days
    # 2. Revoked for more than 7 days
    cutoff_expired = datetime.utcnow() - timedelta(days=30)
    cutoff_revoked = datetime.utcnow() - timedelta(days=7)
    
    result = await db.execute(
        delete(RefreshToken).where(
            (RefreshToken.expires_at < cutoff_expired) |
            ((RefreshToken.revoked == True) & (RefreshToken.revoked_at < cutoff_revoked))
        )
    )
    await db.commit()
    
    count = result.rowcount
    logger.info(f"Cleaned up {count} expired/revoked refresh tokens")
    return count


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
        from app.database import get_async_session
        from app.models import User

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
        from app.database import get_async_session
        from app.models import User

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
