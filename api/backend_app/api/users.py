from typing import List, Optional
import logging
import re

from app.api.auth import get_current_user
from app.core.user_cache import user_cache
from app.database import get_db
from app.models import Follow, Notification, NotificationType, User, Post
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = logging.getLogger(__name__)

# Constants
MAX_INT32 = 2147483647  # 2^31 - 1: Maximum value for 32-bit signed integer (PostgreSQL INTEGER type)
USERNAME_PATTERN = r'^[a-zA-Z0-9_-]+$'  # Valid username format: alphanumeric, underscore, hyphen


async def resolve_user_by_identifier(
    identifier: str,
    db: AsyncSession,
    requester_id: int
) -> User:
    """Resolve a user by ID or username.
    
    Args:
        identifier: User ID (integer as string) or username
        db: Database session
        requester_id: ID of the user making the request (for logging)
        
    Returns:
        User object if found and active
        
    Raises:
        HTTPException: 400 for invalid input, 404 if user not found or inactive
    """
    # Validate identifier is not empty
    if not identifier or not identifier.strip():
        logger.warning(f"Empty identifier provided by user_id={requester_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier cannot be empty"
        )
    
    identifier = identifier.strip()
    
    # Validate identifier length
    if len(identifier) > 150:
        logger.warning(f"Identifier too long ({len(identifier)} chars) from user_id={requester_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid identifier: too long (max 150 characters)"
        )
    
    # Try to parse as integer ID first
    target_user = None
    if identifier.isdigit():
        try:
            user_id = int(identifier)
            if user_id <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID: must be a positive integer"
                )
            if user_id > MAX_INT32:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID: value too large"
                )
            # Use cached lookup for better performance
            target_user = await user_cache.get_user_by_id(db, user_id)
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
        # Use cached lookup for better performance
        target_user = await user_cache.get_user_by_username(db, identifier)
    
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
        followers_count = followers_result.scalar() or 0

        # Count following
        following_result = await db.execute(
            select(func.count()).select_from(Follow).where(Follow.follower_id == user.id)
        )
        following_count = following_result.scalar() or 0

        users_data.append(
            {
                "id": user.id,
                "first_name": user.first_name or "",
                "last_name": user.last_name or "",
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


# NOTE: Static routes must be defined BEFORE dynamic routes like /{identifier}
# to ensure they are matched correctly by FastAPI's routing.

@router.get("/following/list")
async def get_following(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users that current user is following"""
    result = await db.execute(
        select(User)
        .join(Follow, Follow.followed_id == User.id)
        .where(Follow.follower_id == current_user.id, User.is_active == True)
    )
    following_users = result.scalars().all()
    
    if not following_users:
        return {"success": True, "following": []}
    
    user_ids = [user.id for user in following_users]
    
    # Get followers count for all users in one query
    followers_count_query = (
        select(Follow.followed_id, func.count().label('count'))
        .where(Follow.followed_id.in_(user_ids))
        .group_by(Follow.followed_id)
    )
    followers_result = await db.execute(followers_count_query)
    followers_counts = {row[0]: row[1] for row in followers_result.all()}
    
    # Get following count for all users in one query
    following_count_query = (
        select(Follow.follower_id, func.count().label('count'))
        .where(Follow.follower_id.in_(user_ids))
        .group_by(Follow.follower_id)
    )
    following_result = await db.execute(following_count_query)
    following_counts = {row[0]: row[1] for row in following_result.all()}

    users_data = []
    for user in following_users:
        users_data.append({
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "occupation": user.occupation,
            "location": user.location,
            "is_following": True,  # Current user is following this user by definition
            "followers_count": followers_counts.get(user.id, 0),
            "following_count": following_counts.get(user.id, 0),
        })

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
        .where(Follow.followed_id == current_user.id, User.is_active == True)
    )
    followers = result.scalars().all()
    
    if not followers:
        return {"success": True, "followers": []}

    # Get the list of user IDs that current user is following
    following_ids_result = await db.execute(
        select(Follow.followed_id).where(Follow.follower_id == current_user.id)
    )
    following_ids = {fid for (fid,) in following_ids_result.all()}
    
    user_ids = [user.id for user in followers]
    
    # Get followers count for all users in one query
    followers_count_query = (
        select(Follow.followed_id, func.count().label('count'))
        .where(Follow.followed_id.in_(user_ids))
        .group_by(Follow.followed_id)
    )
    followers_count_result = await db.execute(followers_count_query)
    followers_counts = {row[0]: row[1] for row in followers_count_result.all()}
    
    # Get following count for all users in one query
    following_count_query = (
        select(Follow.follower_id, func.count().label('count'))
        .where(Follow.follower_id.in_(user_ids))
        .group_by(Follow.follower_id)
    )
    following_count_result = await db.execute(following_count_query)
    following_counts = {row[0]: row[1] for row in following_count_result.all()}

    users_data = []
    for user in followers:
        users_data.append({
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "occupation": user.occupation,
            "location": user.location,
            "is_following": user.id in following_ids,  # Check if current user follows this follower
            "followers_count": followers_counts.get(user.id, 0),
            "following_count": following_counts.get(user.id, 0),
        })

    return {"success": True, "followers": users_data}


@router.get("/{identifier}")
async def get_user(
    identifier: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific user by ID or username
    
    Args:
        identifier: User ID (integer) or username (string)
        db: Database session
        current_user: Currently authenticated user
        
    Returns:
        User profile data with follower/following counts
        
    Raises:
        HTTPException: 400 for invalid input, 404 if user not found
    """
    logger.info(f"User lookup requested by user_id={current_user.id} for identifier={identifier}")
    
    # Validate identifier is not empty
    if not identifier or not identifier.strip():
        logger.warning(f"Empty identifier provided by user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier cannot be empty"
        )
    
    # Sanitize and validate identifier length to prevent DoS attacks
    identifier = identifier.strip()
    if len(identifier) > 150:
        logger.warning(f"Identifier too long ({len(identifier)} chars) from user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid identifier: too long (max 150 characters)"
        )
    
    # Validate username format if not a digit (alphanumeric, underscore, hyphen only)
    if not identifier.isdigit():
        if not re.match(USERNAME_PATTERN, identifier):
            logger.warning(f"Invalid username format: {identifier} from user_id={current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid username format. Use only letters, numbers, underscores, and hyphens."
            )
    
    # Try to parse as integer ID first
    user = None
    lookup_method = None
    
    if identifier.isdigit():
        try:
            user_id = int(identifier)
            
            # Validate ID is positive
            if user_id <= 0:
                logger.warning(f"Non-positive user ID: {user_id} from user_id={current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID: must be a positive integer"
                )
            
            # Validate ID doesn't overflow (max int32)
            if user_id > MAX_INT32:
                logger.warning(f"User ID overflow: {user_id} from user_id={current_user.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID: value too large"
                )
            
            # Use cached lookup for better performance
            user = await user_cache.get_user_by_id(db, user_id)
            lookup_method = "ID"
            logger.debug(f"Lookup by ID {user_id}: {'found' if user else 'not found'}")
        except HTTPException:
            # Re-raise our validation errors
            raise
        except (ValueError, OverflowError) as e:
            # Invalid integer format, will try username lookup
            logger.debug(f"Failed to parse as integer: {identifier}, error: {e}")
            pass
    
    # If not found by ID or not a digit, try username
    if not user:
        # Use cached lookup for better performance
        user = await user_cache.get_user_by_username(db, identifier)
        lookup_method = "username"
        logger.debug(f"Lookup by username '{identifier}': {'found' if user else 'not found'}")

    if not user:
        logger.info(f"User not found: identifier={identifier}, method={lookup_method}, requester={current_user.id}")
        # Use generic message to prevent user enumeration attacks
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is active
    if not user.is_active:
        logger.info(f"User account inactive: id={user.id}, requester={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account is not active"
        )
    
    logger.info(f"User found: id={user.id}, username={user.username}, requester={current_user.id}")

    # Check if current user follows this user
    follow_result = await db.execute(
        select(Follow).where(
            and_(
                Follow.follower_id == current_user.id, Follow.followed_id == user.id
            )
        )
    )
    is_following = follow_result.scalar_one_or_none() is not None

    # Get follower/following counts
    followers_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.followed_id == user.id)
    )
    followers_count = followers_result.scalar() or 0

    following_result = await db.execute(
        select(func.count()).select_from(Follow).where(Follow.follower_id == user.id)
    )
    following_count = following_result.scalar() or 0
    
    # Get actual posts count
    posts_result = await db.execute(
        select(func.count()).select_from(Post).where(Post.user_id == user.id)
    )
    posts_count = posts_result.scalar() or 0

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
            "phone": user.phone,
            "skills": user.skills,
            "experience": user.experience,
            "education": user.education,
            "user_type": user.role or "user",
            "is_available_for_hire": user.is_available_for_hire or False,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "posts_count": posts_count,
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
    # Check if user exists and is active
    user_result = await db.execute(select(User).where(User.id == user_id))
    target_user = user_result.scalar_one_or_none()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    if not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User account is not active"
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
    
    # Create notification for the followed user
    notification = Notification(
        user_id=user_id,
        actor_id=current_user.id,
        notification_type=NotificationType.FOLLOW,
        content=f"{current_user.first_name} {current_user.last_name} started following you",
        related_id=current_user.id,
    )
    db.add(notification)
    
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

    db.delete(follow)
    await db.commit()

    return {"success": True, "message": "User unfollowed successfully"}


@router.get("/{identifier}/followers")
async def get_user_followers(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users that follow a specific user
    
    Args:
        identifier: User ID (integer as string) or username
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        List of followers with their profile information
        
    Raises:
        HTTPException: 400 for invalid input, 404 if user not found
    """
    logger.info(f"Fetching followers for identifier={identifier} by user_id={current_user.id}")
    
    # Resolve user by ID or username
    target_user = await resolve_user_by_identifier(identifier, db, current_user.id)
    user_id = target_user.id
    
    result = await db.execute(
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.followed_id == user_id, User.is_active == True)
    )
    followers = result.scalars().all()
    
    if not followers:
        return {"success": True, "followers": []}

    # Get the list of user IDs that current user is following
    following_ids_result = await db.execute(
        select(Follow.followed_id).where(Follow.follower_id == current_user.id)
    )
    following_ids = {fid for (fid,) in following_ids_result.all()}
    
    user_ids = [user.id for user in followers]
    
    # Get followers count for all users in one query
    followers_count_query = (
        select(Follow.followed_id, func.count().label('count'))
        .where(Follow.followed_id.in_(user_ids))
        .group_by(Follow.followed_id)
    )
    followers_count_result = await db.execute(followers_count_query)
    followers_counts = {row[0]: row[1] for row in followers_count_result.all()}
    
    # Get following count for all users in one query
    following_count_query = (
        select(Follow.follower_id, func.count().label('count'))
        .where(Follow.follower_id.in_(user_ids))
        .group_by(Follow.follower_id)
    )
    following_count_result = await db.execute(following_count_query)
    following_counts = {row[0]: row[1] for row in following_count_result.all()}

    users_data = []
    for user in followers:
        users_data.append({
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "occupation": user.occupation,
            "location": user.location,
            "is_following": user.id in following_ids,
            "followers_count": followers_counts.get(user.id, 0),
            "following_count": following_counts.get(user.id, 0),
        })

    return {"success": True, "followers": users_data}


@router.get("/{identifier}/following")
async def get_user_following(
    identifier: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of users that a specific user is following
    
    Args:
        identifier: User ID (integer as string) or username
        current_user: Currently authenticated user
        db: Database session
        
    Returns:
        List of users being followed with their profile information
        
    Raises:
        HTTPException: 400 for invalid input, 404 if user not found
    """
    logger.info(f"Fetching following for identifier={identifier} by user_id={current_user.id}")
    
    # Resolve user by ID or username
    target_user = await resolve_user_by_identifier(identifier, db, current_user.id)
    user_id = target_user.id
    
    result = await db.execute(
        select(User)
        .join(Follow, Follow.followed_id == User.id)
        .where(Follow.follower_id == user_id, User.is_active == True)
    )
    following_users = result.scalars().all()
    
    if not following_users:
        return {"success": True, "following": []}
    
    # Get the list of user IDs that current user is following
    following_ids_result = await db.execute(
        select(Follow.followed_id).where(Follow.follower_id == current_user.id)
    )
    following_ids = {fid for (fid,) in following_ids_result.all()}
    
    user_ids = [user.id for user in following_users]
    
    # Get followers count for all users in one query
    followers_count_query = (
        select(Follow.followed_id, func.count().label('count'))
        .where(Follow.followed_id.in_(user_ids))
        .group_by(Follow.followed_id)
    )
    followers_result = await db.execute(followers_count_query)
    followers_counts = {row[0]: row[1] for row in followers_result.all()}
    
    # Get following count for all users in one query
    following_count_query = (
        select(Follow.follower_id, func.count().label('count'))
        .where(Follow.follower_id.in_(user_ids))
        .group_by(Follow.follower_id)
    )
    following_result = await db.execute(following_count_query)
    following_counts = {row[0]: row[1] for row in following_result.all()}

    users_data = []
    for user in following_users:
        users_data.append({
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "email": user.email,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "occupation": user.occupation,
            "location": user.location,
            "is_following": user.id in following_ids,
            "followers_count": followers_counts.get(user.id, 0),
            "following_count": following_counts.get(user.id, 0),
        })

    return {"success": True, "following": users_data}
