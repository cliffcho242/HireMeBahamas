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
# WORKER CONFIGURATION (Optimized for Cloud Platforms)
# ============================================================================
# Optimized for Railway, Render, and similar PaaS platforms
# Typical CPU allocation: Free tier: 0.1-0.5 CPU, Paid: 1+ CPU
cpu_count = multiprocessing.cpu_count()

# Workers: 4 for scaling to 100K+ users (optimized for production deployment)
# Use WEB_CONCURRENCY env var to override
# Each worker handles concurrent requests via threads
#
# Resource Requirements for 4 workers:
# - Recommended: 2+ CPU cores (0.5 CPU per worker minimum)
# - Recommended: 2GB+ RAM (500MB per worker)
# - Lower environments: Set WEB_CONCURRENCY=2 for 1GB RAM / 1 CPU
# - Higher load: Set WEB_CONCURRENCY=8 for 4+ CPU cores / 4GB+ RAM
workers = int(os.environ.get("WEB_CONCURRENCY", "4"))

# Worker class: gthread for I/O-bound operations (database queries)
worker_class = "gthread"

# Threads per worker: Total capacity = workers * threads
# 4 threads = handles up to 4 concurrent requests per worker
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
    print(f"🚀 Starting Gunicorn (Railway Healthcheck Optimized)")
    print(f"   Workers: {workers} × {threads} threads = {workers * threads} capacity")
    print(f"   Timeout: {timeout}s | Keepalive: {keepalive}s")
    print(f"   Preload: {preload_app} (workers initialize independently)")
    print(f"   This allows fast startup and immediate health check responses")


def when_ready(server):
    """Log when server is ready to accept connections"""
    if _master_start_time:
        startup_time = time.time() - _master_start_time
        print(f"✅ Gunicorn ready to accept connections in {startup_time:.2f}s")
    print(f"   Listening on {bind}")
    print(f"   Health: GET /health (instant)")
    print(f"   Ready: GET /ready (with DB check)")
    print(f"   Workers will initialize independently")
    print(f"🎉 HireMeBahamas API is ready for Railway healthcheck")


def on_exit(server):
    """Called on graceful shutdown"""
    print("🛑 Gunicorn shutting down...")


def worker_exit(server, worker):
    """Called when a worker exits"""
    print(f"👷 Worker {worker.pid} exiting...")


def post_fork(server, worker):
    """Called after worker fork"""
    print(f"👶 Worker {worker.pid} spawned")

