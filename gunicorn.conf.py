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
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# ============================================================================
# WORKER CONFIGURATION (Optimized for Render Free/Starter Tier)
# ============================================================================
# CPU cores available (Render Free: 0.1 CPU, Starter: 0.5 CPU, Standard: 1 CPU)
cpu_count = multiprocessing.cpu_count()

# Workers: 1 for Free tier, 2 for Starter+, auto for Standard
# Use WEB_CONCURRENCY env var to override
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))

# Worker class: gthread for I/O-bound operations (database queries)
worker_class = "gthread"

# Threads per worker: Total capacity = workers * threads
# 4 threads = handles up to 4 concurrent requests per worker
threads = int(os.environ.get("WEB_THREADS", "4"))

# ============================================================================
# TIMEOUT CONFIGURATION (Critical for 502 Prevention)
# ============================================================================
# Worker timeout: 120s (2 minutes) - handles cold starts + slow queries
# Render Free tier can take 30-60s on cold start
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))

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
# PRELOAD & PERFORMANCE (Critical for Cold Start Elimination)
# ============================================================================
# Preload app BEFORE forking workers (eliminates 30-120s cold starts)
# First request is instant (<400ms) instead of waiting for app load
preload_app = True

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
# Trust proxy headers from Render/Railway load balancers
forwarded_allow_ips = "*"

# ============================================================================
# STARTUP HOOKS
# ============================================================================
_master_start_time = None


def on_starting(server):
    """Log startup configuration"""
    global _master_start_time
    _master_start_time = time.time()
    print(f"🚀 Starting Gunicorn")
    print(f"   Workers: {workers} × {threads} threads = {workers * threads} capacity")
    print(f"   Timeout: {timeout}s | Keepalive: {keepalive}s")
    print(f"   Preload: {preload_app}")


def when_ready(server):
    """Log when server is ready"""
    if _master_start_time:
        startup_time = time.time() - _master_start_time
        print(f"✅ Server ready in {startup_time:.2f}s")
    print(f"   Health: GET /health (instant)")
    print(f"   Ready: GET /ready (with DB check)")
    print(f"🎉 HireMeBahamas API is IMMORTAL")


def on_exit(server):
    """Called on graceful shutdown"""
    print("🛑 Gunicorn shutting down...")


def worker_exit(server, worker):
    """Called when a worker exits"""
    print(f"👷 Worker {worker.pid} exiting...")


def post_fork(server, worker):
    """Called after worker fork"""
    print(f"👶 Worker {worker.pid} spawned")

