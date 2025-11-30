"""
Concurrent processing utilities for async/await operations.

This module provides helpers for running database queries and other I/O operations
concurrently using asyncio, improving performance for endpoints that need to
aggregate data from multiple sources.

Usage example:
    from app.core.concurrent import gather_async, run_concurrent

    # Run multiple async functions concurrently
    results = await gather_async(
        get_user_posts(user_id),
        get_user_followers(user_id),
        get_user_following(user_id),
    )
    posts, followers, following = results
"""
import asyncio
import time
import logging
from typing import Any, Callable, Coroutine, List, TypeVar, Optional
from functools import wraps, partial
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Thread pool for CPU-bound operations
_thread_pool: Optional[ThreadPoolExecutor] = None
_thread_pool_size = 4


def get_thread_pool() -> ThreadPoolExecutor:
    """
    Get or create the thread pool executor.
    
    The thread pool is used for CPU-bound operations that would block
    the event loop if run directly in async code.
    """
    global _thread_pool
    if _thread_pool is None:
        _thread_pool = ThreadPoolExecutor(
            max_workers=_thread_pool_size,
            thread_name_prefix="concurrent-"
        )
    return _thread_pool


async def gather_async(*coroutines: Coroutine[Any, Any, T]) -> List[T]:
    """
    Run multiple coroutines concurrently and return all results.
    
    This is a wrapper around asyncio.gather that provides better error handling
    and logging for debugging performance issues.
    
    Args:
        *coroutines: Variable number of coroutines to run concurrently
        
    Returns:
        List of results in the same order as the input coroutines
        
    Raises:
        Exception: Re-raises the first exception encountered
    """
    start_time = time.time()
    
    try:
        results = await asyncio.gather(*coroutines, return_exceptions=False)
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.debug(f"Concurrent gather completed in {elapsed_ms}ms for {len(coroutines)} coroutines")
        return list(results)
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.error(f"Concurrent gather failed after {elapsed_ms}ms: {e}")
        raise


async def gather_with_timeout(
    timeout_seconds: float,
    *coroutines: Coroutine[Any, Any, T]
) -> List[Optional[T]]:
    """
    Run multiple coroutines concurrently with a timeout.
    
    If any coroutine doesn't complete within the timeout, it is cancelled
    and None is returned in its place.
    
    Args:
        timeout_seconds: Maximum time to wait for all coroutines
        *coroutines: Variable number of coroutines to run concurrently
        
    Returns:
        List of results (or None for timed-out coroutines) in the same order
    """
    start_time = time.time()
    
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*coroutines, return_exceptions=True),
            timeout=timeout_seconds
        )
        
        # Convert exceptions to None
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Coroutine failed: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.debug(f"Concurrent gather with timeout completed in {elapsed_ms}ms")
        return processed_results
        
    except asyncio.TimeoutError:
        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.warning(f"Concurrent gather timed out after {elapsed_ms}ms")
        return [None] * len(coroutines)


async def run_in_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Run a synchronous function in a thread pool to avoid blocking the event loop.
    
    This is useful for CPU-bound operations like password hashing or
    synchronous database operations.
    
    Args:
        func: Synchronous function to run
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Result of the function
    """
    loop = asyncio.get_event_loop()
    executor = get_thread_pool()
    
    # Create a partial function with kwargs
    if kwargs:
        func_with_kwargs = partial(func, **kwargs)
        return await loop.run_in_executor(executor, func_with_kwargs, *args)
    else:
        return await loop.run_in_executor(executor, func, *args)


def async_timed(func: Callable) -> Callable:
    """
    Decorator to log execution time of async functions.
    
    Usage:
        @async_timed
        async def slow_operation():
            ...
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.debug(f"{func.__name__} completed in {elapsed_ms}ms")
            return result
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.error(f"{func.__name__} failed after {elapsed_ms}ms: {e}")
            raise
    return wrapper


class ConcurrentBatcher:
    """
    Utility for batching multiple async operations together.
    
    This is useful for aggregating results from multiple sources
    in a single endpoint while maintaining clean code structure.
    
    Usage:
        batcher = ConcurrentBatcher()
        batcher.add("posts", get_user_posts(user_id))
        batcher.add("followers", get_followers_count(user_id))
        batcher.add("following", get_following_count(user_id))
        
        results = await batcher.execute()
        # results = {"posts": [...], "followers": 10, "following": 5}
    """
    
    def __init__(self, timeout: Optional[float] = None):
        """
        Initialize the batcher.
        
        Args:
            timeout: Optional timeout in seconds for all operations
        """
        self._operations: dict[str, Coroutine] = {}
        self._timeout = timeout
    
    def add(self, key: str, coroutine: Coroutine) -> 'ConcurrentBatcher':
        """
        Add an operation to the batch.
        
        Args:
            key: Unique key for this operation's result
            coroutine: Async operation to execute
            
        Returns:
            Self for method chaining
        """
        self._operations[key] = coroutine
        return self
    
    async def execute(self) -> dict[str, Optional[Any]]:
        """
        Execute all batched operations concurrently.
        
        Returns:
            Dictionary mapping keys to their results. Results may be None
            if using timeout and an operation timed out.
        """
        if not self._operations:
            return {}
        
        keys = list(self._operations.keys())
        coroutines = list(self._operations.values())
        
        if self._timeout:
            results = await gather_with_timeout(self._timeout, *coroutines)
        else:
            results = await gather_async(*coroutines)
        
        return dict(zip(keys, results))


def shutdown_thread_pool():
    """
    Shutdown the thread pool executor.
    
    Should be called during application shutdown to clean up resources.
    """
    global _thread_pool
    if _thread_pool is not None:
        _thread_pool.shutdown(wait=False)
        _thread_pool = None
        logger.info("Concurrent thread pool shut down")
