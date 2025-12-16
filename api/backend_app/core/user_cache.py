"""
Redis-backed user caching for authentication and lookups.

This module provides high-performance user caching to reduce database queries
for frequently accessed user data, particularly during authentication and
user profile lookups.

Features:
- Cache user objects by ID for fast token validation
- Cache user lookups by email and username
- Automatic cache invalidation on user updates
- Fallback to database on cache miss
- Graceful degradation when Redis is unavailable

Performance targets:
- Cached user lookup: <1ms
- Database fallback: <10ms
- Cache hit rate: >80% for active users

Usage:
    from app.core.user_cache import user_cache
    
    # Get user by ID (for auth)
    user = await user_cache.get_user_by_id(db, user_id)
    
    # Get user by email (for login)
    user = await user_cache.get_user_by_email(db, email)
    
    # Invalidate on update
    await user_cache.invalidate_user(user_id)
"""
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_cache import redis_cache, CACHE_TTL_CONFIG
from app.models import User

logger = logging.getLogger(__name__)

# Cache TTL configuration for user data
USER_CACHE_TTL = CACHE_TTL_CONFIG.get("users", 300)  # 5 minutes default
USER_PROFILE_TTL = CACHE_TTL_CONFIG.get("user_profile", 180)  # 3 minutes


class UserCache:
    """
    User-specific caching layer with multiple lookup strategies.
    
    Provides efficient caching for user objects accessed during:
    - Authentication (user_id from JWT token)
    - Login (email/phone lookup)
    - Profile views (user_id or username lookup)
    """
    
    def __init__(self):
        self._stats = {
            "hits": 0,
            "misses": 0,
            "invalidations": 0
        }
    
    def _user_cache_key(self, user_id: int) -> str:
        """Generate cache key for user by ID."""
        return f"user:id:{user_id}"
    
    def _user_email_cache_key(self, email: str) -> str:
        """Generate cache key for user ID by email."""
        return f"user:email:{email.lower()}"
    
    def _user_username_cache_key(self, username: str) -> str:
        """Generate cache key for user ID by username."""
        return f"user:username:{username.lower()}"
    
    def _user_phone_cache_key(self, phone: str) -> str:
        """Generate cache key for user ID by phone."""
        return f"user:phone:{phone}"
    
    def _serialize_user(self, user: User) -> dict:
        """
        Serialize user object for caching.
        
        Only cache essential fields to minimize memory usage.
        Excludes sensitive data like hashed_password.
        
        Note: hashed_password is intentionally excluded. Cached user objects 
        are read-only and used for display/validation purposes only. 
        Password verification always requires a fresh database query to get 
        the hashed_password field.
        """
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "phone": user.phone,
            "location": user.location,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "occupation": user.occupation,
            "company_name": user.company_name,
            "skills": user.skills,
            "experience": user.experience,
            "education": user.education,
            "is_available_for_hire": user.is_available_for_hire,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "oauth_provider": user.oauth_provider,
            "oauth_provider_id": user.oauth_provider_id,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            # Note: hashed_password is intentionally excluded for security
        }
    
    def _deserialize_user_data(self, cached_data: dict) -> dict:
        """
        Deserialize cached user data, converting ISO datetime strings back to datetime objects.
        
        Args:
            cached_data: Dictionary from cache with ISO datetime strings
            
        Returns:
            Dictionary with datetime objects suitable for User model
        """
        # Create a copy to avoid modifying the cached data
        user_data = cached_data.copy()
        
        # Convert ISO datetime strings back to datetime objects
        datetime_fields = ['created_at', 'updated_at', 'last_login']
        for field in datetime_fields:
            if field in user_data and user_data[field]:
                try:
                    user_data[field] = datetime.fromisoformat(user_data[field])
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse datetime field '{field}': {e}")
                    user_data[field] = None
        
        return user_data
    
    async def _cache_user(self, user: User, ttl: int = USER_CACHE_TTL):
        """
        Cache a user object with multiple lookup keys.
        
        Caches by:
        - User ID (primary key)
        - Email -> User ID mapping
        - Username -> User ID mapping (if username exists)
        - Phone -> User ID mapping (if phone exists)
        """
        if not user:
            return
        
        try:
            # Serialize user data
            user_data = self._serialize_user(user)
            
            # Cache the full user object by ID
            await redis_cache.set(
                self._user_cache_key(user.id),
                user_data,
                ttl=ttl
            )
            
            # Cache email -> user_id mapping
            if user.email:
                await redis_cache.set(
                    self._user_email_cache_key(user.email),
                    user.id,
                    ttl=ttl
                )
            
            # Cache username -> user_id mapping
            if user.username:
                await redis_cache.set(
                    self._user_username_cache_key(user.username),
                    user.id,
                    ttl=ttl
                )
            
            # Cache phone -> user_id mapping
            if user.phone:
                await redis_cache.set(
                    self._user_phone_cache_key(user.phone),
                    user.id,
                    ttl=ttl
                )
            
            logger.debug(f"Cached user {user.id} with multiple lookup keys")
            
        except Exception as e:
            logger.warning(f"Failed to cache user {user.id}: {e}")
    
    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: int,
        ttl: int = USER_CACHE_TTL
    ) -> Optional[User]:
        """
        Get user by ID with caching.
        
        This is the primary method for authentication - when validating
        JWT tokens, we need fast user lookups by ID.
        
        Args:
            db: Database session
            user_id: User ID to lookup
            ttl: Cache TTL in seconds
            
        Returns:
            User object or None if not found
        """
        # Try cache first
        cache_key = self._user_cache_key(user_id)
        cached_data = await redis_cache.get(cache_key)
        
        if cached_data:
            self._stats["hits"] += 1
            logger.debug(f"Cache hit: user {user_id}")
            
            # Deserialize cached data (converts ISO strings to datetime objects)
            user_data = self._deserialize_user_data(cached_data)
            
            # Reconstruct User object from cached data
            # Note: This is a detached object (not bound to session)
            # For auth purposes this is fine - we only need to read user data
            # The hashed_password field will be None (excluded for security)
            user = User(**user_data)
            return user
        
        # Cache miss - query database
        self._stats["misses"] += 1
        logger.debug(f"Cache miss: user {user_id}, querying database")
        
        try:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            
            if user:
                # Cache the user for next time
                await self._cache_user(user, ttl=ttl)
            
            return user
            
        except Exception as e:
            logger.error(f"Database query failed for user {user_id}: {e}")
            return None
    
    async def get_user_by_email(
        self,
        db: AsyncSession,
        email: str,
        ttl: int = USER_CACHE_TTL
    ) -> Optional[User]:
        """
        Get user by email with caching.
        
        Used during login when user provides email.
        
        Args:
            db: Database session
            email: Email address to lookup
            ttl: Cache TTL in seconds
            
        Returns:
            User object or None if not found
        """
        if not email:
            return None
        
        # Try to get user_id from email mapping cache
        email_cache_key = self._user_email_cache_key(email)
        cached_user_id = await redis_cache.get(email_cache_key)
        
        if cached_user_id:
            # Got user_id, now get the user object
            return await self.get_user_by_id(db, int(cached_user_id), ttl=ttl)
        
        # Cache miss - query database
        self._stats["misses"] += 1
        logger.debug(f"Cache miss: email {email}, querying database")
        
        try:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if user:
                # Cache the user with all lookup keys
                await self._cache_user(user, ttl=ttl)
            
            return user
            
        except Exception as e:
            logger.error(f"Database query failed for email {email}: {e}")
            return None
    
    async def get_user_by_username(
        self,
        db: AsyncSession,
        username: str,
        ttl: int = USER_CACHE_TTL
    ) -> Optional[User]:
        """
        Get user by username with caching.
        
        Used for profile lookups when user visits /users/:username
        
        Args:
            db: Database session
            username: Username to lookup
            ttl: Cache TTL in seconds
            
        Returns:
            User object or None if not found
        """
        if not username:
            return None
        
        # Try to get user_id from username mapping cache
        username_cache_key = self._user_username_cache_key(username)
        cached_user_id = await redis_cache.get(username_cache_key)
        
        if cached_user_id:
            # Got user_id, now get the user object
            return await self.get_user_by_id(db, int(cached_user_id), ttl=ttl)
        
        # Cache miss - query database
        self._stats["misses"] += 1
        logger.debug(f"Cache miss: username {username}, querying database")
        
        try:
            result = await db.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            
            if user:
                # Cache the user with all lookup keys
                await self._cache_user(user, ttl=ttl)
            
            return user
            
        except Exception as e:
            logger.error(f"Database query failed for username {username}: {e}")
            return None
    
    async def get_user_by_phone(
        self,
        db: AsyncSession,
        phone: str,
        ttl: int = USER_CACHE_TTL
    ) -> Optional[User]:
        """
        Get user by phone number with caching.
        
        Used during login when user provides phone number.
        
        Args:
            db: Database session
            phone: Phone number to lookup
            ttl: Cache TTL in seconds
            
        Returns:
            User object or None if not found
        """
        if not phone:
            return None
        
        # Try to get user_id from phone mapping cache
        phone_cache_key = self._user_phone_cache_key(phone)
        cached_user_id = await redis_cache.get(phone_cache_key)
        
        if cached_user_id:
            # Got user_id, now get the user object
            return await self.get_user_by_id(db, int(cached_user_id), ttl=ttl)
        
        # Cache miss - query database
        self._stats["misses"] += 1
        logger.debug(f"Cache miss: phone {phone}, querying database")
        
        try:
            result = await db.execute(select(User).where(User.phone == phone))
            user = result.scalar_one_or_none()
            
            if user:
                # Cache the user with all lookup keys
                await self._cache_user(user, ttl=ttl)
            
            return user
            
        except Exception as e:
            logger.error(f"Database query failed for phone {phone}: {e}")
            return None
    
    async def invalidate_user(self, user_id: int, email: Optional[str] = None,
                             username: Optional[str] = None, phone: Optional[str] = None):
        """
        Invalidate all cache entries for a user.
        
        Should be called when user data is updated (profile edit, password change, etc.)
        
        Args:
            user_id: User ID to invalidate
            email: User email (if known)
            username: User username (if known)
            phone: User phone (if known)
        """
        self._stats["invalidations"] += 1
        
        # Always invalidate the primary user cache
        await redis_cache.delete(self._user_cache_key(user_id))
        
        # Invalidate secondary lookup caches if we know the values
        if email:
            await redis_cache.delete(self._user_email_cache_key(email))
        
        if username:
            await redis_cache.delete(self._user_username_cache_key(username))
        
        if phone:
            await redis_cache.delete(self._user_phone_cache_key(phone))
        
        logger.debug(f"Invalidated cache for user {user_id}")
    
    async def invalidate_all_users(self):
        """
        Invalidate all user caches.
        
        Use sparingly - only for bulk operations or migrations.
        """
        await redis_cache.invalidate_prefix("user:")
        logger.info("Invalidated all user caches")
    
    def get_stats(self) -> dict:
        """Get cache statistics for monitoring."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            **self._stats,
            "hit_rate_percent": round(hit_rate, 2),
            "total_lookups": total
        }


# Global user cache instance
user_cache = UserCache()
