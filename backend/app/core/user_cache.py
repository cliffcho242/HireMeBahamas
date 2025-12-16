"""
User caching layer for high-performance authentication and user lookups.

Implements Redis-backed caching with TTL to reduce database queries
for frequently accessed user data during authentication and profile lookups.

Performance targets:
- Cache hit: <1ms latency  
- Reduces database load by caching user data for 5 minutes
- Automatic cache invalidation on user updates

Usage:
    from app.core.user_cache import get_user
    
    user = await get_user(user_id, db)
"""
import json
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_cache import redis_cache
from app.models import User

logger = logging.getLogger(__name__)

# Cache TTL for user data (5 minutes as specified in requirements)
USER_CACHE_TTL = 300


def _serialize_user(user: User) -> dict:
    """Serialize user object to dictionary for caching.
    
    Args:
        user: User model instance
        
    Returns:
        Dictionary with user data
    """
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "location": user.location,
        "phone": user.phone,
        "bio": user.bio,
        "skills": user.skills,
        "profile_image": user.profile_image,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "oauth_provider": user.oauth_provider,
        "oauth_provider_id": user.oauth_provider_id,
        "hashed_password": user.hashed_password,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def _deserialize_user(data: dict, db: AsyncSession) -> User:
    """Deserialize dictionary back to User object.
    
    Args:
        data: Dictionary with user data
        db: Database session (for ORM context)
        
    Returns:
        User model instance
    """
    from datetime import datetime
    
    user = User()
    user.id = data["id"]
    user.email = data["email"]
    user.username = data.get("username")
    user.first_name = data["first_name"]
    user.last_name = data["last_name"]
    user.role = data["role"]
    user.location = data.get("location")
    user.phone = data.get("phone")
    user.bio = data.get("bio")
    user.skills = data.get("skills")
    user.profile_image = data.get("profile_image")
    user.avatar_url = data.get("avatar_url")
    user.is_active = data["is_active"]
    user.is_admin = data.get("is_admin", False)
    user.oauth_provider = data.get("oauth_provider")
    user.oauth_provider_id = data.get("oauth_provider_id")
    user.hashed_password = data.get("hashed_password")
    
    if data.get("created_at"):
        user.created_at = datetime.fromisoformat(data["created_at"])
    if data.get("updated_at"):
        user.updated_at = datetime.fromisoformat(data["updated_at"])
    
    return user


async def get_user(user_id: int, db: AsyncSession) -> Optional[User]:
    """Get user by ID with Redis caching.
    
    This function implements a cache-aside pattern:
    1. Check Redis cache first
    2. If cached, return deserialized user
    3. If not cached, query database
    4. Store result in cache with TTL
    5. Return user
    
    Args:
        user_id: User ID to look up
        db: Database session
        
    Returns:
        User object if found, None otherwise
        
    Example:
        user = await get_user(123, db)
        if user and user.is_active:
            # User is active and data is fresh
            pass
    """
    cache_key = f"user:{user_id}"
    
    # Try to get from cache first
    cached = await redis_cache.get(cache_key)
    if cached:
        logger.debug(f"Cache hit for user_id={user_id}")
        try:
            # Deserialize cached user data
            user = _deserialize_user(cached, db)
            return user
        except Exception as e:
            logger.warning(f"Failed to deserialize cached user {user_id}: {e}")
            # Fall through to database lookup if deserialization fails
    
    # Cache miss - query database
    logger.debug(f"Cache miss for user_id={user_id}, querying database")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user:
        # Serialize and cache the user data
        try:
            user_data = _serialize_user(user)
            await redis_cache.set(cache_key, user_data, ttl=USER_CACHE_TTL)
            logger.debug(f"Cached user_id={user_id} with TTL={USER_CACHE_TTL}s")
        except Exception as e:
            logger.warning(f"Failed to cache user {user_id}: {e}")
            # Continue even if caching fails - user data is still returned
    
    return user


async def invalidate_user_cache(user_id: int) -> None:
    """Invalidate cached user data.
    
    Call this when user data is updated to ensure cache consistency.
    
    Args:
        user_id: User ID to invalidate
        
    Example:
        # After updating user profile
        await db.commit()
        await invalidate_user_cache(user.id)
    """
    cache_key = f"user:{user_id}"
    await redis_cache.delete(cache_key)
    logger.debug(f"Invalidated cache for user_id={user_id}")


async def get_users_batch(user_ids: list[int], db: AsyncSession) -> dict[int, Optional[User]]:
    """Get multiple users by ID with batch caching.
    
    More efficient than calling get_user() multiple times.
    Uses Redis MGET for batch cache lookups.
    
    Args:
        user_ids: List of user IDs to look up
        db: Database session
        
    Returns:
        Dictionary mapping user_id -> User (or None if not found)
        
    Example:
        users = await get_users_batch([1, 2, 3], db)
        for user_id, user in users.items():
            if user:
                print(f"User {user_id}: {user.email}")
    """
    if not user_ids:
        return {}
    
    # Build cache keys
    cache_keys = [f"user:{uid}" for uid in user_ids]
    
    # Batch get from cache
    cached_data = await redis_cache.mget(cache_keys)
    
    result = {}
    uncached_ids = []
    
    # Process cached results
    for user_id, cache_key in zip(user_ids, cache_keys):
        cached = cached_data.get(cache_key)
        if cached:
            try:
                user = _deserialize_user(cached, db)
                result[user_id] = user
                logger.debug(f"Cache hit for user_id={user_id} (batch)")
            except Exception as e:
                logger.warning(f"Failed to deserialize cached user {user_id}: {e}")
                uncached_ids.append(user_id)
        else:
            uncached_ids.append(user_id)
    
    # Fetch uncached users from database in a single query
    if uncached_ids:
        logger.debug(f"Cache miss for {len(uncached_ids)} users, querying database (batch)")
        db_result = await db.execute(
            select(User).where(User.id.in_(uncached_ids))
        )
        users = db_result.scalars().all()
        
        # Cache the fetched users
        cache_items = {}
        for user in users:
            result[user.id] = user
            try:
                user_data = _serialize_user(user)
                cache_items[f"user:{user.id}"] = user_data
            except Exception as e:
                logger.warning(f"Failed to serialize user {user.id}: {e}")
        
        # Batch cache the new data
        if cache_items:
            try:
                await redis_cache.mset(cache_items, ttl=USER_CACHE_TTL)
                logger.debug(f"Cached {len(cache_items)} users with TTL={USER_CACHE_TTL}s (batch)")
            except Exception as e:
                logger.warning(f"Failed to batch cache users: {e}")
        
        # Mark users not found as None
        for user_id in uncached_ids:
            if user_id not in result:
                result[user_id] = None
    
    return result
