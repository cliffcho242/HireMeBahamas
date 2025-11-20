#!/usr/bin/env python3
"""
Gunicorn configuration for HireMeBahamas backend
"""
import os

# Bind to 0.0.0.0 to accept external connections, use PORT env variable
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
max_requests = 1000
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
