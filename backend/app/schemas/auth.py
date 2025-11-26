from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    user_type: str = "user"  # Default to "user" if not provided
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
    role: str = "user"  # Matches User model default
    username: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
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


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class OAuthLogin(BaseModel):
    token: str  # ID token from OAuth provider
    provider: str  # 'google' or 'apple'
    user_type: Optional[str] = "user"  # For registration flow
