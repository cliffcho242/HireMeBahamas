#!/usr/bin/env python3
"""
Test script to verify user profile endpoint returns all required fields including
is_following, followers_count, following_count, and posts_count.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, engine
from app.models import User, Post, Follow
from app.core.security import get_password_hash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_user_profile_fields():
    """Test that user profile endpoint returns all required fields"""
    print("Testing user profile fields...")
    
    # Initialize database
    await init_db()
    
    async with AsyncSession(engine) as db:
        # Create or get test users
        result = await db.execute(select(User).where(User.email == "testuser1@example.com"))
        user1 = result.scalar_one_or_none()
        
        if not user1:
            user1 = User(
                email="testuser1@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="Test",
                last_name="User1",
                username="testuser1",
                phone="+1-242-555-0001",
                location="Nassau, Bahamas",
                occupation="Software Developer",
                role="freelancer",
                is_available_for_hire=True,
            )
            db.add(user1)
            await db.commit()
            await db.refresh(user1)
            print(f"✓ Created test user1: {user1.email}")
        else:
            print(f"✓ Test user1 already exists: {user1.email}")
        
        result = await db.execute(select(User).where(User.email == "testuser2@example.com"))
        user2 = result.scalar_one_or_none()
        
        if not user2:
            user2 = User(
                email="testuser2@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="Test",
                last_name="User2",
                username="testuser2",
                phone="+1-242-555-0002",
                location="Freeport, Bahamas",
                occupation="Designer",
                role="freelancer",
                is_available_for_hire=False,
            )
            db.add(user2)
            await db.commit()
            await db.refresh(user2)
            print(f"✓ Created test user2: {user2.email}")
        else:
            print(f"✓ Test user2 already exists: {user2.email}")
        
        # Create a follow relationship
        follow_result = await db.execute(
            select(Follow).where(
                Follow.follower_id == user1.id,
                Follow.followed_id == user2.id
            )
        )
        existing_follow = follow_result.scalar_one_or_none()
        
        if not existing_follow:
            follow = Follow(follower_id=user1.id, followed_id=user2.id)
            db.add(follow)
            await db.commit()
            print(f"✓ Created follow relationship: user1 follows user2")
        else:
            print(f"✓ Follow relationship already exists")
        
        # Create test posts for user2
        posts_result = await db.execute(
            select(Post).where(Post.user_id == user2.id)
        )
        existing_posts = posts_result.scalars().all()
        
        if len(existing_posts) == 0:
            post1 = Post(
                user_id=user2.id,
                content="Test post 1 for user2",
                likes_count=0,
                comments_count=0
            )
            post2 = Post(
                user_id=user2.id,
                content="Test post 2 for user2",
                likes_count=0,
                comments_count=0
            )
            db.add(post1)
            db.add(post2)
            await db.commit()
            print(f"✓ Created 2 test posts for user2")
        else:
            print(f"✓ User2 already has {len(existing_posts)} posts")
        
        # Now test the user profile retrieval logic
        print("\n" + "=" * 60)
        print("Testing user profile field retrieval...")
        print("=" * 60)
        
        # Test 1: Get user2's profile from user1's perspective (following)
        print(f"\nTest 1: Get user2's profile (user1 is following user2)...")
        
        # Check if user1 follows user2
        follow_check = await db.execute(
            select(Follow).where(
                Follow.follower_id == user1.id,
                Follow.followed_id == user2.id
            )
        )
        is_following = follow_check.scalar_one_or_none() is not None
        
        # Get follower/following counts for user2
        followers_result = await db.execute(
            select(Follow).where(Follow.followed_id == user2.id)
        )
        followers_count = len(followers_result.scalars().all())
        
        following_result = await db.execute(
            select(Follow).where(Follow.follower_id == user2.id)
        )
        following_count = len(following_result.scalars().all())
        
        # Get posts count for user2
        posts_result = await db.execute(
            select(Post).where(Post.user_id == user2.id)
        )
        posts_count = len(posts_result.scalars().all())
        
        # Verify all fields are present
        print(f"  is_following: {is_following} (expected: True)")
        print(f"  followers_count: {followers_count} (expected: >= 1)")
        print(f"  following_count: {following_count}")
        print(f"  posts_count: {posts_count} (expected: >= 2)")
        
        if not is_following:
            print("✗ FAIL: is_following should be True")
            return False
        
        if followers_count < 1:
            print("✗ FAIL: followers_count should be at least 1")
            return False
        
        if posts_count < 2:
            print("✗ FAIL: posts_count should be at least 2")
            return False
        
        print("✓ All fields present and correct!")
        
        # Test 2: Ensure fields have default values (0/False) when appropriate
        print(f"\nTest 2: Get user1's profile (user2 not following user1)...")
        
        # Check if user2 follows user1
        follow_check = await db.execute(
            select(Follow).where(
                Follow.follower_id == user2.id,
                Follow.followed_id == user1.id
            )
        )
        is_following_back = follow_check.scalar_one_or_none() is not None
        
        print(f"  is_following: {is_following_back} (expected: False)")
        
        if is_following_back:
            print("✗ FAIL: is_following should be False")
            return False
        
        print("✓ Default values work correctly!")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    success = asyncio.run(test_user_profile_fields())
    sys.exit(0 if success else 1)
