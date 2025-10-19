from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models import Job, User, JobApplication
from app.schemas.job import (
    JobCreate, JobUpdate, JobResponse, JobApplicationCreate,
    JobApplicationResponse, JobListResponse
)
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting"""
    db_job = Job(**job.dict(), client_id=current_user.id)
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    
    # Load client relationship
    result = await db.execute(
        select(Job).options(selectinload(Job.client))
        .where(Job.id == db_job.id)
    )
    job_with_client = result.scalar_one()
    
    return job_with_client


@router.get("/", response_model=JobListResponse)
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    budget_min: Optional[float] = Query(None, ge=0),
    budget_max: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    db: AsyncSession = Depends(get_db)
):
    """Get jobs with filtering and pagination"""
    query = select(Job).options(selectinload(Job.client))
    
    # Apply filters
    filters = []
    if status:
        filters.append(Job.status == status)
    if category:
        filters.append(Job.category.ilike(f"%{category}%"))
    if location and not is_remote:
        filters.append(Job.location.ilike(f"%{location}%"))
    if is_remote is not None:
        filters.append(Job.is_remote == is_remote)
    if budget_min is not None:
        filters.append(Job.budget >= budget_min)
    if budget_max is not None:
        filters.append(Job.budget <= budget_max)
    if search:
        filters.append(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%")
            )
        )
    
    if filters:
        query = query.where(and_(*filters))
    
    # Get total count
    count_result = await db.execute(
        select(Job).where(and_(*filters)) if filters else select(Job)
    )
    total = len(count_result.all())
    
    # Apply pagination and ordering
    query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return JobListResponse(
        jobs=jobs,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific job by ID"""
    result = await db.execute(
        select(Job)
        .options(
            selectinload(Job.client),
            selectinload(Job.applications)
            .selectinload(JobApplication.freelancer)
        )
        .where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_update: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a job posting"""
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this job"
        )
    
    # Update job fields
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    await db.commit()
    await db.refresh(job)
    
    # Load relationships
    result = await db.execute(
        select(Job).options(selectinload(Job.client))
        .where(Job.id == job_id)
    )
    updated_job = result.scalar_one()
    
    return updated_job


@router.delete("/{job_id}")
async def delete_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a job posting"""
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this job"
        )
    
    await db.delete(job)
    await db.commit()
    
    return {"message": "Job deleted successfully"}


@router.post("/{job_id}/apply", response_model=JobApplicationResponse)
async def apply_to_job(
    job_id: UUID,
    application: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Apply to a job"""
    # Check if job exists
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not open for applications"
        )
    
    if job.client_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot apply to your own job"
        )
    
    # Check if already applied
    existing_application = await db.execute(
        select(JobApplication).where(
            and_(
                JobApplication.job_id == job_id,
                JobApplication.freelancer_id == current_user.id
            )
        )
    )
    
    if existing_application.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already applied to this job"
        )
    
    # Create application
    db_application = JobApplication(
        **application.dict(),
        job_id=job_id,
        freelancer_id=current_user.id
    )
    db.add(db_application)
    await db.commit()
    await db.refresh(db_application)
    
    # Load relationships
    result = await db.execute(
        select(JobApplication)
        .options(
            selectinload(JobApplication.job),
            selectinload(JobApplication.freelancer)
        )
        .where(JobApplication.id == db_application.id)
    )
    application_with_relations = result.scalar_one()
    
    return application_with_relations


@router.get("/{job_id}/applications", response_model=List[JobApplicationResponse])
async def get_job_applications(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get applications for a job (job owner only)"""
    # Check if job exists and user owns it
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.client_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view applications for this job"
        )
    
    # Get applications
    result = await db.execute(
        select(JobApplication)
        .options(
            selectinload(JobApplication.freelancer),
            selectinload(JobApplication.job)
        )
        .where(JobApplication.job_id == job_id)
        .order_by(desc(JobApplication.created_at))
    )
    applications = result.scalars().all()
    
    return applications


@router.get("/my/posted", response_model=List[JobResponse])
async def get_my_posted_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get jobs posted by current user"""
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.client))
        .where(Job.client_id == current_user.id)
        .order_by(desc(Job.created_at))
    )
    jobs = result.scalars().all()
    
    return jobs


@router.get("/my/applications", response_model=List[JobApplicationResponse])
async def get_my_applications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get applications submitted by current user"""
    result = await db.execute(
        select(JobApplication)
        .options(
            selectinload(JobApplication.job).selectinload(Job.client),
            selectinload(JobApplication.freelancer)
        )
        .where(JobApplication.freelancer_id == current_user.id)
        .order_by(desc(JobApplication.created_at))
    )
    applications = result.scalars().all()
    
    return applications
