#!/bin/bash
# =============================================================================
# HireMeBahamas Backend Startup Script
# =============================================================================
# 
# DATABASE-SAFE STARTUP CONFIGURATION (2025)
# 
# This script provides reliable startup with:
# 1. Database migrations before app start
# 2. Preload health check to verify app can load
# 3. Gunicorn WITHOUT --preload (critical for database safety)
#
# ⚠️ CRITICAL: Never use --preload with databases!
# The --preload flag causes:
# - Database connection pool issues
# - Worker synchronization problems
# - Health check failures during initialization
# - Shared state issues between workers
#
# Configuration (via environment variables):
#   WEB_CONCURRENCY=2       Two workers for optimal performance
#   WEB_THREADS=4           Threads per worker (8 total concurrent requests)
#   GUNICORN_TIMEOUT=60     Worker timeout (optimized for always-on)
#
# For Render:
#   - Standard plan ($25/mo, 1GB RAM): WEB_CONCURRENCY=2, WEB_THREADS=4
#   - Starter plan ($7/mo, 512MB RAM): WEB_CONCURRENCY=1, WEB_THREADS=2
#
# =============================================================================

set -e  # Exit on error

echo "=============================================="
echo "🚀 HireMeBahamas Backend Startup"
echo "=============================================="
echo "Environment: ${ENVIRONMENT:-development}"
echo "Workers: ${WEB_CONCURRENCY:-2}"
echo "Threads: ${WEB_THREADS:-4}"
echo "Timeout: ${GUNICORN_TIMEOUT:-60}s"
echo "Preload: False (database-safe mode)"
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

# Start Gunicorn with database-safe configuration
echo ""
echo "🚀 Starting Gunicorn server..."
echo "   Config: gunicorn.conf.py (preload_app=False)"
echo "   App: final_backend_postgresql:application"
echo "   Bind: 0.0.0.0:${PORT:-8080}"
echo "   Timeout: ${GUNICORN_TIMEOUT:-60}s"
echo "   ⚠️  NOT using --preload (database safety)"
echo ""

exec gunicorn final_backend_postgresql:application \
    --config gunicorn.conf.py
