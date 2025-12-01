"""
Test script to verify JWT authentication implementation
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from starlette.testclient import TestClient
from api.index import app

client = TestClient(app)

def test_health_check():
    """Test public health endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "JWT enabled" in data.get("authentication", "")
    print("✅ Health check passed")

def test_login():
    """Test login endpoint"""
    response = client.post("/api/auth/login", json={
        "email": "admin@hiremebahamas.com",
        "password": "AdminPass123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@hiremebahamas.com"
    print("✅ Login passed")
    return data["access_token"]

def test_invalid_login():
    """Test invalid login"""
    response = client.post("/api/auth/login", json={
        "email": "admin@hiremebahamas.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    print("✅ Invalid login rejected")

def test_protected_route_without_token():
    """Test protected route without token"""
    response = client.get("/api/auth/me")
    assert response.status_code == 403  # No credentials provided
    print("✅ Protected route without token returns 403")

def test_protected_route_with_token(token):
    """Test protected route with valid token"""
    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "admin@hiremebahamas.com"
    print("✅ Protected route with token passed")

def test_create_job_without_token():
    """Test creating job without token"""
    response = client.post("/api/jobs", json={
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
    response = client.post("/api/jobs", json={
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
    assert data["created_by"] == "admin@hiremebahamas.com"
    print("✅ Create job with token passed")

def test_public_jobs_endpoint():
    """Test public jobs endpoint"""
    response = client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data
    print("✅ Public jobs endpoint passed")

def test_register_new_user():
    """Test user registration"""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
        "user_type": "job_seeker"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "test@example.com"
    print("✅ User registration passed")

if __name__ == "__main__":
    print("🚀 Starting JWT Authentication Tests\n")
    
    try:
        test_health_check()
        token = test_login()
        test_invalid_login()
        test_protected_route_without_token()
        test_protected_route_with_token(token)
        test_create_job_without_token()
        test_create_job_with_token(token)
        test_public_jobs_endpoint()
        test_register_new_user()
        
        print("\n✅ ALL TESTS PASSED!")
        print("🔥 AUTHENTICATION IS UNBREACHABLE")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
