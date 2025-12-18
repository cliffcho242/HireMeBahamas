"""
Test HEAD method support for root and health endpoints.

This test verifies that HEAD requests return 200 status without 405 errors,
which fixes the Render/Gunicorn warning logs.
"""
from fastapi.testclient import TestClient


def test_head_root_endpoint():
    """Test HEAD request to root endpoint returns 200"""
    # Import here to avoid import-time side effects
    from api.backend_app.main import app
    
    client = TestClient(app)
    response = client.head("/")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # HEAD requests should have empty body
    assert response.content == b"", "HEAD response should have empty body"


def test_head_health_endpoint():
    """Test HEAD request to /health endpoint returns 200"""
    from api.backend_app.main import app
    
    client = TestClient(app)
    response = client.head("/health")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # HEAD requests should have empty body
    assert response.content == b"", "HEAD response should have empty body"


def test_head_api_health_endpoint():
    """Test HEAD request to /api/health endpoint returns 200"""
    from api.backend_app.main import app
    
    client = TestClient(app)
    response = client.head("/api/health")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # HEAD requests should have empty body
    assert response.content == b"", "HEAD response should have empty body"


def test_head_live_endpoint():
    """Test HEAD request to /live endpoint returns 200"""
    from api.backend_app.main import app
    
    client = TestClient(app)
    response = client.head("/live")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # HEAD requests should have empty body
    assert response.content == b"", "HEAD response should have empty body"


def test_head_ready_endpoint():
    """Test HEAD request to /ready endpoint returns 200"""
    from api.backend_app.main import app
    
    client = TestClient(app)
    response = client.head("/ready")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # HEAD requests should have empty body
    assert response.content == b"", "HEAD response should have empty body"


def test_get_still_works():
    """Verify GET requests still work after adding HEAD support"""
    from api.backend_app.main import app
    
    client = TestClient(app)
    
    # Test GET /
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Test GET /health
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
    # Test GET /api/health
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


if __name__ == "__main__":
    # Run tests
    print("Testing HEAD method support...")
    test_head_root_endpoint()
    print("✅ HEAD / works")
    
    test_head_health_endpoint()
    print("✅ HEAD /health works")
    
    test_head_api_health_endpoint()
    print("✅ HEAD /api/health works")
    
    test_head_live_endpoint()
    print("✅ HEAD /live works")
    
    test_head_ready_endpoint()
    print("✅ HEAD /ready works")
    
    test_get_still_works()
    print("✅ GET requests still work")
    
    print("\n✅ All HEAD method tests passed!")
