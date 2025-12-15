"""
Query Optimization Utilities for Facebook-Level Performance

Implements:
- Query result caching
- N+1 query prevention with eager loading
- Batch loading for related entities
- Query performance tracking
"""
import logging
import time
import asyncio
from typing import List, Dict, Any, Optional, Callable, TypeVar
from functools import wraps
from collections import defaultdict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Track query performance (thread-safe with asyncio.Lock)
query_stats = defaultdict(lambda: {"count": 0, "total_time": 0, "avg_time": 0})
_stats_lock = asyncio.Lock()


def track_query_performance(query_name: str):
    """
    Decorator to track query performance (thread-safe).
    
    Usage:
        @track_query_performance("get_user_posts")
        async def get_user_posts(db: AsyncSession, user_id: int):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                elapsed = (time.time() - start_time) * 1000  # Convert to ms
                
                # Update stats with lock for thread safety
                async with _stats_lock:
                    stats = query_stats[query_name]
                    stats["count"] += 1
                    stats["total_time"] += elapsed
                    stats["avg_time"] = stats["total_time"] / stats["count"]
                
                # Log slow queries
                if elapsed > 100:  # Queries taking more than 100ms
                    logger.warning(
                        f"Slow query detected: {query_name} took {elapsed:.2f}ms"
                    )
                elif elapsed > 50:
                    logger.info(f"Query {query_name} took {elapsed:.2f}ms")
        
        return wrapper
    return decorator


def get_query_stats() -> Dict[str, Dict[str, float]]:
    """Get query performance statistics."""
    return dict(query_stats)


def reset_query_stats():
    """Reset query performance statistics."""
    query_stats.clear()


class DataLoader:
    """
    Generic DataLoader for batching and caching database queries.
    
    Prevents N+1 queries by batching multiple requests into a single query.
    Similar to Facebook's DataLoader pattern.
    """
    
    def __init__(self, batch_load_fn: Callable, max_batch_size: int = 100):
        """
        Initialize DataLoader.
        
        Args:
            batch_load_fn: Function that takes a list of keys and returns a dict
            max_batch_size: Maximum batch size before forcing a load
        """
        self.batch_load_fn = batch_load_fn
        self.max_batch_size = max_batch_size
        self._batch: List[Any] = []
        self._cache: Dict[Any, Any] = {}
        self._promise_cache: Dict[Any, Any] = {}
    
    async def load(self, key: Any) -> Any:
        """
        Load a single item by key.
        
        Batches multiple loads into a single query.
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]
        
        # Add to batch
        self._batch.append(key)
        
        # If batch is full, execute immediately
        if len(self._batch) >= self.max_batch_size:
            await self._dispatch_batch()
        
        return self._cache.get(key)
    
    async def load_many(self, keys: List[Any]) -> List[Any]:
        """Load multiple items by keys."""
        results = []
        for key in keys:
            result = await self.load(key)
            results.append(result)
        return results
    
    async def _dispatch_batch(self):
        """Execute the batched query."""
        if not self._batch:
            return
        
        batch = self._batch[:]
        self._batch.clear()
        
        try:
            # Execute batch load
            results = await self.batch_load_fn(batch)
            
            # Cache results
            for key, value in results.items():
                self._cache[key] = value
        except Exception as e:
            logger.error(f"Batch load failed: {e}")
            # Cache None for failed keys to prevent retry loops
            for key in batch:
                if key not in self._cache:
                    self._cache[key] = None
    
    def clear(self):
        """Clear the cache."""
        self._cache.clear()
        self._batch.clear()


async def batch_load_users(db: AsyncSession, user_ids: List[int]) -> Dict[int, Any]:
    """
    Batch load users by IDs.
    
    Example usage:
        loader = DataLoader(lambda ids: batch_load_users(db, ids))
        users = await loader.load_many([1, 2, 3, 4, 5])
    """
    from app.models import User
    
    result = await db.execute(
        select(User).where(User.id.in_(user_ids))
    )
    users = result.scalars().all()
    
    return {user.id: user for user in users}


async def batch_load_posts(db: AsyncSession, post_ids: List[int]) -> Dict[int, Any]:
    """Batch load posts by IDs."""
    from app.models import Post
    
    result = await db.execute(
        select(Post).where(Post.id.in_(post_ids))
    )
    posts = result.scalars().all()
    
    return {post.id: post for post in posts}


