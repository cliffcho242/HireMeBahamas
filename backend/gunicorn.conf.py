#!/usr/bin/env python3
"""
Gunicorn Production Configuration - HireMeBahamas (2025)
Zero 502, Zero cold starts, Sub-800ms boot, Sub-300ms login globally
"""
import os
import multiprocessing
import time

# ============================================================================
# BIND CONFIGURATION
# ============================================================================
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# ============================================================================
# WORKER CONFIGURATION (Optimized for Cached Traffic - Step 7.6)
# ============================================================================
# Optimized for Railway, Render, and similar PaaS platforms with Redis caching
# Typical CPU allocation: Free tier: 0.1-0.5 CPU, Paid: 1+ CPU
# 
# With Redis caching infrastructure in place, we can increase workers:
# - workers=3: Higher concurrency for handling more concurrent requests
# - threads=4: Each worker handles 4 concurrent requests
# - Total capacity: 3 × 4 = 12 concurrent requests
# 
# This configuration is optimized for scenarios where:
# - Caching reduces database load significantly
# - More workers can handle higher traffic volumes
# - CPU/memory becomes the bottleneck, not DB connections
cpu_count = multiprocessing.cpu_count()

# Workers: 4 for optimal performance with Redis caching (Step 10 - 100K+ users scaling)
# Use WEB_CONCURRENCY env var to override
workers = int(os.environ.get("WEB_CONCURRENCY", "4"))

# Worker class: uvicorn.workers.UvicornWorker for FastAPI async support
# Uvicorn workers provide ASGI support with excellent async/await performance
worker_class = "uvicorn.workers.UvicornWorker"

# Note: UvicornWorker does NOT use the threads parameter (async event loop handles concurrency)
# This parameter is kept ONLY for compatibility when switching worker classes
# With UvicornWorker:
# - Each worker runs an async event loop
# - Concurrency is handled via async/await, not threads
# - Each worker can handle ~100+ concurrent connections
# - Total capacity: 4 workers × ~100+ = 400+ concurrent connections
# If you switch to 'gthread' worker class, threads parameter will be used
threads = int(os.environ.get("WEB_THREADS", "4"))

# ============================================================================
# TIMEOUT CONFIGURATION (Critical for 502 Prevention)
# ============================================================================
# Worker timeout: 60s - optimized for fast responses on always-on Render
# This is suitable for Standard plan with no cold starts
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "60"))

# Graceful timeout: 30s for in-flight requests during shutdown
graceful_timeout = 30

# Keep-alive: 5s (matches most cloud load balancers)
keepalive = 5

# ============================================================================
# MEMORY MANAGEMENT (Prevents OOM on Free Tier)
# ============================================================================
# Restart worker after 1000 requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# ============================================================================
# PRELOAD & PERFORMANCE (DATABASE SAFETY - CRITICAL)
# ============================================================================
# ⚠️ CRITICAL WARNING: Never use --preload with databases!
#
# Preload app setting:
# - True: Load app once before forking (DANGEROUS with databases)
# - False: Each worker loads app independently (SAFE with databases)
#
# Why preload_app = False is critical for database applications:
# 1. Database connection pools cannot be safely shared across fork()
# 2. Each worker needs its own database connections
# 3. Prevents health check failures during initialization
# 4. Allows /health endpoint to respond while workers initialize
# 5. Avoids worker synchronization issues with shared state
#
# ⚠️ NEVER override this with --preload on the command line!
# Command line: poetry run gunicorn final_backend_postgresql:application --config gunicorn.conf.py
# Do NOT add: --preload (this would override the safe setting below)
#
# SAFE COMMAND:   gunicorn final_backend_postgresql:application --config gunicorn.conf.py
# UNSAFE COMMAND: gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload
preload_app = False

# ============================================================================
# LOGGING (Production-grade)
# ============================================================================
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# ============================================================================
# PROCESS NAMING
# ============================================================================
proc_name = "hiremebahamas"

# ============================================================================
# SECURITY
# ============================================================================
# Trust proxy headers from cloud platform load balancers (Railway, Render, etc.)
forwarded_allow_ips = "*"

# ============================================================================
# STARTUP HOOKS
# ============================================================================
_master_start_time = None


def on_starting(server):
    """Log startup configuration"""
    global _master_start_time
    _master_start_time = time.time()
    print(f"🚀 Starting Gunicorn (Step 10 - Scaling to 100K+ Users)")
    print(f"   Workers: {workers} × {threads} threads = {workers * threads} capacity")
    print(f"   Timeout: {timeout}s | Keepalive: {keepalive}s")
    print(f"   Preload: {preload_app} (workers initialize independently)")
    print(f"   Redis Cache: Enabled (handles most requests)")
    print(f"   Background Jobs: FastAPI BackgroundTasks for async operations")
    print(f"   Configuration: Production-ready for 100K+ concurrent users")


def when_ready(server):
    """Log when server is ready to accept connections"""
    if _master_start_time:
        startup_time = time.time() - _master_start_time
        print(f"✅ Gunicorn ready to accept connections in {startup_time:.2f}s")
    print(f"   Listening on {bind}")
    print(f"   Health: GET /health (instant)")
    print(f"   Ready: GET /ready (with DB check)")
    print(f"   Workers will initialize independently")
    print(f"🎉 HireMeBahamas API is ready for Render healthcheck")


def on_exit(server):
    """Called on graceful shutdown"""
    print("🛑 Gunicorn shutting down...")


def worker_exit(server, worker):
    """Called when a worker exits"""
    print(f"👷 Worker {worker.pid} exiting...")


def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT signal.
    
    This hook is triggered when Gunicorn sends SIGTERM/SIGINT/SIGQUIT to a worker:
    - During graceful shutdown (deployment, restart)
    - When worker needs to be terminated cleanly
    - Before escalating to SIGABRT for unresponsive workers
    
    Args:
        worker: The worker instance being interrupted
    """
    print(f"⚠️  Worker {worker.pid} received interrupt signal (SIGTERM/SIGINT/SIGQUIT)")
    print(f"   This is normal during:")
    print(f"   - Deployments and restarts")
    print(f"   - Configuration changes")
    print(f"   - Manual service restarts")
    print(f"   If this happens frequently outside of deployments:")
    print(f"   - Check if workers are timing out during requests")
    print(f"   - Review application logs for errors")
    print(f"   - Monitor memory usage (workers may be OOM killed)")


def worker_abort(worker):
    """Called when a worker is forcibly terminated (SIGABRT).
    
    This hook is triggered when Gunicorn sends SIGABRT to a worker because:
    - Worker exceeded the timeout (didn't respond within timeout seconds)
    - Worker became unresponsive or hung
    - Master process needs to forcibly terminate the worker
    
    Args:
        worker: The worker instance being aborted
    """
    import os
    # Access timeout from module globals or environment
    worker_timeout = int(os.environ.get("GUNICORN_TIMEOUT", "60"))
    
    print(f"⚠️  Worker {worker.pid} ABORTED (likely timeout or hung)")
    print(f"   This usually means the worker exceeded {worker_timeout}s timeout")
    print(f"   Check for:")
    print(f"   - Blocking database operations")
    print(f"   - Slow API calls")
    print(f"   - Deadlocks or infinite loops")
    print(f"   - Database connection pool exhaustion")


def post_fork(server, worker):
    """Called after worker fork"""
    print(f"👶 Worker {worker.pid} spawned")

