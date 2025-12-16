from typing import Optional

from app.core.security import get_current_user
from app.core.cache import get_cached, set_cached
from app.core.cache_headers import CacheStrategy, handle_conditional_request, apply_performance_headers
from app.core.pagination import paginate_auto, format_paginated_response
from app.database import get_db
from app.models import User
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/available")
async def get_available_users(
    request: Request,
    # Dual pagination support
    cursor: Optional[str] = Query(None, description="Cursor for cursor-based pagination (mobile)"),
    skip: Optional[int] = Query(None, ge=0, description="Offset for offset-based pagination (web)"),
    page: Optional[int] = Query(None, ge=1, description="Page number (alternative to skip)"),
    limit: int = Query(20, ge=1, le=100),
    direction: str = Query("next", regex="^(next|previous)$"),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of users available for hire with dual pagination
    
    Mobile API Optimization Features:
    - **Dual Pagination**: Cursor-based (mobile) or offset-based (web)
    - **HTTP Caching**: ETag validation with stale-while-revalidate
    - **Performance**: Cached for 3 minutes for fast response times
    """
    # Build cache key
    cache_params = f"{cursor}:{skip}:{page}:{limit}:{direction}:{search}"
    cache_key = f"hireme:available:{current_user.id}:{cache_params}"
    
    # Try cache first
    cached_response = await get_cached(cache_key)
    if cached_response is not None:
        response = handle_conditional_request(request, cached_response, CacheStrategy.PUBLIC_LIST)
        apply_performance_headers(response)
        return response
    
    # Build query
    base_query = select(User).where(
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
        base_query = base_query.where(search_filter)

    # Use dual pagination
    users, pagination_meta = await paginate_auto(
        db=db,
        query=base_query,
        model_class=User,
        cursor=cursor,
        skip=skip,
        page=page,
        limit=limit,
        direction=direction,
        order_by_field="created_at",
        order_direction="desc",
        count_total=False,
    )

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

    response = format_paginated_response(users_data, pagination_meta)
    
    # Cache for 3 minutes
    await set_cached(cache_key, response, ttl=180)
    
    # Return with HTTP caching headers
    json_response = handle_conditional_request(request, response, CacheStrategy.PUBLIC_LIST)
    apply_performance_headers(json_response)
    return json_response


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
