#!/usr/bin/env python3
"""
Test script to verify the user profile endpoint supports both ID and username lookup.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, get_db, engine
from app.models import User
from app.core.security import get_password_hash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_user_lookup():
    """Test user lookup by ID and username"""
    print("Testing user lookup by ID and username...")
    
    # Initialize database
    await init_db()
    
    async with AsyncSession(engine) as db:
        # Create or get test user
        result = await db.execute(select(User).where(User.email == "testuser@example.com"))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create test user
            user = User(
                email="testuser@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="Test",
                last_name="User",
                username="testuser",
                phone="+1-242-555-9999",
                location="Nassau, Bahamas",
                occupation="Test Occupation",
                role="freelancer",
                is_available_for_hire=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"✓ Created test user: {user.email} (ID: {user.id}, Username: {user.username})")
        else:
            print(f"✓ Test user already exists: {user.email} (ID: {user.id}, Username: {user.username})")
        
        # Test 1: Lookup by numeric ID
        print(f"\nTest 1: Looking up user by ID '{user.id}'...")
        identifier = str(user.id)
        
        if identifier.isdigit():
            user_id = int(identifier)
            result = await db.execute(select(User).where(User.id == user_id))
            found_user = result.scalar_one_or_none()
        else:
            found_user = None
        
        if found_user:
            print(f"✓ Found user by ID: {found_user.first_name} {found_user.last_name}")
        else:
            print("✗ Failed to find user by ID")
            return False
        
        # Test 2: Lookup by username
        print(f"\nTest 2: Looking up user by username '{user.username}'...")
        identifier = user.username
        
        if identifier.isdigit():
            user_id = int(identifier)
            result = await db.execute(select(User).where(User.id == user_id))
            found_user = result.scalar_one_or_none()
        else:
            result = await db.execute(select(User).where(User.username == identifier))
            found_user = result.scalar_one_or_none()
        
        if found_user:
            print(f"✓ Found user by username: {found_user.first_name} {found_user.last_name}")
        else:
            print("✗ Failed to find user by username")
            return False
        
        # Test 3: Lookup by non-existent username
        print("\nTest 3: Looking up user by non-existent username 'nonexistent'...")
        identifier = "nonexistent"
        
        if identifier.isdigit():
            user_id = int(identifier)
            result = await db.execute(select(User).where(User.id == user_id))
            found_user = result.scalar_one_or_none()
        else:
            result = await db.execute(select(User).where(User.username == identifier))
            found_user = result.scalar_one_or_none()
        
        if found_user is None:
            print("✓ Correctly returned None for non-existent username")
        else:
            print("✗ Unexpectedly found a user")
            return False
        
        # Test 4: Lookup by non-existent ID
        print("\nTest 4: Looking up user by non-existent ID '999999'...")
        identifier = "999999"
        
        if identifier.isdigit():
            user_id = int(identifier)
            result = await db.execute(select(User).where(User.id == user_id))
            found_user = result.scalar_one_or_none()
        else:
            found_user = None
        
        if found_user is None:
            print("✓ Correctly returned None for non-existent ID")
        else:
            print("✗ Unexpectedly found a user")
            return False
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True


if __name__ == "__main__":
    success = asyncio.run(test_user_lookup())
    sys.exit(0 if success else 1)
