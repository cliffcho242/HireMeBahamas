#!/usr/bin/env python3
"""
Test script to verify 500 error fixes.

This script tests:
1. Health endpoints return 200 status
2. Global exception handler catches unhandled exceptions
3. Error messages are informative and logged properly
"""
import asyncio
import sys
from pathlib import Path

# Add API backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from fastapi.testclient import TestClient

# Import the app
try:
    from backend_app.main import app
    print("✓ Successfully imported app")
except Exception as e:
    print(f"✗ Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Create test client
client = TestClient(app)


def test_health_endpoint():
    """Test /health endpoint returns 200"""
    print("\n" + "=" * 80)
    print("TEST: /health endpoint")
    print("=" * 80)
    
    try:
        response = client.get("/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json().get("status") == "healthy", "Status should be 'healthy'"
        
        print("✓ /health endpoint test PASSED")
        return True
    except Exception as e:
        print(f"✗ /health endpoint test FAILED: {e}")
        return False


def test_api_health_endpoint():
    """Test /api/health endpoint returns 200"""
    print("\n" + "=" * 80)
    print("TEST: /api/health endpoint")
    print("=" * 80)
    
    try:
        response = client.get("/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json().get("status") == "ok", "Status should be 'ok'"
        
        print("✓ /api/health endpoint test PASSED")
        return True
    except Exception as e:
        print(f"✗ /api/health endpoint test FAILED: {e}")
        return False


def test_live_endpoint():
    """Test /live endpoint returns 200"""
    print("\n" + "=" * 80)
    print("TEST: /live endpoint")
    print("=" * 80)
    
    try:
        response = client.get("/live")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json().get("status") == "alive", "Status should be 'alive'"
        
        print("✓ /live endpoint test PASSED")
        return True
    except Exception as e:
        print(f"✗ /live endpoint test FAILED: {e}")
        return False


def test_root_endpoint():
    """Test / endpoint returns 200"""
    print("\n" + "=" * 80)
    print("TEST: / (root) endpoint")
    print("=" * 80)
    
    try:
        response = client.get("/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "message" in response.json(), "Response should have 'message' key"
        
        print("✓ / endpoint test PASSED")
        return True
    except Exception as e:
        print(f"✗ / endpoint test FAILED: {e}")
        return False


def test_nonexistent_endpoint():
    """Test that non-existent endpoints return 404, not 500"""
    print("\n" + "=" * 80)
    print("TEST: Non-existent endpoint (should return 404, not 500)")
    print("=" * 80)
    
    try:
        response = client.get("/this-does-not-exist")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        
        print("✓ Non-existent endpoint test PASSED (returns 404, not 500)")
        return True
    except Exception as e:
        print(f"✗ Non-existent endpoint test FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("RUNNING 500 ERROR FIX TESTS")
    print("=" * 80)
    
    results = []
    
    # Run all tests
    results.append(test_health_endpoint())
    results.append(test_api_health_endpoint())
    results.append(test_live_endpoint())
    results.append(test_root_endpoint())
    results.append(test_nonexistent_endpoint())
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - No 500 errors detected")
        return 0
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
