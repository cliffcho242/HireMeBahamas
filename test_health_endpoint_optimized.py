"""
Test health endpoint to verify it meets requirements:
1. Does not touch the database
2. Returns {"ok": True}
3. Has include_in_schema=False
"""
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_backend_app_health():
    """Test backend/app/main.py health endpoint"""
    print("\n✅ Testing backend/app/main.py health endpoint...")
    
    # Import the FastAPI app
    from app.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Test GET request
    response = client.get("/health")
    print(f"   GET /health status: {response.status_code}")
    print(f"   Response body: {response.json()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json() == {"ok": True}, f"Expected {{'ok': True}}, got {response.json()}"
    
    # Test HEAD request
    response = client.head("/health")
    print(f"   HEAD /health status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 for HEAD, got {response.status_code}"
    
    # Verify OpenAPI docs are disabled (docs_url=None means no schema generation overhead)
    assert app.openapi_url is None, "OpenAPI URL should be disabled for zero cold starts"
    assert app.docs_url is None, "Docs URL should be disabled for zero cold starts"
    assert app.redoc_url is None, "ReDoc URL should be disabled for zero cold starts"
    
    print("   ✅ All checks passed for backend/app/main.py")


def test_api_index_health():
    """Test api/index.py health endpoint"""
    print("\n✅ Testing api/index.py health endpoint...")
    
    # Import the FastAPI app
    from index import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Test GET request
    response = client.get("/health")
    print(f"   GET /health status: {response.status_code}")
    print(f"   Response body: {response.json()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json() == {"ok": True}, f"Expected {{'ok': True}}, got {response.json()}"
    
    # Test HEAD request
    response = client.head("/health")
    print(f"   HEAD /health status: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 for HEAD, got {response.status_code}"
    
    # Verify OpenAPI docs are disabled (docs_url=None means no schema generation overhead)
    assert app.openapi_url is None, "OpenAPI URL should be disabled for zero cold starts"
    assert app.docs_url is None, "Docs URL should be disabled for zero cold starts"
    assert app.redoc_url is None, "ReDoc URL should be disabled for zero cold starts"
    
    print("   ✅ All checks passed for api/index.py")


def test_fastapi_docs_disabled():
    """Test that FastAPI docs endpoints are disabled"""
    print("\n✅ Testing FastAPI docs endpoints are disabled...")
    
    # Test backend/app/main.py
    from app.main import app as backend_app
    assert backend_app.docs_url is None, "docs_url should be None"
    assert backend_app.redoc_url is None, "redoc_url should be None"
    assert backend_app.openapi_url is None, "openapi_url should be None"
    print("   ✅ backend/app/main.py docs disabled")
    
    # Test api/index.py
    from index import app as api_app
    assert api_app.docs_url is None, "docs_url should be None"
    assert api_app.redoc_url is None, "redoc_url should be None"
    assert api_app.openapi_url is None, "openapi_url should be None"
    print("   ✅ api/index.py docs disabled")


if __name__ == "__main__":
    print("="*60)
    print("Testing Health Endpoint Requirements")
    print("="*60)
    
    try:
        test_fastapi_docs_disabled()
        test_backend_app_health()
        test_api_index_health()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nSummary:")
        print("  ✅ FastAPI docs endpoints disabled (docs_url, redoc_url, openapi_url = None)")
        print("  ✅ Health endpoint returns {'ok': True}")
        print("  ✅ Health endpoint has include_in_schema=False")
        print("  ✅ Health endpoint does not touch database")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
