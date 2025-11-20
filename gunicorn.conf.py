#!/usr/bin/env python3
"""
Gunicorn configuration for HireMeBahamas backend
This file provides defaults but can be overridden by command-line arguments
"""
import os

# Bind to Railway's PORT if available, otherwise fallback
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 2
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
preload_app = False  # Set to False to avoid blocking on database init
pidfile = None  # Don't create pidfile in Railway
user = None
group = None
tmp_upload_dir = None
