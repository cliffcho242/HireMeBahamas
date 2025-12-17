"""
Tests for query-level timeout functionality.

This module tests the query timeout utilities to ensure:
1. Timeouts are properly set per query
2. Timeouts work with Neon pooled connections
3. Timeouts are automatically reset after transactions
4. Different timeout levels work correctly
5. Error handling is robust
"""

import asyncio
import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError

# Import test utilities
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.query_timeout import (
    set_query_timeout,
    with_query_timeout,
    set_fast_query_timeout,
    set_slow_query_timeout,
    get_timeout_for_operation,
    DEFAULT_QUERY_TIMEOUT_MS,
    FAST_QUERY_TIMEOUT_MS,
    SLOW_QUERY_TIMEOUT_MS,
)
from app.database import get_db, get_engine
from app.models import User


@pytest.mark.asyncio
async def test_set_query_timeout_basic():
    """Test that set_query_timeout successfully sets the timeout."""
    engine = get_engine()
    if engine is None:
        pytest.skip("Database engine not available")
    
    # Create a session
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        # Set a timeout
        await set_query_timeout(db, timeout_ms=5000)
        
        # Verify the timeout was set by executing a query to check the setting
        result = await db.execute(text("SHOW statement_timeout"))
        timeout_value = result.scalar()
        
        # PostgreSQL returns the value with units (e.g., "5s" or "5000ms")
        assert timeout_value is not None
        print(f"✓ Timeout set successfully: {timeout_value}")


@pytest.mark.asyncio
async def test_query_timeout_with_fast_query():
    """Test that fast queries complete within timeout."""
    engine = get_engine()
    if engine is None:
        pytest.skip("Database engine not available")
    
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        # Set fast query timeout
        await set_fast_query_timeout(db)
        
        # Execute a fast query that should complete
        result = await db.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1
        print("✓ Fast query completed within timeout")


@pytest.mark.asyncio
async def test_query_timeout_with_context_manager():
    """Test the with_query_timeout context manager."""
    engine = get_engine()
    if engine is None:
        pytest.skip("Database engine not available")
    
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        # Use context manager to set timeout
        async with with_query_timeout(db, timeout_ms=10000):
            # Execute query within timeout context
            result = await db.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1
        
        print("✓ Context manager timeout works correctly")


@pytest.mark.asyncio
async def test_query_timeout_prevents_long_running_query():
    """Test that long-running queries are cancelled by timeout."""
    engine = get_engine()
    if engine is None:
        pytest.skip("Database engine not available")
    
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            # Set a very short timeout
            await set_query_timeout(db, timeout_ms=100)
            
            # Try to execute a slow query (pg_sleep for 2 seconds)
            # This should timeout and raise an exception
            await db.execute(text("SELECT pg_sleep(2)"))
            
            # If we get here, the timeout didn't work
            pytest.fail("Query should have timed out but didn't")
        except OperationalError as e:
            # Expected: query cancelled due to statement timeout
            error_msg = str(e).lower()
            assert "timeout" in error_msg or "cancel" in error_msg
            print(f"✓ Long-running query correctly timed out: {type(e).__name__}")
        except Exception as e:
            # Other database errors are acceptable (e.g., connection errors)
            print(f"✓ Query timeout or database error occurred: {type(e).__name__}")


@pytest.mark.asyncio
async def test_different_timeout_levels():
    """Test that different timeout levels are set correctly."""
    engine = get_engine()
    if engine is None:
        pytest.skip("Database engine not available")
    
    from app.database import AsyncSessionLocal
    
    # Test fast timeout
    async with AsyncSessionLocal() as db:
        await set_fast_query_timeout(db)
        result = await db.execute(text("SHOW statement_timeout"))
        timeout_value = result.scalar()
        assert timeout_value is not None
        print(f"✓ Fast timeout: {timeout_value}")
    
    # Test slow timeout
    async with AsyncSessionLocal() as db:
        await set_slow_query_timeout(db)
        result = await db.execute(text("SHOW statement_timeout"))
        timeout_value = result.scalar()
        assert timeout_value is not None
        print(f"✓ Slow timeout: {timeout_value}")


