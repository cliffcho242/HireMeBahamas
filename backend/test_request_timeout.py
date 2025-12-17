"""
Tests for request timeout utilities.

This module tests the request-level timeout functionality to ensure
long-running operations are properly cancelled and timeouts are enforced.
"""

import asyncio
import pytest
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.request_timeout import (
    with_timeout,
    with_upload_timeout,
    with_api_timeout,
    with_heavy_query_timeout,
    get_timeout_for_operation,
    DEFAULT_TIMEOUT_SECONDS,
    UPLOAD_TIMEOUT_SECONDS,
    EXTERNAL_API_TIMEOUT_SECONDS,
    HEAVY_QUERY_TIMEOUT_SECONDS,
)

# Test constants for simulations
# Simulates upload time: 0.5 seconds per MB (realistic for medium-speed connections)
UPLOAD_SIMULATION_SECONDS_PER_MB = 0.5
# Simulates query processing: 1000 rows per second (typical for complex queries)
QUERY_SIMULATION_ROWS_PER_SECOND = 1000


# Helper async functions for testing
async def fast_operation():
    """Simulates a fast operation that completes quickly"""
    await asyncio.sleep(0.1)
    return "success"


async def slow_operation(delay: float = 10):
    """Simulates a slow operation that takes longer than timeout"""
    await asyncio.sleep(delay)
    return "completed"


async def failing_operation():
    """Simulates an operation that raises an exception"""
    await asyncio.sleep(0.1)
    raise ValueError("Operation failed")


# Test basic timeout functionality
@pytest.mark.asyncio
async def test_with_timeout_success():
    """Test that fast operations complete successfully"""
    result = await with_timeout(fast_operation(), timeout=1)
    assert result == "success"


@pytest.mark.asyncio
async def test_with_timeout_expires():
    """Test that slow operations raise TimeoutError"""
    with pytest.raises(asyncio.TimeoutError):
        await with_timeout(slow_operation(delay=5), timeout=1)


@pytest.mark.asyncio
async def test_with_timeout_propagates_exceptions():
    """Test that exceptions from the coroutine are propagated"""
    with pytest.raises(ValueError, match="Operation failed"):
        await with_timeout(failing_operation(), timeout=5)


@pytest.mark.asyncio
async def test_with_timeout_custom_timeout():
    """Test that custom timeout values work correctly"""
    # This should complete successfully
    result = await with_timeout(slow_operation(delay=1), timeout=2)
    assert result == "completed"
    
    # This should timeout
    with pytest.raises(asyncio.TimeoutError):
        await with_timeout(slow_operation(delay=3), timeout=1)


# Test convenience wrappers
@pytest.mark.asyncio
async def test_with_upload_timeout():
    """Test upload timeout wrapper uses correct timeout"""
    result = await with_upload_timeout(fast_operation())
    assert result == "success"
    
    # Should timeout with upload timeout (10 seconds)
    with pytest.raises(asyncio.TimeoutError):
        await with_upload_timeout(slow_operation(delay=UPLOAD_TIMEOUT_SECONDS + 1))


@pytest.mark.asyncio
async def test_with_api_timeout():
    """Test API timeout wrapper uses correct timeout"""
    result = await with_api_timeout(fast_operation())
    assert result == "success"
    
    # Should timeout with API timeout (8 seconds)
    with pytest.raises(asyncio.TimeoutError):
        await with_api_timeout(slow_operation(delay=EXTERNAL_API_TIMEOUT_SECONDS + 1))


@pytest.mark.asyncio
async def test_with_heavy_query_timeout():
    """Test heavy query timeout wrapper uses correct timeout"""
    result = await with_heavy_query_timeout(fast_operation())
    assert result == "success"
    
    # Should timeout with heavy query timeout (15 seconds)
    with pytest.raises(asyncio.TimeoutError):
        await with_heavy_query_timeout(slow_operation(delay=HEAVY_QUERY_TIMEOUT_SECONDS + 1))


# Test timeout configuration
def test_get_timeout_for_operation():
    """Test that get_timeout_for_operation returns correct timeouts"""
    assert get_timeout_for_operation('upload') == UPLOAD_TIMEOUT_SECONDS
    assert get_timeout_for_operation('api') == EXTERNAL_API_TIMEOUT_SECONDS
    assert get_timeout_for_operation('heavy') == HEAVY_QUERY_TIMEOUT_SECONDS
    assert get_timeout_for_operation('default') == DEFAULT_TIMEOUT_SECONDS
    assert get_timeout_for_operation('unknown') == DEFAULT_TIMEOUT_SECONDS


# Test edge cases
@pytest.mark.asyncio
async def test_with_timeout_zero_delay():
    """Test that operations with zero delay work correctly"""
    async def instant_operation():
        return "instant"
    
    result = await with_timeout(instant_operation(), timeout=1)
    assert result == "instant"


@pytest.mark.asyncio
async def test_with_timeout_multiple_operations():
    """Test that multiple timeouts can be used concurrently"""
    results = await asyncio.gather(
        with_timeout(fast_operation(), timeout=1),
        with_timeout(fast_operation(), timeout=2),
        with_timeout(fast_operation(), timeout=3),
    )
    assert all(r == "success" for r in results)


@pytest.mark.asyncio
async def test_with_timeout_partial_failure():
    """Test that timeout of one operation doesn't affect others"""
    # Run fast and slow operations concurrently
    # Fast should succeed, slow should timeout
    results = await asyncio.gather(
        with_timeout(fast_operation(), timeout=1),
        with_timeout(slow_operation(delay=5), timeout=1),
        return_exceptions=True
    )
    
    assert results[0] == "success"
    assert isinstance(results[1], asyncio.TimeoutError)


# Test realistic scenarios
@pytest.mark.asyncio
async def test_simulated_file_upload():
    """Test simulated file upload with timeout"""
    async def simulate_file_upload(size_mb: int):
        # Simulate upload time based on file size
        await asyncio.sleep(size_mb * UPLOAD_SIMULATION_SECONDS_PER_MB)
        return f"uploaded {size_mb}MB"
    
    # Small file should succeed
    result = await with_upload_timeout(simulate_file_upload(2))
    assert result == "uploaded 2MB"
    
    # Large file should timeout (>10 seconds for 30MB file)
    with pytest.raises(asyncio.TimeoutError):
        await with_upload_timeout(simulate_file_upload(30))


@pytest.mark.asyncio
async def test_simulated_external_api_call():
    """Test simulated external API call with timeout"""
    async def simulate_api_call(response_time: float):
        await asyncio.sleep(response_time)
        return {"status": "ok"}
    
    # Fast API should succeed
    result = await with_api_timeout(simulate_api_call(1))
    assert result == {"status": "ok"}
    
    # Slow API should timeout
    with pytest.raises(asyncio.TimeoutError):
        await with_api_timeout(simulate_api_call(EXTERNAL_API_TIMEOUT_SECONDS + 1))


@pytest.mark.asyncio
async def test_simulated_heavy_query():
    """Test simulated heavy database query with timeout"""
    async def simulate_heavy_query(rows: int):
        # Simulate query time based on rows
        await asyncio.sleep(rows / QUERY_SIMULATION_ROWS_PER_SECOND)
        return [{"id": i} for i in range(min(rows, 10))]
    
    # Normal query should succeed
    result = await with_heavy_query_timeout(simulate_heavy_query(10000))
    assert len(result) == 10
    
    # Extremely large query should timeout
    with pytest.raises(asyncio.TimeoutError):
        await with_heavy_query_timeout(simulate_heavy_query(20000000))


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
