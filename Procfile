# =============================================================================
# HireMeBahamas Procfile (Heroku/Railway)
# =============================================================================
# 
# NUCLEAR FIX FOR 502 BAD GATEWAY (2025)
#
# Configuration:
# - workers=1: Prevents OOM on 512MB-1GB RAM
# - timeout=180: Survives Railway DB cold starts (up to 2 min)
# - keep-alive=5: Matches load balancer settings
# - preload: Eliminates cold start app loading delay
#
# Environment variables:
#   WEB_CONCURRENCY=1    Single worker for low RAM
#   WEB_THREADS=4        Threads per worker
#   GUNICORN_TIMEOUT=180 Worker timeout in seconds
#   PRELOAD_APP=true     Enable app preloading
# 
# See gunicorn.conf.py for full configuration details.
# =============================================================================

web: gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload

# Optional: Use start.sh for migrations + preload health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A final_backend.celery worker --loglevel=info
