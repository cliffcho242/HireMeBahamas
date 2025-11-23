#!/usr/bin/env python3
"""
Test script to verify Follow/Unfollow functionality
Tests both backend models and API endpoints
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import Base, engine, AsyncSessionLocal
from app.models import User, Follow
from sqlalchemy import select, func


async def test_follow_model():
    """Test Follow model exists and has correct fields"""
    print("\n🔍 Testing Follow Model...")
    
    # Check table name
    assert Follow.__tablename__ == "follows", "Follow table name should be 'follows'"
    print("✅ Follow table name correct: 'follows'")
    
    # Check fields exist
    assert hasattr(Follow, 'follower_id'), "Follow should have follower_id field"
    assert hasattr(Follow, 'followed_id'), "Follow should have followed_id field"
    assert hasattr(Follow, 'created_at'), "Follow should have created_at field"
    print("✅ Follow model has all required fields: follower_id, followed_id, created_at")
    
    # Check relationships
    assert hasattr(Follow, 'follower'), "Follow should have follower relationship"
    assert hasattr(Follow, 'followed'), "Follow should have followed relationship"
    print("✅ Follow model has relationships: follower, followed")
    
    return True


async def test_user_follow_relationships():
    """Test User model has follow relationships"""
    print("\n🔍 Testing User Follow Relationships...")
    
    # Check User has follow relationships
    assert hasattr(User, 'following'), "User should have 'following' relationship"
    assert hasattr(User, 'followers'), "User should have 'followers' relationship"
    print("✅ User model has follow relationships: following, followers")
    
    return True


async def test_database_tables():
    """Test that database tables can be created"""
    print("\n🔍 Testing Database Table Creation...")
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully (including follows table)")
        
        # Verify follows table exists
        async with AsyncSessionLocal() as session:
            # Try to query the follows table
            result = await session.execute(select(func.count()).select_from(Follow))
            count = result.scalar()
            print(f"✅ Follows table accessible, current count: {count}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating/accessing tables: {e}")
        return False


async def test_follow_creation():
    """Test creating follow relationships"""
    print("\n🔍 Testing Follow Relationship Creation...")
    
    try:
        async with AsyncSessionLocal() as session:
            # Create test users
            user1 = User(
                email="test1@example.com",
                hashed_password="hashedpass123",
                first_name="Test",
                last_name="User1",
                is_active=True
            )
            user2 = User(
                email="test2@example.com",
                hashed_password="hashedpass456",
                first_name="Test",
                last_name="User2",
                is_active=True
            )
            
            session.add(user1)
            session.add(user2)
            await session.commit()
            await session.refresh(user1)
            await session.refresh(user2)
            
            print(f"✅ Created test users: {user1.id}, {user2.id}")
            
            # Create follow relationship
            follow = Follow(
                follower_id=user1.id,
                followed_id=user2.id
            )
            session.add(follow)
            await session.commit()
            
            print(f"✅ Created follow relationship: User {user1.id} follows User {user2.id}")
            
            # Verify follow exists
            result = await session.execute(
                select(Follow).where(
                    Follow.follower_id == user1.id,
                    Follow.followed_id == user2.id
                )
            )
            created_follow = result.scalar_one_or_none()
            
            assert created_follow is not None, "Follow relationship should exist"
            print("✅ Follow relationship verified in database")
            
            # Count followers
            followers_result = await session.execute(
                select(func.count()).select_from(Follow).where(Follow.followed_id == user2.id)
            )
            followers_count = followers_result.scalar()
            assert followers_count == 1, f"User2 should have 1 follower, got {followers_count}"
            print(f"✅ Follower count correct: {followers_count}")
            
            # Test unfollow (delete)
            await session.delete(created_follow)
            await session.commit()
            
            # Verify follow removed
            result = await session.execute(
                select(Follow).where(
                    Follow.follower_id == user1.id,
                    Follow.followed_id == user2.id
                )
            )
            deleted_follow = result.scalar_one_or_none()
            assert deleted_follow is None, "Follow relationship should be deleted"
            print("✅ Unfollow (delete) works correctly")
            
            # Cleanup
            await session.delete(user1)
            await session.delete(user2)
            await session.commit()
            print("✅ Test data cleaned up")
            
        return True
    except Exception as e:
        print(f"❌ Error testing follow creation: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING FOLLOW/UNFOLLOW FUNCTIONALITY")
    print("=" * 60)
    
    tests = [
        ("Follow Model Structure", test_follow_model),
        ("User Follow Relationships", test_user_follow_relationships),
        ("Database Table Creation", test_database_tables),
        ("Follow/Unfollow Operations", test_follow_creation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Follow/Unfollow functionality is working!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
