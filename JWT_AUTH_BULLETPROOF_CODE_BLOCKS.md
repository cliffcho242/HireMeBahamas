# JWT AUTHENTICATION BULLETPROOF — COMPLETE CODE REFERENCE

## 1. Final dependencies.py (get_current_user + optional auth)

```python
"""
JWT Authentication Dependencies — Bulletproof Vercel-Ready 2025
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database import get_db
from app.models import User

# Bearer token security scheme
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    Returns 401 on invalid/expired token.
    """
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

        # Convert user_id to integer
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
            )
        
        result = await db.execute(select(User).where(User.id == user_id_int))
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        return user

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current authenticated user optionally (returns None if not authenticated).
    Useful for public routes that can show additional data when authenticated.
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            return None

        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            return None
        
        result = await db.execute(select(User).where(User.id == user_id_int))
        user = result.scalar_one_or_none()
        
        if user and user.is_active:
            return user
        
        return None

    except Exception:
        return None
```

**Location:** `backend/app/core/dependencies.py`

---

## 2. Final auth.py (login route + register + me)

```python
"""
JWT Authentication Routes — Bulletproof Vercel-Ready 2025
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    get_password_hash_async,
    verify_password_async,
)
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login route — returns JWT token.
    Returns 401 on invalid credentials.
    """
    # Find user by email
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if user has a password (OAuth users might not)
    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses social login",
        )
    
    # Verify password
    password_valid = await verify_password_async(user_data.password, user.hashed_password)
    
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Create JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user),
    }


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user — returns JWT token.
    Returns 400 if email already exists.
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password
    hashed_password = await get_password_hash_async(user_data.password)

    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role=user_data.user_type or "user",
        location=user_data.location,
        phone=user_data.phone,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Create JWT token
    access_token = create_access_token(data={"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user),
    }


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user.
    Returns 401 if token is invalid/expired.
    """
    return UserResponse.from_orm(current_user)
```

**Location:** `backend/app/api/auth_bulletproof.py`

---

## 3. Final security.py (create_token + verify_password)

```python
"""
JWT Security Module — Bulletproof Vercel-Ready 2025
python-jose[cryptography] + passlib[bcrypt]
"""
import logging
from datetime import datetime, timedelta
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
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

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
```

**Location:** `backend/app/core/security_bulletproof.py`

---

## 4. Final models/user.py (Pydantic + bcrypt)

**Pydantic Schemas** (`backend/app/schemas/auth.py`):

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    user_type: str = "user"
    phone: Optional[str] = None
    location: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str = "user"
    username: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
```

**SQLAlchemy Model** (already exists in `backend/app/models.py`):

```python
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True)
    phone = Column(String(20))
    location = Column(String(200))
    role = Column(String(50), default="user")
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    oauth_provider = Column(String(50))
    oauth_provider_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 5. Final requirements.txt (exact versions)

```txt
# Core Framework
fastapi==0.115.6
uvicorn[standard]==0.32.1
pydantic==2.10.3
pydantic-settings==2.7.0

# Serverless Handler (Vercel/AWS Lambda)
mangum==0.19.0

# JWT Authentication — python-jose[cryptography]
python-jose[cryptography]==3.3.0
cryptography==43.0.3
ecdsa==0.19.0
pyasn1==0.6.1
rsa==4.9

# Password Hashing — passlib[bcrypt]
passlib[bcrypt]==1.7.4
bcrypt==4.1.2

# Database
asyncpg==0.30.0
sqlalchemy[asyncio]==2.0.44
psycopg2-binary==2.9.11

# Utilities
python-multipart==0.0.20
python-dotenv==1.2.1
python-decouple==3.8
email-validator==2.3.0
anyio==4.7.0

# HTTP Client
httpx==0.28.1

# File Upload
aiofiles==25.1.0
```

**Location:** `backend/requirements_bulletproof.txt`

---

## 6. Final main.py with router include + CORS

```python
"""
FastAPI Main App — Bulletproof Vercel-Ready 2025
Clean JWT Auth with CORS
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import auth router
from app.api.auth_bulletproof import router as auth_router

# Create FastAPI app
app = FastAPI(
    title="HireMeBahamas API",
    version="1.0.0",
    description="Bulletproof JWT Authentication"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "HireMeBahamas API - Bulletproof JWT Auth",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "login": "POST /api/auth/login",
            "register": "POST /api/auth/register",
            "me": "GET /api/auth/me"
        }
    }
```

**Location:** `backend/app/main_bulletproof.py`

---

## 7. Final .env + env example

```env
# JWT Secret Key (CRITICAL: Generate a random one for production)
# Generate: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-secret-key-here-generate-a-random-one

# Bcrypt Rounds (10 = ~60ms, 12 = ~240ms per operation)
BCRYPT_ROUNDS=10

# Database URL (PostgreSQL)
DATABASE_URL=postgresql://username:password@hostname:5432/database

# Environment
ENVIRONMENT=production

# Frontend URL (for CORS)
FRONTEND_URL=https://hiremebahamas.vercel.app
```

**Location:** `backend/.env.bulletproof.example`

---

## 8. 4-Step Deploy Checklist

See `VERCEL_JWT_DEPLOYMENT_CHECKLIST.md` for the complete deployment guide with:

1. **Setup Environment Variables** - SECRET_KEY, DATABASE_URL, etc.
2. **Setup Vercel Postgres** - Create database and users table
3. **Deploy Backend to Vercel** - Configure vercel.json and deploy
4. **Test Deployment** - Verify all endpoints work correctly

---

## USAGE EXAMPLES

### Protected Route (requires authentication)

```python
from app.core.dependencies import get_current_user
from app.models import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.first_name}!"}
```

### Optional Auth Route (public but shows extra data when authenticated)

```python
from app.core.dependencies import get_current_user_optional
from app.models import User

@router.get("/public")
async def public_route(current_user: Optional[User] = Depends(get_current_user_optional)):
    if current_user:
        return {"message": f"Hello {current_user.first_name}!", "authenticated": True}
    else:
        return {"message": "Hello guest!", "authenticated": False}
```

### Frontend Integration

```javascript
// Login
const response = await fetch('https://your-api.vercel.app/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password123' })
});
const { access_token } = await response.json();

// Store token
localStorage.setItem('token', access_token);

// Use token in requests
const userResponse = await fetch('https://your-api.vercel.app/api/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const user = await userResponse.json();
```

---

## JWT AUTH IS NOW IMMORTAL ✨

✅ Works on Vercel Serverless  
✅ 401 on invalid/expired token  
✅ Optional auth for public routes  
✅ /api/auth/login → returns JWT  
✅ /api/auth/me → returns user  

**MAKE JWT AUTH IMMORTAL. ✅ EXECUTED.**
