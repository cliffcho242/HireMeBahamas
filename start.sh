#!/bin/bash
# =============================================================================
# HireMeBahamas Backend Startup Script
# =============================================================================
# 
# COLD START ELIMINATION (2025 Best Practice)
# 
# This script uses Gunicorn with preload to eliminate 30-120s cold starts:
# 
# How --preload works:
#   1. App loads ONCE in master process BEFORE forking workers
#   2. Workers inherit pre-loaded app via copy-on-write memory
#   3. First request after boot is instant (<400ms)
#
# Configuration (via environment variables):
#   WEB_CONCURRENCY=2-4    Number of workers (2 for 512MB, 4 for 1-2GB RAM)
#   WEB_THREADS=8          Threads per worker (total capacity = workers * threads)
#   PRELOAD_APP=true       Enable app preloading (default: true)
#
# For Render:
#   - Starter plan ($7/mo, 512MB): WEB_CONCURRENCY=2
#   - Standard plan ($25/mo, 2GB): WEB_CONCURRENCY=4
#
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "🚀 HireMeBahamas Backend Startup"
echo "=============================================="
echo "Environment: ${ENVIRONMENT:-development}"
echo "Workers: ${WEB_CONCURRENCY:-2}"
echo "Threads: ${WEB_THREADS:-8}"
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

# Start Gunicorn with preload configuration
echo ""
echo "🚀 Starting Gunicorn server with preload..."
echo "   Config: gunicorn.conf.py"
echo "   App: final_backend_postgresql:application"
echo "   Bind: 0.0.0.0:${PORT:-8080}"
echo ""

# Using gunicorn.conf.py which has preload_app=True by default
# The --preload flag is redundant when preload_app=True in config,
# but we include it explicitly for clarity and to ensure it's enabled
exec gunicorn final_backend_postgresql:application \
    --config gunicorn.conf.py \
    --preload
