from typing import List, Optional

from app.core.security import get_current_user
from app.core.pagination import PaginationParams, get_pagination_metadata
from app.database import get_db
from app.models import Job, JobApplication, Notification, NotificationType, Post, User
from app.schemas.job import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobCreate,
    JobListResponse,
    JobResponse,
    JobUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import and_, desc, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.post("/", response_model=JobResponse)
async def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new job posting"""
    db_job = Job(**job.dict(), employer_id=current_user.id)
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)

    # Load employer relationship
    result = await db.execute(
        select(Job).options(selectinload(Job.employer)).where(Job.id == db_job.id)
    )
    job_with_employer = result.scalar_one()

    # Create a post for the job so it appears in the news feed
    job_post_content = f"🚀 New Job Opening: {job_with_employer.title}\n\n"
    job_post_content += f"Company: {job_with_employer.company}\n"
    job_post_content += f"Location: {job_with_employer.location}\n"
    job_post_content += f"Type: {job_with_employer.job_type}\n\n"
    job_post_content += f"{job_with_employer.description[:200]}{'...' if len(job_with_employer.description) > 200 else ''}"

    db_post = Post(
        user_id=current_user.id,
        content=job_post_content,
        post_type="job",
        related_job_id=db_job.id
    )
    db.add(db_post)
    await db.commit()

    return job_with_employer


@router.get("/", response_model=dict)
async def get_jobs(
    response: Response,
    pagination: PaginationParams = Depends(),
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    budget_min: Optional[float] = Query(None, ge=0),
    budget_max: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    db: AsyncSession = Depends(get_db),
):
    """Get jobs with filtering and pagination
    
    Mobile Optimization:
    - Supports both ?page=1&limit=20 and ?skip=0&limit=20 pagination
    - HTTP caching with Cache-Control: public, max-age=30
    - Small JSON payloads (max 100 items per page)
    - Optimized filtering for mobile search
    """
    query = select(Job).options(selectinload(Job.employer))

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
            or_(Job.title.ilike(f"%{search}%"), Job.description.ilike(f"%{search}%"))
        )

    if filters:
        query = query.where(and_(*filters))

    # Get total count efficiently
    count_query = select(func.count()).select_from(Job)
    if filters:
        count_query = count_query.where(and_(*filters))
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(desc(Job.created_at)).offset(pagination.skip).limit(pagination.limit)

    result = await db.execute(query)
    jobs = result.scalars().all()

    # Add HTTP cache headers for mobile optimization
    response.headers["Cache-Control"] = "public, max-age=30"

    return {
        "success": True,
        "jobs": [JobResponse.model_validate(job).model_dump() for job in jobs],
        "pagination": get_pagination_metadata(
            total=total,
            page=pagination.page,
            skip=pagination.skip,
            limit=pagination.limit
        )
    }


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific job by ID
    
    Mobile Optimization:
    - HTTP caching with Cache-Control: public, max-age=30
    - Optimized N+1 prevention with selectinload
    """
    result = await db.execute(
        select(Job)
        .options(
            selectinload(Job.employer),
            selectinload(Job.applications).selectinload(JobApplication.applicant),
        )
        .where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    # Add HTTP cache headers for mobile optimization
    response.headers["Cache-Control"] = "public, max-age=30"

    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a job posting"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this job",
        )

    # Update job fields
    update_data = job_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    await db.commit()
    await db.refresh(job)

    # Load relationships
    result = await db.execute(
        select(Job).options(selectinload(Job.employer)).where(Job.id == job_id)
    )
    updated_job = result.scalar_one()

    return updated_job


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a job posting"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this job",
        )

    await db.delete(job)
    await db.commit()

    return {"message": "Job deleted successfully"}


@router.post("/{job_id}/toggle")
async def toggle_job_status(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a job's status between active and inactive (HireMe off/on for jobs)"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this job",
        )

    # Only allow toggling between active and inactive status
    # Other statuses (closed, etc.) should not be toggleable
    if job.status not in ("active", "inactive"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot toggle job with status '{job.status}'. Only active or inactive jobs can be toggled.",
        )

    # Toggle between active and inactive
    job.status = "inactive" if job.status == "active" else "active"

    await db.commit()
    await db.refresh(job)

    return {
        "success": True,
        "job_status": job.status,
        "is_active": job.status == "active",
        "message": f"Job is now {'active' if job.status == 'active' else 'inactive'}",
    }


