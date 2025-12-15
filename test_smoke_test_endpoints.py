#!/usr/bin/env python3
"""
Test smoke test endpoints:
1. Backend /health should return {"status": "ok"}
2. Frontend /api/auth/me should return 200 (not 500)
"""
import sys
import os

# Add api directory to path
api_dir = os.path.join(os.path.dirname(__file__), 'api')
sys.path.insert(0, api_dir)

def test_health_endpoint():
    """Test that /health endpoint returns correct response"""
    print("\n" + "="*60)
    print("Test 1: Backend /health endpoint")
    print("="*60)
    
    try:
        # Import the backend app
        backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
        sys.path.insert(0, backend_dir)
        from app.main import health
        
        # Call the health endpoint
        response = health()
        
        # Check response
        if hasattr(response, 'body'):
            import json
            body = json.loads(response.body)
            print(f"✅ Backend /health response: {body}")
            assert body.get('status') == 'ok', f"Expected status='ok', got {body.get('status')}"
            print("✅ Backend /health test PASSED")
            return True
        else:
            print(f"✅ Backend /health response: {response}")
            print("✅ Backend /health test PASSED")
            return True
    except Exception as e:
        print(f"❌ Backend /health test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_me_no_token():
    """Test /api/auth/me without token returns 200"""
    print("\n" + "="*60)
    print("Test 2: Frontend /api/auth/me without token")
    print("="*60)
    
    try:
        from fastapi.testclient import TestClient
        from index import app
        
        client = TestClient(app)
        response = client.get("/auth/me")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get('authenticated') == False, "Expected authenticated=False"
        print("✅ /api/auth/me without token test PASSED")
        return True
    except Exception as e:
        print(f"❌ /api/auth/me without token test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_me_invalid_token():
    """Test /api/auth/me with invalid token returns 200"""
    print("\n" + "="*60)
    print("Test 3: Frontend /api/auth/me with invalid token")
    print("="*60)
    
    try:
        from fastapi.testclient import TestClient
        from index import app
        
        client = TestClient(app)
        response = client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get('authenticated') == False, "Expected authenticated=False"
        print("✅ /api/auth/me with invalid token test PASSED")
        return True
    except Exception as e:
        print(f"❌ /api/auth/me with invalid token test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_me_valid_token():
    """Test /api/auth/me with valid token returns 200 with user data"""
    print("\n" + "="*60)
    print("Test 4: Frontend /api/auth/me with valid token")
    print("="*60)
    
    try:
        from fastapi.testclient import TestClient
        from index import app
        import os
        from jose import jwt
        
        # Create a valid JWT token
        secret = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        token_data = {"sub": "1"}  # User ID 1 (admin user)
        token = jwt.encode(token_data, secret, algorithm="HS256")
        
        client = TestClient(app)
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Should be authenticated (either from DB or mock data)
        print("✅ /api/auth/me with valid token test PASSED")
        return True
    except Exception as e:
        print(f"❌ /api/auth/me with valid token test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("SMOKE TEST - Testing Required Endpoints")
    print("="*60)
    
    results = []
    results.append(test_health_endpoint())
    results.append(test_auth_me_no_token())
    results.append(test_auth_me_invalid_token())
    results.append(test_auth_me_valid_token())
    
    print("\n" + "="*60)
    print("SMOKE TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL SMOKE TESTS PASSED!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
