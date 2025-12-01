#!/bin/bash
# =============================================================================
# HireMeBahamas Backend Startup Script
# =============================================================================
# 
# NUCLEAR FIX FOR 502 BAD GATEWAY (2025)
# 
# This script eliminates cold start timeouts with:
# 1. Database migrations before app start
# 2. Preload health check to verify app can load
# 3. Gunicorn with --preload for instant first request
#
# Configuration (via environment variables):
#   WEB_CONCURRENCY=1       Single worker for 512MB-1GB RAM
#   WEB_THREADS=4           Threads per worker
#   GUNICORN_TIMEOUT=180    Worker timeout (survives cold starts)
#   PRELOAD_APP=true        Enable app preloading
#
# For Render:
#   - Standard plan ($25/mo, 1GB RAM): WEB_CONCURRENCY=1, WEB_THREADS=4
#   - Starter plan ($7/mo, 512MB RAM): WEB_CONCURRENCY=1, WEB_THREADS=2
#
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "🚀 HireMeBahamas Backend Startup"
echo "=============================================="
echo "Environment: ${ENVIRONMENT:-development}"
echo "Workers: ${WEB_CONCURRENCY:-1}"
echo "Threads: ${WEB_THREADS:-4}"
echo "Timeout: ${GUNICORN_TIMEOUT:-180}s"
echo "Preload: ${PRELOAD_APP:-true}"
echo "=============================================="

# Run database migrations
echo ""
echo "🔧 Running database migrations..."
if python add_missing_user_columns.py; then
    echo "✅ Migrations completed successfully"
else
    echo "⚠️ Warning: Migration script had errors, but continuing..."
fi

# Startup health check - verify app loads before accepting traffic
echo ""
echo "🔍 Verifying app can load (preload health check)..."
if python -c "
import sys
import time
start = time.time()
try:
    from final_backend_postgresql import application
    elapsed = time.time() - start
    print(f'✅ App imported successfully in {elapsed:.2f}s')
    sys.exit(0)
except Exception as e:
    print(f'❌ App failed to load: {e}')
    sys.exit(1)
"; then
    echo "✅ Preload health check passed"
else
    echo "❌ Preload health check failed - app cannot start"
    exit 1
fi

# Start Gunicorn with nuclear configuration
echo ""
echo "🚀 Starting Gunicorn server..."
echo "   Config: gunicorn.conf.py"
echo "   App: final_backend_postgresql:application"
echo "   Bind: 0.0.0.0:${PORT:-8080}"
echo "   Timeout: ${GUNICORN_TIMEOUT:-180}s"
echo ""

exec gunicorn final_backend_postgresql:application \
    --config gunicorn.conf.py \
    --preload
