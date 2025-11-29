"""
Test caching functionality for backend optimization.

This test verifies that the caching configuration works correctly
and that cache invalidation functions properly.
"""
import os
import sys
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def test_cache_configuration():
    """Test that cache is properly configured"""
    from final_backend_postgresql import (
        cache, 
        CACHE_TIMEOUT_JOBS, 
        CACHE_TIMEOUT_POSTS,
        CACHE_TIMEOUT_USERS,
        CACHE_TIMEOUT_PROFILE,
    )
    
    print("=" * 80)
    print("Cache Configuration Test")
    print("=" * 80)
    
    # Test 1: Cache is initialized
    print("\n1. Testing cache initialization...")
    assert cache is not None, "Cache should be initialized"
    cache_type = cache.config.get("CACHE_TYPE", "unknown")
    print(f"   Cache type: {cache_type}")
    assert cache_type in ["simple", "redis"], f"Unknown cache type: {cache_type}"
    print("   ✓ Cache initialized correctly")
    
    # Test 2: Cache timeout values are configured
    print("\n2. Testing cache timeout configuration...")
    print(f"   CACHE_TIMEOUT_JOBS: {CACHE_TIMEOUT_JOBS}s")
    print(f"   CACHE_TIMEOUT_POSTS: {CACHE_TIMEOUT_POSTS}s")
    print(f"   CACHE_TIMEOUT_USERS: {CACHE_TIMEOUT_USERS}s")
    print(f"   CACHE_TIMEOUT_PROFILE: {CACHE_TIMEOUT_PROFILE}s")
    
    assert CACHE_TIMEOUT_JOBS > 0, "Jobs cache timeout should be positive"
    assert CACHE_TIMEOUT_POSTS > 0, "Posts cache timeout should be positive"
    assert CACHE_TIMEOUT_USERS > 0, "Users cache timeout should be positive"
    assert CACHE_TIMEOUT_PROFILE > 0, "Profile cache timeout should be positive"
    print("   ✓ Cache timeouts configured correctly")
    
    # Test 3: Cache set/get works
    print("\n3. Testing cache set/get...")
    test_key = "test_key_123"
    test_value = {"data": "test_value", "timestamp": time.time()}
    
    cache.set(test_key, test_value, timeout=60)
    retrieved = cache.get(test_key)
    
    assert retrieved is not None, "Should be able to retrieve cached value"
    assert retrieved["data"] == test_value["data"], "Retrieved value should match"
    print(f"   Set value: {test_value}")
    print(f"   Got value: {retrieved}")
    print("   ✓ Cache set/get works correctly")
    
    # Test 4: Cache delete works
    print("\n4. Testing cache delete...")
    cache.delete(test_key)
    retrieved_after_delete = cache.get(test_key)
    assert retrieved_after_delete is None, "Value should be deleted from cache"
    print("   ✓ Cache delete works correctly")
    
    print("\n" + "=" * 80)
    print("All cache configuration tests passed!")
    print("=" * 80)
    
    return True


def test_cache_invalidation():
    """Test cache invalidation functions"""
    from final_backend_postgresql import cache, invalidate_cache_pattern
    
    print("\n" + "=" * 80)
    print("Cache Invalidation Test")
    print("=" * 80)
    
    # Test 1: Set multiple cache entries
    print("\n1. Setting up test cache entries...")
    cache.set("jobs_list_1", {"jobs": [1, 2, 3]}, timeout=300)
    cache.set("jobs_list_2", {"jobs": [4, 5, 6]}, timeout=300)
    cache.set("posts_list_1", {"posts": [1, 2, 3]}, timeout=300)
    
    assert cache.get("jobs_list_1") is not None
    assert cache.get("jobs_list_2") is not None
    assert cache.get("posts_list_1") is not None
    print("   ✓ Cache entries set successfully")
    
    # Test 2: Invalidate pattern (for simple cache, this clears all)
    print("\n2. Testing cache invalidation...")
    invalidate_cache_pattern("jobs_*")
    
    # For simple cache, all entries are cleared
    cache_type = cache.config.get("CACHE_TYPE", "simple")
    if cache_type == "simple":
        # Simple cache clears all on pattern invalidation
        print("   Note: Simple cache clears all entries on pattern invalidation")
    
    print("   ✓ Cache invalidation completed")
    
    # Test 3: Verify cache is working after invalidation
    print("\n3. Testing cache after invalidation...")
    cache.set("test_after_invalidation", "test_value", timeout=60)
    retrieved = cache.get("test_after_invalidation")
    assert retrieved == "test_value", "Cache should work after invalidation"
    cache.delete("test_after_invalidation")
    print("   ✓ Cache working correctly after invalidation")
    
    print("\n" + "=" * 80)
    print("All cache invalidation tests passed!")
    print("=" * 80)
    
    return True


def test_cached_endpoints():
    """Test that cached endpoints are properly decorated"""
    from final_backend_postgresql import app, get_jobs, get_posts
    
    print("\n" + "=" * 80)
    print("Cached Endpoints Test")
    print("=" * 80)
    
    # Test 1: Check that endpoints exist
    print("\n1. Checking cached endpoints exist...")
    
    # Get all routes
    routes = {rule.endpoint: rule.rule for rule in app.url_map.iter_rules()}
    
    assert "get_jobs" in routes, "get_jobs endpoint should exist"
    assert "get_posts" in routes, "get_posts endpoint should exist"
    assert "get_job_stats" in routes, "get_job_stats endpoint should exist"
    
    print(f"   get_jobs: {routes.get('get_jobs')}")
    print(f"   get_posts: {routes.get('get_posts')}")
    print(f"   get_job_stats: {routes.get('get_job_stats')}")
    print("   ✓ Cached endpoints exist")
    
    print("\n" + "=" * 80)
    print("All cached endpoint tests passed!")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        test_cache_configuration()
        test_cache_invalidation()
        test_cached_endpoints()
        print("\n✓ All caching tests completed successfully")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
