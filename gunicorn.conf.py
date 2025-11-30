#!/usr/bin/env python3
"""
Gunicorn configuration for HireMeBahamas backend

=============================================================================
PRODUCTION-IMMORTAL CONFIGURATION (2025)
=============================================================================

PERFORMANCE TARGETS:
- Cold start: <12 seconds total
- First request: <400ms
- RAM: <450MB (Render Starter 512MB plan)
- Boot time: <10 seconds

KEY OPTIMIZATIONS:
1. preload_app = True: Load app BEFORE forking (instant first request)
2. 2 workers x 8 threads = 16 concurrent requests
3. max_requests = 500: Prevent memory leaks
4. timeout = 55: Below Render's 60s gateway timeout
5. gthread worker class: Efficient for I/O-bound workloads

MEMORY BUDGET (512MB Render Starter):
- Master process: ~50MB
- Worker 1: ~150MB (with preload memory sharing)
- Worker 2: ~150MB (with preload memory sharing)
- Connection pool: ~30MB
- Overhead buffer: ~70MB
- Total: ~450MB < 512MB ✅

=============================================================================
"""
import os
import time

# =============================================================================
# BIND CONFIGURATION
# =============================================================================
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# =============================================================================
# WORKER CONFIGURATION - OPTIMIZED FOR <450MB RAM
# =============================================================================
# Formula: workers = min(2 * CPU + 1, RAM / 200MB)
# For 512MB: 2 workers
# For 2GB: 4 workers
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "gthread"
threads = int(os.environ.get("WEB_THREADS", "8"))

# =============================================================================
# TIMEOUT CONFIGURATION - PREVENT 499/502/503
# =============================================================================
# timeout < gateway timeout (Render: 60s, Railway: 300s)
# graceful_timeout < health check interval
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "55"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# =============================================================================
# MEMORY MANAGEMENT - PREVENT OOM
# =============================================================================
# Restart workers periodically to prevent memory leaks
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "500"))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "50"))

# =============================================================================
# LOGGING - STRUCTURED FOR MONITORING
# =============================================================================
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# =============================================================================
# PROCESS CONFIGURATION
# =============================================================================
proc_name = "hiremebahamas_backend"

# =============================================================================
# PRELOAD CONFIGURATION - CRITICAL FOR COLD START ELIMINATION
# =============================================================================
# preload_app = True:
# 1. App loads ONCE in master BEFORE forking workers
# 2. Workers inherit pre-loaded app via copy-on-write
# 3. First request is instant (<400ms)
# 4. Memory shared between workers
preload_app = os.environ.get("PRELOAD_APP", "true").lower() in ("true", "1", "yes")

pidfile = None
user = None
group = None
tmp_upload_dir = None

# Trust load balancer headers (Render, Railway, Vercel)
forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "*")

# =============================================================================
# LIFECYCLE HOOKS - MONITORING & GRACEFUL SHUTDOWN
# =============================================================================

_master_start_time = None


def on_starting(server):
    """Called before master process initializes."""
    global _master_start_time
    _master_start_time = time.time()
    preload_status = "enabled" if preload_app else "disabled"
    print(f"🚀 Starting Gunicorn (preload: {preload_status})")
    print(f"   Workers: {workers}, Threads: {threads}")
    print(f"   Capacity: {workers * threads} concurrent requests")
    print(f"   Timeout: {timeout}s, Max requests: {max_requests}")


def when_ready(server):
    """Called when server is ready to accept connections."""
    if _master_start_time:
        startup_time = time.time() - _master_start_time
        print(f"✅ Server ready in {startup_time:.2f}s")
        print(f"   Health: GET /health (instant, no DB)")
        print(f"   Ready: GET /ready (checks DB)")
    else:
        print("✅ Server ready")


def on_exit(server):
    """Called when gunicorn server shuts down."""
    print("🛑 Gunicorn shutting down...")


def worker_exit(server, worker):
    """Called when a worker exits."""
    print(f"👷 Worker {worker.pid} exiting...")


def pre_fork(server, worker):
    """Called before worker is forked."""
    pass


def post_fork(server, worker):
    """Called after worker is forked."""
    instance_id = os.environ.get("INSTANCE_ID", "local")
    print(f"👶 Worker {worker.pid} spawned (instance: {instance_id})")