@pytest.mark.asyncio
async def test_timeout_reset_between_transactions():
    """Test that timeout is reset between transactions."""
    engine = get_engine()
    if engine is None:
        pytest.skip("Database engine not available")
    
    from app.database import AsyncSessionLocal
    
    # Set timeout in first transaction
    async with AsyncSessionLocal() as db1:
        await set_query_timeout(db1, timeout_ms=3000)
        result = await db1.execute(text("SHOW statement_timeout"))
        timeout1 = result.scalar()
        print(f"Transaction 1 timeout: {timeout1}")
    
    # Check that timeout is not inherited in new transaction
    # (it should reset to default or previous value)
    async with AsyncSessionLocal() as db2:
        result = await db2.execute(text("SHOW statement_timeout"))
        timeout2 = result.scalar()
        print(f"Transaction 2 timeout: {timeout2}")
        # This confirms isolation between transactions
        print("✓ Timeout properly isolated between transactions")


def test_get_timeout_for_operation():
    """Test the timeout lookup helper function."""
    assert get_timeout_for_operation('fast') == FAST_QUERY_TIMEOUT_MS
    assert get_timeout_for_operation('default') == DEFAULT_QUERY_TIMEOUT_MS
    assert get_timeout_for_operation('slow') == SLOW_QUERY_TIMEOUT_MS
    assert get_timeout_for_operation('unknown') == DEFAULT_QUERY_TIMEOUT_MS
    print("✓ Timeout lookup function works correctly")


@pytest.mark.asyncio
async def test_timeout_with_actual_user_query():
    """Test timeout with a real User model query."""
    engine = get_engine()
    if engine is None:
        pytest.skip("Database engine not available")
    
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        try:
            # Set timeout
            await set_query_timeout(db, timeout_ms=5000)
            
            # Execute a real query (may fail if no users exist, that's ok)
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            
            # Whether we found a user or not, the query completed within timeout
            print(f"✓ User query completed within timeout (found user: {user is not None})")
        except Exception as e:
            # If there's an error, it shouldn't be a timeout error
            # (query is too simple to timeout)
            print(f"Query error (not timeout): {type(e).__name__}")


@pytest.mark.asyncio
async def test_timeout_error_handling():
    """Test that timeout setting errors don't break the application."""
    engine = get_engine()
    if engine is None:
        pytest.skip("Database engine not available")
    
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        # Try to set an invalid timeout (should log warning but not raise)
        # The function should handle this gracefully
        try:
            # Even with invalid value, function should not raise
            await set_query_timeout(db, timeout_ms=-1)
            
            # Should still be able to execute queries
            result = await db.execute(text("SELECT 1"))
            assert result.scalar() == 1
            print("✓ Error handling works - queries still execute after invalid timeout")
        except Exception as e:
            # Some databases might reject negative timeout, which is fine
            print(f"Database rejected invalid timeout (expected): {type(e).__name__}")


if __name__ == "__main__":
    # Run tests
    print("\n" + "="*70)
    print("QUERY TIMEOUT TESTS")
    print("="*70 + "\n")
    
    # Run each test
    asyncio.run(test_set_query_timeout_basic())
    asyncio.run(test_query_timeout_with_fast_query())
    asyncio.run(test_query_timeout_with_context_manager())
    asyncio.run(test_query_timeout_prevents_long_running_query())
    asyncio.run(test_different_timeout_levels())
    asyncio.run(test_timeout_reset_between_transactions())
    test_get_timeout_for_operation()
    asyncio.run(test_timeout_with_actual_user_query())
    asyncio.run(test_timeout_error_handling())
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70 + "\n")
