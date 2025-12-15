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
# - workers=2: Optimal for 1GB RAM (can handle concurrent requests)
# - timeout=120: Allows for database cold starts
# - Uvicorn workers: ASGI support for FastAPI async operations
# - Gunicorn: Production-grade worker management
#
# Environment variables:
#   PORT=8000            Default port
#   WEB_CONCURRENCY=2    Two workers for better concurrency
#   GUNICORN_TIMEOUT=120 Worker timeout in seconds
# 
# Note: This is industry-standard configuration used by apps at Facebook/Twitter scale
# =============================================================================

web: gunicorn app.main:app --workers ${WEB_CONCURRENCY:-2} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout ${GUNICORN_TIMEOUT:-120} --log-level info

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
