"""
Integration test for the health router endpoint through FastAPI app.
"""
import sys
import os

# Add backend_app to path
backend_path = os.path.join(os.path.dirname(__file__), 'api', 'backend_app')
parent_path = os.path.join(os.path.dirname(__file__), 'api')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

# Suppress database warnings during test
os.environ['DATABASE_URL'] = 'sqlite:///test.db'

def test_health_ping_integration():
    """Test /health/ping endpoint through FastAPI app"""
    print("Testing /health/ping endpoint through FastAPI app...")
    
    # Import after setting up paths
    from fastapi.testclient import TestClient
    from backend_app.main import app
    
    # Create test client
    client = TestClient(app)
    
    # Test GET request to /health/ping
    response = client.get("/health/ping")
    print(f"GET /health/ping status code: {response.status_code}")
    print(f"Response body: {response.json()}")
    
    # Verify response
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert response.json() == {"status": "ok"}, f"Expected {{'status': 'ok'}}, got {response.json()}"
    
    print("✅ Health endpoint integration test passed!")

if __name__ == "__main__":
    test_health_ping_integration()
    print("\n✅ All integration tests passed!")
