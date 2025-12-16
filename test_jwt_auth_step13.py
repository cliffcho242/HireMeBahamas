"""
Test for STEP 13 JWT Authentication Implementation
Validates config.py and auth/jwt.py functionality
"""
import os
import sys
from datetime import datetime, timedelta

# Set test environment variables
os.environ["ENV"] = "development"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
os.environ["JWT_SECRET"] = "test-secret-key-for-step-13"

def test_config():
    """Test config.py module"""
    print("Testing config.py...")
    from app.config import ENV, DATABASE_URL, JWT_SECRET, JWT_ALGORITHM
    
    assert ENV == "development", f"ENV should be 'development', got {ENV}"
    assert DATABASE_URL == "postgresql://test:test@localhost:5432/test", "DATABASE_URL not set correctly"
    assert JWT_SECRET == "test-secret-key-for-step-13", "JWT_SECRET not set correctly"
    assert JWT_ALGORITHM == "HS256", f"JWT_ALGORITHM should be 'HS256', got {JWT_ALGORITHM}"
    
    print("✓ config.py validated successfully")
    return True


def test_jwt_functions():
    """Test JWT token creation and decoding"""
    print("\nTesting auth/jwt.py...")
    from app.auth.jwt import create_access_token, create_refresh_token, decode_token
    
    # Test access token creation
    user_id = "test_user_123"
    access_token = create_access_token(user_id)
    assert isinstance(access_token, str), "Access token should be a string"
    assert len(access_token) > 50, "Access token seems too short"
    print(f"✓ Access token created: {access_token[:50]}...")
    
    # Test access token decoding
    decoded = decode_token(access_token)
    assert decoded["sub"] == user_id, f"User ID mismatch: expected {user_id}, got {decoded['sub']}"
    assert decoded["type"] == "access", f"Token type should be 'access', got {decoded['type']}"
    assert "exp" in decoded, "Token should have expiration"
    assert "iat" in decoded, "Token should have issued at time"
    print(f"✓ Access token decoded successfully: {decoded}")
    
    # Test refresh token creation
    refresh_token = create_refresh_token(user_id)
    assert isinstance(refresh_token, str), "Refresh token should be a string"
    assert len(refresh_token) > 50, "Refresh token seems too short"
    print(f"✓ Refresh token created: {refresh_token[:50]}...")
    
    # Test refresh token decoding
    decoded_refresh = decode_token(refresh_token)
    assert decoded_refresh["sub"] == user_id, f"User ID mismatch in refresh token"
    assert decoded_refresh["type"] == "refresh", f"Token type should be 'refresh', got {decoded_refresh['type']}"
    print(f"✓ Refresh token decoded successfully: {decoded_refresh}")
    
    # Test custom expiration for access token
    custom_delta = timedelta(minutes=5)
    custom_access = create_access_token(user_id, expires_delta=custom_delta)
    decoded_custom = decode_token(custom_access)
    exp_time = datetime.fromtimestamp(decoded_custom["exp"])
    iat_time = datetime.fromtimestamp(decoded_custom["iat"])
    time_diff = (exp_time - iat_time).total_seconds()
    assert 290 <= time_diff <= 310, f"Custom expiration not working correctly: {time_diff} seconds"
    print(f"✓ Custom expiration working: {time_diff} seconds")
    
    print("✓ auth/jwt.py validated successfully")
    return True


def test_auth_router():
    """Test auth router endpoints"""
    print("\nTesting auth/router.py...")
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from app.auth.router import router
    
    # Create a test app
    app = FastAPI()
    app.include_router(router)
    
    client = TestClient(app)
    
    # Test login endpoint
    response = client.post("/auth/login")
    assert response.status_code == 200, f"Login should return 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "logged_in", f"Expected 'logged_in', got {data.get('status')}"
    
    # Check cookies are set
    assert "access_token" in response.cookies, "access_token cookie not set"
    assert "refresh_token" in response.cookies, "refresh_token cookie not set"
    
    # Verify cookie attributes
    access_cookie = response.cookies.get("access_token")
    print(f"✓ Login successful, access_token cookie: {access_cookie[:30]}...")
    
    # Test logout endpoint
    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 200, f"Logout should return 200"
    logout_data = logout_response.json()
    assert logout_data["status"] == "logged_out", "Logout status should be 'logged_out'"
    print("✓ Logout successful")
    
    # Test refresh endpoint
    refresh_response = client.post("/auth/refresh")
    assert refresh_response.status_code == 200, f"Refresh should return 200"
    refresh_data = refresh_response.json()
    assert refresh_data["status"] == "token_refreshed", "Refresh status should be 'token_refreshed'"
    print("✓ Token refresh successful")
    
    print("✓ auth/router.py validated successfully")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("STEP 13 JWT Authentication Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Config
        test_config()
        
        # Test 2: JWT Functions
        test_jwt_functions()
        
        # Test 3: Auth Router
        test_auth_router()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - STEP 13 Implementation Verified")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
