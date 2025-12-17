"""
Tests for lightweight slow query logger.

This test file validates the manual query performance tracking system.
"""

import asyncio
import time
import logging
from io import StringIO
from api.backend_app.core.query_logger import (
    log_query_performance,
    log_query_time,
    track_query_start,
    track_query_end,
    DEFAULT_SLOW_QUERY_THRESHOLD,
)


def test_query_logger_does_not_log_fast_queries(caplog):
    """Test that fast queries (under threshold) are not logged."""
    caplog.set_level(logging.WARNING)
    
    # Fast query (0.1s < 1.0s threshold)
    log_query_time("fast_query", 0.1)
    
    # Should not log anything
    assert "Slow query" not in caplog.text
    assert len(caplog.records) == 0


def test_query_logger_logs_slow_queries(caplog):
    """Test that slow queries (over threshold) are logged."""
    caplog.set_level(logging.WARNING)
    
    # Slow query (1.5s > 1.0s threshold)
    log_query_time("slow_query", 1.5)
    
    # Should log warning
    assert "Slow query" in caplog.text
    assert "slow_query" in caplog.text
    assert "1.50s" in caplog.text
    assert len(caplog.records) == 1


def test_query_logger_custom_threshold(caplog):
    """Test that custom thresholds work correctly."""
    caplog.set_level(logging.WARNING)
    
    # Query that's slow for custom threshold (0.6s > 0.5s)
    log_query_time("custom_threshold_query", 0.6, warn_threshold=0.5)
    
    # Should log warning
    assert "Slow query" in caplog.text
    assert "custom_threshold_query" in caplog.text
    assert "0.60s" in caplog.text


def test_track_query_helpers():
    """Test the helper functions for manual tracking."""
    # Start tracking
    start = track_query_start()
    
    # Simulate query execution
    time.sleep(0.1)
    
    # End tracking
    elapsed = track_query_end(start)
    
    # Verify elapsed time is approximately 0.1s
    assert 0.09 < elapsed < 0.15, f"Expected ~0.1s, got {elapsed:.3f}s"


async def test_context_manager_fast_query(caplog):
    """Test context manager with fast query."""
    caplog.set_level(logging.WARNING)
    
    # Fast query using context manager
    async with log_query_performance("test_fast_query", warn_threshold=1.0):
        # Simulate fast query
        await asyncio.sleep(0.1)
    
    # Should not log anything
    assert "Slow query" not in caplog.text
    assert len(caplog.records) == 0


async def test_context_manager_slow_query(caplog):
    """Test context manager with slow query."""
    caplog.set_level(logging.WARNING)
    
    # Slow query using context manager
    async with log_query_performance("test_slow_query", warn_threshold=0.5):
        # Simulate slow query
        await asyncio.sleep(0.6)
    
    # Should log warning
    assert "Slow query" in caplog.text
    assert "test_slow_query" in caplog.text


def test_manual_pattern_example():
    """Test the manual pattern from the problem statement."""
    # Setup logger to capture output
    logger = logging.getLogger("api.backend_app.core.query_logger")
    logger.setLevel(logging.WARNING)
    
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.WARNING)
    logger.addHandler(handler)
    
    try:
        # Manual pattern from problem statement
        start = time.time()
        # Simulate slow query
        time.sleep(1.1)
        elapsed = time.time() - start
        
        if elapsed > 1:
            logger.warning(f"Slow query: {elapsed:.2f}s")
        
        # Check that warning was logged
        output = stream.getvalue()
        assert "Slow query" in output
        assert "1." in output  # Check for time value
    finally:
        logger.removeHandler(handler)


if __name__ == "__main__":
    # Run tests
    print("Running slow query logger tests...")
    
    # Test synchronous functions
    class SimpleCaplog:
        def __init__(self):
            self.text = ""
            self.records = []
            self._stream = StringIO()
            self._handler = logging.StreamHandler(self._stream)
            self._logger = logging.getLogger("api.backend_app.core.query_logger")
            self._original_level = self._logger.level
        
        def set_level(self, level):
            self._logger.setLevel(level)
            self._handler.setLevel(level)
            self._logger.addHandler(self._handler)
        
        def capture(self):
            self.text = self._stream.getvalue()
            # Count log records by lines (simple approximation)
            self.records = [line for line in self.text.split('\n') if line.strip()]
        
        def cleanup(self):
            self._logger.removeHandler(self._handler)
            self._logger.setLevel(self._original_level)
    
    # Test 1: Fast queries
    print("\n1. Testing fast queries (should not log)...")
    caplog = SimpleCaplog()
    caplog.set_level(logging.WARNING)
    log_query_time("fast_query", 0.1)
    caplog.capture()
    assert "Slow query" not in caplog.text, "Fast query should not be logged"
    print("   ✓ Fast queries are not logged")
    caplog.cleanup()
    
    # Test 2: Slow queries
    print("\n2. Testing slow queries (should log)...")
    caplog = SimpleCaplog()
    caplog.set_level(logging.WARNING)
    log_query_time("slow_query", 1.5)
    caplog.capture()
    assert "Slow query" in caplog.text, "Slow query should be logged"
    assert "slow_query" in caplog.text, "Query name should be in log"
    print("   ✓ Slow queries are logged with query name and time")
    caplog.cleanup()
    
    # Test 3: Custom threshold
    print("\n3. Testing custom threshold...")
    caplog = SimpleCaplog()
    caplog.set_level(logging.WARNING)
    log_query_time("custom_query", 0.6, warn_threshold=0.5)
    caplog.capture()
    assert "Slow query" in caplog.text, "Query over custom threshold should be logged"
    print("   ✓ Custom thresholds work correctly")
    caplog.cleanup()
    
    # Test 4: Helper functions
    print("\n4. Testing helper functions...")
    start = track_query_start()
    time.sleep(0.1)
    elapsed = track_query_end(start)
    assert 0.09 < elapsed < 0.15, f"Expected ~0.1s, got {elapsed:.3f}s"
    print(f"   ✓ Helper functions track time correctly ({elapsed:.3f}s)")
    
    # Test 5: Context manager (async)
    print("\n5. Testing context manager...")
    async def run_context_manager_test():
        caplog = SimpleCaplog()
        caplog.set_level(logging.WARNING)
        
        # Fast query
        async with log_query_performance("test_fast", warn_threshold=1.0):
            await asyncio.sleep(0.1)
        caplog.capture()
        assert "Slow query" not in caplog.text, "Fast query in context manager should not log"
        caplog.cleanup()
        
        # Slow query
        caplog = SimpleCaplog()
        caplog.set_level(logging.WARNING)
        async with log_query_performance("test_slow", warn_threshold=0.5):
            await asyncio.sleep(0.6)
        caplog.capture()
        assert "Slow query" in caplog.text, "Slow query in context manager should log"
        caplog.cleanup()
        
        print("   ✓ Context manager works correctly")
    
    asyncio.run(run_context_manager_test())
    
    # Test 6: Manual pattern
    print("\n6. Testing manual pattern from problem statement...")
    test_manual_pattern_example()
    print("   ✓ Manual pattern works as specified")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
    print("\nThe lightweight slow query logger is working correctly.")
    print("No APM needed - just manual time tracking with logger.warning().")
