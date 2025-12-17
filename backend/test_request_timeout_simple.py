"""
Simple tests for request timeout utilities (without pytest).

This module tests the request-level timeout functionality to ensure
long-running operations are properly cancelled and timeouts are enforced.
"""

import asyncio
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


# Test functions
async def test_with_timeout_success():
    """Test that fast operations complete successfully"""
    print("Testing fast operation with timeout...")
    result = await with_timeout(fast_operation(), timeout=1)
    assert result == "success", f"Expected 'success', got {result}"
    print("✓ Fast operation completed successfully")


async def test_with_timeout_expires():
    """Test that slow operations raise TimeoutError"""
    print("Testing slow operation timeout...")
    try:
        await with_timeout(slow_operation(delay=5), timeout=1)
        assert False, "Expected TimeoutError but operation completed"
    except asyncio.TimeoutError:
        print("✓ Slow operation timed out as expected")


async def test_with_timeout_propagates_exceptions():
    """Test that exceptions from the coroutine are propagated"""
    print("Testing exception propagation...")
    try:
        await with_timeout(failing_operation(), timeout=5)
        assert False, "Expected ValueError but operation completed"
    except ValueError as e:
        assert "Operation failed" in str(e)
        print("✓ Exception propagated correctly")


async def test_with_upload_timeout():
    """Test upload timeout wrapper uses correct timeout"""
    print("Testing upload timeout wrapper...")
    result = await with_upload_timeout(fast_operation())
    assert result == "success"
    print("✓ Upload timeout wrapper works correctly")


async def test_with_api_timeout():
    """Test API timeout wrapper uses correct timeout"""
    print("Testing API timeout wrapper...")
    result = await with_api_timeout(fast_operation())
    assert result == "success"
    print("✓ API timeout wrapper works correctly")


async def test_with_heavy_query_timeout():
    """Test heavy query timeout wrapper uses correct timeout"""
    print("Testing heavy query timeout wrapper...")
    result = await with_heavy_query_timeout(fast_operation())
    assert result == "success"
    print("✓ Heavy query timeout wrapper works correctly")


def test_get_timeout_for_operation():
    """Test that get_timeout_for_operation returns correct timeouts"""
    print("Testing get_timeout_for_operation...")
    assert get_timeout_for_operation('upload') == UPLOAD_TIMEOUT_SECONDS
    assert get_timeout_for_operation('api') == EXTERNAL_API_TIMEOUT_SECONDS
    assert get_timeout_for_operation('heavy') == HEAVY_QUERY_TIMEOUT_SECONDS
    assert get_timeout_for_operation('default') == DEFAULT_TIMEOUT_SECONDS
    assert get_timeout_for_operation('unknown') == DEFAULT_TIMEOUT_SECONDS
    print("✓ get_timeout_for_operation returns correct values")


async def test_simulated_file_upload():
    """Test simulated file upload with timeout"""
    print("Testing simulated file upload...")
    
    async def simulate_file_upload(size_mb: int):
        # Simulate upload time based on file size (0.5s per MB)
        await asyncio.sleep(size_mb * 0.5)
        return f"uploaded {size_mb}MB"
    
    # Small file should succeed
    result = await with_upload_timeout(simulate_file_upload(2))
    assert result == "uploaded 2MB"
    print("✓ Small file upload succeeded")


async def test_multiple_concurrent_operations():
    """Test that multiple timeouts can be used concurrently"""
    print("Testing multiple concurrent operations...")
    results = await asyncio.gather(
        with_timeout(fast_operation(), timeout=1),
        with_timeout(fast_operation(), timeout=2),
        with_timeout(fast_operation(), timeout=3),
    )
    assert all(r == "success" for r in results)
    print("✓ Multiple concurrent operations completed successfully")


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("REQUEST TIMEOUT UTILITY TESTS")
    print("=" * 60)
    print()
    
    # Synchronous test
    test_get_timeout_for_operation()
    print()
    
    # Async tests
    await test_with_timeout_success()
    await test_with_timeout_expires()
    await test_with_timeout_propagates_exceptions()
    print()
    
    await test_with_upload_timeout()
    await test_with_api_timeout()
    await test_with_heavy_query_timeout()
    print()
    
    await test_simulated_file_upload()
    await test_multiple_concurrent_operations()
    print()
    
    print("=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(run_all_tests())
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
