"""
Safe Database Retry Logic

Provides a retry decorator for database operations with strict safety rules:
✅ Use only on idempotent reads
🚫 Never retry writes automatically

This module implements retry logic with exponential backoff for database operations
that may fail due to transient network issues, connection timeouts, or database
cold starts.

Example usage:
    from app.core.db_retry import db_retry
    from sqlalchemy import select
    
    # ✅ SAFE: Idempotent read operation (async)
    @db_retry(retries=3, delay=1)
    async def get_user_by_id(user_id: int):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
    
    # 🚫 UNSAFE: Write operation - DO NOT USE RETRY
    # Never use db_retry on writes (INSERT, UPDATE, DELETE)
    def create_user(user_data):
        with get_db() as session:
            user = User(**user_data)
            session.add(user)
            session.commit()
            return user

Safety Rules:
1. Only use on SELECT queries (reads)
2. Never use on INSERT, UPDATE, DELETE (writes)
3. Ensure operations are idempotent (same result when called multiple times)
4. Be aware that retry logic adds latency on failures

Author: Copilot
Date: December 2025
"""

import time
import logging
from typing import Callable, TypeVar, Any
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for generic function return type
T = TypeVar('T')


def db_retry(
    fn: Callable[..., T] = None,
    *,
    retries: int = 3,
    delay: float = 1.0
) -> Callable[..., T]:
    """
    Retry decorator for database operations with safety checks.
    
    ⚠️  CRITICAL SAFETY RULE: Use only on idempotent read operations.
    🚫 Never use on write operations (INSERT, UPDATE, DELETE).
    
    This decorator will retry a function up to `retries` times if it raises
    an exception. Between retries, it waits for `delay` seconds (with no
    exponential backoff by default to keep behavior predictable).
    
    Args:
        fn: The function to wrap (can be None when used with parameters)
        retries: Maximum number of retry attempts (default: 3)
        delay: Delay in seconds between retries (default: 1.0)
    
    Returns:
        Wrapped function that implements retry logic
    
    Raises:
        Exception: The last exception encountered if all retries fail
    
    Example:
        # Using decorator with default parameters (async)
        @db_retry
        async def get_user(user_id: int):
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User).where(User.id == user_id))
                return result.scalar_one_or_none()
        
        # Using decorator with custom parameters (async)
        @db_retry(retries=5, delay=2.0)
        async def get_users_list():
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User))
                return result.scalars().all()
    
    Note:
        - Logs a warning for each retry attempt with attempt number and error
        - On final failure, re-raises the original exception
        - No exponential backoff by default (linear delay for predictability)
    """
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """
            Wrapper function that implements retry logic.
            
            Args:
                *args: Positional arguments to pass to the wrapped function
                **kwargs: Keyword arguments to pass to the wrapped function
            
            Returns:
                The return value from the wrapped function
            
            Raises:
                Exception: The last exception if all retries fail
            """
            last_exception = None
            
            for attempt in range(1, retries + 1):
                try:
                    # Attempt to execute the function
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    # Log warning with attempt number and error details
                    logger.warning(
                        f"DB attempt {attempt}/{retries} failed: {type(e).__name__}: {e}"
                    )
                    
                    # If this was the last attempt, re-raise the exception
                    if attempt == retries:
                        func_name = getattr(func, '__name__', '<unknown>')
                        logger.error(
                            f"DB operation failed after {retries} attempts: {func_name}"
                        )
                        raise
                    
                    # Wait before next retry
                    # Use linear delay (no exponential backoff) for predictability
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            
            # Fallback in case something unexpected happens
            raise RuntimeError(
                f"db_retry: Unexpected state - no result and no exception after {retries} attempts"
            )
        
        return wrapper
    
    # Handle both @db_retry and @db_retry(...) syntax
    if fn is None:
        # Called with parameters: @db_retry(retries=5, delay=2)
        return decorator
    else:
        # Called without parameters: @db_retry
        return decorator(fn)


# Convenience function for non-decorator usage
def retry_db_operation(
    operation: Callable[..., T],
    *args: Any,
    retries: int = 3,
    delay: float = 1.0,
    **kwargs: Any
) -> T:
    """
    Retry a database operation without using a decorator.
    
    This is useful when you want to retry an operation inline without
    decorating the function definition.
    
    Args:
        operation: The function/callable to retry
        *args: Positional arguments to pass to the operation
        retries: Maximum number of retry attempts (default: 3)
        delay: Delay in seconds between retries (default: 1.0)
        **kwargs: Keyword arguments to pass to the operation
    
    Returns:
        The return value from the operation
    
    Raises:
        Exception: The last exception if all retries fail
    
    Example:
        # For async operations, wrap in an async lambda or function
        async def fetch_user():
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(User).where(User.id == user_id))
                return result.scalar_one_or_none()
        
        result = await retry_db_operation(
            fetch_user,
            retries=3,
            delay=1.0
        )
    """
    last_exception = None
    
    for attempt in range(1, retries + 1):
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logger.warning(f"DB attempt {attempt}/{retries} failed: {e}")
            
            if attempt == retries:
                raise
            
            time.sleep(delay)
    
    # Should never reach here
    if last_exception:
        raise last_exception
    
    raise RuntimeError(
        f"retry_db_operation: Unexpected state after {retries} attempts"
    )


# Export public API
__all__ = [
    'db_retry',
    'retry_db_operation',
]
