"""
Health check endpoints.

Provides various health check endpoints for monitoring application status,
database connectivity, and service health.
"""
import os
import logging
from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, get_pool_status

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", include_in_schema=False)
@router.head("/health", include_in_schema=False)
def health():
    """Instant health check - no database dependency.
    
    This endpoint is designed to respond immediately (<5ms) even during
    the coldest start. It does NOT check database connectivity.
    
    Use /ready for database connectivity check.
    
    ✅ CRITICAL: Does NOT touch the database to ensure instant response.
    """
    return {
        "status": "ok",
        "service": "hiremebahamas-backend",
        "uptime": "healthy"
    }


@router.get("/live", tags=["health"])
@router.head("/live", tags=["health"])
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


@router.get("/ready", tags=["health"])
@router.head("/ready", tags=["health"])
def ready():
    """Readiness check - instant response, no database dependency.
    
    ✅ PRODUCTION-GRADE: This endpoint NEVER touches the database.
    Returns immediately (<5ms) to confirm the application is ready to serve traffic.
    
    For database connectivity checks, use:
    - /ready/db - Full database connectivity check
    - /health/detailed - Comprehensive health check with database statistics
    
    This follows production best practices:
    - Health checks must never touch DB, APIs, or disk
    - Load balancers need instant responses
    - Prevents cascading failures during database issues
    """
    return JSONResponse({
        "status": "ready",
        "message": "Application is ready to serve traffic",
    }, status_code=200)


@router.get("/ready/db", tags=["health"])
async def db_readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness probe with database connectivity check.
    
    K8s-style readiness probe that checks if the application is ready to
    receive traffic. Checks database connectivity.
    
    Returns 200 if the app is ready, 503 if database is unavailable.
    
    Note: Use /ready for instant cold start response.
    Use /ready/db for full database connectivity check.
    """
    try:
        from app.core.db_health import check_database_health
        db_health = await check_database_health(db)
        
        if db_health["status"] == "healthy":
            return JSONResponse(
                content={"status": "ready", "database": "connected"},
                status_code=200
            )
        else:
            return JSONResponse(
                content={"status": "not_ready", "database": db_health},
                status_code=503
            )
    except Exception as e:
        return JSONResponse(
            content={"status": "not_ready", "error": str(e)},
            status_code=503
        )


@router.get("/health/ping")
def health_ping():
    """Ultra-fast health ping endpoint.
    
    ✅ PRODUCTION-GRADE: Database-free, instant response.
    Returns immediately without database check.
    Use this for load balancer health checks and quick availability tests.
    """
    return {"status": "ok", "message": "pong"}


@router.get("/api/health")
@router.head("/api/health")
def api_health():
    """Simple API health check endpoint.
    
    Returns a simple status response for basic health verification.
    
    ✅ NO DATABASE - instant response
    ✅ NO IO - instant response
    ✅ NO async/await - synchronous function for fastest response
    
    Note: HEAD method automatically returns same response as GET but with no body.
    FastAPI handles this automatically - no special logic needed.
    """
    return {
        "status": "ok",
        "service": "hiremebahamas-backend",
        "uptime": "healthy"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with database statistics.
    
    Provides additional database statistics for monitoring.
    May require admin permissions in production environments.
    
    For quick health checks, use /health (no DB dependency).
    For readiness probes, use /ready (checks DB connectivity).
    """
    from app.core.db_health import check_database_health, get_database_stats
    
    # Check API health
    api_status = {
        "status": "healthy",
        "message": "HireMeBahamas API is running",
        "version": "1.0.0"
    }
    
    # Check database health
    db_health = await check_database_health(db)
    
    # Determine overall health status
    overall_status = "healthy" if db_health["status"] == "healthy" else "degraded"
    
    health_response = {
        "status": overall_status,
        "api": api_status,
        "database": db_health
    }
    
    # Get database statistics
    db_stats = await get_database_stats(db)
    
    if db_stats:
        health_response["database"]["statistics"] = db_stats
    
    # Add pool status
    try:
        pool_status = await get_pool_status()
        health_response["database"]["pool"] = pool_status
    except Exception as e:
        health_response["database"]["pool"] = {"error": str(e)}
    
    # Add cache stats
    try:
        from app.core.cache import _redis_available, _redis_client
        if _redis_available and _redis_client:
            health_response["cache"] = {"status": "healthy", "backend": "redis"}
        else:
            health_response["cache"] = {"status": "healthy", "backend": "in-memory"}
    except Exception as e:
        health_response["cache"] = {"status": "degraded", "error": str(e)}
    
    return health_response


@router.get("/health/cache")
async def cache_health():
    """Get cache health status and statistics.
    
    Returns cache hit rates, backend status, and performance metrics.
    """
    try:
        from app.redis import redis_cache
        return await redis_cache.health_check()
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "message": "Cache health check failed"
        }


@router.post("/warm-cache")
async def warm_cache_endpoint():
    """Warm up cache with frequently accessed data.
    
    This endpoint should be called by a cron job every 5 minutes
    to keep the cache hot and ensure sub-100ms response times.
    
    Example cron job: */5 * * * * curl -X POST https://your-backend-url/warm-cache
    
    For Railway: Use GitHub Actions workflow (scheduled-ping.yml)
    For Vercel: Add to vercel.json cron configuration
    """
    try:
        from app.core.cache import warmup_cache
        result = await warmup_cache()
        return result
    except Exception as e:
        logger.error(f"Cache warmup failed: {e}")
        return {
            "status": "error",
            "message": "Cache warmup failed",
            "error": str(e)
        }
