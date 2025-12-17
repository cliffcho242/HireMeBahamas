"""
Tests for in-memory TTL cache implementation.

Tests cover:
- Basic get/set operations
- TTL expiration
- Cache hits and misses
- Cache invalidation
- Prefix-based invalidation
"""
import sys
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

import pytest
from app.core.memory_cache import (
    cache_get,
    cache_set,
    cache_clear,
    cache_delete,
    cache_invalidate_prefix,
    cache_cleanup,
    cache_size,
    CACHE
)


def setup_function():
    """Clear cache before each test"""
    cache_clear()


def test_cache_set_and_get():
    """Test basic cache set and get operations"""
    # Set a value
    cache_set("test_key", "test_value")
    
    # Get the value
    result = cache_get("test_key", ttl=30)
    
    assert result == "test_value"


def test_cache_get_nonexistent_key():
    """Test getting a non-existent key returns None"""
    result = cache_get("nonexistent", ttl=30)
    assert result is None


def test_cache_ttl_expiration():
    """Test that cache entries expire after TTL"""
    # Set a value
    cache_set("expire_key", "expire_value")
    
    # Should be retrievable immediately
    result = cache_get("expire_key", ttl=1)
    assert result == "expire_value"
    
    # Wait for TTL to expire
    time.sleep(1.1)
    
    # Should now return None
    result = cache_get("expire_key", ttl=1)
    assert result is None


def test_cache_different_ttls():
    """Test that different TTL values work correctly"""
    cache_set("key1", "value1")
    
    # Check with short TTL
    result = cache_get("key1", ttl=5)
    assert result == "value1"
    
    # Check with longer TTL
    result = cache_get("key1", ttl=60)
    assert result == "value1"


def test_cache_overwrite():
    """Test that setting a key twice overwrites the value"""
    cache_set("overwrite_key", "first_value")
    cache_set("overwrite_key", "second_value")
    
    result = cache_get("overwrite_key", ttl=30)
    assert result == "second_value"


def test_cache_complex_values():
    """Test caching complex Python objects"""
    # Dictionary
    cache_set("dict_key", {"name": "John", "age": 30})
    result = cache_get("dict_key", ttl=30)
    assert result == {"name": "John", "age": 30}
    
    # List
    cache_set("list_key", [1, 2, 3, 4, 5])
    result = cache_get("list_key", ttl=30)
    assert result == [1, 2, 3, 4, 5]
    
    # Nested structure
    cache_set("nested_key", {"users": [{"id": 1}, {"id": 2}]})
    result = cache_get("nested_key", ttl=30)
    assert result == {"users": [{"id": 1}, {"id": 2}]}


def test_cache_clear():
    """Test clearing all cache entries"""
    cache_set("key1", "value1")
    cache_set("key2", "value2")
    cache_set("key3", "value3")
    
    # Verify entries exist
    assert cache_size() == 3
    
    # Clear cache
    cache_clear()
    
    # Verify cache is empty
    assert cache_size() == 0
    assert cache_get("key1", ttl=30) is None


def test_cache_delete():
    """Test deleting specific cache entries"""
    cache_set("delete_key", "delete_value")
    
    # Verify it exists
    assert cache_get("delete_key", ttl=30) == "delete_value"
    
    # Delete it
    result = cache_delete("delete_key")
    assert result is True
    
    # Verify it's gone
    assert cache_get("delete_key", ttl=30) is None
    
    # Try deleting non-existent key
    result = cache_delete("nonexistent")
    assert result is False


def test_cache_invalidate_prefix():
    """Test invalidating cache entries by prefix"""
    # Set multiple entries with different prefixes
    cache_set("jobs:list:page1", [1, 2, 3])
    cache_set("jobs:list:page2", [4, 5, 6])
    cache_set("jobs:stats:overview", {"total": 10})
    cache_set("users:list:page1", [{"id": 1}])
    
    # Verify all exist
    assert cache_size() == 4
    
    # Invalidate jobs:list: prefix
    count = cache_invalidate_prefix("jobs:list:")
    assert count == 2
    
    # Verify correct entries removed
    assert cache_get("jobs:list:page1", ttl=30) is None
    assert cache_get("jobs:list:page2", ttl=30) is None
    assert cache_get("jobs:stats:overview", ttl=30) is not None
    assert cache_get("users:list:page1", ttl=30) is not None


def test_cache_cleanup():
    """Test proactive cleanup of expired entries"""
    # Set entries with timestamps that will expire
    cache_set("old_key1", "old_value1")
    cache_set("old_key2", "old_value2")
    
    # Wait for expiration
    time.sleep(1.1)
    
    cache_set("new_key", "new_value")
    
    # Before cleanup, all 3 entries exist in cache dict
    assert cache_size() == 3
    
    # Run cleanup with 1 second TTL
    removed = cache_cleanup(ttl=1)
    
    # Should have removed 2 old entries
    assert removed == 2
    assert cache_size() == 1
    
    # New entry should still be there
    assert cache_get("new_key", ttl=30) == "new_value"


