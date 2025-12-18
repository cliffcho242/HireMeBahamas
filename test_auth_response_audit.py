#!/usr/bin/env python3
"""
Test authentication response behavior to ensure proper HTTP status codes.

This test verifies:
1. ✅ Valid credentials return 200 with user data
2. ✅ Invalid credentials return 401 (NOT 200 with error)
3. ✅ Non-existent user returns 401 (NOT 200 with error)
"""
import asyncio
import pytest
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


@pytest.fixture
async def test_db():
    """Create test database tables"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_user():
    """Create a test user"""
    async with TestSessionLocal() as session:
        # Create test user with known credentials
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
        await session.refresh(user)
        return user


@pytest.mark.asyncio
async def test_valid_credentials_return_200(test_db, test_user):
    """Test that valid credentials return 200 with user data"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@hiremebahamas.com",
                "password": "TestPassword123!"
            }
        )
        
        # Assert correct status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Assert response has correct structure
        data = response.json()
        assert "access_token" in data, "Response should contain access_token"
        assert "refresh_token" in data, "Response should contain refresh_token"
        assert "user" in data, "Response should contain user data"
        assert "error" not in data, "Response should NOT contain error field"
        
        # Assert user data is correct
        user_data = data["user"]
        assert user_data["email"] == "test@hiremebahamas.com"
        assert user_data["first_name"] == "Test"
        
        print("✅ Valid credentials test PASSED: Returns 200 with tokens and user data")


@pytest.mark.asyncio
async def test_invalid_password_returns_401(test_db, test_user):
    """Test that invalid password returns 401 (NOT 200 with error)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@hiremebahamas.com",
                "password": "WrongPassword123!"
            }
        )
        
        # Assert correct status code - MUST be 401, NOT 200
        assert response.status_code == 401, (
            f"Invalid password should return 401, got {response.status_code}. "
            f"Response: {response.json()}"
        )
        
        # Assert response has error detail
        data = response.json()
        assert "detail" in data, "401 response should contain detail field"
        assert "access_token" not in data, "401 response should NOT contain access_token"
        assert "user" not in data, "401 response should NOT contain user data"
        
        print("✅ Invalid password test PASSED: Returns 401 Unauthorized")


@pytest.mark.asyncio
async def test_nonexistent_user_returns_401(test_db):
    """Test that non-existent user returns 401 (NOT 200 with error)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123!"
            }
        )
        
        # Assert correct status code - MUST be 401, NOT 200
        assert response.status_code == 401, (
            f"Non-existent user should return 401, got {response.status_code}. "
            f"Response: {response.json()}"
        )
        
        # Assert response has error detail
        data = response.json()
        assert "detail" in data, "401 response should contain detail field"
        assert "access_token" not in data, "401 response should NOT contain access_token"
        assert "user" not in data, "401 response should NOT contain user data"
        
        print("✅ Non-existent user test PASSED: Returns 401 Unauthorized")


@pytest.mark.asyncio
async def test_response_format_correctness(test_db, test_user):
    """Test response format matches specifications"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test successful login
        success_response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@hiremebahamas.com",
                "password": "TestPassword123!"
            }
        )
        
        assert success_response.status_code == 200
        success_data = success_response.json()
        
        # Verify SUCCESS pattern: 200 OK with user object
        assert "user" in success_data, "200 response must have 'user' field"
        assert isinstance(success_data["user"], dict), "user must be an object"
        assert "id" in success_data["user"], "user must have 'id' field"
        assert "email" in success_data["user"], "user must have 'email' field"
        assert "role" in success_data["user"], "user must have 'role' field"
        
        # Test failed login
        failure_response = await client.post(
            "/api/auth/login",
            json={
                "email": "test@hiremebahamas.com",
                "password": "WrongPassword!"
            }
        )
        
        assert failure_response.status_code == 401
        failure_data = failure_response.json()
        
        # Verify FAILURE pattern: 401 with error detail
        assert "detail" in failure_data, "401 response must have 'detail' field"
        assert isinstance(failure_data["detail"], str), "detail must be a string"
        assert "user" not in failure_data, "401 response must NOT have 'user' field"
        assert "error" not in failure_data or failure_data.get("error") is None, (
            "401 response should use 'detail', not 'error'"
        )
        
        print("✅ Response format test PASSED: Correct patterns for success/failure")


if __name__ == "__main__":
    # Run tests
    print("\n" + "="*80)
    print("🔐 AUTH ROUTE & RESPONSE AUDIT TEST")
    print("="*80 + "\n")
    
    async def run_tests():
        # Setup
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        try:
            # Create test user
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
            
            # Run tests
            await test_valid_credentials_return_200(None, None)
            await test_invalid_password_returns_401(None, None)
            await test_nonexistent_user_returns_401(None)
            await test_response_format_correctness(None, None)
            
            print("\n" + "="*80)
            print("✅ ALL TESTS PASSED")
            print("="*80 + "\n")
            
        finally:
            # Cleanup
            async with test_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
    
    asyncio.run(run_tests())
