"""
Verify that the health endpoint exists and returns the correct format for Render.

Render requires:
- Endpoint: /health
- Response: {"status": "ok"} 
- Status code: 200
"""
import sys
import os
import traceback
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

def test_health_endpoint():
    """Test that health endpoint exists and returns correct format"""
    print("\n" + "="*60)
    print("Testing Health Endpoint for Render Deployment")
    print("="*60)
    
    try:
        # Import the FastAPI app
        from app.main import app
        from fastapi.testclient import TestClient
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print(f"   Make sure you're running from the project root and dependencies are installed")
        raise
    
    client = TestClient(app)
    
    # Test GET request
    print("\n1. Testing GET /health...")
    response = client.get("/health")
    
    print(f"   Status code: {response.status_code}")
    print(f"   Response body: {response.json()}")
    
    # Verify status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    print("   ✅ Status code is 200")
    
    # Verify response format
    response_json = response.json()
    assert "status" in response_json, "Response should contain 'status' key"
    assert response_json["status"] == "ok", f"Expected status='ok', got status='{response_json.get('status')}'"
    print("   ✅ Response format is correct: {'status': 'ok'}")
    
    # Test HEAD request (Render may use this for health checks)
    print("\n2. Testing HEAD /health...")
    response = client.head("/health")
    print(f"   Status code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 for HEAD, got {response.status_code}"
    print("   ✅ HEAD request works correctly")
    
    print("\n" + "="*60)
    print("✅ ALL HEALTH ENDPOINT TESTS PASSED")
    print("="*60)
    print("\nSummary:")
    print("  ✅ Endpoint exists at /health")
    print("  ✅ Returns status code 200")
    print("  ✅ Returns {'status': 'ok'}")
    print("  ✅ Supports both GET and HEAD methods")
    print("\n✅ Health endpoint meets Render requirements!")
    
    return True


if __name__ == "__main__":
    try:
        test_health_endpoint()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)
