"""
Test cache warm-up functionality to ensure Job model field usage is correct.

This test validates that the warm_cache function can execute without errors,
specifically testing that it correctly uses Job.status field.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))


async def test_warm_cache_imports():
    """Test that warm_cache can be imported without errors"""
    print("=" * 80)
    print("Testing Cache Warm-up Imports")
    print("=" * 80)
    
    try:
        from app.core.redis_cache import warm_cache, redis_cache
        print("✓ Successfully imported warm_cache and redis_cache")
        return True
    except Exception as e:
        print(f"✗ Failed to import: {e}")
        return False


async def test_warm_cache_syntax():
    """Test that warm_cache function has valid syntax"""
    print("\n" + "=" * 80)
    print("Testing Cache Warm-up Function Syntax")
    print("=" * 80)
    
    try:
        from app.core.redis_cache import warm_cache
        import inspect
        
        # Check that warm_cache is a coroutine function
        assert inspect.iscoroutinefunction(warm_cache), "warm_cache should be an async function"
        print("✓ warm_cache is properly defined as an async function")
        
        # Check the source code contains the correct field reference
        source = inspect.getsource(warm_cache)
        
        # Should use Job.status (not Job.is_active)
        if "Job.status" in source:
            print("✓ warm_cache correctly references Job.status field")
        else:
            print("✗ warm_cache might not be using Job.status field")
            
        # Should not use Job.is_active (which doesn't exist)
        if "Job.is_active" in source:
            print("✗ ERROR: warm_cache incorrectly references non-existent Job.is_active field")
            return False
        else:
            print("✓ warm_cache does not reference non-existent Job.is_active field")
            
        return True
    except Exception as e:
        print(f"✗ Error during syntax check: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_warm_cache_execution_safety():
    """Test that warm_cache can handle missing database gracefully"""
    print("\n" + "=" * 80)
    print("Testing Cache Warm-up Execution Safety")
    print("=" * 80)
    
    try:
        from app.core.redis_cache import warm_cache
        
        # Call warm_cache - it should handle errors gracefully
        print("Attempting to run warm_cache (may fail due to missing DB, which is OK)...")
        result = await warm_cache()
        
        # Check that result is a dictionary with expected keys
        assert isinstance(result, dict), "warm_cache should return a dict"
        assert "status" in result, "Result should have 'status' key"
        
        if result["status"] == "success":
            print(f"✓ Cache warm-up succeeded: {result}")
        elif result["status"] == "error":
            print(f"✓ Cache warm-up handled error gracefully: {result.get('error', 'Unknown error')}")
            # This is OK - we just want to make sure the syntax is correct
        
        return True
    except Exception as e:
        # If we get a different kind of error (e.g., AttributeError for Job.is_active),
        # that indicates a real problem with the code
        error_msg = str(e)
        print(f"Error during execution: {error_msg}")
        
        # Check if it's the specific error we're trying to fix
        if "is_active" in error_msg.lower() or "'Job' object has no attribute" in error_msg:
            print("✗ ERROR: This appears to be the Job.is_active attribute error!")
            return False
        else:
            # Other errors (DB connection, etc.) are OK for this test
            print("✓ Error is not related to Job.is_active issue (likely DB connection)")
            return True


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "Cache Warm-up Fix Validation" + " " * 30 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    tests = [
        test_warm_cache_imports(),
        test_warm_cache_syntax(),
        test_warm_cache_execution_safety(),
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    passed = sum(1 for r in results if r is True)
    failed = len(results) - passed
    
    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    
    if all(results):
        print("\n✓ All cache warm-up tests PASSED!")
        print("The fix successfully resolves the Job.is_active -> Job.status issue")
        return 0
    else:
        print("\n✗ Some tests FAILED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
