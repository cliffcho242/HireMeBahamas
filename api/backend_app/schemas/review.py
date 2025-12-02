from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class ReviewCreate(BaseModel):
    job_id: int
    reviewee_id: int
    rating: int
    comment: Optional[str] = None

    @validator("rating")
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

    @validator("rating")
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError("Rating must be between 1 and 5")
        return v


class UserInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    profile_image: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class JobInfo(BaseModel):
    id: int
    title: str

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    id: int
    job_id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    reviewer: UserInfo
    reviewee: UserInfo
    job: JobInfo

    class Config:
        from_attributes = True
