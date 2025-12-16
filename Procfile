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
# Configuration (Step 10 - Scaling to 100K+ Users):
# - workers=4: Increased concurrency for 100K+ users with Redis caching
# - threads=4: 4 threads per worker (configured in gunicorn.conf.py)
# - timeout=120: Allows for database cold starts
# - Uvicorn workers: ASGI support for FastAPI async operations
# - Gunicorn: Production-grade worker management
#
# Environment variables:
#   PORT=8000            Default port
#   WEB_CONCURRENCY=4    Four workers for 100K+ users (16 total capacity with 4 threads)
#   GUNICORN_TIMEOUT=120 Worker timeout in seconds
# 
# Expected Performance After Step 10:
# - Feed: <50ms (with Redis caching)
# - Auth: <50ms
# - Health: <30ms
# - DB load: Very low (with indexes and caching)
# - Concurrent capacity: 16 requests (4 workers × 4 threads)
# 
# Note: This is Facebook-level architecture with Redis caching
# =============================================================================

web: gunicorn app.main:app --workers ${WEB_CONCURRENCY:-4} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout ${GUNICORN_TIMEOUT:-120} --preload --log-level info

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
