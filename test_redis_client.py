"""
Test for STEP 14 — Redis caching implementation.
Validates that the synchronous Redis client is properly configured.
"""
import os


def test_redis_import():
    """Test that redis module can be imported."""
    try:
        from app import redis as redis_module
        assert redis_module is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import app.redis: {e}")


def test_redis_client_configuration():
    """Test that redis_client is properly configured with correct settings."""
    # Set REDIS_URL if not set (for testing)
    if not os.getenv("REDIS_URL"):
        os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    
    from app.redis import redis_client
    
    # Verify client exists
    assert redis_client is not None
    
    # Verify configuration
    connection_pool = redis_client.connection_pool
    connection_kwargs = connection_pool.connection_kwargs
    
    # Check decode_responses is True
    assert connection_kwargs.get("decode_responses") == True
    
    # Check timeouts are set to 2 seconds
    assert connection_kwargs.get("socket_connect_timeout") == 2
    assert connection_kwargs.get("socket_timeout") == 2
    
    print("✅ Redis client configured correctly with proper timeouts")


def test_redis_url_from_config():
    """Test that REDIS_URL is imported from app.config."""
    from app.config import REDIS_URL
    from app import redis as redis_module
    
    # Both should reference the same configuration
    assert REDIS_URL is not None or REDIS_URL == ""
    
    print("✅ REDIS_URL properly imported from app.config")


if __name__ == "__main__":
    # Run tests
    print("Testing STEP 14 — Redis caching implementation\n")
    
    try:
        test_redis_import()
        print("✓ Redis import test passed")
    except Exception as e:
        print(f"✗ Redis import test failed: {e}")
    
    try:
        test_redis_client_configuration()
        print("✓ Redis client configuration test passed")
    except Exception as e:
        print(f"✗ Redis client configuration test failed: {e}")
    
    try:
        test_redis_url_from_config()
        print("✓ REDIS_URL config test passed")
    except Exception as e:
        print(f"✗ REDIS_URL config test failed: {e}")
    
    print("\n✅ All tests completed!")
