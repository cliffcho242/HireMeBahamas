# =============================================================================
# HireMeBahamas Procfile - ✅ CORRECT STACK (2025) - Step 7.6 Cached Traffic
# =============================================================================
# 
# ⚡ OPTIMIZED FOR CACHED TRAFFIC:
# - Backend API: Render (Always-on Gunicorn service)
# - FastAPI with Gunicorn + Redis caching for Facebook-level performance
#
# Gunicorn with Uvicorn workers provides:
# - Built-in async support (prevents blocking operations)
# - Better performance under load
# - Worker process management (graceful restarts, health checks)
# - Modern async/await patterns via Uvicorn workers
#
# Configuration (Step 7.6 - Tuned for Cached Traffic):
# - workers=3: Higher concurrency now that Redis handles most requests
# - timeout=120: Allows for database cold starts
# - Uvicorn workers: ASGI support for FastAPI async operations
# - Gunicorn: Production-grade worker management
# - NO --preload: Safer for database applications (see gunicorn.conf.py)
#
# Environment variables:
#   PORT=8000            Default port
#   WEB_CONCURRENCY=3    Three workers for cached traffic (12 total capacity with 4 threads)
#   GUNICORN_TIMEOUT=120 Worker timeout in seconds
# 
# Expected Performance After Step 7.6:
# - Feed: 400-800ms → 20-60ms
# - Auth: 200ms → <50ms
# - Health: 6s → <30ms
# - DB load: High → Very low
# 
# Note: This is Facebook-level architecture with Redis caching
# =============================================================================

web: gunicorn app.main:app --workers ${WEB_CONCURRENCY:-3} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout ${GUNICORN_TIMEOUT:-120} --log-level info

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
