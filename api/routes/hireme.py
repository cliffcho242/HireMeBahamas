from typing import Optional

from ..core.security import get_current_user
from ..database import get_db
from ..models import User
from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/available")
async def get_available_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of users available for hire"""
    query = select(User).where(
        and_(
            User.is_active == True,
            User.is_available_for_hire == True,
            User.id != current_user.id,
        )
    )

    if search:
        search_filter = or_(
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%"),
            User.occupation.ilike(f"%{search}%"),
            User.location.ilike(f"%{search}%"),
            User.skills.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    # Format users data
    users_data = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "occupation": user.occupation,
            "company_name": user.company_name,
            "location": user.location,
            "skills": user.skills,
            "experience": user.experience,
            "education": user.education,
            "is_available_for_hire": user.is_available_for_hire,
        }
        for user in users
    ]

    return {"success": True, "users": users_data, "total": total}


@router.post("/toggle")
async def toggle_availability(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle user's availability for hire status"""
    # Toggle the availability
    current_user.is_available_for_hire = not current_user.is_available_for_hire
    
    await db.commit()
    await db.refresh(current_user)

    return {
        "success": True,
        "is_available": current_user.is_available_for_hire,
        "message": f"You are now {'available' if current_user.is_available_for_hire else 'not available'} for hire",
    }
