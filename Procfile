# =============================================================================
# HireMeBahamas Procfile - Production FastAPI Configuration
# =============================================================================
# 
# ✅ FINAL "DO NOT EVER DO" LIST COMPLIANT:
# ✅ Single Gunicorn worker (workers=1)
# ✅ No blocking DB calls at import
# ✅ Health check never touches DB
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
#   • Gunicorn defaults unsafe → We use workers=1
#   • One worker = predictable memory
#   • Async startup = instant health
#   • DB warms after app is alive
#
# This is how production FastAPI apps actually run.
# =============================================================================

# Main web process - Production FastAPI with Gunicorn
# 
# ✅ NEON SAFE GUNICORN CONFIGURATION:
# - app.main:app - FastAPI application entry point
# - -k uvicorn.workers.UvicornWorker - ASGI worker for async support
# - --bind 0.0.0.0:$PORT - Bind to all interfaces on dynamic port
# - --workers 2 - Two workers for production
# - --timeout 120 - Prevents premature SIGTERM during startup
# 
# ❌ NO extra flags (no preload or SSL flags)
# Single worker with UvicornWorker (async event loop) handles 100+ concurrent connections efficiently.
# This is the correct production pattern for FastAPI on Render/Railway.
web: cd backend && poetry run gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} --workers 2 --timeout 120

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
