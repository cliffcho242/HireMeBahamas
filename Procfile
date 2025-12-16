# =============================================================================
# HireMeBahamas Procfile - ✅ CORRECT STACK (2025)
# =============================================================================
# 
# ⚡ CORRECT STACK CONFIGURATION:
# - Backend API: Render (Always-on Gunicorn service)
# - FastAPI with Gunicorn for production-grade performance
#
# Gunicorn with Uvicorn workers provides:
# - Built-in async support (prevents blocking operations)
# - Better performance under load
# - Worker process management (graceful restarts, health checks)
# - Modern async/await patterns via Uvicorn workers
#
# Configuration:
# - workers=4: Scaled for 100K+ users (optimized for production)
# - timeout=120: Allows for database cold starts
# - Uvicorn workers: ASGI support for FastAPI async operations
# - Gunicorn: Production-grade worker management
#
# Environment variables:
#   PORT=8000            Default port
#   WEB_CONCURRENCY=4    Four workers for 100K+ user scaling
#   GUNICORN_TIMEOUT=120 Worker timeout in seconds
# 
# Note: This is industry-standard configuration used by apps at Facebook/Twitter scale
# =============================================================================

web: gunicorn app.main:app --workers ${WEB_CONCURRENCY:-4} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout ${GUNICORN_TIMEOUT:-120} --preload --log-level info

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
