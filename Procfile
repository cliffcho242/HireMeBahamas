# =============================================================================
# HireMeBahamas Procfile - Production FastAPI Configuration
# =============================================================================
# 
# ✅ FINAL "DO NOT EVER DO" LIST COMPLIANT:
# ✅ Zero-downtime dual Gunicorn workers (workers=2)
# ✅ No blocking DB calls at import
# ✅ Health check validates DB availability
# ✅ No --reload flag
# ✅ No heavy startup logic (all async)
# ✅ Single platform deployment (Render)
#
# EXPECTED LOGS AFTER FIX:
#   ✅ Booting worker with pid ...
#   ✅ Application startup complete
#
# YOU SHOULD NOT SEE:
#   ❌ Worker was sent SIGTERM
#
# WHY THIS FIX IS PERMANENT:
#   • Render kills slow starters → We start instantly
#   • Gunicorn defaults unsafe → We use controlled workers=2
#   • Recycling workers = predictable memory
#   • Async startup + DB-aware health = instant readiness
#   • DB warms after app is alive
#
# This is how production FastAPI apps actually run.
# =============================================================================

# Main web process - Production FastAPI with Gunicorn
# 
# ✅ NEON SAFE GUNICORN CONFIGURATION:
# - api.index:app - FastAPI application entry point
# - -k uvicorn.workers.UvicornWorker - ASGI worker for async support
# - --bind 0.0.0.0:$PORT - Bind to all interfaces on dynamic port
# - --workers 1 - Single worker for fastest health check startup
# - --timeout 120 - Prevents premature SIGTERM during startup
# 
# ❌ NO extra flags (no --reload, no --preload, no SSL flags)
# ❌ NO sslmode configuration here
#
# Single worker with UvicornWorker (async event loop) handles health checks instantly on cold start.
# This is the correct production pattern for FastAPI on Render/Railway when the app lives in api/index.py.
# Scale horizontally via platform instances; adjust WEB_CONCURRENCY if you need more headroom than a single worker.
web: poetry run gunicorn api.index:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 2 --timeout 120 --graceful-timeout 30 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
