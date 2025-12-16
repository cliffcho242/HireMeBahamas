"""
Test user caching functionality.

Tests the Redis-backed user cache implementation to ensure:
1. Cache hits return user data quickly
2. Cache misses query the database
3. Cache invalidation works correctly
4. Batch operations work efficiently
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))


async def test_user_cache():
    """Test user caching with get_user function."""
    from app.core.user_cache import get_user, invalidate_user_cache, USER_CACHE_TTL
    from app.core.redis_cache import redis_cache
    from app.database import AsyncSessionLocal
    from app.models import User
    from sqlalchemy import select
    
    print("=" * 80)
    print("User Cache Functionality Test")
    print("=" * 80)
    
    # Initialize Redis connection
    await redis_cache.connect()
    
    async with AsyncSessionLocal() as db:
        # Test 1: Get a user from database (should cache it)
        print("\n1. Testing initial user lookup (cache miss)...")
        result = await db.execute(select(User).limit(1))
        test_user = result.scalar_one_or_none()
        
        if not test_user:
            print("   ⚠ No users in database, skipping cache tests")
            return
        
        user_id = test_user.id
        print(f"   Found test user: id={user_id}, email={test_user.email}")
        
        # Clear cache first
        await invalidate_user_cache(user_id)
        
        # First lookup - should be cache miss
        user = await get_user(user_id, db)
        assert user is not None, "User should be found"
        assert user.id == user_id, "User ID should match"
        assert user.email == test_user.email, "User email should match"
        print(f"   ✓ User fetched from database: {user.email}")
        
        # Test 2: Get the same user again (should be cache hit)
        print(f"\n2. Testing cached user lookup (cache hit)...")
        cached_user = await get_user(user_id, db)
        assert cached_user is not None, "Cached user should be found"
        assert cached_user.id == user_id, "Cached user ID should match"
        assert cached_user.email == test_user.email, "Cached user email should match"
        print(f"   ✓ User fetched from cache: {cached_user.email}")
        
        # Test 3: Verify cache TTL configuration
        print(f"\n3. Testing cache TTL configuration...")
        print(f"   USER_CACHE_TTL: {USER_CACHE_TTL}s")
        assert USER_CACHE_TTL == 300, f"Expected cache TTL to be 300s, got {USER_CACHE_TTL}s"
        print("   ✓ Cache TTL configured correctly (5 minutes)")
        
        # Test 4: Test cache invalidation
        print(f"\n4. Testing cache invalidation...")
        await invalidate_user_cache(user_id)
        print(f"   ✓ Cache invalidated for user_id={user_id}")
        
        # After invalidation, should fetch from database again
        user_after_invalidation = await get_user(user_id, db)
        assert user_after_invalidation is not None, "User should still be found after invalidation"
        assert user_after_invalidation.id == user_id, "User ID should still match"
        print(f"   ✓ User re-fetched from database after invalidation")
        
        # Test 5: Test cache with non-existent user
        print(f"\n5. Testing cache with non-existent user...")
        non_existent_id = 999999999
        non_existent_user = await get_user(non_existent_id, db)
        assert non_existent_user is None, "Non-existent user should return None"
        print(f"   ✓ Non-existent user returns None")
        
        print("\n" + "=" * 80)
        print("User cache functionality test passed!")
        print("=" * 80)


async def test_batch_user_cache():
    """Test batch user caching functionality."""
    from app.core.user_cache import get_users_batch, invalidate_user_cache
    from app.core.redis_cache import redis_cache
    from app.database import AsyncSessionLocal
    from app.models import User
    from sqlalchemy import select
    
    print("\n" + "=" * 80)
    print("Batch User Cache Functionality Test")
    print("=" * 80)
    
    # Initialize Redis connection
    await redis_cache.connect()
    
    async with AsyncSessionLocal() as db:
        # Get some test users
        print("\n1. Getting test users from database...")
        result = await db.execute(select(User).limit(3))
        test_users = result.scalars().all()
        
        if len(test_users) < 2:
            print("   ⚠ Not enough users in database for batch test, skipping")
            return
        
        user_ids = [user.id for user in test_users]
        print(f"   Found {len(user_ids)} test users: {user_ids}")
        
        # Clear cache
        for user_id in user_ids:
            await invalidate_user_cache(user_id)
        
        # Test batch fetch
        print(f"\n2. Testing batch user lookup...")
        users = await get_users_batch(user_ids, db)
        assert len(users) == len(user_ids), "Should return all requested users"
        for user_id in user_ids:
            assert user_id in users, f"User {user_id} should be in results"
            assert users[user_id] is not None, f"User {user_id} should not be None"
        print(f"   ✓ Batch fetched {len(users)} users")
        
        # Test batch fetch again (should hit cache)
        print(f"\n3. Testing cached batch user lookup...")
        cached_users = await get_users_batch(user_ids, db)
        assert len(cached_users) == len(user_ids), "Should return all requested users from cache"
        for user_id in user_ids:
            assert user_id in cached_users, f"User {user_id} should be in cached results"
            assert cached_users[user_id] is not None, f"Cached user {user_id} should not be None"
        print(f"   ✓ Batch fetched {len(cached_users)} users from cache")
        
        print("\n" + "=" * 80)
        print("Batch user cache functionality test passed!")
        print("=" * 80)


async def test_cache_stats():
    """Test cache statistics functionality."""
    from app.core.redis_cache import redis_cache
    
    print("\n" + "=" * 80)
    print("Cache Statistics Test")
    print("=" * 80)
    
    # Initialize Redis connection
    await redis_cache.connect()
    
    print("\n1. Getting cache statistics...")
    stats = redis_cache.get_stats()
    print(f"   Cache stats: {stats}")
    
    print("\n2. Testing health check...")
    health = await redis_cache.health_check()
    print(f"   Health status: {health}")
    
    assert "status" in health, "Health check should return status"
    assert "backend" in health, "Health check should return backend type"
    
    print("\n" + "=" * 80)
    print("Cache statistics test passed!")
    print("=" * 80)


async def main():
    """Run all cache tests."""
    try:
        await test_user_cache()
        await test_batch_user_cache()
        await test_cache_stats()
        print("\n✓ All user cache tests passed!")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
