"""
Tests for background job infrastructure.

This tests the background job processing system to ensure:
1. Jobs execute asynchronously without blocking
2. Jobs complete successfully
3. Error handling works correctly
4. Thread pool manages resources properly
"""
import time
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from backend.background_jobs import (
    run_in_background,
    submit_background_job,
    send_email_async,
    send_push_notification_async,
    fanout_feed_update_async,
    process_image_async,
)


def test_background_decorator():
    """Test that @run_in_background decorator works correctly."""
    print("\n" + "=" * 80)
    print("Test 1: Background Decorator")
    print("=" * 80)
    
    # Track execution
    results = []
    
    @run_in_background
    def slow_task(task_id: int, delay: float):
        """Simulate a slow task."""
        time.sleep(delay)
        results.append(task_id)
        return f"Task {task_id} completed"
    
    # Submit tasks
    start_time = time.time()
    futures = []
    for i in range(3):
        future = slow_task(i, 0.1)
        futures.append(future)
    
    # Check that function returns immediately (non-blocking)
    elapsed = time.time() - start_time
    print(f"✓ Submitted 3 tasks in {elapsed:.3f}s (should be < 0.05s)")
    assert elapsed < 0.05, f"Tasks should submit immediately, took {elapsed:.3f}s"
    
    # Wait for tasks to complete
    for future in futures:
        future.result(timeout=2.0)
    
    print(f"✓ All tasks completed")
    print(f"✓ Results: {results}")
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"
    
    print("✅ Background decorator test passed")


def test_submit_background_job():
    """Test submit_background_job function."""
    print("\n" + "=" * 80)
    print("Test 2: Submit Background Job")
    print("=" * 80)
    
    def compute_sum(numbers: list) -> int:
        """Simulate computation."""
        time.sleep(0.1)
        return sum(numbers)
    
    # Submit job
    start_time = time.time()
    future = submit_background_job(compute_sum, [1, 2, 3, 4, 5])
    
    # Check non-blocking
    elapsed = time.time() - start_time
    print(f"✓ Job submitted in {elapsed:.3f}s")
    assert elapsed < 0.05, "Job submission should be non-blocking"
    
    # Get result
    result = future.result(timeout=2.0)
    print(f"✓ Job completed with result: {result}")
    assert result == 15, f"Expected sum of 15, got {result}"
    
    print("✅ Submit background job test passed")


def test_error_handling():
    """Test that errors in background jobs are handled correctly."""
    print("\n" + "=" * 80)
    print("Test 3: Error Handling")
    print("=" * 80)
    
    @run_in_background
    def failing_task():
        """Task that raises an exception."""
        time.sleep(0.1)
        raise ValueError("Intentional test error")
    
    # Submit failing task
    future = failing_task()
    
    # Check that error is captured
    try:
        future.result(timeout=2.0)
        print("✗ Expected exception but got none")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        print(f"✓ Exception correctly captured: {e}")
    
    print("✅ Error handling test passed")


def test_concurrent_execution():
    """Test that multiple jobs run concurrently."""
    print("\n" + "=" * 80)
    print("Test 4: Concurrent Execution")
    print("=" * 80)
    
    @run_in_background
    def concurrent_task(task_id: int):
        """Task that runs for a fixed duration."""
        time.sleep(0.5)
        return task_id
    
    # Submit 4 tasks
    start_time = time.time()
    futures = [concurrent_task(i) for i in range(4)]
    
    # Wait for all to complete
    results = [f.result(timeout=5.0) for f in futures]
    elapsed = time.time() - start_time
    
    print(f"✓ 4 tasks completed in {elapsed:.2f}s")
    print(f"✓ Results: {results}")
    
    # If tasks ran sequentially, would take 2.0s
    # With concurrency, should take ~0.5s (all run in parallel)
    assert elapsed < 1.5, f"Tasks should run concurrently, took {elapsed:.2f}s"
    
    print("✅ Concurrent execution test passed")


def test_email_async():
    """Test async email sending (placeholder implementation)."""
    print("\n" + "=" * 80)
    print("Test 5: Async Email Sending")
    print("=" * 80)
    
    # Submit email
    future = send_email_async(
        to="test@example.com",
        subject="Test Email",
        body="This is a test email"
    )
    
    # Wait for completion
    future.result(timeout=2.0)
    print("✓ Email sent successfully (placeholder implementation)")
    
    print("✅ Async email test passed")


def test_push_notification_async():
    """Test async push notification (placeholder implementation)."""
    print("\n" + "=" * 80)
    print("Test 6: Async Push Notification")
    print("=" * 80)
    
    # Submit notification
    future = send_push_notification_async(
        user_id=123,
        title="Test Notification",
        body="This is a test notification",
        data={"type": "test"}
    )
    
    # Wait for completion
    future.result(timeout=2.0)
    print("✓ Push notification sent successfully (placeholder implementation)")
    
    print("✅ Async push notification test passed")


def test_fanout_feed_async():
    """Test async feed fan-out (placeholder implementation)."""
    print("\n" + "=" * 80)
    print("Test 7: Async Feed Fan-out")
    print("=" * 80)
    
    # Submit fan-out job
    follower_ids = list(range(1, 101))  # 100 followers
    future = fanout_feed_update_async(
        post_id=456,
        author_id=123,
        follower_ids=follower_ids
    )
    
    # Wait for completion
    future.result(timeout=2.0)
    print(f"✓ Feed fan-out completed for {len(follower_ids)} followers")
    
    print("✅ Async feed fan-out test passed")


def test_image_processing_async():
    """Test async image processing (placeholder implementation)."""
    print("\n" + "=" * 80)
    print("Test 8: Async Image Processing")
    print("=" * 80)
    
    # Submit image processing job
    future = process_image_async(
        image_path="/tmp/test_image.jpg",
        sizes=[(200, 200), (500, 500)]
    )
    
    # Wait for completion
    future.result(timeout=2.0)
    print("✓ Image processing completed (placeholder implementation)")
    
    print("✅ Async image processing test passed")


def test_performance_non_blocking():
    """Test that background jobs don't block the main thread."""
    print("\n" + "=" * 80)
    print("Test 9: Performance (Non-blocking)")
    print("=" * 80)
    
    @run_in_background
    def slow_operation():
        """Simulate a slow operation (e.g., sending email)."""
        time.sleep(1.0)
        return "done"
    
    # Time how long it takes to submit 10 slow operations
    start_time = time.time()
    futures = [slow_operation() for _ in range(10)]
    submit_time = time.time() - start_time
    
    print(f"✓ Submitted 10 slow operations in {submit_time:.3f}s")
    assert submit_time < 0.1, f"Should submit instantly, took {submit_time:.3f}s"
    
    # This demonstrates non-blocking behavior:
    # If these ran synchronously, would take 10 seconds
    # With background jobs, submission takes < 0.1 seconds
    print("✓ Main thread was not blocked")
    
    # Clean up - wait for completion (but don't count this time)
    for future in futures:
        future.result(timeout=5.0)
    
    print("✅ Performance test passed")


def run_all_tests():
    """Run all background job tests."""
    print("\n" + "=" * 80)
    print("HireMeBahamas Background Jobs Test Suite")
    print("=" * 80)
    
    tests = [
        test_background_decorator,
        test_submit_background_job,
        test_error_handling,
        test_concurrent_execution,
        test_email_async,
        test_push_notification_async,
        test_fanout_feed_async,
        test_image_processing_async,
        test_performance_non_blocking,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ Test failed: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Test crashed: {test.__name__}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
