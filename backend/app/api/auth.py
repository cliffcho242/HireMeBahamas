import uuid
from datetime import datetime, timedelta
from typing import Optional
import logging

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
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


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

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
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

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user),
    }


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return token"""

    # Find user by email
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

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


@router.post("/oauth/google", response_model=Token)
async def google_oauth(oauth_data: OAuthLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate or register user via Google OAuth"""
    from google.oauth2 import id_token
    from google.auth.transport import requests
    
    try:
        # Verify the Google token
        idinfo = id_token.verify_oauth2_token(
            oauth_data.token,
            requests.Request(),
            # In production, you should validate the audience (client ID)
        )
        
        # Extract user information from token
        email = idinfo.get('email')
        given_name = idinfo.get('given_name', '')
        family_name = idinfo.get('family_name', '')
        google_id = idinfo.get('sub')
        picture = idinfo.get('picture')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
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
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
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
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )


@router.post("/oauth/apple", response_model=Token)
async def apple_oauth(oauth_data: OAuthLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate or register user via Apple OAuth"""
    import jwt
    from jwt import PyJWKClient
    
    try:
        # Apple's public keys endpoint
        jwks_url = 'https://appleid.apple.com/auth/keys'
        jwks_client = PyJWKClient(jwks_url)
        
        # Get signing key from token
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Apple"
            )
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            # Update OAuth info if this is first time signing in with Apple
            if not user.oauth_provider:
                user.oauth_provider = 'apple'
                user.oauth_provider_id = apple_id
                user.updated_at = datetime.utcnow()
                await db.commit()
                await db.refresh(user)
        else:
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
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
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
    except Exception as e:
        logger.error(f"Apple OAuth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth authentication failed"
        )
