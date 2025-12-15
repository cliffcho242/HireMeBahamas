# =============================================================================
# HireMeBahamas Procfile (Heroku/Railway) - FASTAPI VERSION
# =============================================================================
# 
# PERMANENT FIX FOR 198-SECOND LOGIN TIMEOUT (2025)
#
# Switched from Flask to FastAPI for:
# - Built-in async support (prevents blocking operations)
# - Better performance under load
# - Request timeout middleware (prevents 198s hangs)
# - Modern async/await patterns
#
# Configuration:
# - workers=1: Prevents OOM on 512MB-1GB RAM  
# - timeout=120: Allows for database cold starts
# - Uvicorn with uvloop for maximum performance
# - Request-level timeout middleware enforces 60s max per request
#
# Environment variables:
#   PORT=8000            Default port
#   WEB_CONCURRENCY=1    Single worker for low RAM
#   UVICORN_TIMEOUT=120  Worker timeout in seconds
# 
# =============================================================================

web: uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
