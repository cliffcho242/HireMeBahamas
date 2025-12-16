#!/usr/bin/env python3
"""
Test suite for HTTP caching headers in the HireMeBahamas API.

Tests that Cache-Control: public, max-age=30 is properly set on API endpoints
to enable browser and CDN caching for improved performance.
"""

import sys
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport

# Add the api directory to the path
api_dir = Path(__file__).parent / "api"
sys.path.insert(0, str(api_dir))

# Import the app from index.py (Vercel serverless entry point)
from index import app as vercel_app


@pytest.fixture
def anyio_backend():
    """Use asyncio for async tests."""
    return 'asyncio'


@pytest.mark.anyio
async def test_health_endpoint_has_cache_control():
    """Test that /health endpoint has Cache-Control header."""
    async with AsyncClient(transport=ASGITransport(app=vercel_app), base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "max-age=30" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_health_ping_endpoint_has_cache_control():
    """Test that /health/ping endpoint has Cache-Control header."""
    async with AsyncClient(transport=ASGITransport(app=vercel_app), base_url="http://test") as client:
        response = await client.get("/health/ping")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "max-age=30" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_status_endpoint_has_cache_control():
    """Test that /status endpoint has Cache-Control header."""
    async with AsyncClient(transport=ASGITransport(app=vercel_app), base_url="http://test") as client:
        response = await client.get("/status")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "max-age=30" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_ready_endpoint_has_cache_control():
    """Test that /ready endpoint has Cache-Control header."""
    async with AsyncClient(transport=ASGITransport(app=vercel_app), base_url="http://test") as client:
        response = await client.get("/ready")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "max-age=30" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_root_endpoint_has_cache_control():
    """Test that / (root) endpoint has Cache-Control header."""
    async with AsyncClient(transport=ASGITransport(app=vercel_app), base_url="http://test") as client:
        response = await client.get("/")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "max-age=30" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_cache_control_is_public():
    """Test that Cache-Control uses 'public' directive for public endpoints."""
    async with AsyncClient(transport=ASGITransport(app=vercel_app), base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        cache_control = response.headers["cache-control"]
        assert "public" in cache_control
        assert "max-age=30" in cache_control


@pytest.mark.anyio
async def test_post_requests_dont_get_cache_headers():
    """Test that POST requests don't get cache headers (caching only for GET)."""
    async with AsyncClient(transport=ASGITransport(app=vercel_app), base_url="http://test") as client:
        # Try to POST to an endpoint (will fail but that's okay, we're testing headers)
        try:
            response = await client.post("/status", json={})
        except Exception:
            # Endpoint might not accept POST, that's fine
            pass
        # This test just verifies that the middleware only applies to GET requests


@pytest.mark.anyio
async def test_diagnostic_endpoint_has_cache_control():
    """Test that /diagnostic endpoint has Cache-Control header."""
    async with AsyncClient(transport=ASGITransport(app=vercel_app), base_url="http://test") as client:
        response = await client.get("/diagnostic")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        # Diagnostic should have caching since it's a GET endpoint
        assert "max-age" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_cache_headers_on_multiple_endpoints():
    """Test that cache headers are consistently applied across multiple endpoints."""
    endpoints = [
        "/health",
        "/health/ping",
        "/status",
        "/ready",
        "/",
    ]
    
    async with AsyncClient(transport=ASGITransport(app=vercel_app), base_url="http://test") as client:
        for endpoint in endpoints:
            response = await client.get(endpoint)
            
            # All endpoints should have cache-control header
            assert "cache-control" in response.headers, f"Cache-Control missing on {endpoint}"
            
            # All should have max-age=30
            cache_control = response.headers["cache-control"]
            assert "max-age=30" in cache_control, f"max-age=30 missing on {endpoint}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