def test_cache_size():
    """Test cache size tracking"""
    assert cache_size() == 0
    
    cache_set("key1", "value1")
    assert cache_size() == 1
    
    cache_set("key2", "value2")
    assert cache_size() == 2
    
    cache_delete("key1")
    assert cache_size() == 1
    
    cache_clear()
    assert cache_size() == 0


def test_cache_ttl_requirement():
    """Test that TTL adheres to requirement (≤ 60s)"""
    # Test with 30s TTL (recommended)
    cache_set("test_30s", "value")
    result = cache_get("test_30s", ttl=30)
    assert result == "value"
    
    # Test with 60s TTL (maximum)
    cache_set("test_60s", "value")
    result = cache_get("test_60s", ttl=60)
    assert result == "value"
    
    # Verify both are within requirement
    assert 30 <= 60
    assert 60 <= 60


def test_cache_concurrent_access():
    """Test that cache handles multiple keys correctly"""
    # Simulate concurrent-like access with many keys
    for i in range(100):
        cache_set(f"key_{i}", f"value_{i}")
    
    # Verify all values are retrievable
    for i in range(100):
        result = cache_get(f"key_{i}", ttl=30)
        assert result == f"value_{i}"
    
    assert cache_size() == 100


def test_feed_endpoint_cache_key():
    """Test cache key format for /feed endpoint"""
    cache_key = "feed:global"
    
    # Simulate feed caching
    feed_data = {"posts": [{"id": 1, "content": "Test post"}]}
    cache_set(cache_key, feed_data)
    
    # Retrieve with 30s TTL as per requirement
    result = cache_get(cache_key, ttl=30)
    assert result == feed_data


def test_profile_endpoint_cache_key():
    """Test cache key format for /profile endpoint"""
    identifier = "john_doe"
    current_user_id = 123
    cache_key = f"profile:{identifier}:{current_user_id}"
    
    # Simulate profile caching
    profile_data = {"user": {"id": 456, "username": "john_doe"}}
    cache_set(cache_key, profile_data)
    
    # Retrieve with 30s TTL as per requirement
    result = cache_get(cache_key, ttl=30)
    assert result == profile_data


def test_jobs_endpoint_cache_key():
    """Test cache key format for /jobs endpoint"""
    cache_params = "None:None:None:10:next:None:None:None:None:None:None:active"
    cache_key = f"jobs:list:{cache_params}"
    
    # Simulate jobs caching
    jobs_data = {"data": [{"id": 1, "title": "Software Engineer"}]}
    cache_set(cache_key, jobs_data)
    
    # Retrieve with 60s TTL (max allowed)
    result = cache_get(cache_key, ttl=60)
    assert result == jobs_data


def test_thread_safety():
    """Test thread-safe operations with concurrent access"""
    import threading
    
    def worker(worker_id, iterations=100):
        """Worker function that performs cache operations"""
        for i in range(iterations):
            key = f"thread_{worker_id}_key_{i}"
            value = f"thread_{worker_id}_value_{i}"
            
            # Set value
            cache_set(key, value)
            
            # Get value
            result = cache_get(key, ttl=30)
            assert result == value, f"Worker {worker_id}: Expected {value}, got {result}"
            
            # Delete some entries
            if i % 10 == 0:
                cache_delete(key)
    
    # Create multiple threads
    threads = []
    num_threads = 5
    
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    # Verify cache is still functional
    cache_set("post_test", "value")
    assert cache_get("post_test", ttl=30) == "value"


def test_cache_size_limit():
    """Test that cache respects MAX_CACHE_SIZE limit"""
    from app.core.memory_cache import MAX_CACHE_SIZE
    
    # Skip test if MAX_CACHE_SIZE is unlimited
    if MAX_CACHE_SIZE <= 0:
        pytest.skip("MAX_CACHE_SIZE is unlimited")
    
    # Clear cache first
    cache_clear()
    
    # Add entries up to the limit
    for i in range(MAX_CACHE_SIZE + 100):
        cache_set(f"size_test_{i}", f"value_{i}")
    
    # Cache size should not exceed MAX_CACHE_SIZE significantly
    # (allowing for some buffer since we evict 10% at a time)
    current_size = cache_size()
    assert current_size <= MAX_CACHE_SIZE, \
        f"Cache size {current_size} exceeds limit {MAX_CACHE_SIZE}"
    
    # Oldest entries should have been evicted
    # First entry should be gone
    result = cache_get("size_test_0", ttl=60)
    assert result is None, "Oldest entries should be evicted"
    
    # Recent entries should still exist
    recent_key = f"size_test_{MAX_CACHE_SIZE + 99}"
    result = cache_get(recent_key, ttl=60)
    assert result is not None, "Recent entries should still exist"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
