#!/usr/bin/env python3
"""
Test script to verify the user profile endpoint returns all required fields.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.database import init_db, get_db, engine
from app.models import User, Follow
from app.core.security import get_password_hash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def setup_test_data():
    """Create test users for testing"""
    print("Setting up test data...")
    
    # Initialize database
    await init_db()
    
    async with AsyncSession(engine) as db:
        # Check if test users exist
        result = await db.execute(select(User).where(User.email == "test1@example.com"))
        user1 = result.scalar_one_or_none()
        
        if not user1:
            # Create test user 1
            user1 = User(
                email="test1@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="John",
                last_name="Doe",
                username="johndoe",
                phone="+1-242-555-0001",
                location="Nassau, Bahamas",
                occupation="Software Developer",
                company_name="Tech Corp",
                bio="Experienced developer",
                role="freelancer",
                is_available_for_hire=True,
            )
            db.add(user1)
            await db.commit()
            await db.refresh(user1)
            print(f"Created test user 1: {user1.email} (ID: {user1.id})")
        else:
            print(f"Test user 1 already exists: {user1.email} (ID: {user1.id})")
        
        # Check if test user 2 exists
        result = await db.execute(select(User).where(User.email == "test2@example.com"))
        user2 = result.scalar_one_or_none()
        
        if not user2:
            # Create test user 2
            user2 = User(
                email="test2@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="Jane",
                last_name="Smith",
                username="janesmith",
                phone="+1-242-555-0002",
                location="Freeport, Bahamas",
                occupation="Designer",
                company_name="Design Studio",
                bio="Creative designer",
                role="client",
                is_available_for_hire=False,
            )
            db.add(user2)
            await db.commit()
            await db.refresh(user2)
            print(f"Created test user 2: {user2.email} (ID: {user2.id})")
        else:
            print(f"Test user 2 already exists: {user2.email} (ID: {user2.id})")
        
        return user1, user2


async def test_get_user_endpoint():
    """Test the user profile endpoint"""
    print("\n" + "="*60)
    print("Testing User Profile Endpoint")
    print("="*60)
    
    # Setup test data
    user1, user2 = await setup_test_data()
    
    # Import the endpoint function
    from app.api.users import get_user
    
    async with AsyncSession(engine) as db:
        try:
            # Refresh users in the current session
            result = await db.execute(select(User).where(User.id == user1.id))
            user1 = result.scalar_one()
            
            # Test getting user2's profile as user1
            print(f"\nTesting GET /api/users/{user2.id}")
            result = await get_user(user2.id, db, user1)
            
            # Check response structure
            print("\nResponse structure:")
            print(f"  - success: {result.get('success')}")
            print(f"  - user: {type(result.get('user'))}")
            
            # Check required fields
            user_data = result.get('user', {})
            required_fields = [
                'id', 'first_name', 'last_name', 'email', 'username',
                'user_type', 'created_at', 'is_available_for_hire',
                'posts_count', 'followers_count', 'following_count',
                'is_following', 'phone', 'location', 'occupation',
                'company_name', 'bio', 'avatar_url', 'skills',
                'experience', 'education', 'updated_at'
            ]
            
            print("\nChecking required fields:")
            all_present = True
            for field in required_fields:
                present = field in user_data
                status = "✓" if present else "✗"
                value = user_data.get(field)
                print(f"  {status} {field}: {value}")
                if not present:
                    all_present = False
            
            if all_present:
                print("\n✅ SUCCESS: All required fields are present!")
                
                # Verify specific field values
                print("\nVerifying field values:")
                assert user_data['id'] == user2.id, "ID mismatch"
                assert user_data['first_name'] == user2.first_name, "first_name mismatch"
                assert user_data['last_name'] == user2.last_name, "last_name mismatch"
                assert user_data['email'] == user2.email, "email mismatch"
                assert user_data['user_type'] == user2.role, "user_type mismatch"
                assert user_data['is_available_for_hire'] == user2.is_available_for_hire, "is_available_for_hire mismatch"
                assert user_data['posts_count'] == 0, "posts_count should be 0"
                assert user_data['phone'] == user2.phone, "phone mismatch"
                print("  ✓ All field values are correct!")
                
                return True
            else:
                print("\n❌ FAILURE: Some required fields are missing!")
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Main test runner"""
    try:
        success = await test_get_user_endpoint()
        
        # Cleanup
        await engine.dispose()
        
        if success:
            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED!")
            print("="*60)
            sys.exit(0)
        else:
            print("\n" + "="*60)
            print("❌ TESTS FAILED!")
            print("="*60)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
