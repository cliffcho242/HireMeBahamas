from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BudgetType(str, Enum):
    FIXED = "fixed"
    HOURLY = "hourly"


class JobStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class JobBase(BaseModel):
    title: str
    description: str
    category: str
    budget: float
    budget_type: BudgetType
    location: str
    is_remote: bool = False
    skills: Optional[List[str]] = None
    
    @validator('budget')
    def validate_budget(cls, v):
        if v <= 0:
            raise ValueError('Budget must be greater than 0')
        return v


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    budget: Optional[float] = None
    budget_type: Optional[BudgetType] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    skills: Optional[List[str]] = None
    status: Optional[JobStatus] = None


class ClientInfo(BaseModel):
    id: str
    first_name: str
    last_name: str
    profile_image: Optional[str] = None
    average_rating: Optional[float] = None
    
    class Config:
        from_attributes = True


class FreelancerInfo(BaseModel):
    id: str
    first_name: str
    last_name: str
    profile_image: Optional[str] = None
    skills: Optional[List[str]] = None
    average_rating: Optional[float] = None
    
    class Config:
        from_attributes = True


class JobApplicationCreate(BaseModel):
    cover_letter: str
    proposed_budget: float
    
    @validator('proposed_budget')
    def validate_proposed_budget(cls, v):
        if v <= 0:
            raise ValueError('Proposed budget must be greater than 0')
        return v


class JobApplicationResponse(BaseModel):
    id: str
    job_id: str
    freelancer_id: str
    freelancer: FreelancerInfo
    cover_letter: str
    proposed_budget: float
    status: ApplicationStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class JobResponse(JobBase):
    id: str
    client_id: str
    client: ClientInfo
    status: JobStatus
    applications: Optional[List[JobApplicationResponse]] = None
    application_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    skip: int
    limit: int