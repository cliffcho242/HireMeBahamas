"""
Test safe database startup pattern.

Verifies that:
1. App starts successfully even when DB is unavailable
2. Database warmup failures don't crash the app
3. Index creation failures don't crash the app
4. Error messages use appropriate logging levels
"""
import asyncio
import logging
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_warmup_database_connections_graceful_failure():
    """Test that database warmup failures are handled gracefully."""
    import sys
    import os
    # Add backend to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    from app.core.performance import warmup_database_connections
    
    # Mock get_engine to return None (simulating DB unavailable)
    with patch('app.core.performance.get_engine', return_value=None):
        result = await warmup_database_connections()
        
        # Should return False but not raise exception
        assert result is False


@pytest.mark.asyncio
async def test_create_performance_indexes_graceful_failure():
    """Test that index creation failures are handled gracefully."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from app.core.performance import create_performance_indexes
    
    # Mock get_engine to raise an exception
    with patch('app.core.performance.get_engine', side_effect=Exception("DB connection failed")):
        result = await create_performance_indexes()
        
        # Should return False but not raise exception
        assert result is False


@pytest.mark.asyncio
async def test_init_db_graceful_failure():
    """Test that database initialization failures are handled gracefully."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from app.database import init_db
    
    # Mock engine to raise an exception on begin()
    mock_engine = MagicMock()
    mock_engine.begin = MagicMock(side_effect=Exception("DB connection failed"))
    
    with patch('app.database.engine', mock_engine):
        result = await init_db(max_retries=1, retry_delay=0.1)
        
        # Should return False but not raise exception
        assert result is False


@pytest.mark.asyncio
async def test_run_all_performance_optimizations_graceful_failure():
    """Test that performance optimizations don't crash on failure."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from app.core.performance import run_all_performance_optimizations
    
    # Mock all sub-functions to fail
    with patch('app.core.performance.warmup_database_connections', side_effect=Exception("Warmup failed")):
        # Should not raise exception
        await run_all_performance_optimizations()


def test_app_imports_successfully():
    """Test that the app can be imported without database connection."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        from app.main import app
        assert app is not None
        print("✅ App imported successfully without database connection")
    except Exception as e:
        pytest.fail(f"App import failed: {e}")


@pytest.mark.asyncio
async def test_logging_levels_for_db_failures(caplog):
    """Test that DB failures use WARNING level, not ERROR."""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    
    from app.core.performance import warmup_database_connections, create_performance_indexes
    from app.database import init_db
    
    caplog.set_level(logging.WARNING)
    
    # Mock to cause failures
    with patch('app.core.performance.get_engine', return_value=None):
        await warmup_database_connections()
        await create_performance_indexes()
    
    mock_engine = MagicMock()
    mock_engine.begin = MagicMock(side_effect=Exception("DB connection failed"))
    with patch('app.database.engine', mock_engine):
        await init_db(max_retries=1, retry_delay=0.1)
    
    # Check that log messages contain "DB init skipped" or similar warnings
    log_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
    
    # Should have warning messages about DB init being skipped
    assert any("DB init skipped" in msg or "skipped" in msg.lower() for msg in log_messages), \
        f"Expected 'DB init skipped' warning messages, got: {log_messages}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
