import uuid
import time
from datetime import datetime, timedelta
from typing import Optional
import logging
import re
import hashlib
from threading import Lock

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.core.upload import upload_image
from app.database import get_db
from app.models import User
from app.schemas.auth import (
    OAuthLogin,
    PasswordChange,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


# Simple rate limiting using in-memory storage
# NOTE: For production with multiple instances, use Redis or similar distributed cache
# This in-memory implementation is suitable for single-instance deployments
# Example with Redis: from redis import asyncio as aioredis; redis = await aioredis.from_url(...)
login_attempts = {}
login_attempts_lock = Lock()  # Thread safety for concurrent requests
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)


def check_rate_limit(identifier: str) -> bool:
    """Check if the identifier (IP or email) has exceeded rate limit
    
    Args:
        identifier: IP address or email to check
        
    Returns:
        True if within rate limit, False if rate limit exceeded
    """
    with login_attempts_lock:
        current_time = datetime.utcnow()
        
        if identifier in login_attempts:
            attempts, lockout_until = login_attempts[identifier]
            
            # Check if still locked out
            if lockout_until and current_time < lockout_until:
                return False
            
            # Check if we should reset the counter (been more than 15 minutes since last attempt)
            if lockout_until and current_time >= lockout_until:
                login_attempts[identifier] = (0, None)
                return True
            
            # Increment attempt counter
            if attempts >= MAX_LOGIN_ATTEMPTS:
                login_attempts[identifier] = (attempts, current_time + LOCKOUT_DURATION)
                logger.warning(f"Rate limit exceeded for {identifier}, locked out for {LOCKOUT_DURATION}")
                return False
        
        return True


def record_login_attempt(identifier: str, success: bool):
    """Record a login attempt
    
    Args:
        identifier: IP address or email
        success: Whether the login was successful
    """
    with login_attempts_lock:
        if success:
            # Reset on successful login
            if identifier in login_attempts:
                del login_attempts[identifier]
        else:
            # Increment failed attempts
            current_time = datetime.utcnow()
            if identifier in login_attempts:
                attempts, lockout_until = login_attempts[identifier]
                login_attempts[identifier] = (attempts + 1, lockout_until)
            else:
                login_attempts[identifier] = (1, None)


