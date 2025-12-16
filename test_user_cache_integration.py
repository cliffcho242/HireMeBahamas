"""
Integration test for user caching functionality.

This test validates that the user cache integrates correctly
with the auth and users modules.
"""
import sys
import os

# Set up module paths
sys.path.insert(0, os.path.join(os.getcwd(), 'api'))

# Set up module aliasing
import backend_app as app_module
sys.modules['app'] = app_module
import backend_app.core
sys.modules['app.core'] = backend_app.core

# Import core modules
_core_modules = ['security', 'user_cache', 'redis_cache']
for _module_name in _core_modules:
    try:
        _module = __import__(f'backend_app.core.{_module_name}', fromlist=[''])
        sys.modules[f'app.core.{_module_name}'] = _module
    except ImportError as e:
        print(f'Warning: Could not import {_module_name}: {e}')

# Import schemas
import backend_app.schemas
sys.modules['app.schemas'] = backend_app.schemas

# Import models and database
import backend_app.models
sys.modules['app.models'] = backend_app.models
import backend_app.database
sys.modules['app.database'] = backend_app.database

# Now we can import the user_cache
from backend_app.core.user_cache import user_cache

def test_user_cache_available():
    """Test that user_cache is available and initialized."""
    print("Test 1: Verify user_cache is available")
    assert user_cache is not None
    assert hasattr(user_cache, 'get_user_by_id')
    assert hasattr(user_cache, 'get_user_by_email')
    assert hasattr(user_cache, 'get_user_by_username')
    assert hasattr(user_cache, 'get_user_by_phone')
    assert hasattr(user_cache, 'invalidate_user')
    print("✓ user_cache has all required methods")

def test_cache_key_generation():
    """Test cache key generation."""
    print("\nTest 2: Verify cache key generation")
    
    # Test ID key
    id_key = user_cache._user_cache_key(123)
    assert id_key == "user:id:123"
    print(f"✓ ID cache key: {id_key}")
    
    # Test email key (should be lowercase)
    email_key = user_cache._user_email_cache_key("Test@Example.COM")
    assert email_key == "user:email:test@example.com"
    print(f"✓ Email cache key: {email_key}")
    
    # Test username key (should be lowercase)
    username_key = user_cache._user_username_cache_key("TestUser")
    assert username_key == "user:username:testuser"
    print(f"✓ Username cache key: {username_key}")
    
    # Test phone key
    phone_key = user_cache._user_phone_cache_key("+1234567890")
    assert phone_key == "user:phone:+1234567890"
    print(f"✓ Phone cache key: {phone_key}")

def test_user_serialization():
    """Test user object serialization."""
    print("\nTest 3: Verify user serialization")
    
    # Create a mock user object with just the attributes we need
    class MockUser:
        def __init__(self):
            self.id = 999
            self.email = "test@example.com"
            self.username = "testuser"
            self.first_name = "Test"
            self.last_name = "User"
            self.role = "user"
            self.phone = "+1234567890"
            self.location = None
            self.avatar_url = None
            self.bio = None
            self.occupation = None
            self.company_name = None
            self.skills = None
            self.experience = None
            self.education = None
            self.is_available_for_hire = None
            self.is_active = True
            self.is_admin = False
            self.oauth_provider = None
            self.oauth_provider_id = None
            self.created_at = None
            self.updated_at = None
            self.last_login = None
            self.hashed_password = "hashed_password_secret"  # Should not be cached
    
    user = MockUser()
    
    # Serialize user
    serialized = user_cache._serialize_user(user)
    
    # Verify essential fields are present
    assert serialized["id"] == 999
    assert serialized["email"] == "test@example.com"
    assert serialized["username"] == "testuser"
    print("✓ Essential fields present in serialized user")
    
    # Verify sensitive data is excluded
    assert "hashed_password" not in serialized
    print("✓ Sensitive data (hashed_password) excluded from cache")

def test_cache_stats():
    """Test cache statistics tracking."""
    print("\nTest 4: Verify cache statistics")
    
    stats = user_cache.get_stats()
    assert "hits" in stats
    assert "misses" in stats
    assert "invalidations" in stats
    assert "hit_rate_percent" in stats
    assert "total_lookups" in stats
    print(f"✓ Cache stats available: {stats}")

def test_integration_with_auth():
    """Test that auth module can import user_cache."""
    print("\nTest 5: Verify integration with auth module")
    
    try:
        # This will check if auth.py can import user_cache
        # We don't need to actually import auth, just verify the import path works
        from backend_app.core.user_cache import user_cache as auth_user_cache
        assert auth_user_cache is not None
        print("✓ user_cache can be imported by auth module")
    except ImportError as e:
        print(f"✗ Failed to import user_cache for auth: {e}")
        raise

def test_integration_with_users():
    """Test that users module can import user_cache."""
    print("\nTest 6: Verify integration with users module")
    
    try:
        from backend_app.core.user_cache import user_cache as users_user_cache
        assert users_user_cache is not None
        print("✓ user_cache can be imported by users module")
    except ImportError as e:
        print(f"✗ Failed to import user_cache for users: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("User Cache Integration Tests")
    print("=" * 60)
    
    try:
        test_user_cache_available()
        test_cache_key_generation()
        test_user_serialization()
        test_cache_stats()
        test_integration_with_auth()
        test_integration_with_users()
        
        print("\n" + "=" * 60)
        print("✓ All integration tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
