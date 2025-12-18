"""
Test CORS configuration with credentials support.

This test verifies:
1. CORS is configured with allow_credentials=True
2. Explicit origins are configured (no wildcard *)
3. Proper CORS headers are returned
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_cors_headers_present_on_preflight():
    """Test that CORS headers are present on OPTIONS preflight requests."""
    # Make OPTIONS request (preflight)
    response = client.options(
        "/api/auth/me",
        headers={
            "Origin": "https://www.hiremebahamas.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        }
    )
    
    # Check that CORS headers are present
    assert "access-control-allow-origin" in response.headers, \
        "Missing Access-Control-Allow-Origin header"
    assert "access-control-allow-credentials" in response.headers, \
        "Missing Access-Control-Allow-Credentials header"


def test_cors_allows_credentials():
    """Test that CORS configuration allows credentials.
    
    Verifies that Access-Control-Allow-Credentials header is set to 'true'.
    """
    # Make OPTIONS request
    response = client.options(
        "/api/auth/me",
        headers={
            "Origin": "https://www.hiremebahamas.com",
            "Access-Control-Request-Method": "GET",
        }
    )
    
    # Check that credentials are allowed
    credentials_header = response.headers.get("access-control-allow-credentials", "").lower()
    assert credentials_header == "true", \
        f"Expected Access-Control-Allow-Credentials: true, got {credentials_header}"


def test_cors_has_explicit_origin():
    """Test that CORS uses explicit origin (not wildcard *).
    
    When credentials are enabled, CORS must use explicit origins.
    Wildcard (*) is not allowed with credentials.
    """
    # Make OPTIONS request
    response = client.options(
        "/api/auth/me",
        headers={
            "Origin": "https://www.hiremebahamas.com",
            "Access-Control-Request-Method": "GET",
        }
    )
    
    # Check origin header
    origin_header = response.headers.get("access-control-allow-origin", "")
    
    # Should NOT be wildcard
    assert origin_header != "*", \
        "CORS origin must not be wildcard (*) when credentials are enabled"
    
    # Should be explicit origin
    assert origin_header in [
        "https://www.hiremebahamas.com",
        "https://hiremebahamas.com"
    ], f"Expected explicit origin, got {origin_header}"


def test_cors_production_origin_allowed():
    """Test that production origin is allowed."""
    # Make request with production origin
    response = client.get(
        "/health",
        headers={"Origin": "https://www.hiremebahamas.com"}
    )
    
    # Check CORS headers
    assert response.status_code == 200
    origin_header = response.headers.get("access-control-allow-origin", "")
    assert origin_header == "https://www.hiremebahamas.com", \
        f"Production origin should be allowed, got {origin_header}"


def test_cors_allows_authorization_header():
    """Test that CORS allows Authorization header.
    
    The Authorization header is required for JWT authentication.
    """
    # Make OPTIONS request
    response = client.options(
        "/api/auth/me",
        headers={
            "Origin": "https://www.hiremebahamas.com",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        }
    )
    
    # Check that Authorization header is allowed
    allowed_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "authorization" in allowed_headers, \
        f"Authorization header should be allowed, got {allowed_headers}"


def test_cors_allows_content_type_header():
    """Test that CORS allows Content-Type header.
    
    The Content-Type header is required for JSON requests.
    """
    # Make OPTIONS request
    response = client.options(
        "/api/auth/login",
        headers={
            "Origin": "https://www.hiremebahamas.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )
    
    # Check that Content-Type header is allowed
    allowed_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "content-type" in allowed_headers, \
        f"Content-Type header should be allowed, got {allowed_headers}"


def test_cors_allows_required_methods():
    """Test that CORS allows required HTTP methods.
    
    Should allow: GET, POST, PUT, DELETE
    """
    required_methods = ["GET", "POST", "PUT", "DELETE"]
    
    for method in required_methods:
        # Make OPTIONS request
        response = client.options(
            "/api/auth/me",
            headers={
                "Origin": "https://www.hiremebahamas.com",
                "Access-Control-Request-Method": method,
            }
        )
        
        # Check that method is allowed
        allowed_methods = response.headers.get("access-control-allow-methods", "").upper()
        assert method in allowed_methods, \
            f"Method {method} should be allowed, got {allowed_methods}"


def test_cors_configuration_consistency():
    """Test that CORS configuration is consistent across endpoints.
    
    All API endpoints should have the same CORS configuration.
    """
    endpoints = [
        "/api/auth/me",
        "/api/auth/login",
        "/health",
    ]
    
    for endpoint in endpoints:
        response = client.options(
            endpoint,
            headers={
                "Origin": "https://www.hiremebahamas.com",
                "Access-Control-Request-Method": "GET",
            }
        )
        
        # All endpoints should allow credentials
        credentials_header = response.headers.get("access-control-allow-credentials", "").lower()
        assert credentials_header == "true", \
            f"Endpoint {endpoint} should allow credentials, got {credentials_header}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
