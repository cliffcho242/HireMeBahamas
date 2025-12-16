"""
Tests for Redis-backed user caching functionality.

This test suite validates:
- User caching by ID, email, username, and phone
- Cache invalidation on user updates
- Fallback behavior when Redis is unavailable
- Cache hit/miss statistics
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.backend_app.core.user_cache import UserCache
from api.backend_app.models import User
from datetime import datetime


class TestUserCache:
    """Test suite for UserCache functionality."""
    
    @pytest.fixture
    def user_cache(self):
        """Create a fresh UserCache instance for testing."""
        return UserCache()
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user object for testing."""
        user = User(
            id=123,
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            role="user",
            phone="+1234567890",
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        # Set hashed_password separately to avoid it being in cache
        user.hashed_password = "hashed_password_value"
        return user
    
    @pytest.mark.asyncio
    async def test_cache_user_serialization(self, user_cache, mock_user):
        """Test that user serialization excludes sensitive data."""
        serialized = user_cache._serialize_user(mock_user)
        
        assert serialized["id"] == 123
        assert serialized["email"] == "test@example.com"
        assert serialized["username"] == "testuser"
        assert serialized["first_name"] == "Test"
        assert serialized["last_name"] == "User"
        assert "hashed_password" not in serialized
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, user_cache):
        """Test that cache keys are generated correctly."""
        assert user_cache._user_cache_key(123) == "user:id:123"
        assert user_cache._user_email_cache_key("Test@Example.com") == "user:email:test@example.com"
        assert user_cache._user_username_cache_key("TestUser") == "user:username:testuser"
        assert user_cache._user_phone_cache_key("+1234567890") == "user:phone:+1234567890"
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_cache_miss(self, user_cache, mock_user):
        """Test user lookup by ID with cache miss (database fallback)."""
        # Mock redis_cache to return None (cache miss)
        with patch("api.backend_app.core.user_cache.redis_cache") as mock_redis:
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock()
            
            # Mock database session
            mock_db = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none = AsyncMock(return_value=mock_user)
            mock_db.execute = AsyncMock(return_value=mock_result)
            
            # Execute lookup
            user = await user_cache.get_user_by_id(mock_db, 123)
            
            # Verify cache was checked
            mock_redis.get.assert_called_once()
            
            # Verify database was queried
            mock_db.execute.assert_called_once()
            
            # Verify user was cached
            assert mock_redis.set.call_count >= 1
            
            # Verify correct user returned
            assert user.id == 123
            assert user.email == "test@example.com"
            
            # Verify stats
            assert user_cache._stats["misses"] == 1
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_cache_hit(self, user_cache, mock_user):
        """Test user lookup by ID with cache hit (no database query)."""
        cached_data = {
            "id": 123,
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "role": "user",
            "is_active": True,
            "is_admin": False,
            "phone": "+1234567890",
            "location": None,
            "avatar_url": None,
            "bio": None,
            "occupation": None,
            "company_name": None,
            "skills": None,
            "experience": None,
            "education": None,
            "is_available_for_hire": None,
            "oauth_provider": None,
            "oauth_provider_id": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_login": None
        }
        
        # Mock redis_cache to return cached data
        with patch("api.backend_app.core.user_cache.redis_cache") as mock_redis:
            mock_redis.get = AsyncMock(return_value=cached_data)
            
            # Mock database session (should not be used)
            mock_db = AsyncMock()
            
            # Execute lookup
            user = await user_cache.get_user_by_id(mock_db, 123)
            
            # Verify cache was checked
            mock_redis.get.assert_called_once()
            
            # Verify database was NOT queried (cache hit)
            mock_db.execute.assert_not_called()
            
            # Verify correct user returned
            assert user.id == 123
            assert user.email == "test@example.com"
            
            # Verify stats
            assert user_cache._stats["hits"] == 1
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_cache, mock_user):
        """Test user lookup by email with two-level caching."""
        # Mock redis_cache to return user_id mapping, then full user data
        with patch("api.backend_app.core.user_cache.redis_cache") as mock_redis:
            # First call: email -> user_id mapping (returns user_id)
            # Second call: user_id -> user data (returns cached user)
            mock_redis.get = AsyncMock(side_effect=[123, user_cache._serialize_user(mock_user)])
            
            # Mock database session (should not be used with full cache hit)
            mock_db = AsyncMock()
            
            # Execute lookup
            user = await user_cache.get_user_by_email(mock_db, "test@example.com")
            
            # Verify cache was checked twice (email mapping + user data)
            assert mock_redis.get.call_count == 2
            
            # Verify correct user returned
            assert user.id == 123
            assert user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_invalidate_user(self, user_cache):
        """Test cache invalidation for a user."""
        with patch("api.backend_app.core.user_cache.redis_cache") as mock_redis:
            mock_redis.delete = AsyncMock()
            
            # Invalidate user with all identifiers
            await user_cache.invalidate_user(
                123,
                email="test@example.com",
                username="testuser",
                phone="+1234567890"
            )
            
            # Verify all cache keys were deleted
            assert mock_redis.delete.call_count == 4
            
            # Verify stats
            assert user_cache._stats["invalidations"] == 1
    
    @pytest.mark.asyncio
    async def test_get_stats(self, user_cache):
        """Test cache statistics tracking."""
        # Simulate some cache operations
        user_cache._stats["hits"] = 80
        user_cache._stats["misses"] = 20
        user_cache._stats["invalidations"] = 5
        
        stats = user_cache.get_stats()
        
        assert stats["hits"] == 80
        assert stats["misses"] == 20
        assert stats["invalidations"] == 5
        assert stats["total_lookups"] == 100
        assert stats["hit_rate_percent"] == 80.0
    
    @pytest.mark.asyncio
    async def test_cache_user_multiple_keys(self, user_cache, mock_user):
        """Test that caching a user creates multiple lookup keys."""
        with patch("api.backend_app.core.user_cache.redis_cache") as mock_redis:
            mock_redis.set = AsyncMock()
            
            # Cache the user
            await user_cache._cache_user(mock_user)
            
            # Verify multiple cache entries were created:
            # 1. user:id:123
            # 2. user:email:test@example.com
            # 3. user:username:testuser
            # 4. user:phone:+1234567890
            assert mock_redis.set.call_count == 4
    
    @pytest.mark.asyncio
    async def test_get_user_by_username(self, user_cache, mock_user):
        """Test user lookup by username."""
        with patch("api.backend_app.core.user_cache.redis_cache") as mock_redis:
            # Mock cache miss for username, then database query
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock()
            
            # Mock database session
            mock_db = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none = AsyncMock(return_value=mock_user)
            mock_db.execute = AsyncMock(return_value=mock_result)
            
            # Execute lookup
            user = await user_cache.get_user_by_username(mock_db, "testuser")
            
            # Verify correct user returned
            assert user.id == 123
            assert user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_user_by_phone(self, user_cache, mock_user):
        """Test user lookup by phone number."""
        with patch("api.backend_app.core.user_cache.redis_cache") as mock_redis:
            # Mock cache miss for phone, then database query
            mock_redis.get = AsyncMock(return_value=None)
            mock_redis.set = AsyncMock()
            
            # Mock database session
            mock_db = AsyncMock()
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none = AsyncMock(return_value=mock_user)
            mock_db.execute = AsyncMock(return_value=mock_result)
            
            # Execute lookup
            user = await user_cache.get_user_by_phone(mock_db, "+1234567890")
            
            # Verify correct user returned
            assert user.id == 123
            assert user.phone == "+1234567890"


def test_user_cache_import():
    """Test that user_cache module can be imported successfully."""
    from api.backend_app.core.user_cache import user_cache
    assert user_cache is not None
    assert isinstance(user_cache, UserCache)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
