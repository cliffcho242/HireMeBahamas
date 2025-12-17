"""
Examples of integrating slow query logging into API endpoints.

⚠️  IMPORTANT: This is a REFERENCE/EXAMPLE file, not executable code.
    It demonstrates usage patterns. Copy these patterns into your actual
    API endpoints and adjust imports and model references to match your
    application structure.

This file demonstrates practical usage patterns for the lightweight query logger.
The examples show different ways to integrate slow query logging, but you'll
need to adjust:
- Import paths to match your project structure
- Model names and relationships to match your database schema
- Query logic to match your business requirements

For a working example, see: api/backend_app/api/users.py
"""

import time
import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Example imports - adjust to match your actual project structure
# from app.core.query_logger import log_query_performance, log_query_time, track_query_start, track_query_end
# from app.models import User, Post

logger = logging.getLogger(__name__)


# =============================================================================
# EXAMPLE 1: Context Manager (Recommended)
# =============================================================================
# This is the cleanest and most Pythonic approach
# NOTE: These examples use pseudo-code. Adjust model names and relationships
# to match your actual database schema.

async def get_user_posts_with_context_manager(
    user_id: int,
    db: AsyncSession
):
    """Fetch user posts with automatic slow query logging.
    
    Example usage pattern - adjust imports and model references for your code.
    """
    from app.core.query_logger import log_query_performance
    from app.models import Post
    
    # Context manager automatically tracks time and logs if > threshold
    async with log_query_performance("fetch_user_posts", warn_threshold=1.0):
        result = await db.execute(
            select(Post)
            .where(Post.user_id == user_id)
            .order_by(Post.created_at.desc())
            .limit(100)
        )
        posts = result.scalars().all()
    
    return posts


# =============================================================================
# EXAMPLE 2: Manual Pattern (As Specified in Problem Statement)
# =============================================================================
# This is the exact pattern from the requirements:
# start = time.time()
# # query
# elapsed = time.time() - start
# if elapsed > 1:
#     logger.warning(f"Slow query: {elapsed:.2f}s")

async def get_user_by_email_manual_pattern(
    email: str,
    db: AsyncSession
) -> User:
    """Fetch user by email with manual slow query logging."""
    
    # Manual pattern from problem statement
    start = time.time()
    
    # Execute query
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    # Check for slow query
    elapsed = time.time() - start
    if elapsed > 1:
        logger.warning(f"Slow query: {elapsed:.2f}s")
    
    return user


# =============================================================================
# EXAMPLE 3: Using Helper Functions
# =============================================================================
# This provides better code organization while keeping the manual approach

async def get_user_feed_with_helpers(
    user_id: int,
    db: AsyncSession,
    limit: int = 50
) -> List[Post]:
    """Fetch user feed with helper-based slow query logging."""
    
    # Start timing
    start = track_query_start()
    
    # Execute query
    result = await db.execute(
        select(Post)
        .join(Post.user)
        .where(Post.user_id.in_(
            select(User.id).where(User.followers.any(id=user_id))
        ))
        .order_by(Post.created_at.desc())
        .limit(limit)
    )
    posts = result.scalars().all()
    
    # Track elapsed time and log if slow
    elapsed = track_query_end(start)
    log_query_time("fetch_user_feed", elapsed)
    
    return posts


# =============================================================================
# EXAMPLE 4: Multiple Queries with Individual Tracking
# =============================================================================
# Track multiple queries separately to identify which one is slow

async def get_user_profile_data(
    user_id: int,
    db: AsyncSession
):
    """Fetch user profile data with per-query tracking."""
    
    # Query 1: Get user
    start = time.time()
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    elapsed = time.time() - start
    if elapsed > 1:
        logger.warning(f"Slow query: fetch_user took {elapsed:.2f}s")
    
    # Query 2: Get user posts
    start = time.time()
    posts_result = await db.execute(
        select(Post)
        .where(Post.user_id == user_id)
        .limit(10)
    )
    posts = posts_result.scalars().all()
    elapsed = time.time() - start
    if elapsed > 1:
        logger.warning(f"Slow query: fetch_user_posts took {elapsed:.2f}s")
    
    # Query 3: Get followers count
    start = time.time()
    followers_result = await db.execute(
        select(User.id).where(User.following.any(id=user_id))
    )
    followers_count = len(followers_result.scalars().all())
    elapsed = time.time() - start
    if elapsed > 1:
        logger.warning(f"Slow query: count_followers took {elapsed:.2f}s")
    
    return {
        "user": user,
        "posts": posts,
        "followers_count": followers_count,
    }


# =============================================================================
# EXAMPLE 5: Custom Thresholds for Different Operations
# =============================================================================
# Use different thresholds based on expected query complexity

async def run_analytics_query(db: AsyncSession):
    """Run analytics query with higher threshold (analytics are expected to be slower)."""
    
    # Use context manager with custom threshold (5 seconds for analytics)
    async with log_query_performance("analytics_query", warn_threshold=5.0):
        # Complex analytics query
        result = await db.execute(
            select(User.id, Post.id)
            .join(Post.user)
            .where(Post.created_at > '2024-01-01')
        )
        data = result.all()
    
    return data


async def run_lookup_query(user_id: int, db: AsyncSession):
    """Run fast lookup with lower threshold (lookups should be very fast)."""
    
    # Use context manager with custom threshold (0.5 seconds for lookups)
    async with log_query_performance("user_lookup", warn_threshold=0.5):
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    
    return user


# =============================================================================
# EXAMPLE 6: Integration with Existing Monitoring
# =============================================================================
# Combine slow query logging with existing performance monitoring

async def get_trending_posts(
    db: AsyncSession,
    limit: int = 20
) -> List[Post]:
    """Fetch trending posts with query logging."""
    
    # Track query with logging
    start = track_query_start()
    
    result = await db.execute(
        select(Post)
        .order_by(Post.likes.desc())
        .limit(limit)
    )
    posts = result.scalars().all()
    
    elapsed = track_query_end(start)
    
    # Log slow query if threshold exceeded
    log_query_time("fetch_trending_posts", elapsed)
    
    return posts


# =============================================================================
# USAGE RECOMMENDATIONS
# =============================================================================
"""
WHEN TO USE EACH PATTERN:

1. Context Manager (log_query_performance):
   - Best for: Most use cases, clean and Pythonic
   - Use when: You want automatic tracking with minimal code

2. Manual Pattern (time.time() + logger.warning):
   - Best for: Following exact problem statement requirements
   - Use when: You want explicit control or need to match specific patterns

3. Helper Functions (track_query_start/end + log_query_time):
   - Best for: Multiple queries or complex logic
   - Use when: You need fine-grained control but want helper utilities

4. Custom Thresholds:
   - Fast lookups: 0.5s threshold
   - Regular queries: 1.0s threshold (default)
   - Analytics/reports: 5.0s threshold
   - Complex aggregations: 10.0s threshold

ENVIRONMENT VARIABLES:
   Set SLOW_QUERY_THRESHOLD to change default threshold globally:
   SLOW_QUERY_THRESHOLD=2.0  # 2 seconds instead of 1 second

NO APM REQUIRED:
   This is a lightweight solution that requires NO external APM tools.
   Just Python's time.time() and logging module.
"""
