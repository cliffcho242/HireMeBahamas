from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# User schema for post responses (minimal)
class PostUser(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    username: Optional[str] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


# Post schemas
class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    post_type: str = Field(default="text")
    related_job_id: Optional[int] = None


class PostUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class PostResponse(BaseModel):
    id: int
    user_id: int
    user: PostUser
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    post_type: str
    related_job_id: Optional[int] = None
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Comment schemas
class CommentUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    user: CommentUser
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
