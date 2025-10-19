#!/usr/bin/env python3
"""
Gunicorn configuration for HireMeBahamas backend
"""

bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
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
preload_app = True
pidfile = "gunicorn.pid"
user = None
group = None
tmp_upload_dir = None