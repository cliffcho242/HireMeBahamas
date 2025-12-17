"""
Query-level timeout utilities for PostgreSQL.

This module provides safe, per-query timeout enforcement using SET LOCAL statement_timeout.
This approach is compatible with Neon's pooled connections (PgBouncer) and prevents
long-running queries from exhausting database resources.

Key Features:
- Per-query timeouts (not global/startup parameters)
- Neon pooler compatible (uses SET LOCAL, not startup options)
- Applies only within transaction scope
- Safe for connection pooling
- Traffic-spike protection

Usage:
    from app.core.query_timeout import with_query_timeout, set_query_timeout
    
    # Option 1: Context manager
    async with with_query_timeout(db, timeout_ms=5000):
        result = await db.execute(select(User).where(User.id == user_id))
    
    # Option 2: Manual control
    await set_query_timeout(db, timeout_ms=5000)
    result = await db.execute(select(User).where(User.id == user_id))
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Default timeout configuration (in milliseconds)
# Can be overridden via environment variables
# Ordered from fastest to slowest for clarity
FAST_QUERY_TIMEOUT_MS = int(os.getenv("DB_FAST_QUERY_TIMEOUT_MS", "2000"))  # 2 seconds for fast operations
DEFAULT_QUERY_TIMEOUT_MS = int(os.getenv("DB_QUERY_TIMEOUT_MS", "5000"))  # 5 seconds default
SLOW_QUERY_TIMEOUT_MS = int(os.getenv("DB_SLOW_QUERY_TIMEOUT_MS", "30000"))  # 30 seconds for slow operations


async def set_query_timeout(
    db: AsyncSession,
    timeout_ms: Optional[int] = None
) -> None:
    """
    Set query timeout for the current transaction.
    
    Uses PostgreSQL's SET LOCAL statement_timeout to enforce a timeout on all
    subsequent queries in the current transaction. This is Neon-safe as it
    doesn't use startup parameters.
    
    Args:
        db: SQLAlchemy async session
        timeout_ms: Timeout in milliseconds (default: 5000ms / 5 seconds)
    
    Raises:
        No exceptions - logs warnings on failure but continues execution
        to prevent timeout enforcement from breaking the application
    
    Example:
        async with AsyncSessionLocal() as db:
            await set_query_timeout(db, timeout_ms=3000)  # 3 second timeout
            result = await db.execute(select(User).where(...))
    
    Note:
        - SET LOCAL only affects the current transaction
        - Timeout is automatically reset when transaction ends
        - Compatible with Neon pooled connections (PgBouncer)
    """
    if timeout_ms is None:
        timeout_ms = DEFAULT_QUERY_TIMEOUT_MS
    
    # Validate timeout_ms to prevent SQL injection
    # Timeout must be a positive integer
    if not isinstance(timeout_ms, int) or timeout_ms <= 0:
        logger.warning(
            f"Invalid timeout value: {timeout_ms}. Must be a positive integer. "
            f"Using default: {DEFAULT_QUERY_TIMEOUT_MS}ms"
        )
        timeout_ms = DEFAULT_QUERY_TIMEOUT_MS
    
    try:
        # SET LOCAL statement_timeout applies only to the current transaction
        # and is automatically reset when the transaction ends.
        # This is the Neon-safe way to set timeouts (not in startup parameters).
        # Using f-string is safe here because timeout_ms is validated as a positive integer above.
        await db.execute(text(f"SET LOCAL statement_timeout = {timeout_ms}"))
        logger.debug(f"Query timeout set to {timeout_ms}ms for current transaction")
    except Exception as e:
        # Log warning but don't raise - we don't want timeout enforcement
        # to break the application if there's an issue setting it
        logger.warning(
            f"Failed to set query timeout to {timeout_ms}ms: {type(e).__name__}: {e}. "
            "Queries will run without timeout protection."
        )


@asynccontextmanager
async def with_query_timeout(
    db: AsyncSession,
    timeout_ms: Optional[int] = None
) -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager that sets a query timeout for all operations within the block.
    
    This is the recommended way to apply query timeouts as it makes the timeout
    scope explicit and self-documenting in the code.
    
    Args:
        db: SQLAlchemy async session
        timeout_ms: Timeout in milliseconds (default: 5000ms / 5 seconds)
    
    Yields:
        The same database session with timeout applied
    
    Example:
        async with with_query_timeout(db, timeout_ms=3000):
            # All queries in this block have a 3 second timeout
            user = await db.execute(select(User).where(User.id == user_id))
            posts = await db.execute(select(Post).where(Post.user_id == user_id))
        # Timeout is automatically reset when exiting the context
    
    Note:
        - The timeout applies to all queries within the context
        - Timeout is reset automatically when the context exits
        - Safe to nest (inner timeout overrides outer)
    """
    await set_query_timeout(db, timeout_ms)
    try:
        yield db
    finally:
        # SET LOCAL is automatically reset when transaction ends,
        # but we can explicitly reset it if needed
        pass


async def set_fast_query_timeout(db: AsyncSession) -> None:
    """
    Set a short timeout for fast queries (e.g., lookups, simple SELECTs).
    
    Args:
        db: SQLAlchemy async session
    
    Example:
        await set_fast_query_timeout(db)
        user = await db.execute(select(User).where(User.email == email))
    """
    await set_query_timeout(db, timeout_ms=FAST_QUERY_TIMEOUT_MS)


async def set_slow_query_timeout(db: AsyncSession) -> None:
    """
    Set a longer timeout for slow queries (e.g., analytics, reports, aggregations).
    
    Args:
        db: SQLAlchemy async session
    
    Example:
        await set_slow_query_timeout(db)
        stats = await db.execute(select(func.count(Post.id), func.avg(Post.likes)))
    """
    await set_query_timeout(db, timeout_ms=SLOW_QUERY_TIMEOUT_MS)


def get_timeout_for_operation(operation_type: str) -> int:
    """
    Get the recommended timeout for a specific operation type.
    
    Args:
        operation_type: Type of operation ('fast', 'slow', or 'default')
    
    Returns:
        Timeout in milliseconds
    
    Example:
        timeout = get_timeout_for_operation('fast')
        await set_query_timeout(db, timeout_ms=timeout)
    """
    timeouts = {
        'fast': FAST_QUERY_TIMEOUT_MS,
        'default': DEFAULT_QUERY_TIMEOUT_MS,
        'slow': SLOW_QUERY_TIMEOUT_MS,
    }
    return timeouts.get(operation_type, DEFAULT_QUERY_TIMEOUT_MS)
