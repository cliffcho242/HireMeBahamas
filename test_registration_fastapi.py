#!/usr/bin/env python3
"""
Test script to verify registration endpoint functionality
Tests both the FastAPI backend registration and OAuth flows
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient


async def test_registration():
    """Test the registration endpoint"""
    print("=" * 60)
    print("Testing HireMeBahamas Registration Endpoint")
    print("=" * 60)
    print()
    
    # Import the app
    from app.main import app
    from app.database import init_db, engine, Base
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    # Initialize database
    print("Initializing test database...")
    # Use a fresh test database with secure temp file
    import os
    import tempfile
    fd, test_db = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close the file descriptor, we'll use the path
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{test_db}"
    
    # Recreate engine with test database
    from sqlalchemy.ext.asyncio import create_async_engine
    test_engine = create_async_engine(f"sqlite+aiosqlite:///{test_db}")
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Test database initialized")
    print()
    
    # Update the database engine in the app
    from app import database
    old_engine = database.engine
    database.engine = test_engine
    database.AsyncSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    
    # Create test client
    client = TestClient(app)
    
    # Test 1: Successful registration
    print("Test 1: Successful registration")
    registration_data = {
        "email": "test@hiremebahamas.com",
        "password": "SecurePass123",
        "first_name": "John",
        "last_name": "Doe",
        "user_type": "freelancer",
        "location": "Nassau, Bahamas",
        "phone": "+1-242-555-1234"
    }
    
    response = client.post("/api/auth/register", json=registration_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✓ Registration successful")
        data = response.json()
        assert "access_token" in data, "No access token in response"
        assert "user" in data, "No user data in response"
        assert data["user"]["email"] == "test@hiremebahamas.com"
        print("✓ Access token generated")
        print("✓ User data returned correctly")
    else:
        print(f"✗ Registration failed: {response.json()}")
        return False
    
    print()
    
    # Test 2: Duplicate email
    print("Test 2: Duplicate email registration")
    response = client.post("/api/auth/register", json=registration_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400:
        print("✓ Correctly rejected duplicate email")
    else:
        print("✗ Should have rejected duplicate email")
        return False
    
    print()
    
    # Test 3: Missing required fields
    print("Test 3: Missing required fields")
    invalid_data = {
        "email": "test2@hiremebahamas.com",
        "password": "SecurePass123",
        # Missing first_name, last_name, etc.
    }
    
    response = client.post("/api/auth/register", json=invalid_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 422:  # FastAPI validation error
        print("✓ Correctly rejected missing fields")
    else:
        print("⚠ Unexpected status code for missing fields")
    
    print()
    
    # Test 4: Login with registered user
    print("Test 4: Login with registered user")
    login_data = {
        "email": "test@hiremebahamas.com",
        "password": "SecurePass123"
    }
    
    response = client.post("/api/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✓ Login successful")
        data = response.json()
        assert "access_token" in data, "No access token in response"
        print("✓ Access token generated for login")
    else:
        print(f"✗ Login failed: {response.json()}")
        return False
    
    print()
    
    # Test 5: Get profile with token
    print("Test 5: Get profile with authentication")
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/auth/profile", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✓ Profile retrieved successfully")
        profile = response.json()
        assert profile["email"] == "test@hiremebahamas.com"
        print("✓ Profile data is correct")
    else:
        print(f"✗ Profile retrieval failed: {response.json()}")
        return False
    
    print()
    print("=" * 60)
    print("✓ All registration tests passed!")
    print("=" * 60)
    
    return True


async def test_oauth_endpoints():
    """Test OAuth endpoint availability"""
    print()
    print("=" * 60)
    print("Testing OAuth Endpoints")
    print("=" * 60)
    print()
    
    from app.main import app
    client = TestClient(app)
    
    # Test that OAuth endpoints exist
    print("Checking OAuth endpoint availability...")
    
    # We can't actually test OAuth without valid tokens, but we can check the endpoints exist
    # and return expected errors for invalid/missing tokens
    
    # Test Google OAuth endpoint
    print("\nTest: Google OAuth endpoint")
    response = client.post("/api/auth/oauth/google", json={"token": "invalid_token"})
    print(f"Status Code: {response.status_code}")
    # Should return 401 or 500 for invalid token, not 404
    if response.status_code != 404:
        print("✓ Google OAuth endpoint exists")
    else:
        print("✗ Google OAuth endpoint not found")
        return False
    
    # Test Apple OAuth endpoint
    print("\nTest: Apple OAuth endpoint")
    response = client.post("/api/auth/oauth/apple", json={"token": "invalid_token"})
    print(f"Status Code: {response.status_code}")
    # Should return 401 or 500 for invalid token, not 404
    if response.status_code != 404:
        print("✓ Apple OAuth endpoint exists")
    else:
        print("✗ Apple OAuth endpoint not found")
        return False
    
    print()
    print("=" * 60)
    print("✓ OAuth endpoints are properly configured!")
    print("=" * 60)
    
    return True


def test_dependency_imports():
    """Test that all required dependencies can be imported"""
    print()
    print("=" * 60)
    print("Testing Critical Dependency Imports")
    print("=" * 60)
    print()
    
    errors = []
    
    # Test core dependencies
    try:
        import fastapi
        print("✓ FastAPI")
    except ImportError as e:
        errors.append(f"FastAPI: {e}")
        print(f"✗ FastAPI: {e}")
    
    try:
        from jose import jwt
        print("✓ python-jose")
    except ImportError as e:
        errors.append(f"python-jose: {e}")
        print(f"✗ python-jose: {e}")
    
    try:
        from passlib.context import CryptContext
        print("✓ passlib")
    except ImportError as e:
        errors.append(f"passlib: {e}")
        print(f"✗ passlib: {e}")
    
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        print("✓ google-auth (OAuth)")
    except ImportError as e:
        errors.append(f"google-auth: {e}")
        print(f"✗ google-auth: {e}")
    
    try:
        import jwt as pyjwt
        from jwt import PyJWKClient
        print("✓ PyJWT (Apple OAuth)")
    except ImportError as e:
        errors.append(f"PyJWT: {e}")
        print(f"✗ PyJWT: {e}")
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy")
    except ImportError as e:
        errors.append(f"SQLAlchemy: {e}")
        print(f"✗ SQLAlchemy: {e}")
    
    try:
        import psycopg2
        print("✓ psycopg2-binary")
    except ImportError as e:
        errors.append(f"psycopg2-binary: {e}")
        print(f"✗ psycopg2-binary: {e}")
    
    try:
        import asyncpg
        print("✓ asyncpg")
    except ImportError as e:
        errors.append(f"asyncpg: {e}")
        print(f"✗ asyncpg: {e}")
    
    try:
        import pydantic
        print("✓ Pydantic")
    except ImportError as e:
        errors.append(f"Pydantic: {e}")
        print(f"✗ Pydantic: {e}")
    
    if errors:
        print()
        print("=" * 60)
        print(f"✗ {len(errors)} dependencies missing!")
        print("=" * 60)
        return False
    else:
        print()
        print("=" * 60)
        print("✓ All critical dependencies available!")
        print("=" * 60)
        return True


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("HireMeBahamas Registration & Dependency Test Suite")
    print("=" * 60)
    
    # Test 1: Dependencies
    deps_ok = test_dependency_imports()
    if not deps_ok:
        print("\n✗ Dependency test failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        print("  pip install -r backend/requirements.txt")
        return False
    
    # Test 2: Registration endpoints
    try:
        reg_ok = await test_registration()
        if not reg_ok:
            print("\n✗ Registration tests failed")
            return False
    except Exception as e:
        print(f"\n✗ Registration test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: OAuth endpoints
    try:
        oauth_ok = await test_oauth_endpoints()
        if not oauth_ok:
            print("\n✗ OAuth endpoint tests failed")
            return False
    except Exception as e:
        print(f"\n✗ OAuth test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nRegistration system is working correctly.")
    print("Dependencies are properly installed.")
    print("OAuth endpoints are configured.")
    print()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