# Helper function to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user
    
    Args:
        credentials: Bearer token credentials
        db: Database session
        
    Returns:
        User object for the authenticated user
        
    Raises:
        HTTPException: 401 if authentication fails
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            logger.warning("Token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Convert user_id to integer (User model uses Integer primary key)
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid user ID format in token: {user_id}, error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
            )
        
        result = await db.execute(select(User).where(User.id == user_id_int))
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User not found for authenticated token: user_id={user_id_int}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User not found. Your account may have been deleted or deactivated."
            )
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user attempted access: user_id={user_id_int}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    
    logger.info(f"Registration attempt for email: {user_data.email}")

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.warning(f"Registration failed - Email already registered: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.user_type,  # Map user_type to role field
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
async def login(user_data: UserLogin, request: Request, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return token
    
    Supports login with email address or phone number.
    Includes rate limiting to prevent brute force attacks.
    """
    
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Check rate limit by IP
    if not check_rate_limit(client_ip):
        logger.warning(
            f"[{request_id}] Rate limit exceeded for IP: {client_ip}, "
            f"login attempt for: {user_data.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again in 15 minutes.",
        )
    
    logger.info(
        f"[{request_id}] Login attempt - email/phone: {user_data.email}, "
        f"client_ip: {client_ip}"
    )

    # Try to find user by email first, then by phone number
    db_query_start = time.time()
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    db_query_ms = int((time.time() - db_query_start) * 1000)
    
    logger.info(
        f"[{request_id}] Database query (email lookup) completed in {db_query_ms}ms"
    )
    
    # If not found by email, try phone number
    if not user:
        # Check if input looks like a phone number (contains digits and phone formatting chars)
        # Must have at least one digit and reasonable length for a phone number
        if re.match(r'^\+?[\d\s\-\(\)]+$', user_data.email) and any(c.isdigit() for c in user_data.email) and len(user_data.email) >= 7:
            logger.info(
                f"[{request_id}] Email not found, attempting phone number lookup"
            )
            db_query_start = time.time()
            result = await db.execute(select(User).where(User.phone == user_data.email))
            user = result.scalar_one_or_none()
            db_query_ms = int((time.time() - db_query_start) * 1000)
            logger.info(
                f"[{request_id}] Database query (phone lookup) completed in {db_query_ms}ms"
            )

    if not user:
        logger.warning(
            f"[{request_id}] Login failed - User not found: {user_data.email}, "
            f"client_ip: {client_ip}"
        )
        record_login_attempt(client_ip, False)
        record_login_attempt(user_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check rate limit by email as well
    if not check_rate_limit(user_data.email):
        logger.warning(
            f"[{request_id}] Rate limit exceeded for email: {user_data.email}, "
            f"user_id: {user.id}, client_ip: {client_ip}"
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts for this account. Please try again in 15 minutes.",
        )
    
    # Check if user has a password (OAuth users might not)
    if not user.hashed_password:
        logger.warning(
            f"[{request_id}] Login failed - OAuth user attempting password login: "
            f"{user_data.email}, user_id: {user.id}, oauth_provider: {user.oauth_provider}, "
            f"client_ip: {client_ip}"
        )
        record_login_attempt(client_ip, False)
        record_login_attempt(user_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses social login. Please sign in with Google or Apple.",
        )
    
    # Verify password
    password_verify_start = time.time()
    password_valid = verify_password(user_data.password, user.hashed_password)
    password_verify_ms = int((time.time() - password_verify_start) * 1000)
    
    logger.info(
        f"[{request_id}] Password verification completed in {password_verify_ms}ms"
    )
    
    if not password_valid:
        logger.warning(
            f"[{request_id}] Login failed - Invalid password for user: {user_data.email}, "
            f"user_id: {user.id}, client_ip: {client_ip}"
        )
        record_login_attempt(client_ip, False)
        record_login_attempt(user_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        logger.warning(
            f"[{request_id}] Login failed - Inactive account: {user_data.email}, "
            f"user_id: {user.id}, client_ip: {client_ip}"
        )
        record_login_attempt(client_ip, False)
        record_login_attempt(user_data.email, False)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
        )

    # Create access token
    token_create_start = time.time()
    access_token = create_access_token(data={"sub": str(user.id)})
    token_create_ms = int((time.time() - token_create_start) * 1000)
    
    logger.info(
        f"[{request_id}] Token creation completed in {token_create_ms}ms"
    )
    
    # Reset rate limit counters on successful login
    record_login_attempt(client_ip, True)
    record_login_attempt(user_data.email, True)
    
    logger.info(
        f"[{request_id}] Login successful - user: {user.email}, user_id: {user.id}, "
        f"role: {user.role}, client_ip: {client_ip}"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user),
    }


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.from_orm(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile"""

    # Update user fields
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.from_orm(current_user)


@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload user profile image"""

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image"
        )

    # Upload image
    image_url = await upload_image(file, folder="avatars")

    # Update user profile
    current_user.profile_image = image_url
    current_user.updated_at = datetime.utcnow()

    await db.commit()

    return {"image_url": image_url}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password"""

    # Verify current password
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()

    await db.commit()

    return {"message": "Password changed successfully"}


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Deactivate user account"""

    current_user.is_active = False
    current_user.updated_at = datetime.utcnow()

    await db.commit()

    return {"message": "Account deactivated successfully"}


@router.get("/login-stats")
async def get_login_stats(current_user: User = Depends(get_current_user)):
    """Get login attempt statistics (for monitoring)
    
    Returns statistics about login attempts and rate limiting.
    This is useful for detecting brute force attacks.
    Requires admin authentication.
    """
    # Restrict to admin users only
    if not current_user.is_admin:
        logger.warning(f"Unauthorized access to login stats by user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    with login_attempts_lock:
        current_time = datetime.utcnow()
        
        stats = {
            "total_tracked_identifiers": len(login_attempts),
            "locked_out": 0,
            "high_attempts": 0,
            "details": []
        }
        
        for identifier, (attempts, lockout_until) in login_attempts.items():
            is_locked = lockout_until and current_time < lockout_until
            
            if is_locked:
                stats["locked_out"] += 1
            elif attempts >= 3:
                stats["high_attempts"] += 1
            
            # Only include identifiers with high attempts or locked out
            # Anonymize identifiers for security
            if attempts >= 3 or is_locked:
                # Hash the identifier to anonymize it
                hashed = hashlib.sha256(identifier.encode()).hexdigest()[:16]
                
                stats["details"].append({
                    "identifier_hash": hashed,  # Anonymized identifier
                    "attempts": attempts,
                    "locked_out": is_locked,
                    "lockout_until": lockout_until.isoformat() if lockout_until else None
                })
    
    logger.info(f"Login stats requested by admin user_id={current_user.id}: {stats['locked_out']} locked out, {stats['high_attempts']} high attempts")
    
    return stats


@router.post("/oauth/google", response_model=Token)
async def google_oauth(oauth_data: OAuthLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate or register user via Google OAuth"""
    from google.oauth2 import id_token
    from google.auth.transport import requests
    import os
    
    logger.info("Google OAuth login attempt")
    
    try:
        # Get Google Client ID from environment
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        
        if not google_client_id:
            logger.error("Google OAuth attempted but GOOGLE_CLIENT_ID not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth is not configured on the server"
            )
        
        # Verify the Google token with audience validation
        logger.info("Verifying Google OAuth token")
        idinfo = id_token.verify_oauth2_token(
            oauth_data.token,
            requests.Request(),
            audience=google_client_id  # Validate token was issued for our app
        )
        
        # Extract user information from token
        email = idinfo.get('email')
        given_name = idinfo.get('given_name', '')
        family_name = idinfo.get('family_name', '')
        google_id = idinfo.get('sub')
        picture = idinfo.get('picture')
        
        if not email:
            logger.error("Google OAuth token missing email claim")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        logger.info(f"Google OAuth verified for email: {email}")
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            logger.info(f"Existing user logging in with Google: {email} (user_id={user.id})")
            # Update OAuth info if this is first time signing in with Google
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_provider_id = google_id
                if picture and not user.avatar_url:
                    user.avatar_url = picture
                user.updated_at = datetime.utcnow()
                await db.commit()
                await db.refresh(user)
        else:
            logger.info(f"Creating new user via Google OAuth: {email}")
            # Create new user
            user = User(
                email=email,
                first_name=given_name or 'User',
                last_name=family_name or '',
                oauth_provider='google',
                oauth_provider_id=google_id,
                avatar_url=picture,
                role=oauth_data.user_type or 'user',
                location='Bahamas',
                hashed_password=None  # No password for OAuth users
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"New user created via Google OAuth: {email} (user_id={user.id})")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        logger.info(f"Google OAuth login successful for: {email} (user_id={user.id})")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user),
        }
        
    except ValueError as e:
        logger.error(f"Google OAuth verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )


@router.post("/oauth/apple", response_model=Token)
async def apple_oauth(oauth_data: OAuthLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate or register user via Apple OAuth"""
    import jwt
    from jwt import PyJWKClient
    
    logger.info("Apple OAuth login attempt")
    
    try:
        # Apple's public keys endpoint
        jwks_url = 'https://appleid.apple.com/auth/keys'
        jwks_client = PyJWKClient(jwks_url)
        
        # Get signing key from token
        logger.info("Verifying Apple OAuth token")
        signing_key = jwks_client.get_signing_key_from_jwt(oauth_data.token)
        
        # Decode and verify the token
        decoded_token = jwt.decode(
            oauth_data.token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_exp": True}
        )
        
        # Extract user information
        email = decoded_token.get('email')
        apple_id = decoded_token.get('sub')
        
        if not email:
            logger.error("Apple OAuth token missing email claim")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Apple"
            )
        
        logger.info(f"Apple OAuth verified for email: {email}")
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            logger.info(f"Existing user logging in with Apple: {email} (user_id={user.id})")
            # Update OAuth info if this is first time signing in with Apple
            if not user.oauth_provider:
                user.oauth_provider = 'apple'
                user.oauth_provider_id = apple_id
                user.updated_at = datetime.utcnow()
                await db.commit()
                await db.refresh(user)
        else:
            logger.info(f"Creating new user via Apple OAuth: {email}")
            # Create new user - Apple doesn't always provide name
            # The name should be sent from the frontend on first sign in
            user = User(
                email=email,
                first_name='User',  # Frontend should update this
                last_name='',
                oauth_provider='apple',
                oauth_provider_id=apple_id,
                role=oauth_data.user_type or 'user',
                location='Bahamas',
                hashed_password=None  # No password for OAuth users
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"New user created via Apple OAuth: {email} (user_id={user.id})")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        logger.info(f"Apple OAuth login successful for: {email} (user_id={user.id})")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user),
        }
        
    except jwt.InvalidTokenError as e:
        logger.error(f"Apple OAuth verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Apple token"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Apple OAuth error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )
