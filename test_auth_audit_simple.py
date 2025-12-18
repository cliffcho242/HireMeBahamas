#!/usr/bin/env python3
"""
Simple test for authentication response behavior to ensure proper HTTP status codes.

This test verifies:
1. ✅ Valid credentials return 200 with user data
2. ✅ Invalid credentials return 401 (NOT 200 with error)
3. ✅ Non-existent user returns 401 (NOT 200 with error)
"""
import asyncio
import sys
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Import the app and models
from api.backend_app.main import app
from api.backend_app.database import Base, get_db
from api.backend_app.models import User
from api.backend_app.core.security import get_password_hash_async


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create test database engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    """Override database dependency for testing"""
    async with TestSessionLocal() as session:
        yield session


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


async def test_valid_credentials():
    """Test that valid credentials return 200 with user data"""
    print("\n📝 Test 1: Valid credentials should return 200 with user data...")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@hiremebahamas.com",
                "password": "TestPassword123!"
            }
        )
        
        # Check status code
        if response.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {response.status_code}")
            print(f"   Response: {response.json()}")
            return False
        
        # Check response structure
        data = response.json()
        if "access_token" not in data:
            print(f"❌ FAILED: Response missing 'access_token'")
            return False
        
        if "user" not in data:
            print(f"❌ FAILED: Response missing 'user' data")
            return False
        
        if "error" in data:
            print(f"❌ FAILED: 200 response should NOT contain 'error' field")
            return False
        
        user_data = data["user"]
        if user_data["email"] != "test@hiremebahamas.com":
            print(f"❌ FAILED: User email mismatch")
            return False
        
        print("✅ PASSED: Valid credentials return 200 with tokens and user data")
        return True


async def test_invalid_password():
    """Test that invalid password returns 401 (NOT 200 with error)"""
    print("\n📝 Test 2: Invalid password should return 401...")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@hiremebahamas.com",
                "password": "WrongPassword123!"
            }
        )
        
        # Check status code - MUST be 401, NOT 200
        if response.status_code == 200:
            data = response.json()
            print(f"❌ FAILED: Invalid password returned 200 instead of 401")
            print(f"   Response: {data}")
            if "error" in data:
                print(f"   ⚠️  CRITICAL BUG: Returns 200 + error message pattern!")
            return False
        
        if response.status_code != 401:
            print(f"❌ FAILED: Expected 401, got {response.status_code}")
            return False
        
        # Check response has error detail
        data = response.json()
        if "detail" not in data:
            print(f"❌ FAILED: 401 response missing 'detail' field")
            return False
        
        if "access_token" in data:
            print(f"❌ FAILED: 401 response should NOT contain 'access_token'")
            return False
        
        print("✅ PASSED: Invalid password returns 401 Unauthorized")
        return True


async def test_nonexistent_user():
    """Test that non-existent user returns 401 (NOT 200 with error)"""
    print("\n📝 Test 3: Non-existent user should return 401...")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123!"
            }
        )
        
        # Check status code - MUST be 401, NOT 200
        if response.status_code == 200:
            data = response.json()
            print(f"❌ FAILED: Non-existent user returned 200 instead of 401")
            print(f"   Response: {data}")
            if "error" in data:
                print(f"   ⚠️  CRITICAL BUG: Returns 200 + error message pattern!")
            return False
        
        if response.status_code != 401:
            print(f"❌ FAILED: Expected 401, got {response.status_code}")
            return False
        
        # Check response has error detail
        data = response.json()
        if "detail" not in data:
            print(f"❌ FAILED: 401 response missing 'detail' field")
            return False
        
        print("✅ PASSED: Non-existent user returns 401 Unauthorized")
        return True


async def test_response_format():
    """Test response format matches specifications"""
    print("\n📝 Test 4: Response format correctness...")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test successful login
        success_response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@hiremebahamas.com",
                "password": "TestPassword123!"
            }
        )
        
        if success_response.status_code != 200:
            print(f"❌ FAILED: Success case returned {success_response.status_code}")
            return False
        
        success_data = success_response.json()
        
        # Verify SUCCESS pattern: 200 OK with user object
        if "user" not in success_data:
            print(f"❌ FAILED: 200 response missing 'user' field")
            return False
        
        if not isinstance(success_data["user"], dict):
            print(f"❌ FAILED: 'user' must be an object")
            return False
        
        user = success_data["user"]
        required_fields = ["id", "email", "role"]
        for field in required_fields:
            if field not in user:
                print(f"❌ FAILED: user object missing '{field}' field")
                return False
        
        # Test failed login
        failure_response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@hiremebahamas.com",
                "password": "WrongPassword!"
            }
        )
        
        if failure_response.status_code != 401:
            print(f"❌ FAILED: Failure case returned {failure_response.status_code}")
            return False
        
        failure_data = failure_response.json()
        
        # Verify FAILURE pattern: 401 with error detail
        if "detail" not in failure_data:
            print(f"❌ FAILED: 401 response missing 'detail' field")
            return False
        
        if not isinstance(failure_data["detail"], str):
            print(f"❌ FAILED: 'detail' must be a string")
            return False
        
        if "user" in failure_data:
            print(f"❌ FAILED: 401 response must NOT have 'user' field")
            return False
        
        print("✅ PASSED: Response formats are correct")
        return True


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("🔐 AUTH ROUTE & RESPONSE AUDIT TEST")
    print("="*80)
    
    # Setup database
    print("\n🔧 Setting up test database...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create test user
    print("👤 Creating test user...")
    async with TestSessionLocal() as session:
        hashed_password = await get_password_hash_async("TestPassword123!")
        user = User(
            email="test@hiremebahamas.com",
            hashed_password=hashed_password,
            first_name="Test",
            last_name="User",
            role="user",
            location="Nassau, Bahamas",
            is_active=True
        )
        session.add(user)
        await session.commit()
    
    print("✅ Test setup complete\n")
    
    # Run tests
    results = []
    try:
        results.append(await test_valid_credentials())
        results.append(await test_invalid_password())
        results.append(await test_nonexistent_user())
        results.append(await test_response_format())
    finally:
        # Cleanup
        print("\n🔧 Cleaning up test database...")
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    # Summary
    print("\n" + "="*80)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("="*80 + "\n")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*80 + "\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
