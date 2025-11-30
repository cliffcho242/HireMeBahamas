#!/usr/bin/env python3
"""
Gunicorn configuration for HireMeBahamas backend

High Availability Configuration:
- Multi-worker deployment with thread-based concurrency
- Graceful shutdown and worker recycling
- Health check optimized timeouts
- Load balancer compatible settings

Optimized for:
- Memory-constrained environments (free tier hosting)
- CPU-intensive bcrypt password hashing
- PostgreSQL connections with SSL
- Preventing HTTP 499 (Client Closed Request) timeout errors
- Multi-instance deployments with load balancing
"""
import os

# Bind to 0.0.0.0 to accept external connections, use PORT env variable
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# ============================================
# High Availability Worker Configuration
# ============================================
# Worker configuration optimized for multi-instance deployments
# - Using gthread for thread-based concurrency with I/O waiting
# - Each worker handles multiple concurrent connections via threads
# - Formula: Total concurrent connections = workers × threads
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "gthread"
# Configurable via WEB_THREADS environment variable (default 8)
# Increased from 4 to 8 threads per worker for better concurrent handling
# This helps prevent HTTP 499 errors by allowing more simultaneous requests
threads = int(os.environ.get("WEB_THREADS", "8"))

# ============================================
# Timeout Configuration for Load Balancing
# ============================================
# - Reduced from 60s to 55s to ensure worker fails before platform's ~100s timeout
# - This helps return a proper 502/504 error instead of client disconnect (499)
# - Railway/Render have approximately 100-second gateway timeout
# - Setting worker timeout slightly below this ensures controlled failure
# - Graceful timeout allows clean worker shutdown during rolling deployments
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "55"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))
# Keep-alive for persistent connections (load balancer optimization)
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# ============================================
# Memory Management & Worker Recycling
# ============================================
# - max_requests limits worker memory growth from request processing
# - jitter prevents all workers from restarting simultaneously
# - Important for maintaining availability during recycling
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "500"))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "50"))

# ============================================
# Logging Configuration
# ============================================
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"  # Log to stdout for platform log aggregation
errorlog = "-"   # Log to stderr for platform log aggregation
# Access log format for monitoring and debugging
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ============================================
# Process Configuration
# ============================================
proc_name = "hiremebahamas_backend"

# Server mechanics
# Disabled preload_app to allow better error handling on startup
# and independent worker initialization (important for HA)
preload_app = False
pidfile = None  # Don't create pidfile in containerized environments
user = None
group = None
tmp_upload_dir = None

# Forwarded headers from load balancer
# Trust X-Forwarded-* headers from the load balancer
forwarded_allow_ips = os.environ.get("FORWARDED_ALLOW_IPS", "*")
secure_scheme_headers = {
    "X-FORWARDED-PROTOCOL": "ssl",
    "X-FORWARDED-PROTO": "https",
    "X-FORWARDED-SSL": "on",
}


# ============================================
# Server Hooks for High Availability
# ============================================
def on_starting(server):
    """
    Called just before the master process is initialized.
    """
    print("🚀 Gunicorn master process starting...")
    print(f"   Workers: {workers}")
    print(f"   Threads per worker: {threads}")
    print(f"   Total capacity: {workers * threads} concurrent connections")


def on_exit(server):
    """
    Called when gunicorn server is shutting down.
    
    Logs the shutdown event. The actual cleanup of database connections
    and other resources is handled by atexit handlers in each worker process,
    not by this server-level hook.
    """
    print("🛑 Gunicorn server shutting down...")


def worker_int(worker):
    """
    Called when a worker receives SIGINT or SIGQUIT.
    
    Important for graceful shutdown during rolling deployments.
    """
    print(f"👷 Worker {worker.pid} received interrupt signal, shutting down gracefully...")


def worker_exit(server, worker):
    """
    Called when a worker is exiting.
    
    Logs the worker exit event. The actual cleanup of database connections
    is handled by atexit handlers registered in final_backend_postgresql.py
    within each worker process.
    """
    print(f"👷 Worker {worker.pid} exiting...")


def worker_abort(worker):
    """
    Called when a worker is aborted due to timeout.
    
    Helps identify workers that are stuck or taking too long.
    """
    print(f"⚠️ Worker {worker.pid} aborted (timeout exceeded)")


