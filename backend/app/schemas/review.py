from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class ReviewCreate(BaseModel):
    job_id: UUID
    reviewee_id: UUID
    rating: int
    comment: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v


class UserInfo(BaseModel):
    id: str
    first_name: str
    last_name: str
    profile_image: Optional[str] = None
    
    class Config:
        from_attributes = True


class JobInfo(BaseModel):
    id: str
    title: str
    
    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    id: str
    job_id: str
    reviewer_id: str
    reviewee_id: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    reviewer: UserInfo
    reviewee: UserInfo
    job: JobInfo
    
    class Config:
        from_attributes = True