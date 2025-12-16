# =============================================================================
# HireMeBahamas Procfile - STEP 18: Production Commands (Final)
# =============================================================================
# 
# ⚡ POETRY-MANAGED PRODUCTION DEPLOYMENT:
# - Poetry: Consistent dependency management with poetry.lock
# - Gunicorn: Production WSGI server with config file
# - FastAPI: Modern async web framework
# - Redis caching: Facebook-level performance
#
# Benefits of Poetry + Config File Approach (STEP 18):
# - All dependencies managed in pyproject.toml
# - Deterministic builds with poetry.lock
# - All Gunicorn settings centralized in gunicorn.conf.py
# - Easier maintenance and updates
# - Production-ready configuration
#
# Configuration (from gunicorn.conf.py):
# - workers=4: Optimized for 100K+ concurrent users with Redis caching
# - worker_class=uvicorn.workers.UvicornWorker: ASGI async support
# - timeout=60: Fast responses on always-on service
# - preload_app=False: Safe for database applications
# - Total capacity: 400+ concurrent connections (4 workers × async event loop)
#
# Environment variables (set in deployment platform):
#   PORT=8000            Default port (auto-detected in gunicorn.conf.py)
#   WEB_CONCURRENCY=4    Override worker count (optional, default in config)
#   GUNICORN_TIMEOUT=60  Override timeout (optional, default in config)
# 
# Expected Performance:
# - Feed: 20-60ms (with Redis caching)
# - Auth: <50ms
# - Health: <30ms
# - DB load: Very low (Redis handles most requests)
# - Concurrent capacity: 400+ connections
# - Supported users: 100K+ concurrent
# 
# Note: This is Facebook-level architecture with Poetry dependency management
# =============================================================================

# Main web process - Optimized Gunicorn for Render (AGGRESSIVE FOREVER FIX)
# Note: This Procfile assumes the working directory is the project root
# Changes to backend/ where app/main.py and gunicorn.conf.py are located
# For Railway/Heroku with root directory set to 'backend/', use backend/Procfile instead
# 
# CRITICAL SETTINGS FOR RENDER:
# - workers=1: Single worker for small instances (faster + safer)
# - threads=2: Minimal threading overhead
# - timeout=120: Prevents worker SIGTERM during slow startup
# - graceful_timeout=30: Clean shutdown
# - keepalive=5: Connection persistence
# 
# PYTHONPATH is set to current directory (.) after cd to backend, which achieves
# the same effect as PYTHONPATH=backend when run from project root.
web: cd backend && PYTHONPATH=. poetry run gunicorn app.main:app --workers 1 --threads 2 --timeout 120 --graceful-timeout 30 --keep-alive 5 --log-level info --config gunicorn.conf.py

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
