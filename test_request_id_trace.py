"""
Test Request ID Trace Middleware Implementation

Tests that the X-Request-ID header is properly added to responses
for request tracing (like Facebook's debugging system).
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the api directory to the path for imports
PROJECT_ROOT = Path(__file__).parent
API_DIR = PROJECT_ROOT / "api"
sys.path.insert(0, str(API_DIR))

# Set test environment to avoid database requirements
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost/test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"

from fastapi.testclient import TestClient


def test_request_id_header_present():
    """Test that X-Request-ID header is present in responses"""
    # Import here after environment is set
    from backend_app.main import app
    
    client = TestClient(app)
    
    # Make a request to the health endpoint
    response = client.get("/health")
    
    # Check that the response is successful
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Check that X-Request-ID header is present
    assert "X-Request-ID" in response.headers, "X-Request-ID header not found in response"
    
    # Check that X-Request-ID is a valid UUID
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0, "X-Request-ID is empty"
    
    # UUID should have hyphens in the standard format
    assert "-" in request_id, f"X-Request-ID doesn't look like a UUID: {request_id}"
    
    print(f"✓ X-Request-ID header present: {request_id}")
    return True


def test_request_id_unique():
    """Test that each request gets a unique request ID"""
    from backend_app.main import app
    
    client = TestClient(app)
    
    # Make multiple requests
    request_ids = []
    for i in range(5):
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        request_ids.append(response.headers["X-Request-ID"])
    
    # Check that all request IDs are unique
    unique_ids = set(request_ids)
    assert len(unique_ids) == len(request_ids), f"Request IDs are not unique: {request_ids}"
    
    print(f"✓ All {len(request_ids)} requests have unique request IDs")
    return True


def test_request_id_in_state():
    """Test that request.state.id is set correctly"""
    from backend_app.main import app
    from fastapi import Request
    
    # Create a test endpoint that returns the request.state.id
    @app.get("/test-request-state")
    async def test_endpoint(request: Request):
        return {
            "id": getattr(request.state, "id", None),
            "request_id": getattr(request.state, "request_id", None)
        }
    
    client = TestClient(app)
    
    # Make a request to the test endpoint
    response = client.get("/test-request-state")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check that request.state.id is set
    assert data["id"] is not None, "request.state.id is not set"
    assert len(data["id"]) > 0, "request.state.id is empty"
    
    # Check that request.state.request_id is also set (short version for logging)
    assert data["request_id"] is not None, "request.state.request_id is not set"
    
    # Check that the X-Request-ID header matches request.state.id
    request_id_header = response.headers.get("X-Request-ID")
    assert request_id_header == data["id"], \
        f"X-Request-ID header ({request_id_header}) doesn't match request.state.id ({data['id']})"
    
    print(f"✓ request.state.id is set correctly: {data['id']}")
    print(f"✓ request.state.request_id (short): {data['request_id']}")
    print(f"✓ X-Request-ID header matches request.state.id")
    return True


def test_request_id_on_different_endpoints():
    """Test that X-Request-ID is added to different endpoints"""
    from backend_app.main import app
    
    client = TestClient(app)
    
    # Test different endpoints
    endpoints = [
        "/health",
        "/live",
        "/ready",
        "/",
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        
        # All should return 200
        assert response.status_code == 200, \
            f"Endpoint {endpoint} returned {response.status_code}"
        
        # All should have X-Request-ID header
        assert "X-Request-ID" in response.headers, \
            f"X-Request-ID header not found for endpoint {endpoint}"
        
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 0, \
            f"X-Request-ID is empty for endpoint {endpoint}"
        
        print(f"✓ {endpoint} has X-Request-ID: {request_id}")
    
    return True


def run_tests():
    """Run all tests"""
    tests = [
        ("Request ID Header Present", test_request_id_header_present),
        ("Request ID Unique", test_request_id_unique),
        ("Request ID in State", test_request_id_in_state),
        ("Request ID on Different Endpoints", test_request_id_on_different_endpoints),
    ]
    
    print("=" * 70)
    print("TESTING REQUEST ID TRACE MIDDLEWARE")
    print("=" * 70)
    print()
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 70)
        try:
            test_func()
            passed += 1
            print(f"✓ {name} PASSED\n")
        except Exception as e:
            failed += 1
            print(f"✗ {name} FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - REQUEST ID TRACING IS WORKING!\n")
        return 0
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED - PLEASE FIX BEFORE DEPLOYMENT\n")
        return 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
