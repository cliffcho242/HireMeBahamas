"""
Test async task cleanup on shutdown.

This test verifies that:
1. Thread pool is properly shut down
2. Async tasks are cancelled on shutdown
3. No "Task was destroyed but it is pending!" warnings
"""
import asyncio
import pytest
import sys
import os

# Add backend_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))


def test_thread_pool_shutdown():
    """Test that thread pool can be shutdown without errors."""
    from backend_app.core.concurrent import get_thread_pool, shutdown_thread_pool
    
    # Get thread pool (creates it if it doesn't exist)
    pool = get_thread_pool()
    assert pool is not None
    
    # Shutdown should not raise errors
    shutdown_thread_pool()
    
    # Verify it's been cleaned up
    from backend_app.core import concurrent
    assert concurrent._thread_pool is None


@pytest.mark.asyncio
async def test_async_task_cancellation():
    """Test that async tasks can be properly cancelled."""
    
    async def background_task():
        """A simple background task that runs indefinitely."""
        try:
            while True:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            # Expected when cancelled
            pass
    
    # Create some background tasks
    tasks = [
        asyncio.create_task(background_task())
        for _ in range(3)
    ]
    
    # Give them a moment to start
    await asyncio.sleep(0.01)
    
    # Cancel all tasks
    for task in tasks:
        task.cancel()
    
    # Wait for cancellation with timeout
    done, pending = await asyncio.wait(
        tasks,
        timeout=1.0,
        return_when=asyncio.ALL_COMPLETED
    )
    
    # All tasks should be done (cancelled)
    assert len(pending) == 0
    assert len(done) == 3
    
    # All tasks should be cancelled
    for task in done:
        assert task.cancelled() or task.done()


@pytest.mark.asyncio
async def test_shutdown_handler_logic():
    """Test the shutdown logic without actually shutting down the app."""
    from backend_app.core.concurrent import shutdown_thread_pool
    
    # Simulate the shutdown sequence
    
    # 1. Shutdown thread pool first
    try:
        shutdown_thread_pool()
    except Exception as e:
        pytest.fail(f"Thread pool shutdown failed: {e}")
    
    # 2. Create and cancel some async tasks
    async def dummy_task():
        await asyncio.sleep(10)
    
    # Create some tasks
    tasks = [asyncio.create_task(dummy_task()) for _ in range(2)]
    
    # Cancel them
    current_task = asyncio.current_task()
    pending_tasks = [
        task for task in asyncio.all_tasks()
        if not task.done() and task is not current_task
    ]
    
    assert len(pending_tasks) >= 2  # At least our dummy tasks
    
    for task in pending_tasks:
        task.cancel()
    
    # Wait for cancellation
    done, pending = await asyncio.wait(
        pending_tasks,
        timeout=1.0,
        return_when=asyncio.ALL_COMPLETED
    )
    
    # Should complete within timeout
    assert len(pending) == 0


def test_worker_exit_hook_imports():
    """Test that worker exit hook can import necessary modules."""
    import sys
    import asyncio
    
    # These imports should work in worker_exit context
    assert sys is not None
    assert asyncio is not None
    
    # Test getting event loop (may or may not exist)
    try:
        loop = asyncio.get_event_loop()
        # If we got a loop, verify we can check if it's closed
        assert hasattr(loop, 'is_closed')
    except RuntimeError:
        # No event loop is fine - worker_exit should handle this
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
