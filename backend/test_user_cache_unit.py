"""
Unit tests for user cache module without database dependency.

Tests the caching logic and configuration without needing a live database.
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))


def test_user_cache_configuration():
    """Test that user cache configuration is correct."""
    from app.core.user_cache import USER_CACHE_TTL
    
    print("=" * 80)
    print("User Cache Configuration Test")
    print("=" * 80)
    
    print("\n1. Testing cache TTL configuration...")
    print(f"   USER_CACHE_TTL: {USER_CACHE_TTL}s")
    
    # Verify TTL is 300 seconds (5 minutes) as specified in requirements
    assert USER_CACHE_TTL == 300, (
        f"Expected cache TTL to be 300s (5 min), got {USER_CACHE_TTL}s"
    )
    print("   ✓ Cache TTL configured correctly (5 minutes)")
    
    print("\n" + "=" * 80)
    print("User cache configuration test passed!")
    print("=" * 80)


def test_user_cache_imports():
    """Test that all required functions are importable."""
    print("\n" + "=" * 80)
    print("User Cache Import Test")
    print("=" * 80)
    
    print("\n1. Testing imports...")
    
    try:
        from app.core.user_cache import (
            get_user,
            invalidate_user_cache,
            get_users_batch,
            USER_CACHE_TTL
        )
        print("   ✓ Successfully imported get_user")
        print("   ✓ Successfully imported invalidate_user_cache")
        print("   ✓ Successfully imported get_users_batch")
        print("   ✓ Successfully imported USER_CACHE_TTL")
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        raise
    
    print("\n" + "=" * 80)
    print("User cache import test passed!")
    print("=" * 80)


def test_serialization_functions():
    """Test user serialization/deserialization functions."""
    print("\n" + "=" * 80)
    print("User Serialization Test")
    print("=" * 80)
    
    print("\n1. Testing serialization functions exist...")
    
    try:
        from app.core.user_cache import _serialize_user, _deserialize_user
        print("   ✓ _serialize_user function exists")
        print("   ✓ _deserialize_user function exists")
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        raise
    
    print("\n" + "=" * 80)
    print("User serialization test passed!")
    print("=" * 80)


def test_auth_integration():
    """Test that auth.py properly imports user cache functions."""
    print("\n" + "=" * 80)
    print("Auth Integration Test")
    print("=" * 80)
    
    print("\n1. Testing auth.py imports user_cache...")
    
    try:
        # This will fail if the import is wrong
        from app.api import auth
        print("   ✓ auth module loaded successfully")
        
        # Check if get_user is imported
        import inspect
        source = inspect.getsource(auth)
        assert "from app.core.user_cache import get_user" in source or \
               "from app.core.user_cache import get_user," in source, \
               "get_user should be imported in auth.py"
        print("   ✓ get_user is imported in auth.py")
        
        # Check if invalidate_user_cache is imported
        assert "invalidate_user_cache" in source, \
               "invalidate_user_cache should be imported in auth.py"
        print("   ✓ invalidate_user_cache is imported in auth.py")
        
    except Exception as e:
        print(f"   ✗ Integration check failed: {e}")
        raise
    
    print("\n" + "=" * 80)
    print("Auth integration test passed!")
    print("=" * 80)


def test_users_integration():
    """Test that users.py properly imports user cache functions."""
    print("\n" + "=" * 80)
    print("Users Integration Test")
    print("=" * 80)
    
    print("\n1. Testing users.py imports user_cache...")
    
    try:
        # This will fail if the import is wrong
        from app.api import users
        print("   ✓ users module loaded successfully")
        
        # Check if get_cached_user is imported
        import inspect
        source = inspect.getsource(users)
        assert "from app.core.user_cache import" in source, \
               "user_cache functions should be imported in users.py"
        print("   ✓ user_cache functions are imported in users.py")
        
        # Check if get_cached_user is actually used
        assert "get_cached_user" in source, \
               "get_cached_user should be used in users.py"
        print("   ✓ get_cached_user is used in users.py")
        
    except Exception as e:
        print(f"   ✗ Integration check failed: {e}")
        raise
    
    print("\n" + "=" * 80)
    print("Users integration test passed!")
    print("=" * 80)


def main():
    """Run all unit tests."""
    try:
        test_user_cache_configuration()
        test_user_cache_imports()
        test_serialization_functions()
        test_auth_integration()
        test_users_integration()
        print("\n" + "=" * 80)
        print("✓ All unit tests passed!")
        print("=" * 80)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
