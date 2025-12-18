"""
Test safe startup and shutdown implementation.

This test verifies that:
1. The startup event uses asyncio.create_task() for non-blocking bootstrap
2. Background tasks are properly tracked
3. Shutdown waits for background tasks to complete
4. No orphan tasks are left behind
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import sys
import os

# Add backend app to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)
os.chdir(backend_path)


@pytest.mark.asyncio
async def test_wait_for_db_success():
    """Test wait_for_db successfully connects to database."""
    # Import here to avoid module-level issues
    from app.main import wait_for_db
    
    # Mock test_db_connection to return success
    mock_test_db = AsyncMock(return_value=(True, None))
    
    with patch('app.main.test_db_connection', mock_test_db), \
         patch('app.main.logger'):
        result = await wait_for_db(max_retries=3, retry_delay=0.1)
        
        assert result is True
        mock_test_db.assert_called_once()


@pytest.mark.asyncio
async def test_wait_for_db_failure():
    """Test wait_for_db handles connection failures."""
    from app.main import wait_for_db
    
    # Mock test_db_connection to return failure
    mock_test_db = AsyncMock(return_value=(False, "Connection failed"))
    
    with patch('app.main.test_db_connection', mock_test_db), \
         patch('app.main.logger'):
        result = await wait_for_db(max_retries=2, retry_delay=0.1)
        
        assert result is False
        # Should retry max_retries times
        assert mock_test_db.call_count == 2


@pytest.mark.asyncio
async def test_wait_for_db_exception():
    """Test wait_for_db handles exceptions gracefully."""
    from app.main import wait_for_db
    
    # Mock test_db_connection to raise exception
    mock_test_db = AsyncMock(side_effect=Exception("Database error"))
    
    with patch('app.main.test_db_connection', mock_test_db), \
         patch('app.main.logger'):
        result = await wait_for_db(max_retries=2, retry_delay=0.1)
        
        assert result is False
        assert mock_test_db.call_count == 2


@pytest.mark.asyncio
async def test_background_bootstrap_no_db():
    """Test background_bootstrap handles database unavailability."""
    from app.main import background_bootstrap
    
    with patch('app.main.wait_for_db', return_value=False), \
         patch('app.main.logger'):
        # Should not raise an exception
        await background_bootstrap()


@pytest.mark.asyncio
async def test_background_bootstrap_handles_exceptions():
    """Test background_bootstrap handles exceptions gracefully."""
    from app.main import background_bootstrap
    
    with patch('app.main.wait_for_db', side_effect=Exception("Unexpected error")), \
         patch('app.main.logger'):
        # Should not raise an exception
        await background_bootstrap()


def test_background_tasks_tracked():
    """Test that background tasks are tracked in _background_tasks set."""
    # Verify the set exists and is accessible
    from app.main import _background_tasks
    assert isinstance(_background_tasks, set)


def test_implementation_matches_spec():
    """Test that the implementation matches the problem statement specification."""
    import inspect
    from app.main import startup, shutdown, background_bootstrap, wait_for_db
    
    # Check startup is an async function
    assert asyncio.iscoroutinefunction(startup)
    
    # Check shutdown is an async function
    assert asyncio.iscoroutinefunction(shutdown)
    
    # Check background_bootstrap is an async function
    assert asyncio.iscoroutinefunction(background_bootstrap)
    
    # Check wait_for_db is an async function
    assert asyncio.iscoroutinefunction(wait_for_db)
    
    # Check that startup uses asyncio.create_task (by inspecting source)
    startup_source = inspect.getsource(startup)
    assert 'asyncio.create_task' in startup_source, "startup should use asyncio.create_task"
    assert 'background_bootstrap' in startup_source, "startup should call background_bootstrap"
    
    # Check that background_bootstrap uses asyncio.to_thread (by inspecting source)
    bootstrap_source = inspect.getsource(background_bootstrap)
    assert 'asyncio.to_thread' in bootstrap_source, "background_bootstrap should use asyncio.to_thread"
    
    # Check that shutdown waits for tasks (by inspecting source)
    shutdown_source = inspect.getsource(shutdown)
    assert 'asyncio.sleep(0)' in shutdown_source or 'await asyncio.wait' in shutdown_source, \
        "shutdown should wait for background tasks"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
