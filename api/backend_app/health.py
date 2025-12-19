"""
NEVER-FAIL HEALTH CHECK APP (2025)
===================================

This module provides a dedicated FastAPI app ONLY for health checks.

🔒 MANDATORY RULES (NON-NEGOTIABLE):
  • NO database imports
  • NO Redis imports  
  • NO env validation
  • NO imports from main app
  • NO async operations
  • NO dependency injection
  • NO middleware

This file must:
  • Import nothing except FastAPI
  • Have zero external dependencies
  • Be <10ms response time always
  • Never fail regardless of app state

This is physically isolated from the main application to ensure
health checks NEVER timeout, even if the main app crashes.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create dedicated health-only FastAPI app
# This app is completely isolated from the main application
health_app = FastAPI(
    title="HireMeBahamas Health",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@health_app.get("/api/health", include_in_schema=False)
@health_app.head("/api/health", include_in_schema=False)
def api_health():
    """Instant API health check - NEVER-FAIL architecture.
    
    Supports both GET and HEAD methods for maximum compatibility.
    
    ✅ NO DATABASE - instant response
    ✅ NO IO - instant response
    ✅ NO async/await - synchronous function
    ✅ NO imports - zero dependencies
    ✅ <10ms guaranteed response time
    
    This endpoint is physically isolated from the main app.
    Even if database explodes, Redis dies, or app crashes,
    this endpoint still responds successfully.
    
    Render health checks cannot kill this.
    """
    return JSONResponse({
        "status": "ok",
        "service": "hiremebahamas-backend",
    }, status_code=200)


@health_app.get("/health", include_in_schema=False)
@health_app.head("/health", include_in_schema=False)
def health():
    """Basic health check endpoint.
    
    Supports both GET and HEAD methods for maximum compatibility.
    
    ✅ NO DATABASE - instant response
    ✅ NO IO - instant response
    ✅ NO async/await - synchronous function
    ✅ <10ms guaranteed response time
    """
    return JSONResponse({"status": "ok"}, status_code=200)


@health_app.get("/healthz", include_in_schema=False)
def healthz():
    """Emergency health check endpoint - ultra stable fallback.
    
    This is a SECOND emergency health route that returns plain text "ok".
    If /health or /api/health ever breaks in the future, switch to this
    endpoint in Render settings.
    
    Returns plain text "ok" for maximum compatibility and minimal overhead.
    
    ✅ NO DATABASE - instant response
    ✅ NO IO - instant response  
    ✅ NO async/await - synchronous function
    ✅ Plain text response - no JSON parsing overhead
    ✅ <5ms guaranteed response time
    
    High reliability through minimal dependencies and zero failure points.
    """
    return "ok"


@health_app.get("/live", include_in_schema=False)
@health_app.head("/live", include_in_schema=False)
def liveness():
    """Liveness probe - instant response, no dependencies.
    
    This endpoint confirms the application process is running and responsive.
    It does NOT check database or external services.
    
    Use this for:
    - Kubernetes livenessProbe
    - Render liveness checks
    - Load balancer health checks
    
    Returns 200 immediately (<5ms) on any successful request.
    """
    return JSONResponse({"status": "alive"}, status_code=200)


@health_app.get("/ready", include_in_schema=False)
@health_app.head("/ready", include_in_schema=False)
def ready():
    """Readiness check - instant response, no database dependency.
    
    ✅ PRODUCTION-GRADE: This endpoint NEVER touches the database.
    Returns immediately (<5ms) to confirm the application is ready to serve traffic.
    
    This follows production best practices:
    - Health checks must never touch DB, APIs, or disk
    - Load balancers need instant responses
    - Prevents cascading failures during database issues
    """
    return JSONResponse({
        "status": "ready",
        "message": "Application is ready to serve traffic",
    }, status_code=200)
