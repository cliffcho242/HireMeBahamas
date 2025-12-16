#!/usr/bin/env python3
"""
Test to verify that performance functions handle None engine correctly.

This test validates that when get_engine() returns None (due to invalid DATABASE_URL),
the performance functions handle it gracefully without raising AttributeError.
"""

import asyncio
import os
import sys
from unittest.mock import patch

# Set up test environment with invalid DATABASE_URL that will cause get_engine() to return None
os.environ['ENVIRONMENT'] = 'production'  # Use production to get placeholder URL
os.environ['DATABASE_URL'] = 'invalid://url'  # Invalid URL to trigger None return

# Import after setting environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


async def test_none_engine_handling():
    """Test that performance functions handle None engine gracefully."""
    print("Test: None Engine Handling")
    print("=" * 70)
    
    from app.core import performance
    
    # Mock get_engine to return None
    with patch('app.core.performance.get_engine', return_value=None):
        print("\n1. Testing create_performance_indexes()...")
        try:
            result = await performance.create_performance_indexes()
            assert result is False, "Expected False when engine is None"
            print("   ✓ create_performance_indexes() handled None engine correctly")
        except AttributeError as e:
            print(f"   ✗ AttributeError raised: {e}")
            raise
        
        print("\n2. Testing warmup_database_connections()...")
        try:
            result = await performance.warmup_database_connections()
            assert result is False, "Expected False when engine is None"
            print("   ✓ warmup_database_connections() handled None engine correctly")
        except AttributeError as e:
            print(f"   ✗ AttributeError raised: {e}")
            raise
        
        print("\n3. Testing optimize_postgres_settings()...")
        try:
            result = await performance.optimize_postgres_settings()
            assert result is False, "Expected False when engine is None"
            print("   ✓ optimize_postgres_settings() handled None engine correctly")
        except AttributeError as e:
            print(f"   ✗ AttributeError raised: {e}")
            raise
        
        print("\n4. Testing analyze_query_performance()...")
        try:
            result = await performance.analyze_query_performance()
            assert result is None, "Expected None when engine is None"
            print("   ✓ analyze_query_performance() handled None engine correctly")
        except AttributeError as e:
            print(f"   ✗ AttributeError raised: {e}")
            raise
        
        print("\n5. Testing run_all_performance_optimizations()...")
        try:
            # This should not raise any exception
            await performance.run_all_performance_optimizations()
            print("   ✓ run_all_performance_optimizations() handled None engine correctly")
        except AttributeError as e:
            print(f"   ✗ AttributeError raised: {e}")
            raise
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - No AttributeError: 'NoneType' object has no attribute 'begin'")
    print("=" * 70)


async def main():
    """Run all tests."""
    try:
        await test_none_engine_handling()
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
