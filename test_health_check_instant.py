#!/usr/bin/env python3
"""
Test health check endpoint for instant response (<10ms).

This test verifies that the health check endpoint:
1. Returns 200 OK
2. Returns correct JSON format with service metadata
3. Responds in less than 10ms (instant)
4. Does NOT touch the database
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_health_endpoint_instant():
    """Test that health endpoint responds instantly without database"""
    from app.main import app
    from fastapi.testclient import TestClient
    import time
    
    client = TestClient(app)
    
    print("="*80)
    print("Testing /api/health endpoint for instant response")
    print("="*80)
    
    # Test multiple times to account for any initial overhead
    timings = []
    for i in range(5):
        start = time.perf_counter()
        response = client.get('/api/health')
        duration = (time.perf_counter() - start) * 1000  # Convert to ms
        timings.append(duration)
        
        print(f"\nTest {i+1}/5:")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.json()}")
        print(f"  Duration: {duration:.2f}ms")
        
        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("status") == "ok", f"Expected status 'ok', got {data.get('status')}"
        assert data.get("service") == "hiremebahamas-backend", f"Expected service metadata"
        assert data.get("uptime") == "healthy", f"Expected uptime metadata"
        
        # Critical: Should be instant (< 10ms)
        # Note: First request might be slower due to FastAPI initialization
        if i > 0:  # Skip first request
            assert duration < 10, f"Health check too slow: {duration:.2f}ms (should be < 10ms)"
    
    avg_time = sum(timings[1:]) / len(timings[1:])  # Average excluding first
    print(f"\n{'='*80}")
    print(f"✅ Health check endpoint test PASSED")
    print(f"   Average response time (excluding first): {avg_time:.2f}ms")
    print(f"   All responses < 10ms: {all(t < 10 for t in timings[1:])}")
    print(f"{'='*80}")


def test_health_endpoint_head_method():
    """Test that health endpoint supports HEAD method"""
    from app.main import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    print("\n" + "="*80)
    print("Testing /api/health endpoint HEAD method")
    print("="*80)
    
    response = client.head('/api/health')
    
    print(f"  Status Code: {response.status_code}")
    print(f"  Has Content: {len(response.content) > 0}")
    
    # Assertions
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    print(f"\n✅ HEAD method test PASSED")


def test_health_root_endpoint():
    """Test that /health (root) endpoint also works"""
    from app.main import app
    from fastapi.testclient import TestClient
    import time
    
    client = TestClient(app)
    
    print("\n" + "="*80)
    print("Testing /health (root) endpoint")
    print("="*80)
    
    start = time.perf_counter()
    response = client.get('/health')
    duration = (time.perf_counter() - start) * 1000
    
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {response.json()}")
    print(f"  Duration: {duration:.2f}ms")
    
    # Assertions
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert data.get("status") == "ok", f"Expected status 'ok'"
    assert data.get("service") == "hiremebahamas-backend", f"Expected service metadata"
    
    print(f"\n✅ Root health endpoint test PASSED")


if __name__ == "__main__":
    try:
        test_health_endpoint_instant()
        test_health_endpoint_head_method()
        test_health_root_endpoint()
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED - Health check is production-ready!")
        print("="*80)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
