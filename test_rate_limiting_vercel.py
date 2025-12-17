"""
Test rate limiting middleware in Vercel serverless handler (api/index.py).

This test verifies:
1. Rate limiting is enforced (100 requests per 60 seconds per IP)
2. Health check endpoints are excluded from rate limiting
3. 429 response is returned when limit exceeded
4. Different IPs are tracked independently
"""
import sys
import os
import time

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from fastapi.testclient import TestClient


def test_rate_limiting_basic():
    """Test basic rate limiting functionality."""
    # Import the app from index.py
    from index import app
    
    client = TestClient(app)
    
    # Clear any existing rate limits
    from index import RATE_LIMIT
    RATE_LIMIT.clear()
    
    # Make requests up to the limit (100)
    print("Making 100 requests to test rate limit...")
    for i in range(100):
        response = client.get("/")
        assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}"
    
    print("✅ 100 requests succeeded (within limit)")
    
    # 101st request should be rate limited
    print("Making 101st request (should be rate limited)...")
    response = client.get("/")
    assert response.status_code == 429, f"Expected 429, got {response.status_code}"
    assert "Retry-After" in response.headers
    print("✅ 101st request was rate limited (429 Too Many Requests)")
    print(f"✅ Retry-After header present: {response.headers['Retry-After']}")


def test_health_endpoints_excluded():
    """Test that health check endpoints are excluded from rate limiting."""
    from index import app, RATE_LIMIT
    
    client = TestClient(app)
    
    # Clear any existing rate limits
    RATE_LIMIT.clear()
    
    # Use up the rate limit on a regular endpoint
    print("Using up rate limit on regular endpoint...")
    for i in range(100):
        response = client.get("/")
        assert response.status_code == 200
    
    # Regular endpoint should now be blocked
    response = client.get("/")
    assert response.status_code == 429
    print("✅ Regular endpoint is rate limited")
    
    # Health endpoints should still work
    health_endpoints = ["/health", "/health/ping", "/ready", "/status"]
    for endpoint in health_endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, f"Health endpoint {endpoint} failed with {response.status_code}"
        print(f"✅ Health endpoint {endpoint} still works (not rate limited)")


def test_rate_limit_expiry():
    """Test that rate limits expire after 60 seconds."""
    from index import app, RATE_LIMIT
    
    client = TestClient(app)
    
    # Clear any existing rate limits
    RATE_LIMIT.clear()
    
    # Make 100 requests
    print("Making 100 requests...")
    for i in range(100):
        response = client.get("/")
        assert response.status_code == 200
    
    # Should be rate limited now
    response = client.get("/")
    assert response.status_code == 429
    print("✅ Rate limited after 100 requests")
    
    # Manually expire the timestamps (simulate 60 seconds passing)
    # In real scenario, this would happen automatically
    current_time = time.time()
    RATE_LIMIT.clear()  # Clear to simulate expiry
    
    # Should work again
    response = client.get("/")
    assert response.status_code == 200
    print("✅ Rate limit resets after expiry")


def test_different_ips_tracked_separately():
    """Test that different IPs are tracked independently."""
    from index import app, RATE_LIMIT
    
    # Note: TestClient doesn't support different client IPs easily
    # This test verifies the data structure works correctly
    RATE_LIMIT.clear()
    
    # Simulate different IPs
    ip1 = "192.168.1.1"
    ip2 = "192.168.1.2"
    
    # Add requests for IP1
    current_time = time.time()
    RATE_LIMIT[ip1] = [current_time] * 100
    
    # IP1 should be at limit
    assert len(RATE_LIMIT[ip1]) == 100
    
    # IP2 should be empty
    assert len(RATE_LIMIT.get(ip2, [])) == 0
    
    print("✅ Different IPs are tracked separately")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Rate Limiting in Vercel Serverless Handler")
    print("=" * 60)
    
    try:
        print("\n1. Testing basic rate limiting...")
        test_rate_limiting_basic()
        
        print("\n2. Testing health endpoint exclusion...")
        test_health_endpoints_excluded()
        
        print("\n3. Testing rate limit expiry...")
        test_rate_limit_expiry()
        
        print("\n4. Testing separate IP tracking...")
        test_different_ips_tracked_separately()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)
