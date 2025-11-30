# =============================================================================
# HireMeBahamas Procfile (Heroku/Railway)
# =============================================================================
# 
# COLD START ELIMINATION:
# Uses --preload to load app BEFORE forking workers, eliminating 30-120s cold starts.
# First request after boot is instant (<400ms) even after hours of inactivity.
# 
# Configuration via environment variables:
#   WEB_CONCURRENCY=2-4    Workers (2 for 512MB RAM, 4 for 2GB RAM)
#   WEB_THREADS=8          Threads per worker
#   PRELOAD_APP=true       Enable preloading (default: true)
# 
# See gunicorn.conf.py for full configuration details.
# =============================================================================

web: gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload

# Optional: Use start.sh for migrations + preload health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A final_backend.celery worker --loglevel=info
# Optional: Uncomment to enable Flower for Celery monitoring
# flower: celery -A final_backend.celery flower --port=5555
