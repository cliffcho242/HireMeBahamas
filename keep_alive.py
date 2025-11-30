#!/usr/bin/env python3
"""
Keep-Alive Background Worker for Render

This script runs as a background worker on Render to prevent the backend
from going to sleep due to inactivity. It pings the health endpoint
every 70 seconds.

Render's free tier sleeps services after 15 minutes of inactivity.
By pinging every 70 seconds, we ensure the service stays awake.

Usage:
    Set RENDER_EXTERNAL_URL environment variable to your service's URL
    (e.g., https://hiremebahamas.onrender.com)

    Add to render.yaml as a background worker:
    - type: worker
      name: keep-alive
      runtime: python
      startCommand: python keep_alive.py
"""
import os
import sys
import time

import requests

# Get the Render external URL from environment
url = os.environ.get("RENDER_EXTERNAL_URL")
if not url:
    print("ERROR: RENDER_EXTERNAL_URL environment variable is not set.", file=sys.stderr)
    print("Please set RENDER_EXTERNAL_URL to your Render service URL", file=sys.stderr)
    print("Example: RENDER_EXTERNAL_URL=https://hiremebahamas.onrender.com", file=sys.stderr)
    sys.exit(1)

while True:
    try:
        requests.get(f"{url}/health/ping", timeout=10)
    except Exception:
        pass
    time.sleep(70)  # every 70 seconds
