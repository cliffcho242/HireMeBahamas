#!/usr/bin/env python3
"""
Test script to verify the socket close error fix.

This script tests that the close_db() function handles already-closed
connections gracefully without raising "Bad file descriptor" errors.
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_close_db_defensive():
    """Test that close_db handles already-closed connections gracefully."""
    from app.database import close_db, get_engine, _engine
    
    print("Testing close_db() defensive handling...")
    
    # Test 1: Close without ever initializing the engine
    print("\n1. Test closing without initialization...")
    try:
        await close_db()
        print("   ✅ close_db() succeeded without initialization")
    except Exception as e:
        print(f"   ❌ close_db() failed: {e}")
        return False
    
    # Test 2: Try to initialize engine and close it
    print("\n2. Test normal close after initialization...")
    try:
        # Force engine initialization
        engine = get_engine()
        if engine is not None:
            print("   Engine initialized successfully")
            await close_db()
            print("   ✅ close_db() succeeded after initialization")
        else:
            print("   ⚠️  Engine returned None (likely no DATABASE_URL), skipping this test")
    except Exception as e:
        print(f"   ❌ close_db() failed: {e}")
        return False
    
    # Test 3: Try to close again (should handle already-closed gracefully)
    print("\n3. Test double close (already closed)...")
    try:
        await close_db()
        print("   ✅ close_db() succeeded on already-closed engine")
    except Exception as e:
        print(f"   ❌ close_db() failed on double close: {e}")
        return False
    
    print("\n✅ All tests passed!")
    return True


async def test_core_database():
    """Test the core database module's close_db function."""
    try:
        from app.core.database import close_db as core_close_db
        
        print("\n4. Test core database close_db()...")
        await core_close_db()
        print("   ✅ core close_db() succeeded")
        return True
    except ImportError:
        print("   ⚠️  Core database module not found, skipping")
        return True
    except Exception as e:
        print(f"   ❌ core close_db() failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("="*80)
    print("Socket Close Error Fix - Test Suite")
    print("="*80)
    
    test1_passed = await test_close_db_defensive()
    test2_passed = await test_core_database()
    
    print("\n" + "="*80)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED - Socket close error fix is working correctly")
        print("="*80)
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please review the output above")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
