# =============================================================================
# HireMeBahamas Procfile - NUCLEAR 2025-PROOF EDITION
# =============================================================================
# 
# FINAL START COMMAND (Railway/Heroku/Render):
#   gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload
#
# PERFORMANCE TARGETS:
#   - Boot time: < 9 seconds
#   - First request: < 400ms
#   - Login: < 180ms (cached)
#   - Zero 502/499/timeout/OOM forever
#
# ENVIRONMENT VARIABLES (set in dashboard):
#   WEB_CONCURRENCY=1    Single worker for 512MB-1GB RAM
#   WEB_THREADS=4        Threads per worker
#   GUNICORN_TIMEOUT=120 Worker timeout in seconds
#   PRELOAD_APP=true     Enable app preloading
#
# See gunicorn.conf.py for full configuration details.
# =============================================================================

web: gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload

# Optional: Use start.sh for migrations + preload health check
# web: bash start.sh

# Optional: Celery worker for background tasks
# worker: celery -A final_backend.celery worker --loglevel=info
