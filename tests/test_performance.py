"""
Performance Testing Suite for Facebook/Instagram-Level Response Times

Tests:
- Sub-1s page load time
- 50-150ms API response time
- Zero cold starts
- Cache hit rates >80%
"""
import asyncio
import time
import statistics
from typing import List
import httpx
import pytest

# Target metrics
TARGET_API_RESPONSE_MS = 150  # 50-150ms target
TARGET_PAGE_LOAD_MS = 1000  # Sub-1s target
TARGET_CACHE_HIT_RATE = 0.80  # >80% cache hit rate

# Test configuration
API_BASE_URL = "http://127.0.0.1:8008"  # Local development
FRONTEND_URL = "http://localhost:3000"  # Local frontend
CONCURRENT_REQUESTS = 10  # Simulate concurrent users


@pytest.fixture
async def http_client():
    """Create async HTTP client."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.mark.asyncio
async def test_health_endpoint_response_time(http_client):
    """Test health endpoint responds in <50ms."""
    times = []
    
    # Warm up
    await http_client.get(f"{API_BASE_URL}/health")
    
    # Test 10 times
    for _ in range(10):
        start = time.time()
        response = await http_client.get(f"{API_BASE_URL}/health")
        duration_ms = (time.time() - start) * 1000
        
        assert response.status_code == 200
        times.append(duration_ms)
    
    avg_time = statistics.mean(times)
    max_time = max(times)
    
    print(f"\n✓ Health endpoint average: {avg_time:.2f}ms")
    print(f"  Max time: {max_time:.2f}ms")
    
    # Health endpoint should be <50ms
    assert avg_time < 50, f"Health endpoint too slow: {avg_time:.2f}ms (target: <50ms)"


@pytest.mark.asyncio
async def test_posts_api_response_time(http_client):
    """Test posts API responds in <150ms (with cache)."""
    # First request (cache miss, may be slower)
    start = time.time()
    response = await http_client.get(f"{API_BASE_URL}/api/posts?skip=0&limit=20")
    first_request_ms = (time.time() - start) * 1000
    
    assert response.status_code == 200
    print(f"\n✓ First request (cache miss): {first_request_ms:.2f}ms")
    
    # Subsequent requests (cache hits, should be faster)
    times = []
    for _ in range(10):
        start = time.time()
        response = await http_client.get(f"{API_BASE_URL}/api/posts?skip=0&limit=20")
        duration_ms = (time.time() - start) * 1000
        
        assert response.status_code == 200
        times.append(duration_ms)
    
    avg_time = statistics.mean(times)
    max_time = max(times)
    min_time = min(times)
    
    print(f"✓ Cached requests average: {avg_time:.2f}ms")
    print(f"  Min: {min_time:.2f}ms, Max: {max_time:.2f}ms")
    
    # Cached requests should be significantly faster
    assert avg_time < TARGET_API_RESPONSE_MS, \
        f"API too slow: {avg_time:.2f}ms (target: <{TARGET_API_RESPONSE_MS}ms)"
    
    # At least one request should be <50ms (cache hit)
    assert min_time < 50, \
        f"No fast cache hits: {min_time:.2f}ms (expected: <50ms)"


@pytest.mark.asyncio
async def test_concurrent_requests(http_client):
    """Test API handles concurrent requests efficiently."""
    async def make_request():
        start = time.time()
        response = await http_client.get(f"{API_BASE_URL}/api/posts?skip=0&limit=20")
        duration_ms = (time.time() - start) * 1000
        return response.status_code, duration_ms
    
    # Make concurrent requests
    tasks = [make_request() for _ in range(CONCURRENT_REQUESTS)]
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_time_ms = (time.time() - start_time) * 1000
    
    # All requests should succeed
    for status_code, duration in results:
        assert status_code == 200
    
    # Extract timings
    response_times = [duration for _, duration in results]
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)
    
    print(f"\n✓ {CONCURRENT_REQUESTS} concurrent requests:")
    print(f"  Total time: {total_time_ms:.2f}ms")
    print(f"  Average response: {avg_time:.2f}ms")
    print(f"  Max response: {max_time:.2f}ms")
    
    # Average should still be within target
    assert avg_time < TARGET_API_RESPONSE_MS * 1.5, \
        f"Concurrent requests too slow: {avg_time:.2f}ms"


@pytest.mark.asyncio
async def test_cache_effectiveness(http_client):
    """Test cache hit rate is >80%."""
    # Make 20 requests (10 unique URLs, each repeated)
    cache_hits = 0
    total_requests = 20
    
    for i in range(total_requests):
        # Alternate between 2 URLs
        skip = (i % 2) * 20
        
        start = time.time()
        response = await http_client.get(
            f"{API_BASE_URL}/api/posts?skip={skip}&limit=20"
        )
        duration_ms = (time.time() - start) * 1000
        
        assert response.status_code == 200
        
        # If response is <50ms, likely a cache hit
        if duration_ms < 50:
            cache_hits += 1
    
    cache_hit_rate = cache_hits / total_requests
    print(f"\n✓ Cache hit rate: {cache_hit_rate * 100:.1f}%")
    print(f"  Cache hits: {cache_hits}/{total_requests}")
    
    # Should have >80% cache hit rate
    assert cache_hit_rate >= TARGET_CACHE_HIT_RATE, \
        f"Cache hit rate too low: {cache_hit_rate * 100:.1f}% (target: >{TARGET_CACHE_HIT_RATE * 100}%)"


@pytest.mark.asyncio
async def test_no_cold_starts(http_client):
    """Test that there are no cold starts (connection pool is warm)."""
    # Test multiple requests in quick succession
    times = []
    
    for i in range(5):
        start = time.time()
        response = await http_client.get(f"{API_BASE_URL}/health")
        duration_ms = (time.time() - start) * 1000
        
        assert response.status_code == 200
        times.append(duration_ms)
        
        if i > 0:
            # Subsequent requests should not be significantly slower
            # (indicating cold start/connection setup)
            assert duration_ms < times[0] * 2, \
                f"Possible cold start: request {i+1} took {duration_ms:.2f}ms vs first {times[0]:.2f}ms"
    
    print(f"\n✓ No cold starts detected")
    print(f"  Request times: {[f'{t:.2f}ms' for t in times]}")


@pytest.mark.asyncio
async def test_performance_metrics_endpoint(http_client):
    """Test performance metrics endpoint returns valid data."""
    # Make some requests to generate metrics
    for _ in range(5):
        await http_client.get(f"{API_BASE_URL}/api/posts?skip=0&limit=20")
    
    # Get metrics
    response = await http_client.get(f"{API_BASE_URL}/metrics")
    assert response.status_code == 200
    
    metrics = response.json()
    
    # Validate metrics structure
    assert "requests" in metrics
    assert "cache" in metrics
    assert "endpoints" in metrics
    assert "performance_targets" in metrics
    
    print(f"\n✓ Performance metrics:")
    print(f"  Total requests: {metrics['requests']['total']}")
    print(f"  Avg response time: {metrics['requests']['avg_response_time_ms']}ms")
    print(f"  Cache hit rate: {metrics['cache']['hit_rate']}%")


def test_frontend_bundle_size():
    """Test frontend bundle size is reasonable for sub-1s load."""
    import os
    import glob
    
    # Path to frontend dist directory
    dist_dir = "frontend/dist/assets"
    
    if not os.path.exists(dist_dir):
        pytest.skip("Frontend not built, run 'npm run build' first")
    
    # Get all JS files
    js_files = glob.glob(f"{dist_dir}/*.js")
    
    total_size = 0
    for file in js_files:
        size = os.path.getsize(file)
        total_size += size
        print(f"  {os.path.basename(file)}: {size / 1024:.1f}KB")
    
    total_size_kb = total_size / 1024
    print(f"\n✓ Total JS bundle size: {total_size_kb:.1f}KB")
    
    # Target: <500KB for fast loading (compressed will be much smaller)
    assert total_size_kb < 500, \
        f"Bundle too large: {total_size_kb:.1f}KB (target: <500KB)"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
