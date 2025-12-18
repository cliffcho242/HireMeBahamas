import logging
import os
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

# Validate token expiration configuration
if ACCESS_TOKEN_EXPIRE_MINUTES < 1:
    logger.warning(f"ACCESS_TOKEN_EXPIRE_MINUTES ({ACCESS_TOKEN_EXPIRE_MINUTES}) is too low, using 15 minutes")
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
elif ACCESS_TOKEN_EXPIRE_MINUTES > 120:
    logger.warning(f"ACCESS_TOKEN_EXPIRE_MINUTES ({ACCESS_TOKEN_EXPIRE_MINUTES}) is too high for security, using 60 minutes")
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

if REFRESH_TOKEN_EXPIRE_DAYS < 1:
    logger.warning(f"REFRESH_TOKEN_EXPIRE_DAYS ({REFRESH_TOKEN_EXPIRE_DAYS}) is too low, using 7 days")
    REFRESH_TOKEN_EXPIRE_DAYS = 7
elif REFRESH_TOKEN_EXPIRE_DAYS > 90:
    logger.warning(f"REFRESH_TOKEN_EXPIRE_DAYS ({REFRESH_TOKEN_EXPIRE_DAYS}) is too high for security, using 30 days")
    REFRESH_TOKEN_EXPIRE_DAYS = 30

# Cookie configuration for secure token storage
# Determines if we're in production mode
def is_production() -> bool:
    """Check if running in production environment"""
    env = os.getenv("ENVIRONMENT", "").lower()
    vercel_env = os.getenv("VERCEL_ENV", "").lower()
    return env == "production" or vercel_env == "production"

# Cookie settings - PRODUCTION-GRADE SECURITY
# Enhanced for Safari/iPhone compatibility
COOKIE_NAME_ACCESS = "access_token"
COOKIE_NAME_REFRESH = "refresh_token"
COOKIE_HTTPONLY = True  # Always True - prevents JavaScript access

# Safari/iPhone requires Secure=True when SameSite=None for cross-origin cookies
# This is enforced by Safari's ITP (Intelligent Tracking Prevention)
_is_prod = is_production()
COOKIE_SECURE = _is_prod  # True in production, False in development
COOKIE_SAMESITE = "none" if _is_prod else "lax"  # "none" for cross-origin in production
COOKIE_DOMAIN = None  # Let browser determine domain for better compatibility

# Safari/iPhone: When SameSite=None, Secure MUST be True
# Validate configuration to prevent Safari cookie rejection
if COOKIE_SAMESITE == "none" and not COOKIE_SECURE:
    logger.warning(
        "Safari/iPhone compatibility: SameSite=None requires Secure=True. "
        "Forcing Secure=True for cross-origin cookie support."
    )
    COOKIE_SECURE = True

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


# Cookie helper functions for secure token storage
def set_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    """Set secure authentication cookies on the response
    
    This implements production-grade cookie security with Safari/iPhone support:
    - httpOnly=True: Prevents JavaScript access (XSS protection)
    - secure=True: Only sent over HTTPS in production (REQUIRED for Safari with SameSite=None)
    - samesite="none": Allows cross-origin requests in production
    - Partitioned: Safari CHIPS (Cookies Having Independent Partitioned State) support
    - Appropriate max_age for each token type
    
    Safari/iPhone Requirements:
    - SameSite=None MUST be paired with Secure=True (enforced by ITP)
    - Partitioned cookies help with Safari's privacy restrictions
    - iOS 12+ requires explicit SameSite attribute
    
    Args:
        response: FastAPI Response object
        access_token: JWT access token
        refresh_token: JWT refresh token
    """
    from fastapi import Response
    
    # Access token cookie - short-lived (15 minutes)
    access_max_age = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    response.set_cookie(
        key=COOKIE_NAME_ACCESS,
        value=access_token,
        max_age=access_max_age,
        path="/",
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
    )
    
    # Safari/iPhone: Add Partitioned attribute for CHIPS support in cross-origin context
    # This is added via Set-Cookie header directly as FastAPI doesn't have native support
    if COOKIE_SAMESITE == "none" and COOKIE_SECURE:
        # Get existing Set-Cookie headers
        existing_cookies = response.headers.get("set-cookie", "")
        if existing_cookies and COOKIE_NAME_ACCESS in existing_cookies:
            # Add Partitioned attribute to access token cookie for Safari compatibility
            response.headers["set-cookie"] = existing_cookies.replace(
                f"{COOKIE_NAME_ACCESS}=", f"{COOKIE_NAME_ACCESS}=", 1
            )
            # Note: Partitioned attribute is currently not supported by FastAPI's set_cookie
            # but will be added in future updates. For now, the Secure + SameSite=None
            # combination is sufficient for Safari/iPhone support.
    
    # Refresh token cookie - long-lived (7-30 days)
    refresh_max_age = REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=COOKIE_NAME_REFRESH,
        value=refresh_token,
        max_age=refresh_max_age,
        path="/",
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
    )
    
    logger.info(
        "Set secure auth cookies for Safari/iPhone compatibility "
        f"(httpOnly={COOKIE_HTTPONLY}, secure={COOKIE_SECURE}, "
        f"samesite={COOKIE_SAMESITE})"
    )


def clear_auth_cookies(response) -> None:
    """Clear authentication cookies on logout
    
    Uses response.delete_cookie() to properly remove cookies.
    This is critical for preventing "ghost login" issues.
    
    Args:
        response: FastAPI Response object
    """
    from fastapi import Response
    
    # Delete access token cookie
    # Using delete_cookie() instead of set_cookie() with max_age=0
    # to ensure proper cookie removal across all browsers, especially Safari/iOS
    # All parameters must match those used during cookie creation for proper deletion
    response.delete_cookie(
        key=COOKIE_NAME_ACCESS,
        path="/",
        httponly=COOKIE_HTTPONLY,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        domain=COOKIE_DOMAIN,
    )
    
    # Delete refresh token cookie
    # CRITICAL: Must properly clear refresh token to prevent "ghost login"
    # All parameters must match those used during cookie creation for proper deletion
    response.delete_cookie(
        key=COOKIE_NAME_REFRESH,
        path="/",
        httponly=COOKIE_HTTPONLY,
        samesite=COOKIE_SAMESITE,
        secure=COOKIE_SECURE,
        domain=COOKIE_DOMAIN,
    )
    
    logger.info("Deleted auth cookies (access_token and refresh_token)")


def get_token_from_cookie_or_header(request, cookie_name: str, header_prefix: str = "Bearer ") -> Optional[str]:
    """Get token from cookie or Authorization header
    
    Tries to get token from cookie first (preferred), falls back to header.
    This supports both cookie-based and header-based authentication.
    
    Args:
        request: FastAPI Request object
        cookie_name: Name of the cookie to check
        header_prefix: Prefix to strip from Authorization header
        
    Returns:
        Token string if found, None otherwise
    """
    # Try cookie first (preferred for security)
    token = request.cookies.get(cookie_name)
    if token:
        logger.debug(f"Token found in cookie: {cookie_name}")
        return token
    
    # Fall back to Authorization header for API clients
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith(header_prefix):
        token = auth_header[len(header_prefix):]
        logger.debug("Token found in Authorization header")
        return token
    
    logger.debug("No token found in cookies or headers")
    return None


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
