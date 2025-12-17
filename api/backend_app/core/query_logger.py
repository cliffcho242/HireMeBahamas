"""
Lightweight Query Performance Logger

This module provides a simple, manual query performance tracking system that logs
slow queries without requiring any APM (Application Performance Monitoring) tool.

Key Features:
- Manual time tracking with start = time.time()
- Logs queries that exceed configurable threshold (default: 1 second)
- No external dependencies (pure Python + logging)
- Zero performance overhead for fast queries
- Production-ready and lightweight

Usage:
    from app.core.query_logger import log_query_performance
    
    # Option 1: Context manager (recommended)
    async with log_query_performance("fetch_user_posts", warn_threshold=1.0):
        result = await db.execute(select(Post).where(Post.user_id == user_id))
    
    # Option 2: Manual tracking
    start = time.time()
    result = await db.execute(select(User).where(User.email == email))
    elapsed = time.time() - start
    if elapsed > 1:
        logger.warning(f"Slow query: {elapsed:.2f}s")
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import os

logger = logging.getLogger(__name__)

# Default threshold for slow query warnings (in seconds)
# Can be overridden via environment variable
DEFAULT_SLOW_QUERY_THRESHOLD = float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0"))


@asynccontextmanager
async def log_query_performance(
    query_name: str,
    warn_threshold: Optional[float] = None
) -> AsyncGenerator[None, None]:
    """
    Context manager that tracks query execution time and logs slow queries.
    
    This is a lightweight, manual approach to query performance monitoring
    without requiring any APM tool. It simply uses time.time() to measure
    query duration and logs warnings when queries exceed the threshold.
    
    Args:
        query_name: Descriptive name for the query (e.g., "fetch_user_posts")
        warn_threshold: Threshold in seconds for logging warnings (default: 1.0)
    
    Example:
        async with log_query_performance("fetch_user_by_email", warn_threshold=1.0):
            result = await db.execute(select(User).where(User.email == email))
        
        # If query takes > 1 second, logs:
        # WARNING: Slow query: fetch_user_by_email took 1.23s
    
    Note:
        - Zero overhead for fast queries (no logging if under threshold)
        - Lightweight: uses only time.time() and logging
        - No APM needed
    """
    if warn_threshold is None:
        warn_threshold = DEFAULT_SLOW_QUERY_THRESHOLD
    
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        if elapsed > warn_threshold:
            logger.warning(f"Slow query: {query_name} took {elapsed:.2f}s")


def log_query_time(query_name: str, elapsed: float, warn_threshold: Optional[float] = None) -> None:
    """
    Log query execution time if it exceeds the threshold.
    
    This is a convenience function for manual query time tracking.
    Use this when you need more control over timing or can't use the context manager.
    
    Args:
        query_name: Descriptive name for the query
        elapsed: Query execution time in seconds
        warn_threshold: Threshold in seconds for logging warnings (default: 1.0)
    
    Example:
        start = time.time()
        result = await db.execute(query)
        elapsed = time.time() - start
        log_query_time("complex_join_query", elapsed)
        
        # If elapsed > 1.0s, logs:
        # WARNING: Slow query: complex_join_query took 1.45s
    
    Note:
        - Only logs if elapsed time exceeds threshold
        - Lightweight: single if-check and log call
        - No APM needed
    """
    if warn_threshold is None:
        warn_threshold = DEFAULT_SLOW_QUERY_THRESHOLD
    
    if elapsed > warn_threshold:
        logger.warning(f"Slow query: {query_name} took {elapsed:.2f}s")


def track_query_start() -> float:
    """
    Get the current timestamp for query timing.
    
    This is a convenience wrapper around time.time() to make the pattern
    more explicit in code.
    
    Returns:
        Current timestamp (seconds since epoch)
    
    Example:
        start = track_query_start()
        result = await db.execute(query)
        elapsed = track_query_end(start)
        log_query_time("my_query", elapsed)
    """
    return time.time()


def track_query_end(start: float) -> float:
    """
    Calculate elapsed time since query start.
    
    This is a convenience wrapper to make the pattern more explicit.
    
    Args:
        start: Start timestamp from track_query_start()
    
    Returns:
        Elapsed time in seconds
    
    Example:
        start = track_query_start()
        result = await db.execute(query)
        elapsed = track_query_end(start)
        if elapsed > 1:
            logger.warning(f"Slow query: {elapsed:.2f}s")
    """
    return time.time() - start


# ============================================================================
# INTEGRATION WITH EXISTING MONITORING
# ============================================================================
# Optional: Integrate with existing monitoring system if available
# Note: The monitoring module is located at backend/app/core/monitoring.py
# If you want to enable this integration, import and use it in your endpoint code.
# Example:
#   from backend.app.core.monitoring import track_database_query
#   elapsed_ms = elapsed * 1000
#   track_database_query(elapsed_ms)

def log_query_with_monitoring(query_name: str, elapsed: float, warn_threshold: Optional[float] = None) -> None:
    """
    Log query time. This is an alias for log_query_time for convenience.
    
    To integrate with the monitoring system, you can extend this function
    in your application code to call both logging and monitoring functions.
    
    Args:
        query_name: Descriptive name for the query
        elapsed: Query execution time in seconds
        warn_threshold: Threshold in seconds for logging warnings (default: 1.0)
    """
    # Log slow query if threshold exceeded
    log_query_time(query_name, elapsed, warn_threshold)


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
# Example 1: Context manager (recommended)
# async with log_query_performance("fetch_user_posts"):
#     result = await db.execute(select(Post).where(Post.user_id == user_id))
#
# Example 2: Manual tracking (for fine-grained control)
# start = time.time()
# result = await db.execute(query)
# elapsed = time.time() - start
# if elapsed > 1:
#     logger.warning(f"Slow query: {elapsed:.2f}s")
#
# Example 3: Using helper functions
# start = track_query_start()
# result = await db.execute(query)
# elapsed = track_query_end(start)
# log_query_time("my_query", elapsed)
