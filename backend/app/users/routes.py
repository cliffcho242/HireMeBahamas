"""
User routes - User profiles, following, search.

Provides endpoints for user management including profile viewing,
following/unfollowing users, and searching for users.
"""
import logging
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.cache import get_cached, set_cached, invalidate_cache
from app.database import get_db
from app.models import Follow, User
from app.schemas.auth import UserResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Constants
MAX_INT32 = 2147483647
USERNAME_PATTERN = r'^[a-zA-Z0-9_-]+$'


async def resolve_user_by_identifier(
    identifier: str,
    db: AsyncSession,
    requester_id: int
) -> User:
    """Resolve a user by ID or username."""
    if not identifier or not identifier.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier cannot be empty"
        )
    
    identifier = identifier.strip()
    
    if len(identifier) > 150:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid identifier: too long"
        )
    
    # Try to parse as integer ID first
    target_user = None
    if identifier.isdigit():
        try:
            user_id = int(identifier)
            if user_id <= 0 or user_id > MAX_INT32:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID"
                )
            result = await db.execute(select(User).where(User.id == user_id))
            target_user = result.scalar_one_or_none()
        except HTTPException:
            raise
        except (ValueError, OverflowError):
            pass
    
    # If not found by ID, try username lookup
    if not target_user:
        if not re.match(USERNAME_PATTERN, identifier):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid identifier format"
            )
        result = await db.execute(select(User).where(User.username == identifier))
        target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account is not active"
        )
    
    return target_user


@router.get("/list")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of users with optional search."""
    cache_key = f"users:list:{skip}:{limit}:{search}:{current_user.id}"
    
    cached_response = await get_cached(cache_key)
    if cached_response is not None:
        return cached_response
    
    query = select(User).where(User.is_active == True, User.id != current_user.id)

    if search:
        search_filter = or_(
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.occupation.ilike(f"%{search}%"),
            User.location.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()

    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    # Get follow status for each user
    follow_result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id,
                Follow.followed_id.in_([u.id for u in users])
            )
        )
    )
    followed_ids = {f.followed_id for f in follow_result.scalars().all()}

    users_list = [
        {
            **UserResponse.from_orm(user).dict(),
            "is_following": user.id in followed_ids,
        }
        for user in users
    ]
    
    response = {
        "users": users_list,
        "total": total,
        "skip": skip,
        "limit": limit,
    }
    
    # Cache for 3 minutes
    await set_cached(cache_key, response, ttl=180)
    
    return response


@router.get("/{identifier}")
async def get_user_profile(
    identifier: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user profile by ID or username."""
    target_user = await resolve_user_by_identifier(identifier, db, current_user.id)
    
    # Check if current user is following target user
    follow_result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id,
                Follow.followed_id == target_user.id
            )
        )
    )
    is_following = follow_result.scalar_one_or_none() is not None
    
    return {
        **UserResponse.from_orm(target_user).dict(),
        "is_following": is_following,
    }


@router.post("/{identifier}/follow")
async def follow_user(
    identifier: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Follow a user."""
    target_user = await resolve_user_by_identifier(identifier, db, current_user.id)
    
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself"
        )
    
    # Check if already following
    result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id,
                Follow.followed_id == target_user.id
            )
        )
    )
    existing_follow = result.scalar_one_or_none()
    
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    # Create follow relationship
    follow = Follow(follower_id=current_user.id, followed_id=target_user.id)
    db.add(follow)
    await db.commit()
    
    # Invalidate cache
    await invalidate_cache(f"users:list:*")
    
    return {"message": "Successfully followed user"}


@router.delete("/{identifier}/follow")
async def unfollow_user(
    identifier: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unfollow a user."""
    target_user = await resolve_user_by_identifier(identifier, db, current_user.id)
    
    # Find and delete follow relationship
    result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id,
                Follow.followed_id == target_user.id
            )
        )
    )
    follow = result.scalar_one_or_none()
    
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not following this user"
        )
    
    await db.delete(follow)
    await db.commit()
    
    # Invalidate cache
    await invalidate_cache(f"users:list:*")
    
    return {"message": "Successfully unfollowed user"}


@router.get("/{identifier}/followers")
async def get_user_followers(
    identifier: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of users following the specified user."""
    target_user = await resolve_user_by_identifier(identifier, db, current_user.id)
    
    # Get followers
    query = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.followed_id == target_user.id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    followers = result.scalars().all()
    
    # Get count
    count_query = (
        select(func.count())
        .select_from(Follow)
        .where(Follow.followed_id == target_user.id)
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return {
        "users": [UserResponse.from_orm(user).dict() for user in followers],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{identifier}/following")
async def get_user_following(
    identifier: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of users that the specified user is following."""
    target_user = await resolve_user_by_identifier(identifier, db, current_user.id)
    
    # Get following
    query = (
        select(User)
        .join(Follow, Follow.followed_id == User.id)
        .where(Follow.follower_id == target_user.id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    following = result.scalars().all()
    
    # Get count
    count_query = (
        select(func.count())
        .select_from(Follow)
        .where(Follow.follower_id == target_user.id)
    )
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return {
        "users": [UserResponse.from_orm(user).dict() for user in following],
        "total": total,
        "skip": skip,
        "limit": limit,
    }