@router.post("/{job_id}/apply", response_model=JobApplicationResponse)
async def apply_to_job(
    job_id: int,
    application: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply to a job"""
    # Check if job exists
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    if job.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not open for applications",
        )

    if job.employer_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot apply to your own job",
        )

    # Check if already applied
    existing_application = await db.execute(
        select(JobApplication).where(
            and_(
                JobApplication.job_id == job_id,
                JobApplication.applicant_id == current_user.id,
            )
        )
    )

    if existing_application.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already applied to this job",
        )

    # Create application
    db_application = JobApplication(
        **application.dict(), job_id=job_id, applicant_id=current_user.id
    )
    db.add(db_application)
    
    # Create notification for job employer
    notification = Notification(
        user_id=job.employer_id,
        actor_id=current_user.id,
        notification_type=NotificationType.JOB_APPLICATION,
        content=f"{current_user.first_name} {current_user.last_name} applied to your job: {job.title}",
        related_id=job.id,
    )
    db.add(notification)
    
    await db.commit()
    await db.refresh(db_application)

    # Load relationships
    result = await db.execute(
        select(JobApplication)
        .options(
            selectinload(JobApplication.job), selectinload(JobApplication.applicant)
        )
        .where(JobApplication.id == db_application.id)
    )
    application_with_relations = result.scalar_one()

    return application_with_relations


@router.get("/{job_id}/applications", response_model=List[JobApplicationResponse])
async def get_job_applications(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get applications for a job (job owner only)"""
    # Check if job exists and user owns it
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    if job.employer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view applications for this job",
        )

    # Get applications
    result = await db.execute(
        select(JobApplication)
        .options(
            selectinload(JobApplication.applicant), selectinload(JobApplication.job)
        )
        .where(JobApplication.job_id == job_id)
        .order_by(desc(JobApplication.created_at))
    )
    applications = result.scalars().all()

    return applications


@router.get("/my/posted", response_model=List[JobResponse])
async def get_my_posted_jobs(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get jobs posted by current user"""
    result = await db.execute(
        select(Job)
        .options(selectinload(Job.employer))
        .where(Job.employer_id == current_user.id)
        .order_by(desc(Job.created_at))
    )
    jobs = result.scalars().all()

    return jobs


@router.get("/my/applications", response_model=List[JobApplicationResponse])
async def get_my_applications(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get applications submitted by current user"""
    result = await db.execute(
        select(JobApplication)
        .options(
            selectinload(JobApplication.job).selectinload(Job.employer),
            selectinload(JobApplication.applicant),
        )
        .where(JobApplication.applicant_id == current_user.id)
        .order_by(desc(JobApplication.created_at))
    )
    applications = result.scalars().all()

    return applications


@router.get("/stats/overview")
async def get_job_stats(db: AsyncSession = Depends(get_db)):
    """Get job statistics overview"""
    from datetime import datetime, timedelta

    # Get total active jobs
    active_jobs_result = await db.execute(
        select(func.count()).select_from(Job).where(Job.status == "active")
    )
    active_jobs = active_jobs_result.scalar()

    # Get unique companies/employers count
    companies_result = await db.execute(
        select(func.count(func.distinct(Job.employer_id))).select_from(Job).where(Job.status == "active")
    )
    companies_count = companies_result.scalar()

    # Get jobs created in the last 7 days
    one_week_ago = datetime.now() - timedelta(days=7)
    new_jobs_result = await db.execute(
        select(func.count())
        .select_from(Job)
        .where(and_(Job.created_at >= one_week_ago, Job.status == "active"))
    )
    new_this_week = new_jobs_result.scalar()

    return {
        "success": True,
        "stats": {
            "active_jobs": active_jobs,
            "companies_hiring": companies_count,
            "new_this_week": new_this_week,
        },
    }

