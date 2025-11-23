from typing import List, Optional

from app.core.security import get_current_user
from app.database import get_db
from app.models import Follow, User
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/list")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of users with optional search"""
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
                Follow.followed_id.in_([u.id for u in users]),
            )
        )
    )
    following_ids = {f.followed_id for f in follow_result.scalars().all()}

    # Get follower/following counts for each user
    users_data = []
    for user in users:
        # Count followers
        followers_result = await db.execute(
            select(func.count()).select_from(Follow).where(Follow.followed_id == user.id)
        )
        followers_count = followers_result.scalar()

        # Count following
        following_result = await db.execute(
            select(func.count()).select_from(Follow).where(Follow.follower_id == user.id)
        )
        following_count = following_result.scalar()

        users_data.append(
            {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "bio": user.bio,
                "occupation": user.occupation,
                "location": user.location,
                "is_following": user.id in following_ids,
                "followers_count": followers_count,
                "following_count": following_count,
            }
        )

    return {"success": True, "users": users_data, "total": total}


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if current user follows this user
    follow_result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id, Follow.followed_id == user_id
            )
        )
    )
    is_following = follow_result.scalar_one_or_none() is not None

    # Get follower/following counts
    followers_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.followed_id == user_id)
    )
    followers_count = followers_result.scalar()

    following_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
    )
    following_count = following_result.scalar()

    return {
        "success": True,
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "occupation": user.occupation,
            "company_name": user.company_name,
            "location": user.location,
            "skills": user.skills,
            "experience": user.experience,
            "education": user.education,
            "is_following": is_following,
            "followers_count": followers_count,
            "following_count": following_count,
        },
    }


@router.post("/follow/{user_id}")
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Follow a user"""
    # Check if user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    target_user = user_result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot follow yourself",
        )

    # Check if already following
    follow_result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id, Follow.followed_id == user_id
            )
        )
    )
    existing_follow = follow_result.scalar_one_or_none()

    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Already following this user"
        )

    # Create follow
    follow = Follow(follower_id=current_user.id, followed_id=user_id)
    db.add(follow)
    await db.commit()

    return {"success": True, "message": "User followed successfully"}


@router.post("/unfollow/{user_id}")
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unfollow a user"""
    # Check if following
    follow_result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id, Follow.followed_id == user_id
            )
        )
    )
    follow = follow_result.scalar_one_or_none()

    if not follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not following this user"
        )

    await db.delete(follow)
    await db.commit()

    return {"success": True, "message": "User unfollowed successfully"}


@router.get("/following/list")
async def get_following(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users that current user is following"""
    result = await db.execute(
        select(User)
        .join(Follow, Follow.followed_id == User.id)
        .where(Follow.follower_id == current_user.id)
    )
    following_users = result.scalars().all()

    users_data = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "occupation": user.occupation,
            "location": user.location,
        }
        for user in following_users
    ]

    return {"success": True, "following": users_data}


@router.get("/followers/list")
async def get_followers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users that follow current user"""
    result = await db.execute(
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.followed_id == current_user.id)
    )
    followers = result.scalars().all()

    users_data = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "occupation": user.occupation,
            "location": user.location,
        }
        for user in followers
    ]

    return {"success": True, "followers": users_data}