class EagerLoader:
    """
    Utilities for eager loading related entities to prevent N+1 queries.
    """
    
    @staticmethod
    def load_posts_with_user(query):
        """Eager load user relationship for posts."""
        return query.options(selectinload('user'))
    
    @staticmethod
    def load_posts_with_comments(query):
        """Eager load comments for posts."""
        return query.options(selectinload('comments'))
    
    @staticmethod
    def load_posts_with_likes(query):
        """Eager load likes for posts."""
        return query.options(selectinload('likes'))
    
    @staticmethod
    def load_posts_full(query):
        """Eager load all relationships for posts."""
        return query.options(
            selectinload('user'),
            selectinload('comments').selectinload('user'),
            selectinload('likes').selectinload('user'),
        )
    
    @staticmethod
    def load_users_with_posts(query):
        """Eager load posts for users."""
        return query.options(selectinload('posts'))
    
    @staticmethod
    def load_users_with_followers(query):
        """Eager load followers for users."""
        return query.options(
            selectinload('followers'),
            selectinload('following'),
        )


async def optimize_query_for_pagination(
    query,
    skip: int = 0,
    limit: int = 20,
    max_limit: int = 100,
):
    """
    Optimize query for pagination.
    
    Args:
        query: SQLAlchemy query
        skip: Number of records to skip
        limit: Number of records to return
        max_limit: Maximum allowed limit
    
    Returns:
        Optimized query with pagination
    """
    # Enforce max limit
    limit = min(limit, max_limit)
    
    # Apply offset and limit
    return query.offset(skip).limit(limit)


async def get_count_efficiently(db: AsyncSession, query) -> int:
    """
    Get count efficiently using COUNT(*) instead of loading all records.
    
    Much faster than len(results.all()) for large datasets.
    """
    # Convert query to count query
    count_query = select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    return result.scalar() or 0


class QueryCache:
    """
    Simple in-memory query result cache.
    
    For production, use Redis or similar distributed cache.
    """
    
    def __init__(self, ttl: int = 300):
        self._cache: Dict[str, tuple[Any, float]] = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached result if not expired."""
        if key in self._cache:
            value, expires_at = self._cache[key]
            if time.time() < expires_at:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Cache a result with TTL."""
        expires_at = time.time() + self.ttl
        self._cache[key] = (value, expires_at)
    
    def invalidate(self, pattern: str):
        """Invalidate cache entries matching pattern."""
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]
    
    def clear(self):
        """Clear all cached results."""
        self._cache.clear()


# Global query cache instance
query_cache = QueryCache(ttl=60)  # 1 minute default TTL


def cached_query(cache_key: str, ttl: int = 60):
    """
    Decorator for caching query results.
    
    Usage:
        @cached_query("user_posts_{user_id}", ttl=120)
        async def get_user_posts(db: AsyncSession, user_id: int):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from template
            key = cache_key.format(**kwargs)
            
            # Check cache
            cached = query_cache.get(key)
            if cached is not None:
                logger.debug(f"Query cache hit: {key}")
                return cached
            
            # Execute query
            result = await func(*args, **kwargs)
            
            # Cache result
            query_cache.set(key, result)
            logger.debug(f"Query cache miss: {key}")
            
            return result
        
        return wrapper
    return decorator


# Optimization tips and best practices
OPTIMIZATION_TIPS = """
Database Query Optimization Tips:

1. Use indexes on frequently queried columns
   - Foreign keys (user_id, post_id, etc.)
   - Timestamp columns (created_at, updated_at)
   - Columns used in WHERE clauses

2. Avoid N+1 queries with eager loading
   - Use selectinload() for one-to-many relationships
   - Use joinedload() for many-to-one relationships
   
3. Batch queries when possible
   - Use DataLoader pattern for loading related entities
   - Combine multiple small queries into one

4. Use query result caching
   - Cache frequently accessed data
   - Set appropriate TTLs based on data volatility
   
5. Optimize pagination
   - Use offset/limit efficiently
   - Consider cursor-based pagination for large datasets
   
6. Monitor slow queries
   - Use track_query_performance decorator
   - Set alerts for queries > 100ms
   
7. Use connection pooling
   - Configure appropriate pool size
   - Set connection recycling
"""


def print_optimization_tips():
    """Print optimization tips for developers."""
    print(OPTIMIZATION_TIPS)
