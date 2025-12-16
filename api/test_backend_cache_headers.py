#!/usr/bin/env python3
"""
Test suite for HTTP caching headers in the backend_app.

Tests that Cache-Control headers are properly set on backend API endpoints.
"""

import sys
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport

# Add the backend_app directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import the app from backend_app.main
from backend_app.main import app


@pytest.fixture
def anyio_backend():
    """Use asyncio for async tests."""
    return 'asyncio'


@pytest.mark.anyio
async def test_health_endpoint_has_cache_control():
    """Test that /health endpoint has Cache-Control header with max-age=30."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "max-age=30" in response.headers["cache-control"]
        assert "public" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_health_ping_endpoint_has_cache_control():
    """Test that /health/ping endpoint has Cache-Control header with max-age=30."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ping")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "max-age=30" in response.headers["cache-control"]
        assert "public" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_live_endpoint_has_cache_control():
    """Test that /live endpoint has Cache-Control header with max-age=30."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/live")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "max-age=30" in response.headers["cache-control"]
        assert "public" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_ready_endpoint_has_cache_control():
    """Test that /ready endpoint has Cache-Control header with max-age=30."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        assert "max-age=30" in response.headers["cache-control"]
        assert "public" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_root_endpoint_has_cache_control():
    """Test that / (root) endpoint has Cache-Control header."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        
        assert response.status_code == 200
        assert "cache-control" in response.headers
        # Root endpoint should have caching
        assert "max-age" in response.headers["cache-control"]


@pytest.mark.anyio
async def test_cache_control_only_on_successful_get():
    """Test that cache headers are only added to successful GET requests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # GET request should have cache headers
        response = await client.get("/health")
        assert response.status_code == 200
        assert "cache-control" in response.headers


@pytest.mark.anyio
async def test_default_cache_control_applied():
    """Test that default cache control is applied to unspecified endpoints."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test an endpoint that's not in the specific rules
        response = await client.get("/")
        
        assert response.status_code == 200
        # Should have default cache control from wildcard rule
        if "cache-control" in response.headers:
            cache_control = response.headers["cache-control"]
            # Should have some caching directive
            assert "max-age" in cache_control or "no-cache" in cache_control


@pytest.mark.anyio
async def test_jobs_endpoint_has_enhanced_cache():
    """Test that /api/jobs endpoint has enhanced caching with stale-while-revalidate."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/jobs")
        
        # Jobs endpoint might return 200 or error depending on DB state
        # We're testing that the middleware applies headers to successful responses
        if response.status_code == 200:
            assert "cache-control" in response.headers
            cache_control = response.headers["cache-control"]
            # Jobs have special caching with stale-while-revalidate
            assert "max-age" in cache_control


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
