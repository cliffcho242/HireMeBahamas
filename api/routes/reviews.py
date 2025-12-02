from typing import List, Optional
from uuid import UUID

from ..core.security import get_current_user
from ..database import get_db
from ..models import Job, JobApplication, Review, User
from ..schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.post("/", response_model=ReviewResponse)
async def create_review(
    review: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a review for a completed job"""
    # Check if job exists and is completed
    job_result = await db.execute(select(Job).where(Job.id == review.job_id))
    job = job_result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    # Check if user is involved in the job
    if job.client_id != current_user.id:
        # Check if user is the accepted freelancer
        application_result = await db.execute(
            select(JobApplication).where(
                and_(
                    JobApplication.job_id == review.job_id,
                    JobApplication.freelancer_id == current_user.id,
                    JobApplication.status == "accepted",
                )
            )
        )
        application = application_result.scalar_one_or_none()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review jobs you're involved in",
            )

    # Check if review already exists
    existing_review = await db.execute(
        select(Review).where(
            and_(
                Review.job_id == review.job_id,
                Review.reviewer_id == current_user.id,
                Review.reviewee_id == review.reviewee_id,
            )
        )
    )

    if existing_review.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this person for this job",
        )

    # Create review
    db_review = Review(**review.dict(), reviewer_id=current_user.id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)

    # Load relationships
    result = await db.execute(
        select(Review)
        .options(
            selectinload(Review.reviewer),
            selectinload(Review.reviewee),
            selectinload(Review.job),
        )
        .where(Review.id == db_review.id)
    )

    review_with_relations = result.scalar_one()
    return review_with_relations


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get reviews for a specific user"""
    result = await db.execute(
        select(Review)
        .options(
            selectinload(Review.reviewer),
            selectinload(Review.reviewee),
            selectinload(Review.job),
        )
        .where(Review.reviewee_id == user_id)
        .order_by(desc(Review.created_at))
        .offset(skip)
        .limit(limit)
    )

    reviews = result.scalars().all()
    return reviews


@router.get("/job/{job_id}", response_model=List[ReviewResponse])
async def get_job_reviews(job_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get all reviews for a specific job"""
    result = await db.execute(
        select(Review)
        .options(
            selectinload(Review.reviewer),
            selectinload(Review.reviewee),
            selectinload(Review.job),
        )
        .where(Review.job_id == job_id)
        .order_by(desc(Review.created_at))
    )

    reviews = result.scalars().all()
    return reviews


@router.get("/my/given", response_model=List[ReviewResponse])
async def get_my_given_reviews(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get reviews given by current user"""
    result = await db.execute(
        select(Review)
        .options(
            selectinload(Review.reviewer),
            selectinload(Review.reviewee),
            selectinload(Review.job),
        )
        .where(Review.reviewer_id == current_user.id)
        .order_by(desc(Review.created_at))
    )

    reviews = result.scalars().all()
    return reviews


@router.get("/my/received", response_model=List[ReviewResponse])
async def get_my_received_reviews(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get reviews received by current user"""
    result = await db.execute(
        select(Review)
        .options(
            selectinload(Review.reviewer),
            selectinload(Review.reviewee),
            selectinload(Review.job),
        )
        .where(Review.reviewee_id == current_user.id)
        .order_by(desc(Review.created_at))
    )

    reviews = result.scalars().all()
    return reviews


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a review (only by the reviewer)"""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews",
        )

    # Update review fields
    update_data = review_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    await db.commit()
    await db.refresh(review)

    # Load relationships
    result = await db.execute(
        select(Review)
        .options(
            selectinload(Review.reviewer),
            selectinload(Review.reviewee),
            selectinload(Review.job),
        )
        .where(Review.id == review_id)
    )

    updated_review = result.scalar_one()
    return updated_review


@router.delete("/{review_id}")
async def delete_review(
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a review (only by the reviewer)"""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    if review.reviewer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews",
        )

    await db.delete(review)
    await db.commit()

    return {"message": "Review deleted successfully"}


@router.get("/stats/{user_id}")
async def get_user_review_stats(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get review statistics for a user"""
    # Get average rating and count
    result = await db.execute(
        select(
            func.avg(Review.rating).label("average_rating"),
            func.count(Review.id).label("total_reviews"),
            func.count(Review.id).filter(Review.rating == 5).label("five_star"),
            func.count(Review.id).filter(Review.rating == 4).label("four_star"),
            func.count(Review.id).filter(Review.rating == 3).label("three_star"),
            func.count(Review.id).filter(Review.rating == 2).label("two_star"),
            func.count(Review.id).filter(Review.rating == 1).label("one_star"),
        ).where(Review.reviewee_id == user_id)
    )

    stats = result.first()

    return {
        "user_id": str(user_id),
        "average_rating": float(stats.average_rating) if stats.average_rating else None,
        "total_reviews": stats.total_reviews,
        "rating_breakdown": {
            "5": stats.five_star,
            "4": stats.four_star,
            "3": stats.three_star,
            "2": stats.two_star,
            "1": stats.one_star,
        },
    }
