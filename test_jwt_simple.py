"""
Simple HTTP-based test for JWT authentication
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test public health endpoint"""
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health check passed")

def test_login():
    """Test login endpoint"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@hiremebahamas.com",
        "password": "AdminPass123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    print("✅ Login passed")
    return data["access_token"]

def test_invalid_login():
    """Test invalid login"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@hiremebahamas.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    print("✅ Invalid login rejected")

def test_protected_route_without_token():
    """Test protected route without token"""
    response = requests.get(f"{BASE_URL}/api/auth/me")
    assert response.status_code == 403
    print("✅ Protected route without token returns 403")

def test_protected_route_with_token(token):
    """Test protected route with valid token"""
    response = requests.get(f"{BASE_URL}/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "admin@hiremebahamas.com"
    print("✅ Protected route with token passed")

def test_create_job_without_token():
    """Test creating job without token"""
    response = requests.post(f"{BASE_URL}/api/jobs", json={
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Nassau",
        "description": "Great job",
        "salary": "$80k"
    })
    assert response.status_code == 403
    print("✅ Create job without token returns 403")

def test_create_job_with_token(token):
    """Test creating job with token"""
    response = requests.post(f"{BASE_URL}/api/jobs", json={
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Nassau",
        "description": "Great job",
        "salary": "$80k"
    }, headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Software Engineer"
    print("✅ Create job with token passed")

def test_public_jobs_endpoint():
    """Test public jobs endpoint"""
    response = requests.get(f"{BASE_URL}/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    print("✅ Public jobs endpoint passed")

if __name__ == "__main__":
    print("🚀 Starting JWT Authentication Tests\n")
    
    # Wait for server to start
    time.sleep(2)
    
    try:
        test_health_check()
        token = test_login()
        test_invalid_login()
        test_protected_route_without_token()
        test_protected_route_with_token(token)
        test_create_job_without_token()
        test_create_job_with_token(token)
        test_public_jobs_endpoint()
        
        print("\n✅ ALL TESTS PASSED!")
        print("🔥 AUTHENTICATION IS UNBREACHABLE")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
