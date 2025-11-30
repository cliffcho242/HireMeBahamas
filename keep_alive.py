#!/usr/bin/env python3
"""
Keep-alive Background Worker for Render
========================================

This script pings the HireMeBahamas backend every 70 seconds to prevent
Render's free tier from spinning down the service due to inactivity.

Environment Variables:
    RENDER_EXTERNAL_URL: The external URL of the Render web service
                         (e.g., https://hiremebahamas.onrender.com)

Render Dashboard Setup:
    1. New → Background Worker
    2. Connect your GitHub repository  
    3. Runtime: Python 3
    4. Region: Oregon (same as web service)
    5. Build Command: pip install requests
    6. Start Command: python keep_alive.py
    7. Environment Variables:
       - RENDER_EXTERNAL_URL = https://hiremebahamas.onrender.com
       - PYTHONUNBUFFERED = true
"""
import os
import sys
import time

import requests

# Get the external URL from environment variable
url = os.environ.get("RENDER_EXTERNAL_URL")

if not url:
    print("ERROR: RENDER_EXTERNAL_URL environment variable is not set.", flush=True)
    print("Please set it to your Render service URL (e.g., https://hiremebahamas.onrender.com)", flush=True)
    sys.exit(1)

# Use the lightweight /health/ping endpoint
ping_url = f"{url}/health/ping"

print(f"Keep-alive worker started. Pinging {ping_url} every 70 seconds.", flush=True)

while True:
    try:
        response = requests.get(ping_url, timeout=10)
        print(f"[KEEPALIVE] Ping {ping_url}: {response.status_code}", flush=True)
    except Exception:
        # Silently continue on error - the main web service may be restarting
        pass
    time.sleep(70)
