#!/usr/bin/env python3
"""
Test suite for security headers in the HireMeBahamas API.

Tests SSL/TLS and CDN security headers to ensure:
- HSTS (HTTP Strict Transport Security) is properly configured
- Security headers like X-Content-Type-Options, X-Frame-Options are present
- Permissions-Policy header restricts browser features
- All headers follow security best practices
"""

import sys
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.main import app


@pytest.fixture
def anyio_backend():
    """Use asyncio for async tests."""
    return 'asyncio'


@pytest.mark.anyio
async def test_hsts_header_present():
    """Test that HSTS (HTTP Strict Transport Security) header is present."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ping")
        
        assert response.status_code == 200
        assert "strict-transport-security" in response.headers
        
        hsts_value = response.headers["strict-transport-security"]
        assert "max-age=31536000" in hsts_value
        assert "includeSubDomains" in hsts_value
        assert "preload" in hsts_value


@pytest.mark.anyio
async def test_x_content_type_options_header():
    """Test that X-Content-Type-Options header is set to nosniff."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ping")
        
        assert response.status_code == 200
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"


@pytest.mark.anyio
async def test_x_frame_options_header():
    """Test that X-Frame-Options header is set to DENY."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ping")
        
        assert response.status_code == 200
        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"


@pytest.mark.anyio
async def test_x_xss_protection_header():
    """Test that X-XSS-Protection header is enabled."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ping")
        
        assert response.status_code == 200
        assert "x-xss-protection" in response.headers
        assert "1; mode=block" in response.headers["x-xss-protection"]


@pytest.mark.anyio
async def test_referrer_policy_header():
    """Test that Referrer-Policy header is properly set."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ping")
        
        assert response.status_code == 200
        assert "referrer-policy" in response.headers
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


@pytest.mark.anyio
async def test_permissions_policy_header():
    """Test that Permissions-Policy header restricts browser features."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ping")
        
        assert response.status_code == 200
        assert "permissions-policy" in response.headers
        
        policy_value = response.headers["permissions-policy"]
        # Check that sensitive features are restricted
        assert "camera=()" in policy_value
        assert "microphone=()" in policy_value


@pytest.mark.anyio
async def test_dns_prefetch_control_header():
    """Test that X-DNS-Prefetch-Control header is enabled for performance."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health/ping")
        
        assert response.status_code == 200
        assert "x-dns-prefetch-control" in response.headers
        assert response.headers["x-dns-prefetch-control"] == "on"


@pytest.mark.anyio
async def test_security_headers_on_all_endpoints():
    """Test that security headers are present on various API endpoints."""
    endpoints = [
        "/health/ping",
        "/health",
        "/live",
        "/",
    ]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for endpoint in endpoints:
            response = await client.get(endpoint)
            
            # All endpoints should have security headers
            assert "strict-transport-security" in response.headers, f"HSTS missing on {endpoint}"
            assert "x-content-type-options" in response.headers, f"X-Content-Type-Options missing on {endpoint}"
            assert "x-frame-options" in response.headers, f"X-Frame-Options missing on {endpoint}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
