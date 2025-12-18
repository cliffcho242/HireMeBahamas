"""
Verify that the /api/health endpoint exists and returns the correct format for Render.

Render requires:
- Endpoint: /api/health (case-sensitive)
- Response: {"status": "ok"} 
- Status code: 200
- Must support both GET and HEAD methods
"""
import sys
import os
import traceback
from pathlib import Path

# Add api/backend_app to path (where the main app is located)
api_backend_path = Path(__file__).parent / 'api' / 'backend_app'
sys.path.insert(0, str(api_backend_path))

def test_api_health_endpoint():
    """Test that /api/health endpoint exists and returns correct format"""
    print("\n" + "="*70)
    print("Testing /api/health Endpoint for Render Deployment")
    print("="*70)
    
    try:
        # Import the FastAPI app from backend_app
        from main import app
        from fastapi.testclient import TestClient
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print(f"   Make sure you're running from the project root and dependencies are installed")
        raise
    
    client = TestClient(app)
    
    # Test GET request to /api/health
    print("\n1. Testing GET /api/health...")
    response = client.get("/api/health")
    
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
    print("\n2. Testing HEAD /api/health...")
    response = client.head("/api/health")
    print(f"   Status code: {response.status_code}")
    assert response.status_code == 200, f"Expected 200 for HEAD, got {response.status_code}"
    print("   ✅ HEAD request works correctly")
    
    # Test that the endpoint doesn't require authentication
    print("\n3. Testing /api/health without authentication...")
    response = client.get("/api/health")
    assert response.status_code == 200, "Health check should work without authentication"
    print("   ✅ No authentication required")
    
    # Test response time is fast (should be instant, no DB access)
    print("\n4. Testing response time...")
    import time
    start = time.time()
    response = client.get("/api/health")
    elapsed = (time.time() - start) * 1000  # Convert to milliseconds
    print(f"   Response time: {elapsed:.2f}ms")
    assert elapsed < 100, f"Response should be < 100ms, got {elapsed:.2f}ms"
    print("   ✅ Response time is acceptable (< 100ms)")
    
    print("\n" + "="*70)
    print("✅ ALL /api/health ENDPOINT TESTS PASSED")
    print("="*70)
    print("\nSummary:")
    print("  ✅ Endpoint exists at /api/health (case-sensitive)")
    print("  ✅ Returns status code 200")
    print("  ✅ Returns {'status': 'ok'}")
    print("  ✅ Supports both GET and HEAD methods")
    print("  ✅ No authentication required")
    print("  ✅ Fast response (< 100ms)")
    print("\n✅ Health endpoint meets Render requirements!")
    print("\n📋 Next Steps:")
    print("   1. In Render Dashboard → Your Backend → Settings")
    print("   2. Set Health Check Path: /api/health (case-sensitive)")
    print("   3. After deployment, manually verify:")
    print("      https://hiremebahamas.onrender.com/api/health")
    print("   4. You should see: {'status': 'ok'} or 200 OK")
    
    return True


if __name__ == "__main__":
    try:
        test_api_health_endpoint()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)
