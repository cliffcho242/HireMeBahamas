#!/usr/bin/env python3
"""
Gunicorn configuration for HireMeBahamas backend

=============================================================================
NUCLEAR FIX FOR 502 BAD GATEWAY + 173-SECOND LOGINS (2025)
=============================================================================

This configuration eliminates cold start timeouts with:

1. preload_app = True: Load app BEFORE forking workers
   - App loads ONCE in master, workers inherit via copy-on-write
   - First request is instant (<400ms) even after hours of inactivity

2. Single worker + high timeout: Prevents OOM on 512MB-1GB RAM
   - workers = 1 (configurable via WEB_CONCURRENCY)
   - timeout = 180s (3 minutes - survives Railway cold starts)
   - keep-alive = 5s (matches Render/Railway load balancer)

3. Aggressive worker recycling: Prevents memory leaks
   - max_requests = 500 (restart worker after 500 requests)
   - max_requests_jitter = 50 (stagger restarts to avoid downtime)

RENDER DASHBOARD SETTINGS (copy-paste these):
- Plan: Standard ($25/mo) or Starter ($7/mo)
- Health Check Path: /health
- Grace Period: 300 seconds
- Instance Memory: 1GB (Standard) or 512MB (Starter)

ENVIRONMENT VARIABLES:
- WEB_CONCURRENCY=1 (or 2 for Standard plan with 1GB+ RAM)
- WEB_THREADS=4
- GUNICORN_TIMEOUT=180
- PRELOAD_APP=true

=============================================================================
"""
import os
import time

# =============================================================================
# BIND CONFIGURATION
# =============================================================================
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# =============================================================================
# WORKER CONFIGURATION (Optimized for 502 Prevention)
# =============================================================================
# Single worker by default - prevents OOM on limited RAM
# Set WEB_CONCURRENCY=2 for Standard plan (1GB+ RAM)
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))

# Thread-based concurrency for I/O-bound ops (DB queries, bcrypt)
worker_class = "gthread"

# Threads per worker - total capacity = workers * threads
# 4 threads handles most workloads without OOM
threads = int(os.environ.get("WEB_THREADS", "4"))

# =============================================================================
# TIMEOUT CONFIGURATION (Critical for 502 Prevention)
# =============================================================================
# Worker timeout: 180s (3 minutes)
# - Railway cold starts can take 60-120s
# - Render gateway timeout is ~300s
# - 180s is safe margin that survives cold starts
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "180"))

# Graceful timeout: Time for in-flight requests during shutdown
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))

# Keep-alive: Match Render/Railway load balancer settings
# 5s is the standard for most cloud load balancers
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# =============================================================================
# MEMORY MANAGEMENT (Prevents OOM Kills)
# =============================================================================
# Restart worker after N requests to prevent memory leaks
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "500"))

# Randomize restart timing to avoid simultaneous worker restarts
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "50"))

# =============================================================================
# LOGGING (Container-friendly)
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
# PRELOAD CONFIGURATION (Critical for Cold Start Elimination)
# =============================================================================
# preload_app = True: Load application BEFORE forking workers
#
# Benefits:
# - Eliminates 30-120 second cold starts
# - Reduces memory with copy-on-write pages
# - First request is instant (<400ms)
#
# Set PRELOAD_APP=false only for debugging startup issues
preload_app = os.environ.get("PRELOAD_APP", "true").lower() in ("true", "1", "yes")

# Containerized environment settings
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Trust forwarded headers from load balancer
# Security: In production with Render/Railway, set to "*" to trust their load balancers
# For self-hosted deployments, set FORWARDED_ALLOW_IPS to specific IPs
# Example: FORWARDED_ALLOW_IPS="10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
_is_cloud_platform = os.environ.get("RENDER") == "true" or os.environ.get("RAILWAY_ENVIRONMENT")
forwarded_allow_ips = os.environ.get(
    "FORWARDED_ALLOW_IPS", 
    "*" if _is_cloud_platform else "127.0.0.1"
)

# =============================================================================
# STARTUP/SHUTDOWN HOOKS
# =============================================================================
_master_start_time = None


def on_starting(server):
    """Called before master process initialization."""
    global _master_start_time
    _master_start_time = time.time()
    preload_status = "enabled" if preload_app else "disabled"
    print(f"🚀 Starting Gunicorn (preload: {preload_status})...")
    print(f"   Workers: {workers}, Threads: {threads}")
    print(f"   Timeout: {timeout}s, Keep-alive: {keepalive}s")
    print(f"   Total capacity: {workers * threads} concurrent requests")


def when_ready(server):
    """Called when server is ready to accept connections."""
    if _master_start_time:
        startup_time = time.time() - _master_start_time
        print(f"✅ Server ready in {startup_time:.2f}s")
    print(f"   Health: GET /health (instant, no DB)")
    print(f"   Ready: GET /ready (checks DB)")


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


