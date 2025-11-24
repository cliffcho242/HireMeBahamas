#!/usr/bin/env python3
"""
Test script to verify improved error handling for user profile lookups.
Tests input validation, error messages, and edge cases.

Note: This test modifies sys.path to import the app module.
In a production setup, consider using pytest with proper package configuration.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path (needed for standalone script execution)
# In production, use pytest with proper PYTHONPATH configuration
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, get_db, engine
from app.models import User
from app.core.security import get_password_hash, create_access_token
from app.api.auth import get_current_user
from app.api.users import get_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials


class MockCredentials:
    """Mock credentials for testing"""
    def __init__(self, token):
        self.credentials = token


async def test_user_lookup_validation():
    """Test user lookup with various edge cases and validation"""
    print("=" * 80)
    print("Testing User Profile Error Handling and Validation")
    print("=" * 80)
    
    # Initialize database
    await init_db()
    
    async with AsyncSession(engine) as db:
        # Create or get test users
        result = await db.execute(select(User).where(User.email == "testuser1@example.com"))
        test_user = result.scalar_one_or_none()
        
        if not test_user:
            # Create test user
            test_user = User(
                email="testuser1@example.com",
                hashed_password=get_password_hash("password123"),
                first_name="Test",
                last_name="User",
                username="testuser1",
                phone="+1-242-555-0001",
                location="Nassau, Bahamas",
                occupation="Software Developer",
                role="freelancer",
                is_available_for_hire=True,
                is_active=True,
            )
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            print(f"\n✓ Created test user: {test_user.email} (ID: {test_user.id}, Username: {test_user.username})")
        else:
            print(f"\n✓ Using existing test user: {test_user.email} (ID: {test_user.id}, Username: {test_user.username})")
        
        # Create access token for test user
        token = create_access_token(data={"sub": str(test_user.id)})
        mock_credentials = MockCredentials(token)
        
        # Get current user for testing
        current_user = await get_current_user(mock_credentials, db)
        print(f"✓ Authenticated as: {current_user.email}")
        
        # Test 1: Valid user lookup by ID
        print("\n" + "=" * 80)
        print("Test 1: Valid user lookup by ID")
        print("=" * 80)
        try:
            result = await get_user(str(test_user.id), db, current_user)
            print(f"✓ Successfully found user by ID: {result['user']['first_name']} {result['user']['last_name']}")
        except HTTPException as e:
            print(f"✗ Failed: {e.detail}")
            return False
        
        # Test 2: Valid user lookup by username
        print("\n" + "=" * 80)
        print("Test 2: Valid user lookup by username")
        print("=" * 80)
        try:
            result = await get_user(test_user.username, db, current_user)
            print(f"✓ Successfully found user by username: {result['user']['first_name']} {result['user']['last_name']}")
        except HTTPException as e:
            print(f"✗ Failed: {e.detail}")
            return False
        
        # Test 3: Non-existent user ID
        print("\n" + "=" * 80)
        print("Test 3: Non-existent user ID (should return 404)")
        print("=" * 80)
        try:
            result = await get_user("999999", db, current_user)
            print(f"✗ Should have raised 404 error")
            return False
        except HTTPException as e:
            if e.status_code == 404:
                print(f"✓ Correctly raised 404: {e.detail}")
            else:
                print(f"✗ Wrong status code: {e.status_code}")
                return False
        
        # Test 4: Non-existent username
        print("\n" + "=" * 80)
        print("Test 4: Non-existent username (should return 404)")
        print("=" * 80)
        try:
            result = await get_user("nonexistentuser", db, current_user)
            print(f"✗ Should have raised 404 error")
            return False
        except HTTPException as e:
            if e.status_code == 404:
                print(f"✓ Correctly raised 404: {e.detail}")
            else:
                print(f"✗ Wrong status code: {e.status_code}")
                return False
        
        # Test 5: Empty identifier
        print("\n" + "=" * 80)
        print("Test 5: Empty identifier (should return 400)")
        print("=" * 80)
        try:
            result = await get_user("", db, current_user)
            print(f"✗ Should have raised 400 error")
            return False
        except HTTPException as e:
            if e.status_code == 400:
                print(f"✓ Correctly raised 400: {e.detail}")
            else:
                print(f"✗ Wrong status code: {e.status_code}")
                return False
        
        # Test 6: Whitespace-only identifier
        print("\n" + "=" * 80)
        print("Test 6: Whitespace-only identifier (should return 400)")
        print("=" * 80)
        try:
            result = await get_user("   ", db, current_user)
            print(f"✗ Should have raised 400 error")
            return False
        except HTTPException as e:
            if e.status_code == 400:
                print(f"✓ Correctly raised 400: {e.detail}")
            else:
                print(f"✗ Wrong status code: {e.status_code}")
                return False
        
        # Test 7: Too long identifier (DoS protection)
        print("\n" + "=" * 80)
        print("Test 7: Very long identifier (should return 400)")
        print("=" * 80)
        try:
            long_identifier = "a" * 200
            result = await get_user(long_identifier, db, current_user)
            print(f"✗ Should have raised 400 error")
            return False
        except HTTPException as e:
            if e.status_code == 400:
                print(f"✓ Correctly raised 400: {e.detail}")
            else:
                print(f"✗ Wrong status code: {e.status_code}")
                return False
        
        # Test 8: Invalid username format (special characters)
        print("\n" + "=" * 80)
        print("Test 8: Invalid username format with special characters (should return 400)")
        print("=" * 80)
        try:
            result = await get_user("user@#$%", db, current_user)
            print(f"✗ Should have raised 400 error")
            return False
        except HTTPException as e:
            if e.status_code == 400:
                print(f"✓ Correctly raised 400: {e.detail}")
            else:
                print(f"✗ Wrong status code: {e.status_code}")
                return False
        
        # Test 9: Negative user ID
        print("\n" + "=" * 80)
        print("Test 9: Negative user ID (should return 400)")
        print("=" * 80)
        try:
            result = await get_user("-1", db, current_user)
            print(f"✗ Should have raised 400 error")
            return False
        except HTTPException as e:
            if e.status_code == 400:
                print(f"✓ Correctly raised 400: {e.detail}")
            else:
                print(f"✗ Wrong status code: {e.status_code}")
                return False
        
        # Test 10: Zero user ID
        print("\n" + "=" * 80)
        print("Test 10: Zero user ID (should return 400)")
        print("=" * 80)
        try:
            result = await get_user("0", db, current_user)
            print(f"✗ Should have raised 400 error")
            return False
        except HTTPException as e:
            if e.status_code == 400:
                print(f"✓ Correctly raised 400: {e.detail}")
            else:
                print(f"✗ Wrong status code: {e.status_code}")
                return False
        
        # Test 11: Very large user ID (overflow protection)
        print("\n" + "=" * 80)
        print("Test 11: Very large user ID beyond int32 (should return 400)")
        print("=" * 80)
        try:
            result = await get_user("9999999999", db, current_user)
            print(f"✗ Should have raised 400 error")
            return False
        except HTTPException as e:
            if e.status_code == 400:
                print(f"✓ Correctly raised 400: {e.detail}")
            else:
                print(f"✗ Wrong status code: {e.status_code}")
                return False
        
        print("\n" + "=" * 80)
        print("✓ All validation tests passed!")
        print("=" * 80)
        return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_user_lookup_validation())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
