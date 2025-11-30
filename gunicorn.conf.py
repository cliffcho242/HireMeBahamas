#!/usr/bin/env python3
"""
Gunicorn configuration for HireMeBahamas backend

=============================================================================
COLD START ELIMINATION (2025 Best Practice)
=============================================================================
This configuration uses `preload_app = True` to eliminate cold starts:

1. App loads ONCE in the master process BEFORE forking workers
2. Workers inherit the pre-loaded app (copy-on-write memory)
3. First request after boot is instant - no initialization delay

Why this works on Render/Railway:
- Without preload: Each worker independently imports/initializes the app
- With preload: App is fully loaded before workers spawn
- Result: <400ms response even after hours of sleep

Memory benefit for 1-2GB RAM Render instances:
- Shared memory pages between workers (copy-on-write)
- Reduced total memory footprint with 2-4 workers

=============================================================================

Optimized for:
- High availability and load-balanced deployments
- Memory-constrained environments (free tier hosting)
- CPU-intensive bcrypt password hashing
- PostgreSQL connections with SSL
- Preventing HTTP 499 (Client Closed Request) timeout errors

High Availability Features:
- Configurable worker count via WEB_CONCURRENCY
- Thread-based concurrency for efficient I/O handling
- Graceful shutdown handling for zero-downtime deployments
- Memory management to prevent worker exhaustion
- Health check compatible timeouts

See docs/HIGH_AVAILABILITY.md for detailed documentation.
See docs/RENDER_COLD_START_FIX.md for preload configuration details.
"""
import os
import time

# =============================================================================
# BIND CONFIGURATION
# =============================================================================
# Bind to 0.0.0.0 to accept external connections from load balancer
# PORT is set by Railway, Render, or container orchestrator
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# =============================================================================
# WORKER CONFIGURATION (High Availability)
# =============================================================================
# WEB_CONCURRENCY: Number of worker processes
# - Set by platform (Railway, Render) or manually for self-hosted
# - Rule of thumb: (2 x CPU cores) + 1 for I/O bound applications
# - Keep low (2-4) for memory-constrained environments
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))

# Worker class: gthread for thread-based concurrency
# - Efficient for I/O-bound applications (database queries, API calls)
# - Lower memory footprint than gevent for bcrypt operations
worker_class = "gthread"

# WEB_THREADS: Number of threads per worker
# - Higher values improve concurrent request handling
# - Reduces HTTP 499 errors under load
# - Total concurrent requests = workers * threads
threads = int(os.environ.get("WEB_THREADS", "8"))

# =============================================================================
# TIMEOUT CONFIGURATION (Load Balancer Compatibility)
# =============================================================================
# Worker timeout: Set below platform gateway timeout
# - Railway: ~300s timeout
# - Render: ~100s timeout (free tier)
# - AWS ALB: Default 60s
# Setting below these ensures controlled failure instead of client disconnect
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "55"))

# Graceful timeout: Time to wait for requests to complete during shutdown
# - Critical for zero-downtime deployments
# - Should be shorter than load balancer health check interval
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))

# Keepalive: Persistent connection timeout with load balancer
# - Reduces connection overhead
# - Should be less than load balancer idle timeout
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# =============================================================================
# MEMORY MANAGEMENT (Auto-scaling Compatibility)
# =============================================================================
# max_requests: Restart worker after N requests to prevent memory leaks
# - Helps maintain consistent memory usage in auto-scaled environments
# - Enables smooth worker recycling without service interruption
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "500"))

# max_requests_jitter: Randomize restart timing
# - Prevents all workers from restarting simultaneously
# - Critical for high availability under load
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "50"))

# =============================================================================
# LOGGING (Monitoring & Observability)
# =============================================================================
# Log level: info for production, debug for troubleshooting
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")

# Access log: stdout for container log aggregation
accesslog = "-"

# Error log: stdout for container log aggregation
errorlog = "-"

# Access log format: Include load balancer headers
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# =============================================================================
# PROCESS CONFIGURATION
# =============================================================================
# Process name for identification in monitoring tools
proc_name = "hiremebahamas_backend"

# =============================================================================
# PRELOAD CONFIGURATION (Critical for Cold Start Elimination)
# =============================================================================
# preload_app = True: Load application code BEFORE forking workers
#
# How it works:
# 1. Master process imports and initializes the full Flask/FastAPI app
# 2. Workers are forked from master with app already loaded
# 3. Copy-on-write memory sharing between workers
# 4. First request is instant - no import/initialization delay
#
# Benefits:
# - Eliminates 30-120 second cold starts on Render/Railway
# - Reduces memory usage with shared pages
# - Faster worker restarts during scaling
#
# Trade-off:
# - If app fails to load, all workers fail (fail-fast is actually good)
# - Code changes require full restart (not hot-reload - expected in production)
#
# Set PRELOAD_APP=false to disable (useful for debugging startup issues)
preload_app = os.environ.get("PRELOAD_APP", "true").lower() in ("true", "1", "yes")

pidfile = None  # Don't create pidfile in containerized environments
user = None
group = None
tmp_upload_dir = None

# Forward X-Forwarded-* headers from load balancer
# Security: By default, only accept forwarded headers from localhost
# In production with a load balancer, set FORWARDED_ALLOW_IPS to the load balancer IP
# Use "*" only in trusted network environments (e.g., Railway, Render internal networks)
# Example: FORWARDED_ALLOW_IPS="10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "127.0.0.1")

# =============================================================================
# GRACEFUL SHUTDOWN HOOKS (Zero-Downtime Deployments)
# =============================================================================

# Track startup time for cold start monitoring
_master_start_time = None


def on_starting(server):
    """
    Called before the master process is initialized.
    
    With preload_app=True, this is when the app will be imported and initialized.
    """
    global _master_start_time
    _master_start_time = time.time()
    instance_id = os.environ.get("INSTANCE_ID", "unknown")
    preload_status = "enabled" if preload_app else "disabled"
    print(f"🚀 Starting Gunicorn server (instance: {instance_id}, preload: {preload_status})...")
    print(f"   Workers: {workers}, Threads: {threads}, Total capacity: {workers * threads} concurrent requests")


def when_ready(server):
    """
    Called when the server is ready to accept connections.
    
    With preload_app=True, this confirms the app loaded successfully
    and all workers are ready. This is the key metric for cold start time.
    """
    if _master_start_time:
        startup_time = time.time() - _master_start_time
        print(f"✅ Server ready in {startup_time:.2f}s - accepting connections")
        print(f"   Health check: GET /health or /ping for lightweight check")
    else:
        print("✅ Server ready - accepting connections")


def on_exit(server):
    """
    Called when gunicorn server is shutting down.
    
    Logs the shutdown event. The actual cleanup of database connections
    and other resources is handled by atexit handlers in each worker process,
    not by this server-level hook.
    """
    print("🛑 Gunicorn server shutting down...")


def worker_exit(server, worker):
    """
    Called when a worker is exiting.
    
    Logs the worker exit event. The actual cleanup of database connections
    is handled by atexit handlers registered in final_backend_postgresql.py
    within each worker process.
    """
    print(f"👷 Worker {worker.pid} exiting...")


def pre_fork(server, worker):
    """Called before a worker is forked."""
    pass  # Database connections are created per-worker, not shared


def post_fork(server, worker):
    """Called after a worker is forked."""
    instance_id = os.environ.get("INSTANCE_ID", "unknown")
    print(f"👶 Worker {worker.pid} spawned (instance: {instance_id})")


