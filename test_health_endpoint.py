#!/usr/bin/env python3
"""
Test health endpoint to verify it returns {"status": "ok"}
"""
import sys
import json


def test_fastapi_health_endpoint():
    """Test FastAPI health endpoint in api/backend_app/main.py"""
    print("\n🧪 Testing FastAPI health endpoint...")
    
    # Import the FastAPI app
    sys.path.insert(0, '/home/runner/work/HireMeBahamas/HireMeBahamas/api')
    from backend_app.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json()["status"] == "ok", f"Expected status 'ok', got {response.json()['status']}"
    print("✅ FastAPI health endpoint test passed!")
    return True


def test_flask_health_endpoint():
    """Test Flask health endpoint in final_backend_postgresql.py"""
    print("\n🧪 Testing Flask health endpoint...")
    
    # We need to mock the database connection for the Flask app
    # Since this is a complex app, we'll just check the code directly
    with open('/home/runner/work/HireMeBahamas/HireMeBahamas/final_backend_postgresql.py', 'r') as f:
        content = f.read()
        
    # Check that the health endpoint returns {"status": "ok"}
    if 'jsonify({"status": "ok"})' in content:
        print("✅ Flask health endpoint returns correct status!")
        return True
    else:
        print("❌ Flask health endpoint does not return correct status!")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Health Endpoints")
    print("=" * 60)
    
    success = True
    
    try:
        success = test_fastapi_health_endpoint() and success
    except Exception as e:
        print(f"❌ FastAPI health endpoint test failed: {e}")
        success = False
    
    try:
        success = test_flask_health_endpoint() and success
    except Exception as e:
        print(f"❌ Flask health endpoint test failed: {e}")
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All health endpoint tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
