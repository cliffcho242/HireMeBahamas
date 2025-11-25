from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, validator


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

    @validator("budget")
    def validate_budget(cls, v):
        if v <= 0:
            raise ValueError("Budget must be greater than 0")
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


class EmployerInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    profile_image: Optional[str] = None
    avatar_url: Optional[str] = None
    average_rating: Optional[float] = None

    class Config:
        from_attributes = True


class ApplicantInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    profile_image: Optional[str] = None
    avatar_url: Optional[str] = None
    skills: Optional[List[str]] = None
    average_rating: Optional[float] = None

    class Config:
        from_attributes = True


class JobApplicationCreate(BaseModel):
    cover_letter: str
    proposed_budget: float

    @validator("proposed_budget")
    def validate_proposed_budget(cls, v):
        if v <= 0:
            raise ValueError("Proposed budget must be greater than 0")
        return v


class JobApplicationResponse(BaseModel):
    id: int
    job_id: int
    applicant_id: int
    applicant: ApplicantInfo
    cover_letter: str
    proposed_budget: Optional[float] = None
    status: str = "pending"
    created_at: datetime

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    company: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    job_type: str = "full-time"
    budget: Optional[float] = None
    budget_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    location: str
    is_remote: bool = False
    skills: Optional[str] = None
    employer_id: int
    employer: EmployerInfo
    status: str = "active"
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
