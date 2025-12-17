"""
Test suite for Background Tasks notification endpoint.

Tests the /api/notifications/notify endpoint which demonstrates
FastAPI's BackgroundTasks feature with zero blocking.
"""
import pytest
import asyncio
import time
from fastapi import BackgroundTasks
from unittest.mock import AsyncMock, patch


class TestBackgroundTasksNotifyEndpoint:
    """Tests for the /notify endpoint using BackgroundTasks."""

    def test_background_task_function_signature(self):
        """Test that send_notification is an async function."""
        from api.backend_app.api.notifications import send_notification
        
        # Verify it's a coroutine function
        assert asyncio.iscoroutinefunction(send_notification)

    @pytest.mark.asyncio
    async def test_send_notification_executes(self):
        """Test that send_notification background task executes successfully."""
        from api.backend_app.api.notifications import send_notification
        
        # Execute the background task directly
        start_time = time.time()
        await send_notification()
        duration = time.time() - start_time
        
        # Should take approximately 2 seconds (as per the implementation)
        assert duration >= 1.5  # Allow some variance
        assert duration <= 3.0  # Should not take too long

    def test_notify_endpoint_returns_immediately(self):
        """Test that notify endpoint returns without waiting for background task."""
        from api.backend_app.api.notifications import notify
        from fastapi import BackgroundTasks
        
        # Create mock background tasks
        bg_tasks = BackgroundTasks()
        
        # Call the endpoint - this should be fast since it doesn't await the task
        start_time = time.time()
        result = asyncio.run(notify(bg_tasks))
        duration = time.time() - start_time
        
        # Should return immediately (well under 1 second)
        assert duration < 0.5
        
        # Check response structure
        assert result["ok"] is True
        assert "message" in result
        assert "scheduled" in result["message"].lower()

    def test_notify_response_structure(self):
        """Test that notify endpoint returns the correct response structure."""
        from api.backend_app.api.notifications import notify
        from fastapi import BackgroundTasks
        
        bg_tasks = BackgroundTasks()
        result = asyncio.run(notify(bg_tasks))
        
        # Verify response has expected fields
        assert isinstance(result, dict)
        assert "ok" in result
        assert "message" in result
        assert result["ok"] is True
        assert isinstance(result["message"], str)

    @pytest.mark.asyncio
    async def test_background_task_added_to_queue(self):
        """Test that the background task is properly added to the queue."""
        from api.backend_app.api.notifications import notify, send_notification
        from fastapi import BackgroundTasks
        
        bg_tasks = BackgroundTasks()
        
        # Verify queue is empty initially
        assert len(bg_tasks.tasks) == 0
        
        # Call notify endpoint
        result = await notify(bg_tasks)
        
        # Verify task was added
        assert len(bg_tasks.tasks) == 1
        assert result["ok"] is True

    def test_endpoint_no_external_dependencies(self):
        """Test that the endpoint requires no external services (Redis, Celery)."""
        # This is a structural test - the implementation should not import
        # any external queue/worker libraries
        from api.backend_app.api.notifications import notify
        import inspect
        
        source = inspect.getsource(notify)
        
        # Should not contain references to external queue systems
        assert "celery" not in source.lower()
        assert "redis" not in source.lower()
        assert "rq" not in source.lower()
        assert "bull" not in source.lower()
        
        # Should use FastAPI's BackgroundTasks
        assert "BackgroundTasks" in source or "bg" in source

    @pytest.mark.asyncio
    async def test_background_task_logging(self):
        """Test that background task logs execution properly."""
        from api.backend_app.api.notifications import send_notification
        
        # Mock the logger to verify logging calls
        with patch('api.backend_app.api.notifications.logger') as mock_logger:
            await send_notification()
            
            # Verify logging happened
            assert mock_logger.info.call_count >= 2
            
            # Check log messages
            calls = [call.args[0] for call in mock_logger.info.call_args_list]
            assert any("Starting" in msg for msg in calls)
            assert any("sent successfully" in msg for msg in calls)

    def test_endpoint_description_accuracy(self):
        """Test that the endpoint docstring accurately describes the feature."""
        from api.backend_app.api.notifications import notify
        
        docstring = notify.__doc__.lower()
        
        # Verify key features are documented
        assert "backgroundtasks" in docstring
        assert "immediately" in docstring or "returns" in docstring
        assert "redis" in docstring or "dependencies" in docstring
        assert "render" in docstring or "serverless" in docstring

    def test_notify_endpoint_is_post_method(self):
        """Test that the notify endpoint uses POST method (as per spec)."""
        # Check if the router has the notify endpoint registered as POST
        from api.backend_app.api.notifications import router
        
        # Find the notify route
        notify_routes = [route for route in router.routes if "notify" in route.path]
        
        assert len(notify_routes) > 0
        
        # Verify it's a POST method
        notify_route = notify_routes[0]
        assert "POST" in notify_route.methods

    @pytest.mark.asyncio
    async def test_concurrent_notify_requests(self):
        """Test that multiple concurrent notify requests work correctly."""
        from api.backend_app.api.notifications import notify
        from fastapi import BackgroundTasks
        
        # Create multiple background task instances
        tasks = []
        for _ in range(5):
            bg_tasks = BackgroundTasks()
            task = notify(bg_tasks)
            tasks.append(task)
        
        # Execute all concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        
        # All should return immediately
        assert duration < 1.0
        
        # All should succeed
        assert all(result["ok"] for result in results)
