# =============================================================================
# HireMeBahamas Procfile - Production FastAPI Configuration
# =============================================================================
# 
# ✅ FINAL "DO NOT EVER DO" LIST COMPLIANT:
# ✅ Single Gunicorn worker (workers=1)
# ✅ No blocking DB calls at import
# ✅ Health check never touches DB
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
#   • Gunicorn defaults unsafe → We use workers=1
#   • One worker = predictable memory
#   • Async startup = instant health
#   • DB warms after app is alive
#
# This is how production FastAPI apps actually run.
# =============================================================================

# Main web process - Production FastAPI with Gunicorn
# 
# CRITICAL PRODUCTION SETTINGS:
# - workers=1: Single worker (predictable memory, no coordination overhead)
# - threads=2: Minimal threading (async event loop handles concurrency)
# - timeout=120: Prevents premature SIGTERM during startup
# - graceful-timeout=30: Clean shutdown of in-flight requests
# - keep-alive=5: Connection persistence for load balancers
# - log-level=info: Production logging
# - config: Additional settings in gunicorn.conf.py
#
# Single worker with UvicornWorker (async event loop) handles 100+ concurrent connections efficiently.
# This is the correct production pattern for FastAPI on Render.
web: cd backend && PYTHONPATH=. poetry run gunicorn app.main:app --workers 1 --threads 2 --timeout 120 --graceful-timeout 30 --keep-alive 5 --log-level info --config gunicorn.conf.py

# Optional: Use start.sh for migrations + health check
# web: bash start.sh

# Optional: Uncomment to enable Celery worker for background tasks
# worker: celery -A backend.celery worker --loglevel=info
