#!/usr/bin/env python3
"""
Test for the performance optimization fix.

This test validates that:
1. Empty/whitespace DATABASE_URL is handled gracefully
2. Performance optimizations don't crash when database is unavailable
3. get_engine() call inside try-except blocks prevents uncaught exceptions
"""

import asyncio
import os
import sys
from unittest.mock import patch

# Set up test environment
os.environ['ENVIRONMENT'] = 'test'
os.environ['DATABASE_URL'] = '  '  # Whitespace-only URL to trigger the fix

# Import after setting environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


async def test_whitespace_url_handling():
    """Test that whitespace-only DATABASE_URL is handled correctly."""
    print("Test 1: Whitespace-only DATABASE_URL handling")
    
    # Import database module (this will process DATABASE_URL)
    from app import database
    
    # Check that DATABASE_URL was converted to placeholder
    print(f"  DATABASE_URL after processing: {database.DATABASE_URL[:50]}...")
    
    # Verify it's not empty
    assert database.DATABASE_URL, "DATABASE_URL should not be empty"
    
    # Verify it's a valid URL (starts with postgresql)
    assert database.DATABASE_URL.startswith('postgresql'), \
        "DATABASE_URL should start with 'postgresql'"
    
    print("  ✓ Whitespace-only URL handled correctly")


async def test_performance_optimizations_graceful_failure():
    """Test that performance optimizations handle database unavailability."""
    print("\nTest 2: Performance optimizations graceful failure")
    
    from app.core import performance
    
    # Run performance optimizations (should not raise exception)
    try:
        await performance.run_all_performance_optimizations()
        print("  ✓ Performance optimizations completed (or failed gracefully)")
    except Exception as e:
        print(f"  ✗ Unexpected exception: {type(e).__name__}: {e}")
        raise


async def test_individual_functions_handle_errors():
    """Test that individual performance functions handle errors."""
    print("\nTest 3: Individual performance functions error handling")
    
    from app.core import performance
    
    # Test each function individually
    functions = [
        ('warmup_database_connections', performance.warmup_database_connections),
        ('create_performance_indexes', performance.create_performance_indexes),
        ('optimize_postgres_settings', performance.optimize_postgres_settings),
    ]
    
    for name, func in functions:
        try:
            result = await func()
            print(f"  ✓ {name}: returned {result} (graceful failure expected)")
        except Exception as e:
            print(f"  ✗ {name}: raised {type(e).__name__}: {e}")
            raise


async def main():
    """Run all tests."""
    print("=" * 70)
    print("Performance Optimization Fix Tests")
    print("=" * 70)
    
    try:
        await test_whitespace_url_handling()
        await test_performance_optimizations_graceful_failure()
        await test_individual_functions_handle_errors()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ TEST FAILED: {type(e).__name__}: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
