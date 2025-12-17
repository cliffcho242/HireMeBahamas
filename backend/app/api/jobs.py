from typing import List, Optional

from app.core.security import get_current_user
from app.core.cache import get_cached, set_cached, invalidate_cache
from app.core.cache_headers import CacheStrategy, handle_conditional_request, apply_performance_headers
from app.core.pagination import paginate_auto, format_paginated_response
from app.core.query_timeout import set_query_timeout
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
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
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
    # Set query timeout for job creation (5s default)
    await set_query_timeout(db)
    
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
    
    # Invalidate jobs cache after creating new job
    await invalidate_cache("jobs:list:")
    await invalidate_cache("jobs:stats:")

    return job_with_employer


@router.get("/")
async def get_jobs(
    request: Request,
    # Dual pagination support
    cursor: Optional[str] = Query(None, description="Cursor for cursor-based pagination (mobile)"),
    skip: Optional[int] = Query(None, ge=0, description="Offset for offset-based pagination (web)"),
    page: Optional[int] = Query(None, ge=1, description="Page number (alternative to skip)"),
    limit: int = Query(10, ge=1, le=100),
    direction: str = Query("next", regex="^(next|previous)$"),
    # Filters
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    budget_min: Optional[float] = Query(None, ge=0),
    budget_max: Optional[float] = Query(None, ge=0),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    db: AsyncSession = Depends(get_db),
):
    """Get jobs with dual pagination, HTTP caching, and filtering
    
    Mobile API Optimization Features:
    - **Dual Pagination**: Cursor-based (mobile) or offset-based (web)
    - **HTTP Caching**: ETag validation with stale-while-revalidate
    - **N+1 Prevention**: Eager loading of employer relationship
    
    Performance: Cached for 3 minutes (180s) for sub-100ms response times.
    """
    # Build cache key from all parameters
    cache_params = f"{cursor}:{skip}:{page}:{limit}:{direction}:{category}:{location}:{is_remote}:{budget_min}:{budget_max}:{search}:{status}"
    cache_key = f"jobs:list:{cache_params}"
    
    # Try to get from cache first (sub-100ms cache hit)
    cached_response = await get_cached(cache_key)
    if cached_response is not None:
        response = handle_conditional_request(request, cached_response, CacheStrategy.JOBS)
        apply_performance_headers(response)
        return response
    
    # Set query timeout for job listing (5s default)
    await set_query_timeout(db)
    
    # Build query with eager loading (prevents N+1)
    base_query = select(Job).options(selectinload(Job.employer))

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
        base_query = base_query.where(and_(*filters))

    # Use dual pagination system
    jobs, pagination_meta = await paginate_auto(
        db=db,
        query=base_query,
        model_class=Job,
        cursor=cursor,
        skip=skip,
        page=page,
        limit=limit,
        direction=direction,
        order_by_field="created_at",
        order_direction="desc",
        count_total=False,  # Expensive for large datasets
    )

    # Format jobs data
    jobs_data = [job.dict() for job in jobs] if hasattr(jobs[0], 'dict') else [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "location": job.location,
            "is_remote": job.is_remote,
            "job_type": job.job_type,
            "category": job.category,
            "budget": job.budget,
            "status": job.status,
            "employer_id": job.employer_id,
            "employer": {
                "id": job.employer.id,
                "first_name": job.employer.first_name,
                "last_name": job.employer.last_name,
                "username": job.employer.username,
                "avatar_url": job.employer.avatar_url,
                "company_name": job.employer.company_name,
            } if job.employer else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }
        for job in jobs
    ]

    response = format_paginated_response(jobs_data, pagination_meta)
    
    # Cache for 3 minutes (180s)
    # Jobs don't change as frequently as posts, so longer TTL is acceptable
    await set_cached(cache_key, response, ttl=180)
    
    # Return with HTTP caching headers
    json_response = handle_conditional_request(request, response, CacheStrategy.JOBS)
    apply_performance_headers(json_response)
    return json_response


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific job by ID"""
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
    
    # Invalidate jobs cache after updating job
    await invalidate_cache("jobs:list:")
    await invalidate_cache("jobs:stats:")

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
    
    # Invalidate jobs cache after deleting job
    await invalidate_cache("jobs:list:")
    await invalidate_cache("jobs:stats:")

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
    """Get job statistics overview (cached for <100ms response)
    
    Performance: Cached for 5 minutes (300s) since statistics don't need
    to be real-time and this is a relatively expensive query.
    """
    from datetime import datetime, timedelta
    
    # Try to get from cache first (sub-100ms cache hit)
    cache_key = "jobs:stats:overview"
    cached_response = await get_cached(cache_key)
    if cached_response is not None:
        return cached_response

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

    response = {
        "success": True,
        "stats": {
            "active_jobs": active_jobs,
            "companies_hiring": companies_count,
            "new_this_week": new_this_week,
        },
    }
    
    # Cache for 5 minutes (statistics don't need to be real-time)
    await set_cached(cache_key, response, ttl=300)
    
    return response

