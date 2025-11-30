"""
Test login cache functionality for fast user authentication.

This test verifies that the login cache configuration works correctly
and that cache operations function properly.
"""
import os
import sys
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def test_login_cache_timeout_configuration():
    """Test that login cache timeout is properly configured"""
    from final_backend_postgresql import CACHE_TIMEOUT_LOGIN_USER
    
    print("=" * 80)
    print("Login Cache Configuration Test")
    print("=" * 80)
    
    # Test: Login cache timeout is set to 10 minutes (600 seconds)
    print(f"\n1. Testing login cache timeout configuration...")
    print(f"   CACHE_TIMEOUT_LOGIN_USER: {CACHE_TIMEOUT_LOGIN_USER}s")
    
    assert CACHE_TIMEOUT_LOGIN_USER == 600, (
        f"Expected login cache timeout to be 600s (10 min), got {CACHE_TIMEOUT_LOGIN_USER}s"
    )
    print("   ✓ Login cache timeout configured correctly (10 minutes)")
    
    print("\n" + "=" * 80)
    print("Login cache configuration test passed!")
    print("=" * 80)


def test_login_cache_key_generation():
    """Test that login cache keys are generated correctly"""
    from final_backend_postgresql import _get_login_cache_key
    
    print("\n" + "=" * 80)
    print("Login Cache Key Generation Test")
    print("=" * 80)
    
    # Test 1: Normal email
    print("\n1. Testing normal email key generation...")
    key = _get_login_cache_key("user@example.com")
    assert key == "login_user:user@example.com", f"Unexpected key: {key}"
    print(f"   Key for 'user@example.com': {key}")
    print("   ✓ Normal email key generated correctly")
    
    # Test 2: Uppercase email should be lowercased
    print("\n2. Testing uppercase email normalization...")
    key = _get_login_cache_key("USER@EXAMPLE.COM")
    assert key == "login_user:user@example.com", f"Unexpected key: {key}"
    print(f"   Key for 'USER@EXAMPLE.COM': {key}")
    print("   ✓ Uppercase email lowercased correctly")
    
    # Test 3: Email with spaces should be trimmed
    print("\n3. Testing email with spaces...")
    key = _get_login_cache_key("  user@example.com  ")
    assert key == "login_user:user@example.com", f"Unexpected key: {key}"
    print(f"   Key for '  user@example.com  ': {key}")
    print("   ✓ Email spaces trimmed correctly")
    
    print("\n" + "=" * 80)
    print("Login cache key generation tests passed!")
    print("=" * 80)


def test_login_cache_functions_exist():
    """Test that login cache functions are properly defined"""
    from final_backend_postgresql import (
        _get_cached_user_for_login,
        _cache_user_for_login,
        _invalidate_login_cache,
        _get_login_cache_key,
    )
    
    print("\n" + "=" * 80)
    print("Login Cache Functions Test")
    print("=" * 80)
    
    # Test: All functions exist and are callable
    print("\n1. Testing that all login cache functions exist...")
    
    assert callable(_get_cached_user_for_login), "_get_cached_user_for_login should be callable"
    assert callable(_cache_user_for_login), "_cache_user_for_login should be callable"
    assert callable(_invalidate_login_cache), "_invalidate_login_cache should be callable"
    assert callable(_get_login_cache_key), "_get_login_cache_key should be callable"
    
    print("   ✓ _get_cached_user_for_login is callable")
    print("   ✓ _cache_user_for_login is callable")
    print("   ✓ _invalidate_login_cache is callable")
    print("   ✓ _get_login_cache_key is callable")
    
    print("\n" + "=" * 80)
    print("Login cache functions test passed!")
    print("=" * 80)


def test_login_cache_miss_returns_none():
    """Test that cache miss returns None when Redis is unavailable"""
    from final_backend_postgresql import _get_cached_user_for_login
    
    print("\n" + "=" * 80)
    print("Login Cache Miss Test")
    print("=" * 80)
    
    # Without Redis configured, cache should return None
    print("\n1. Testing cache miss when Redis is unavailable...")
    result = _get_cached_user_for_login("nonexistent@example.com")
    assert result is None, f"Expected None for cache miss, got {result}"
    print("   ✓ Cache miss returns None (Redis unavailable)")
    
    print("\n" + "=" * 80)
    print("Login cache miss test passed!")
    print("=" * 80)


def test_pool_configuration():
    """Test that connection pool configuration is correct"""
    from final_backend_postgresql import (
        DB_POOL_MAX_CONNECTIONS,
        DB_POOL_MIN_CONNECTIONS,
        DB_POOL_RECYCLE_SECONDS,
    )
    
    print("\n" + "=" * 80)
    print("Connection Pool Configuration Test")
    print("=" * 80)
    
    # Test 1: Max connections is 30
    print(f"\n1. Testing max connections...")
    print(f"   DB_POOL_MAX_CONNECTIONS: {DB_POOL_MAX_CONNECTIONS}")
    assert DB_POOL_MAX_CONNECTIONS == 30, (
        f"Expected max connections to be 30, got {DB_POOL_MAX_CONNECTIONS}"
    )
    print("   ✓ Max connections is 30")
    
    # Test 2: Min connections is 5
    print(f"\n2. Testing min connections...")
    print(f"   DB_POOL_MIN_CONNECTIONS: {DB_POOL_MIN_CONNECTIONS}")
    assert DB_POOL_MIN_CONNECTIONS == 5, (
        f"Expected min connections to be 5, got {DB_POOL_MIN_CONNECTIONS}"
    )
    print("   ✓ Min connections is 5")
    
    # Test 3: Pool recycle is 180 seconds
    print(f"\n3. Testing pool recycle time...")
    print(f"   DB_POOL_RECYCLE_SECONDS: {DB_POOL_RECYCLE_SECONDS}s")
    assert DB_POOL_RECYCLE_SECONDS == 180, (
        f"Expected pool recycle to be 180s, got {DB_POOL_RECYCLE_SECONDS}s"
    )
    print("   ✓ Pool recycle is 180 seconds")
    
    print("\n" + "=" * 80)
    print("Connection pool configuration tests passed!")
    print("=" * 80)


def test_connection_age_tracking_functions():
    """Test that connection age tracking functions are properly defined"""
    from final_backend_postgresql import (
        _track_connection_age,
        _clear_connection_age,
        _connection_ages,
        _connection_ages_lock,
    )
    
    print("\n" + "=" * 80)
    print("Connection Age Tracking Test")
    print("=" * 80)
    
    # Test: Functions exist
    print("\n1. Testing that age tracking functions exist...")
    assert callable(_track_connection_age), "_track_connection_age should be callable"
    assert callable(_clear_connection_age), "_clear_connection_age should be callable"
    print("   ✓ _track_connection_age is callable")
    print("   ✓ _clear_connection_age is callable")
    
    # Test: Data structures exist
    print("\n2. Testing that data structures exist...")
    assert isinstance(_connection_ages, dict), "_connection_ages should be a dict"
    print("   ✓ _connection_ages is a dict")
    print("   ✓ _connection_ages_lock exists")
    
    print("\n" + "=" * 80)
    print("Connection age tracking tests passed!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_login_cache_timeout_configuration()
        test_login_cache_key_generation()
        test_login_cache_functions_exist()
        test_login_cache_miss_returns_none()
        test_pool_configuration()
        test_connection_age_tracking_functions()
        print("\n✓ All login cache tests completed successfully")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
