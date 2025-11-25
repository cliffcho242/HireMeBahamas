#!/usr/bin/env python3
"""
Gunicorn configuration for HireMeBahamas backend

Optimized for:
- Memory-constrained environments (free tier hosting)
- CPU-intensive bcrypt password hashing
- PostgreSQL connections with SSL
- Preventing HTTP 499 (Client Closed Request) timeout errors
"""
import os

# Bind to 0.0.0.0 to accept external connections, use PORT env variable
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"

# Worker configuration optimized for memory-constrained environments
# - Reduced from 4 to 2 workers to prevent memory exhaustion (SIGKILL)
# - Using gthread for thread-based concurrency with I/O waiting
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
worker_class = "gthread"
# Increased from 4 to 8 threads per worker for better concurrent handling
# This helps prevent HTTP 499 errors by allowing more simultaneous requests
threads = 8

# Timeout configuration
# - Reduced from 180s to 60s to fail faster and prevent long waits
# - If a request takes >60s, something is wrong - better to fail fast
# - Added graceful timeout to allow clean worker shutdown
timeout = 60
graceful_timeout = 30
keepalive = 5

# Memory management
# - max_requests limits worker memory growth from request processing
# - jitter prevents all workers from restarting simultaneously
max_requests = 500
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "hiremebahamas_backend"

# Server mechanics
preload_app = False  # Disabled to allow better error handling on startup
pidfile = None  # Don't create pidfile in Railway
user = None
group = None
tmp_upload_dir = None
