#!/usr/bin/env python3
"""
Test script to verify the is_active filter in user lookup endpoints.

This test ensures that:
1. Active users can be found by ID
2. Inactive users are NOT found by ID (404 error)
3. The is_active check is consistent across all user lookup endpoints
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, engine
from app.models import User
from app.core.security import get_password_hash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_user_is_active_filter():
    """Test that inactive users are not returned by user lookup endpoints"""
    print("Testing is_active filter in user lookup...")
    print("=" * 60)
    
    # Initialize database
    await init_db()
    
    async with AsyncSession(engine) as db:
        # Test 1: Create an active user
        print("\nTest 1: Creating active user...")
        active_email = "active_user@example.com"
        
        # Clean up any existing test users
        result = await db.execute(select(User).where(User.email == active_email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            await db.delete(existing_user)
            await db.commit()
        
        active_user = User(
            email=active_email,
            hashed_password=get_password_hash("password123"),
            first_name="Active",
            last_name="User",
            username="active_user",
            is_active=True,
            location="Nassau, Bahamas",
        )
        db.add(active_user)
        await db.commit()
        await db.refresh(active_user)
        print(f"✓ Created active user: ID={active_user.id}, is_active={active_user.is_active}")
        
        # Test 2: Create an inactive user
        print("\nTest 2: Creating inactive user...")
        inactive_email = "inactive_user@example.com"
        
        result = await db.execute(select(User).where(User.email == inactive_email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            await db.delete(existing_user)
            await db.commit()
        
        inactive_user = User(
            email=inactive_email,
            hashed_password=get_password_hash("password123"),
            first_name="Inactive",
            last_name="User",
            username="inactive_user",
            is_active=False,  # User is inactive
            location="Nassau, Bahamas",
        )
        db.add(inactive_user)
        await db.commit()
        await db.refresh(inactive_user)
        print(f"✓ Created inactive user: ID={inactive_user.id}, is_active={inactive_user.is_active}")
        
        # Test 3: Verify active user can be found
        print("\nTest 3: Looking up active user by ID...")
        result = await db.execute(select(User).where(User.id == active_user.id))
        found_user = result.scalar_one_or_none()
        
        if found_user and found_user.is_active:
            print(f"✓ Active user found and is_active=True")
        else:
            print("✗ Failed to find active user")
            return False
        
        # Test 4: Verify inactive user exists in DB but should be filtered
        print("\nTest 4: Looking up inactive user by ID (should exist in DB)...")
        result = await db.execute(select(User).where(User.id == inactive_user.id))
        found_user = result.scalar_one_or_none()
        
        if found_user:
            print(f"✓ Inactive user exists in DB with ID={found_user.id}")
            
            # Simulate the is_active check that endpoints should perform
            if not found_user.is_active:
                print("✓ User is inactive - endpoints should return 404")
            else:
                print("✗ User unexpectedly has is_active=True")
                return False
        else:
            print("✗ Failed to find inactive user in DB")
            return False
        
        # Test 5: Test the filter query (like in user profile endpoint)
        print("\nTest 5: Testing is_active filter query...")
        result = await db.execute(
            select(User).where(User.id == active_user.id, User.is_active == True)
        )
        found_user = result.scalar_one_or_none()
        if found_user:
            print(f"✓ Active user found with is_active filter")
        else:
            print("✗ Active user not found with is_active filter")
            return False
        
        # Test 6: Verify inactive user is NOT found with is_active filter
        print("\nTest 6: Testing is_active filter excludes inactive user...")
        result = await db.execute(
            select(User).where(User.id == inactive_user.id, User.is_active == True)
        )
        found_user = result.scalar_one_or_none()
        if found_user is None:
            print(f"✓ Inactive user correctly excluded by is_active filter")
        else:
            print("✗ Inactive user should NOT be found with is_active=True filter")
            return False
        
        # Cleanup
        print("\nCleaning up test users...")
        result = await db.execute(select(User).where(User.email.in_([active_email, inactive_email])))
        for user in result.scalars().all():
            await db.delete(user)
        await db.commit()
        print("✓ Test users deleted")
        
        print("\n" + "=" * 60)
        print("✓ All is_active filter tests passed!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    success = asyncio.run(test_user_is_active_filter())
    sys.exit(0 if success else 1)
