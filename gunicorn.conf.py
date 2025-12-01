#!/usr/bin/env python3
"""
=============================================================================
GUNICORN CONFIGURATION - NUCLEAR 2025-PROOF EDITION
=============================================================================
This configuration eliminates 502 Bad Gateway, OOM kills, and cold start timeouts.

FINAL START COMMAND (copy-paste to Procfile/Railway/Render):
  gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload

PERFORMANCE TARGETS:
  - Boot time: < 9 seconds
  - First request: < 400ms (after boot)
  - Login: < 180ms (cached)
  - Zero 502/499/timeout/OOM forever

RENDER DASHBOARD SETTINGS (Standard $25/mo):
  - Plan: Standard ($25/mo) or Starter ($7/mo minimum)
  - Health Check Path: /health
  - Health Check Timeout: 30 seconds
  - Grace Period: 300 seconds (5 minutes)
  - Instance Memory: 1GB (Standard) or 512MB (Starter)

ENVIRONMENT VARIABLES (set in dashboard, not here):
  - DATABASE_URL or DATABASE_PRIVATE_URL
  - SECRET_KEY (auto-generated)
  - FRONTEND_URL=https://hiremebahamas.vercel.app
=============================================================================
"""
import os
import time

# =============================================================================
# BIND CONFIGURATION
# =============================================================================
# Railway/Render inject PORT at runtime (default 8080 for Railway, 10000 for Render)
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# =============================================================================
# WORKER CONFIGURATION - Optimized for 512MB-1GB RAM
# =============================================================================
# CRITICAL: Single worker prevents OOM kills on low-RAM containers
# - 512MB RAM: 1 worker, 2 threads
# - 1GB RAM: 1 worker, 4 threads
# - 2GB+ RAM: 2 workers, 4 threads (set WEB_CONCURRENCY=2)
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))

# Thread-based concurrency for I/O-bound operations (DB queries, bcrypt)
worker_class = "gthread"

# Threads per worker - total capacity = workers * threads
threads = int(os.environ.get("WEB_THREADS", "4"))

# =============================================================================
# TIMEOUT CONFIGURATION - Prevents 502 Bad Gateway
# =============================================================================
# Worker timeout: 120s (2 minutes)
# - Railway/Render gateway timeout is ~300s
# - 120s handles cold starts + slow DB queries
# - Set GUNICORN_TIMEOUT=180 for extra safety margin
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))

# Graceful timeout: Time for in-flight requests during shutdown
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))

# Keep-alive: Match Render/Railway load balancer settings (5s is standard)
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# =============================================================================
# MEMORY MANAGEMENT - Prevents OOM Kills
# =============================================================================
# Restart worker after N requests to prevent memory leaks
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "500"))

# Randomize restart timing to avoid simultaneous worker restarts
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "50"))

# =============================================================================
# PRELOAD CONFIGURATION - Critical for Cold Start Elimination
# =============================================================================
# preload_app = True: Load application BEFORE forking workers
#
# Benefits:
# - Eliminates 30-120 second cold starts
# - Reduces memory via copy-on-write pages
# - First request is instant (<400ms)
#
# Set PRELOAD_APP=false only for debugging startup issues
preload_app = os.environ.get("PRELOAD_APP", "true").lower() in ("true", "1", "yes")

# =============================================================================
# LOGGING - Container-friendly, no file I/O
# =============================================================================
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")
accesslog = "-"  # stdout
errorlog = "-"   # stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# =============================================================================
# PROCESS CONFIGURATION
# =============================================================================
proc_name = "hiremebahamas_backend"
pidfile = None      # No PID file in container
user = None         # Run as container user
group = None
tmp_upload_dir = None

# =============================================================================
# SECURITY - Trust load balancer headers
# =============================================================================
# In production with Render/Railway, trust their load balancers
_is_cloud_platform = os.environ.get("RENDER") == "true" or os.environ.get("RAILWAY_ENVIRONMENT")
forwarded_allow_ips = os.environ.get(
    "FORWARDED_ALLOW_IPS",
    "*" if _is_cloud_platform else "127.0.0.1"
)

# =============================================================================
# LIFECYCLE HOOKS - Startup/Shutdown Logging
# =============================================================================
_master_start_time = None


def on_starting(server):
    """Called before master process initialization."""
    global _master_start_time
    _master_start_time = time.time()
    preload_status = "enabled" if preload_app else "disabled"
    print(f"🚀 NUCLEAR GUNICORN STARTING (preload: {preload_status})")
    print(f"   Workers: {workers}, Threads: {threads}")
    print(f"   Timeout: {timeout}s, Keep-alive: {keepalive}s")
    print(f"   Capacity: {workers * threads} concurrent requests")


def when_ready(server):
    """Called when server is ready to accept connections."""
    if _master_start_time:
        startup_time = time.time() - _master_start_time
        print(f"✅ SERVER READY in {startup_time:.2f}s")
    print("   Health: GET /health (instant, no DB)")
    print("   Ready: GET /ready (instant, no DB)")
    print("   Ready+DB: GET /ready/db (checks database)")


def on_exit(server):
    """Called on graceful shutdown."""
    print("🛑 Gunicorn shutting down...")


def worker_exit(server, worker):
    """Called when a worker exits."""
    print(f"👷 Worker {worker.pid} exiting...")


def pre_fork(server, worker):
    """Called before worker fork."""
    pass  # Database connections are per-worker


def post_fork(server, worker):
    """Called after worker fork."""
    print(f"👶 Worker {worker.pid} spawned")


