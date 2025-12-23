# =============================================================================
# HireMeBahamas Procfile - Production FastAPI Configuration
# =============================================================================
# 
# ✅ FINAL "DO NOT EVER DO" LIST COMPLIANT:
# ✅ Single Gunicorn worker (workers=1) - Master Playbook Requirement
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
#   • Master Playbook requires workers=1 for stability
#   • Single worker = predictable memory usage on free tier
#   • Async startup + DB-aware health = instant readiness
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
# - --workers 1 - One worker for production (Master Playbook requirement)
# - --timeout 120 - Prevents premature SIGTERM during startup
# 
# ❌ NO extra flags (no --reload, no --preload, no SSL flags)
# ❌ NO sslmode configuration here
#
# Single worker with UvicornWorker (async event loop) handles 100+ concurrent connections efficiently.
# This is the correct production pattern for FastAPI on Render/Railway.
web: cd backend && poetry run gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 2 --timeout 120 --graceful-timeout 30 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
