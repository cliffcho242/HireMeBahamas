"""
Request-level timeout utilities for async operations.

This module provides timeout protection for async operations that may hang indefinitely,
such as external API calls, file uploads, and heavy processing tasks.

Key Features:
- Generic timeout wrapper for any async operation
- Prevents long-running requests from blocking resources
- Traffic-spike protection
- Memory-efficient timeout handling
- Compatible with FastAPI async endpoints

Usage:
    from app.core.request_timeout import with_timeout
    
    # Wrap any async operation with timeout
    async def upload_to_external_api(file_data):
        result = await with_timeout(
            external_api.upload(file_data),
            timeout=8
        )
        return result
    
    # Use for heavy processing
    async def process_large_image(image):
        processed = await with_timeout(
            heavy_image_processing(image),
            timeout=10
        )
        return processed
"""

import asyncio
import logging
from typing import TypeVar, Coroutine, Any

logger = logging.getLogger(__name__)

# Type variable for generic return types
T = TypeVar('T')

# Default timeout configuration (in seconds)
# Can be overridden per-operation
DEFAULT_TIMEOUT_SECONDS = 8
UPLOAD_TIMEOUT_SECONDS = 10
HEAVY_QUERY_TIMEOUT_SECONDS = 15
EXTERNAL_API_TIMEOUT_SECONDS = 8


async def with_timeout(
    coro: Coroutine[Any, Any, T],
    timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> T:
    """
    Execute an async operation with a timeout.
    
    This function wraps any async operation (coroutine) with a timeout guard.
    If the operation takes longer than the specified timeout, it will be
    cancelled and raise asyncio.TimeoutError.
    
    Args:
        coro: The coroutine to execute with timeout protection
        timeout: Maximum time to wait in seconds (default: 8 seconds)
    
    Returns:
        The result of the coroutine if it completes within the timeout
    
    Raises:
        asyncio.TimeoutError: If the operation exceeds the timeout
        Any other exception raised by the coroutine
    
    Examples:
        # Upload with timeout
        result = await with_timeout(
            upload_to_cloud(file),
            timeout=10
        )
        
        # External API call with timeout
        data = await with_timeout(
            fetch_external_data(url),
            timeout=5
        )
        
        # Heavy database query with timeout
        results = await with_timeout(
            db.execute(complex_query),
            timeout=15
        )
    
    Note:
        - The timeout is enforced at the Python asyncio level
        - For database queries, also consider using query_timeout.py for PostgreSQL-level timeouts
        - The coroutine is cancelled if timeout is reached
        - Clean-up operations in the coroutine should handle cancellation gracefully
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(
            f"Operation timed out after {timeout} seconds. "
            "This may indicate a slow external service or heavy processing."
        )
        raise


async def with_upload_timeout(coro: Coroutine[Any, Any, T]) -> T:
    """
    Execute a file upload operation with appropriate timeout.
    
    This is a convenience wrapper for upload operations with a
    pre-configured timeout suitable for file uploads (10 seconds).
    
    Args:
        coro: The upload coroutine to execute
    
    Returns:
        The result of the upload operation
    
    Raises:
        asyncio.TimeoutError: If the upload exceeds the timeout
    
    Example:
        uploaded_url = await with_upload_timeout(
            upload_to_gcs(file)
        )
    """
    return await with_timeout(coro, timeout=UPLOAD_TIMEOUT_SECONDS)


async def with_api_timeout(coro: Coroutine[Any, Any, T]) -> T:
    """
    Execute an external API call with appropriate timeout.
    
    This is a convenience wrapper for external API calls with a
    pre-configured timeout (8 seconds).
    
    Args:
        coro: The API call coroutine to execute
    
    Returns:
        The result of the API call
    
    Raises:
        asyncio.TimeoutError: If the API call exceeds the timeout
    
    Example:
        response = await with_api_timeout(
            httpx_client.get(external_api_url)
        )
    """
    return await with_timeout(coro, timeout=EXTERNAL_API_TIMEOUT_SECONDS)


async def with_heavy_query_timeout(coro: Coroutine[Any, Any, T]) -> T:
    """
    Execute a heavy query or processing operation with appropriate timeout.
    
    This is a convenience wrapper for heavy operations with a
    pre-configured timeout (15 seconds).
    
    Args:
        coro: The heavy operation coroutine to execute
    
    Returns:
        The result of the operation
    
    Raises:
        asyncio.TimeoutError: If the operation exceeds the timeout
    
    Example:
        results = await with_heavy_query_timeout(
            generate_analytics_report()
        )
    
    Note:
        For database queries, consider also using query_timeout.py
        for PostgreSQL-level timeout enforcement.
    """
    return await with_timeout(coro, timeout=HEAVY_QUERY_TIMEOUT_SECONDS)


def get_timeout_for_operation(operation_type: str) -> float:
    """
    Get the recommended timeout for a specific operation type.
    
    Args:
        operation_type: Type of operation ('upload', 'api', 'heavy', or 'default')
    
    Returns:
        Timeout in seconds
    
    Example:
        timeout = get_timeout_for_operation('upload')
        result = await with_timeout(operation, timeout=timeout)
    """
    timeouts = {
        'upload': UPLOAD_TIMEOUT_SECONDS,
        'api': EXTERNAL_API_TIMEOUT_SECONDS,
        'heavy': HEAVY_QUERY_TIMEOUT_SECONDS,
        'default': DEFAULT_TIMEOUT_SECONDS,
    }
    return timeouts.get(operation_type, DEFAULT_TIMEOUT_SECONDS)
