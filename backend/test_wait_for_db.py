"""
Tests for wait_for_db function with retry and exponential backoff.

This test suite validates that wait_for_db properly handles database
unavailability at boot time with exponential backoff.

Test Coverage:
- Successful connection on first attempt
- Retry with exponential backoff on failure
- Maximum retry limit enforcement
- Proper logging of retry attempts
- RuntimeError raised when DB never becomes ready

Author: GitHub Copilot
Date: December 2025
"""

import asyncio
import sys
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call
import pytest

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))


class TestWaitForDb:
    """Test suite for wait_for_db function."""

    def _create_mock_engine_success(self):
        """Create a mock engine that succeeds on connection."""
        
        mock_engine = MagicMock()
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock(return_value=None)
        
        # Create an async context manager
        async_ctx = AsyncMock()
        async_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
        async_ctx.__aexit__ = AsyncMock(return_value=None)
        
        # Make connect() return the async context manager
        mock_engine.connect = MagicMock(return_value=async_ctx)
        
        return mock_engine

    def _create_mock_engine_failure(self, error_msg="Connection failed"):
        """Create a mock engine that fails on connection."""
        
        mock_engine = MagicMock()
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock(side_effect=Exception(error_msg))
        
        # Create an async context manager
        async_ctx = AsyncMock()
        async_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
        async_ctx.__aexit__ = AsyncMock(return_value=None)
        
        # Make connect() return the async context manager
        mock_engine.connect = MagicMock(return_value=async_ctx)
        
        return mock_engine

    @pytest.mark.asyncio
    async def test_successful_connection_first_attempt(self):
        """Test that successful connection on first attempt doesn't retry."""
        from backend.app.database import wait_for_db
        
        mock_engine = self._create_mock_engine_success()
        
        with patch('backend.app.database.get_engine', return_value=mock_engine):
            # Should complete without raising
            await wait_for_db(max_retries=5)
            
            # Verify connection was attempted once
            assert mock_engine.connect.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_connection_failure(self):
        """Test retry logic when connection fails."""
        from backend.app.database import wait_for_db
        
        # Create a mock engine that fails twice then succeeds
        call_count = [0]  # Use list to allow mutation in nested function
        
        def connect_side_effect():
            call_count[0] += 1
            mock_conn = AsyncMock()
            
            if call_count[0] <= 2:
                # Fail first two attempts
                mock_conn.execute = AsyncMock(side_effect=Exception("Connection failed"))
            else:
                # Succeed on third attempt
                mock_conn.execute = AsyncMock(return_value=None)
            
            # Create an async context manager
            async_ctx = AsyncMock()
            async_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
            async_ctx.__aexit__ = AsyncMock(return_value=None)
            
            return async_ctx
        
        mock_engine = MagicMock()
        mock_engine.connect = MagicMock(side_effect=connect_side_effect)
        
        with patch('backend.app.database.get_engine', return_value=mock_engine):
            with patch('asyncio.sleep'):  # Mock sleep to speed up test
                # Should complete after 3 attempts
                await wait_for_db(max_retries=5)
                
                # Verify connection was attempted 3 times
                assert mock_engine.connect.call_count == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff_delays(self):
        """Test that exponential backoff delays are correct."""
        from backend.app.database import wait_for_db
        
        # Mock get_engine to return a mock engine that always fails
        mock_engine = self._create_mock_engine_failure()
        
        with patch('backend.app.database.get_engine', return_value=mock_engine):
            with patch('asyncio.sleep') as mock_sleep:
                # Should fail after max_retries
                with pytest.raises(RuntimeError, match="Database never became ready"):
                    await wait_for_db(max_retries=4)
                
                # Verify sleep was called with exponential backoff
                # attempt 1: 2s, attempt 2: 4s, attempt 3: 6s
                # (no sleep after last attempt)
                expected_delays = [2, 4, 6]
                actual_delays = [call_args[0][0] for call_args in mock_sleep.call_args_list]
                assert actual_delays == expected_delays

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that RuntimeError is raised when max retries exceeded."""
        from backend.app.database import wait_for_db
        
        # Mock get_engine to return a mock engine that always fails
        mock_engine = self._create_mock_engine_failure()
        
        with patch('backend.app.database.get_engine', return_value=mock_engine):
            with patch('asyncio.sleep'):  # Mock sleep to speed up test
                # Should raise RuntimeError after max_retries
                with pytest.raises(RuntimeError) as exc_info:
                    await wait_for_db(max_retries=3)
                
                assert "Database never became ready" in str(exc_info.value)
                
                # Verify connection was attempted exactly max_retries times
                assert mock_engine.connect.call_count == 3

    @pytest.mark.asyncio
    async def test_engine_not_available(self):
        """Test behavior when engine is not available (None)."""
        from backend.app.database import wait_for_db
        
        # Mock get_engine to return None (invalid config)
        with patch('backend.app.database.get_engine', return_value=None):
            with patch('asyncio.sleep'):  # Mock sleep to speed up test
                # Should raise RuntimeError after max_retries
                with pytest.raises(RuntimeError) as exc_info:
                    await wait_for_db(max_retries=5)
                
                assert "Database never became ready" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_logging_on_retry(self, caplog):
        """Test that retry attempts are properly logged."""
        from backend.app.database import wait_for_db
        
        # Set up logging to capture warnings
        caplog.set_level(logging.WARNING)
        
        # Create a mock engine that fails once then succeeds
        call_count = [0]
        
        def connect_side_effect():
            call_count[0] += 1
            mock_conn = AsyncMock()
            
            if call_count[0] == 1:
                # Fail first attempt
                mock_conn.execute = AsyncMock(side_effect=Exception("Connection failed"))
            else:
                # Succeed on second attempt
                mock_conn.execute = AsyncMock(return_value=None)
            
            # Create an async context manager
            async_ctx = AsyncMock()
            async_ctx.__aenter__ = AsyncMock(return_value=mock_conn)
            async_ctx.__aexit__ = AsyncMock(return_value=None)
            
            return async_ctx
        
        mock_engine = MagicMock()
        mock_engine.connect = MagicMock(side_effect=connect_side_effect)
        
        with patch('backend.app.database.get_engine', return_value=mock_engine):
            with patch('asyncio.sleep'):  # Mock sleep to speed up test
                await wait_for_db(max_retries=5)
                
                # Verify warning was logged for retry
                assert any("DB not ready (attempt 1)" in record.message 
                          for record in caplog.records)

    @pytest.mark.asyncio
    async def test_logging_on_success(self, caplog):
        """Test that success is properly logged."""
        from backend.app.database import wait_for_db
        
        # Set up logging to capture info messages
        caplog.set_level(logging.INFO)
        
        # Mock get_engine to return a mock engine
        mock_engine = self._create_mock_engine_success()
        
        with patch('backend.app.database.get_engine', return_value=mock_engine):
            await wait_for_db(max_retries=5)
            
            # Verify success was logged
            assert any("Database ready" in record.message 
                      for record in caplog.records)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
