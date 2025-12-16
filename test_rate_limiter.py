"""
Tests for rate limiting functionality.

Tests cover:
- Rate limit enforcement
- Redis integration
- In-memory fallback
- 429 response when limit exceeded
- IP extraction from headers
- Excluded paths (health checks)
"""
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from collections import defaultdict

# Import the rate limiter module
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from backend_app.core.rate_limiter import (
    RateLimiter,
    get_client_ip,
    rate_limit,
    add_rate_limiting_middleware,
    get_rate_limiter,
    RATE_LIMIT_EXCLUDE_PATHS,
)


class TestRateLimiter:
    """Test the RateLimiter class."""
    
    def test_init(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests=50, window=30)
        assert limiter.requests == 50
        assert limiter.window == 30
        assert limiter._redis_available is False
        assert limiter._memory_store is not None
    
    @pytest.mark.asyncio
    async def test_check_memory_allows_requests(self):
        """Test that in-memory rate limiter allows requests under limit."""
        limiter = RateLimiter(requests=5, window=60)
        
        # First 5 requests should be allowed
        for i in range(5):
            result = limiter._check_memory("192.168.1.1")
            assert result is True
    
    @pytest.mark.asyncio
    async def test_check_memory_blocks_excess_requests(self):
        """Test that in-memory rate limiter blocks requests over limit."""
        limiter = RateLimiter(requests=5, window=60)
        
        # Use up all allowed requests
        for i in range(5):
            limiter._check_memory("192.168.1.1")
        
        # 6th request should be blocked
        result = limiter._check_memory("192.168.1.1")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_memory_expires_old_requests(self):
        """Test that in-memory rate limiter expires old requests."""
        limiter = RateLimiter(requests=3, window=1)  # 1 second window
        
        # Use up all requests
        for i in range(3):
            limiter._check_memory("192.168.1.1")
        
        # 4th request should be blocked
        assert limiter._check_memory("192.168.1.1") is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # New request should be allowed
        result = limiter._check_memory("192.168.1.1")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_memory_separates_ips(self):
        """Test that in-memory rate limiter tracks IPs separately."""
        limiter = RateLimiter(requests=2, window=60)
        
        # Use up requests for IP1
        limiter._check_memory("192.168.1.1")
        limiter._check_memory("192.168.1.1")
        
        # IP1 should be blocked
        assert limiter._check_memory("192.168.1.1") is False
        
        # IP2 should still be allowed
        assert limiter._check_memory("192.168.1.2") is True
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test that statistics are tracked correctly."""
        limiter = RateLimiter(requests=5, window=60)
        
        # Make some requests
        await limiter.check_rate_limit("192.168.1.1")
        await limiter.check_rate_limit("192.168.1.1")
        
        stats = limiter.get_stats()
        assert stats["total_requests"] == 2
        assert stats["backend"] in ["redis", "memory"]
        assert "limit" in stats


class TestGetClientIP:
    """Test IP extraction from requests."""
    
    def test_get_client_ip_from_x_forwarded_for(self):
        """Test IP extraction from X-Forwarded-For header."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get = lambda key: "203.0.113.1, 203.0.113.2" if key == "X-Forwarded-For" else None
        mock_request.client = None
        
        ip = get_client_ip(mock_request)
        assert ip == "203.0.113.1"
    
    def test_get_client_ip_from_x_real_ip(self):
        """Test IP extraction from X-Real-IP header."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get = lambda key: "203.0.113.1" if key == "X-Real-IP" else None
        mock_request.client = None
        
        ip = get_client_ip(mock_request)
        assert ip == "203.0.113.1"
    
    def test_get_client_ip_from_client(self):
        """Test IP extraction from request.client."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get = lambda key: None
        mock_request.client = MagicMock()
        mock_request.client.host = "203.0.113.1"
        
        ip = get_client_ip(mock_request)
        assert ip == "203.0.113.1"
    
    def test_get_client_ip_fallback(self):
        """Test IP extraction fallback when no source available."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get = lambda key: None
        mock_request.client = None
        
        ip = get_client_ip(mock_request)
        assert ip == "unknown"


class TestRateLimitMiddleware:
    """Test the rate limiting middleware integration."""
    
    def test_middleware_allows_requests_under_limit(self):
        """Test that middleware allows requests under the rate limit."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        # Add rate limiting with high limit
        limiter = RateLimiter(requests=100, window=60)
        with patch('backend_app.core.rate_limiter.get_rate_limiter', return_value=limiter):
            add_rate_limiting_middleware(app)
        
        client = TestClient(app)
        
        # Should allow request
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "success"}
    
    def test_middleware_blocks_requests_over_limit(self):
        """Test that middleware blocks requests over the rate limit."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        # Add rate limiting with low limit
        limiter = RateLimiter(requests=2, window=60)
        with patch('backend_app.core.rate_limiter.get_rate_limiter', return_value=limiter):
            add_rate_limiting_middleware(app)
        
        client = TestClient(app)
        
        # First 2 requests should succeed
        response1 = client.get("/test")
        assert response1.status_code == 200
        
        response2 = client.get("/test")
        assert response2.status_code == 200
        
        # 3rd request should be rate limited
        response3 = client.get("/test")
        assert response3.status_code == 429
        assert "Too many requests" in response3.json()["detail"]
        assert "Retry-After" in response3.headers
    
    def test_middleware_excludes_health_endpoints(self):
        """Test that health check endpoints are excluded from rate limiting."""
        app = FastAPI()
        
        @app.get("/health")
        async def health():
            return {"status": "ok"}
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        # Add rate limiting with very low limit
        limiter = RateLimiter(requests=1, window=60)
        with patch('backend_app.core.rate_limiter.get_rate_limiter', return_value=limiter):
            add_rate_limiting_middleware(app)
        
        client = TestClient(app)
        
        # Use up the rate limit on /test
        response1 = client.get("/test")
        assert response1.status_code == 200
        
        # /test should now be blocked
        response2 = client.get("/test")
        assert response2.status_code == 429
        
        # But /health should still work
        response3 = client.get("/health")
        assert response3.status_code == 200
        assert response3.json() == {"status": "ok"}
    
    def test_middleware_adds_rate_limit_headers(self):
        """Test that middleware adds rate limit headers to responses."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        limiter = RateLimiter(requests=100, window=60)
        with patch('backend_app.core.rate_limiter.get_rate_limiter', return_value=limiter):
            add_rate_limiting_middleware(app)
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Window" in response.headers
        assert response.headers["X-RateLimit-Limit"] == "100"
        assert response.headers["X-RateLimit-Window"] == "60"


class TestRateLimitFunction:
    """Test the rate_limit() function."""
    
    @pytest.mark.asyncio
    async def test_rate_limit_raises_exception_when_exceeded(self):
        """Test that rate_limit() raises HTTPException when limit exceeded."""
        from fastapi import HTTPException
        
        limiter = RateLimiter(requests=1, window=60)
        
        with patch('backend_app.core.rate_limiter.get_rate_limiter', return_value=limiter):
            # First call should succeed
            await rate_limit("192.168.1.1")
            
            # Second call should raise exception
            with pytest.raises(HTTPException) as exc_info:
                await rate_limit("192.168.1.1")
            
            assert exc_info.value.status_code == 429
            assert "Too many requests" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_rate_limit_allows_requests_under_limit(self):
        """Test that rate_limit() allows requests under limit."""
        limiter = RateLimiter(requests=5, window=60)
        
        with patch('backend_app.core.rate_limiter.get_rate_limiter', return_value=limiter):
            # Should not raise exception for requests under limit
            for i in range(5):
                await rate_limit(f"192.168.1.{i}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
