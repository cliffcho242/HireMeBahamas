"""
Authentication routes - Login, registration, token refresh.

Provides endpoints for user authentication including login, registration,
token refresh, and session verification.
"""
import logging
import re
import time
from datetime import datetime, timedelta
from threading import Lock
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, security
from app.auth.jwt import create_access_token
from app.core.security import (
    get_password_hash_async,
    verify_password_async,
    create_refresh_token,
    BCRYPT_ROUNDS,
    COOKIE_HTTPONLY,
    COOKIE_SECURE,
    COOKIE_SAMESITE,
    COOKIE_PATH,
    COOKIE_MAX_AGE,
    COOKIE_NAME_REFRESH,
)
from app.core.query_timeout import set_fast_query_timeout
from app.database import get_db
from app.models import User
from app.schemas.auth import (
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserMeResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple rate limiting using in-memory storage
login_attempts = {}
login_attempts_lock = Lock()
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)


def check_rate_limit(identifier: str) -> bool:
    """Check if the identifier (IP or email) has exceeded rate limit."""
    with login_attempts_lock:
        current_time = datetime.utcnow()
        
        if identifier in login_attempts:
            attempts, lockout_until = login_attempts[identifier]
            
            if lockout_until and current_time < lockout_until:
                return False
            
            if lockout_until and current_time >= lockout_until:
                login_attempts[identifier] = (0, None)
                return True
            
            if attempts >= MAX_LOGIN_ATTEMPTS:
                login_attempts[identifier] = (attempts, current_time + LOCKOUT_DURATION)
                logger.warning(f"Rate limit exceeded for {identifier}")
                return False
        
        return True


def record_login_attempt(identifier: str, success: bool):
    """Record a login attempt."""
    with login_attempts_lock:
        if success:
            if identifier in login_attempts:
                del login_attempts[identifier]
        else:
            current_time = datetime.utcnow()
            if identifier in login_attempts:
                attempts, lockout_until = login_attempts[identifier]
                login_attempts[identifier] = (attempts + 1, lockout_until)
            else:
                login_attempts[identifier] = (1, None)


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    logger.info(f"Registration attempt for email: {user_data.email}")

    # Set fast query timeout for registration queries (2s)
    await set_fast_query_timeout(db)

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.warning(f"Registration failed - Email already registered: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )

    # Create new user
    hashed_password = await get_password_hash_async(user_data.password)

    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.user_type,
        location=user_data.location,
        phone=user_data.phone,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    logger.info(f"Registration successful for: {user_data.email} (user_id={db_user.id})")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user),
    }


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin, 
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return token.
    
    Sets both access token (returned in JSON) and refresh token (HTTP-only cookie).
    The refresh token cookie is configured for cross-origin support:
    - httponly=True: XSS protection
    - secure=True: HTTPS only (required for Safari)
    - samesite="None": Cross-origin support (Vercel ↔ Backend)
    """
    login_start_time = time.time()
    
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Check rate limit by IP
    if not check_rate_limit(client_ip):
        logger.warning(f"[{request_id}] Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again in 15 minutes.",
        )
    
    logger.info(f"[{request_id}] Login attempt - email/phone: {user_data.email}")

    # Set fast query timeout for login queries (2s)
    await set_fast_query_timeout(db)

    # Try to find user by email first
    db_query_start = time.time()
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    db_email_query_ms = int((time.time() - db_query_start) * 1000)
    
    total_db_ms = db_email_query_ms
    
    # If not found by email, try phone number
    if not user:
        if re.match(r'^\+?[\d\s\-\(\)]+$', user_data.email) and len(user_data.email) >= 7:
            logger.info(f"[{request_id}] Attempting phone number lookup")
            db_query_start = time.time()
            result = await db.execute(select(User).where(User.phone == user_data.email))
            user = result.scalar_one_or_none()
            db_phone_query_ms = int((time.time() - db_query_start) * 1000)
            total_db_ms += db_phone_query_ms

    if not user:
        logger.warning(f"[{request_id}] Login failed - User not found: {user_data.email}")
        record_login_attempt(client_ip, False)
        record_login_attempt(user_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check rate limit by email
    if not check_rate_limit(user_data.email):
        logger.warning(f"[{request_id}] Rate limit exceeded for email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts for this account.",
        )
    
    # Check if user has a password (OAuth users might not)
    if not user.hashed_password:
        logger.warning(f"[{request_id}] OAuth user attempting password login")
        record_login_attempt(client_ip, False)
        record_login_attempt(user_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses social login.",
        )
    
    # Verify password
    password_verify_start = time.time()
    password_valid = await verify_password_async(user_data.password, user.hashed_password)
    password_verify_ms = int((time.time() - password_verify_start) * 1000)
    
    if not password_valid:
        logger.warning(f"[{request_id}] Login failed - Invalid password")
        record_login_attempt(client_ip, False)
        record_login_attempt(user_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        logger.warning(f"[{request_id}] Login failed - Inactive account")
        record_login_attempt(client_ip, False)
        record_login_attempt(user_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account is deactivated"
        )

    # Create access token
    token_create_start = time.time()
    access_token = create_access_token(data={"sub": str(user.id)})
    token_create_ms = int((time.time() - token_create_start) * 1000)
    
    # Create refresh token for long-term authentication
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Set refresh token as HTTP-only cookie
    # ✅ HttpOnly: Prevents JavaScript access (XSS protection)
    # ✅ Secure: HTTPS only (required for Safari with SameSite=None)
    # ✅ SameSite=None: Cross-origin support (Vercel frontend ↔ Render backend)
    # ❗ CRITICAL: SameSite=None is MANDATORY for cross-origin authentication
    #             If SameSite=Lax, Safari login will fail silently!
    response.set_cookie(
        key=COOKIE_NAME_REFRESH,
        value=refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
        max_age=COOKIE_MAX_AGE
    )
    
    # Reset rate limit counters
    record_login_attempt(client_ip, True)
    record_login_attempt(user_data.email, True)
    
    total_login_ms = int((time.time() - login_start_time) * 1000)
    
    logger.info(
        f"[{request_id}] Login successful - user: {user.email}, "
        f"total_time: {total_login_ms}ms, refresh_token_cookie_set=True"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user),
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token."""
    access_token = create_access_token(data={"sub": str(current_user.id)})
    
    logger.info(f"Token refreshed for user: {current_user.email}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(current_user),
    }


@router.get("/verify")
async def verify_session(current_user: User = Depends(get_current_user)):
    """Verify current session."""
    logger.info(f"Session verified for user: {current_user.email}")
    
    return {
        "valid": True,
        "user": UserResponse.from_orm(current_user),
    }


@router.get("/me", response_model=UserMeResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile - Single source of truth for session verification.
    
    Returns minimal user information for authentication verification:
    - id: User's unique identifier
    - email: User's email address
    - role: User's role in the system (user, employer, admin, etc.)
    
    This endpoint is protected and requires a valid JWT token.
    Use this to verify the current session and get authenticated user details.
    """
    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role
    )
