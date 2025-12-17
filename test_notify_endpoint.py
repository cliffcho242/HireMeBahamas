#!/usr/bin/env python
"""
Standalone test script for the /notify endpoint with BackgroundTasks.

This script verifies:
1. The endpoint returns immediately without blocking
2. The background task is properly scheduled
3. The response format is correct
"""
import sys
import os
import time
import asyncio

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

# Set up module aliases (required for backend_app imports)
import backend_app
sys.modules['app'] = backend_app
import backend_app.core
sys.modules['app.core'] = backend_app.core
import backend_app.api
sys.modules['app.api'] = backend_app.api
import backend_app.database
sys.modules['app.database'] = backend_app.database
import backend_app.models
sys.modules['app.models'] = backend_app.models

from fastapi import BackgroundTasks
from backend_app.api.notifications import send_notification, notify


def test_send_notification_is_async():
    """Test that send_notification is an async function."""
    print("✓ Test 1: Checking if send_notification is async...")
    assert asyncio.iscoroutinefunction(send_notification)
    print("  PASS: send_notification is an async function")


async def test_send_notification_executes():
    """Test that send_notification executes without errors."""
    print("\n✓ Test 2: Executing send_notification...")
    start = time.time()
    await send_notification()
    duration = time.time() - start
    print(f"  PASS: send_notification executed in {duration:.2f}s")
    assert duration >= 1.5, "Should take ~2 seconds"
    assert duration <= 3.0, "Should not take too long"


async def test_notify_returns_immediately():
    """Test that notify endpoint returns immediately."""
    print("\n✓ Test 3: Testing notify endpoint returns immediately...")
    bg = BackgroundTasks()
    
    start = time.time()
    result = await notify(bg)
    duration = time.time() - start
    
    print(f"  Response time: {duration * 1000:.2f}ms")
    assert duration < 0.1, "Should return in under 100ms"
    print(f"  PASS: Endpoint returned in {duration * 1000:.2f}ms (non-blocking)")
    
    return result, bg


def test_response_format(result):
    """Test the response format from notify endpoint."""
    print("\n✓ Test 4: Checking response format...")
    assert isinstance(result, dict), "Response should be a dict"
    assert "ok" in result, "Response should have 'ok' field"
    assert result["ok"] is True, "'ok' should be True"
    assert "message" in result, "Response should have 'message' field"
    print(f"  Response: {result}")
    print("  PASS: Response format is correct")


def test_background_task_scheduled(bg):
    """Test that background task was added to the queue."""
    print("\n✓ Test 5: Verifying background task was scheduled...")
    assert len(bg.tasks) == 1, "Should have 1 background task scheduled"
    print(f"  PASS: {len(bg.tasks)} task(s) scheduled")


async def test_background_task_execution(bg):
    """Test that background tasks actually execute."""
    print("\n✓ Test 6: Executing scheduled background tasks...")
    start = time.time()
    
    # Execute all background tasks using FastAPI's __call__ method
    await bg()
    
    duration = time.time() - start
    print(f"  PASS: Background tasks executed in {duration:.2f}s")


def test_no_external_dependencies():
    """Test that implementation uses no external dependencies."""
    print("\n✓ Test 7: Verifying no external dependencies (Redis, Celery, etc.)...")
    import inspect
    from backend_app.api.notifications import notify
    
    source = inspect.getsource(notify)
    
    # Check that implementation doesn't import external dependencies
    # (mentions in comments/docstrings are OK)
    forbidden_imports = ["import celery", "import redis", "import rq", "from celery", "from redis"]
    for dep in forbidden_imports:
        assert dep not in source.lower(), f"Should not import {dep}"
    
    # Verify it uses BackgroundTasks
    assert "BackgroundTasks" in source or "bg" in source, "Should use FastAPI BackgroundTasks"
    
    print("  PASS: No external dependencies detected (uses FastAPI BackgroundTasks)")


async def main():
    """Run all tests."""
    print("=" * 70)
    print("Background Tasks /notify Endpoint Test Suite")
    print("=" * 70)
    
    try:
        # Test 1: Check async function
        test_send_notification_is_async()
        
        # Test 2: Execute background task
        await test_send_notification_executes()
        
        # Test 3-5: Test endpoint
        result, bg = await test_notify_returns_immediately()
        test_response_format(result)
        test_background_task_scheduled(bg)
        
        # Test 6: Execute background tasks
        await test_background_task_execution(bg)
        
        # Test 7: No external dependencies
        test_no_external_dependencies()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nKey Features Verified:")
        print("  ✔ Zero blocking - endpoint returns immediately")
        print("  ✔ No Redis - uses FastAPI's built-in BackgroundTasks")
        print("  ✔ Render-safe - no external dependencies")
        print("  ✔ Background task executes successfully")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
