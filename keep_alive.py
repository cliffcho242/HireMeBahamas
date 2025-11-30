#!/usr/bin/env python3
"""
Keep-alive Background Worker for Render (Zero Cold-Start Solution)
===================================================================

Pings the backend every 40 seconds to prevent Render from sleeping.
Uses exponential backoff on failures to handle service restarts gracefully.

Environment Variables:
    APP_URL: The external URL of the Render web service
             (e.g., https://hiremebahamas.onrender.com)
    
    (Also supports RENDER_EXTERNAL_URL for backward compatibility)

Render Dashboard Setup:
    1. New → Background Worker
    2. Connect your GitHub repository  
    3. Name: keep-alive
    4. Runtime: Python 3
    5. Region: Oregon (same as web service)
    6. Build Command: pip install requests
    7. Start Command: python keep_alive.py
    8. Environment Variables:
       - APP_URL = https://hiremebahamas.onrender.com
       - PYTHONUNBUFFERED = true
"""
import os
import sys
import time
import requests

url = os.environ.get("APP_URL") or os.environ.get("RENDER_EXTERNAL_URL")
if not url:
    print("ERROR: APP_URL not set", flush=True)
    sys.exit(1)

ping_url, delay, max_delay = f"{url}/health", 40, 300
print(f"Keep-alive started: {ping_url} every {delay}s", flush=True)

while True:
    try:
        r = requests.get(ping_url, timeout=10)
        print(f"[OK] {r.status_code} in {r.elapsed.total_seconds()*1000:.0f}ms", flush=True)
        delay = 40  # Reset on success
    except Exception as e:
        print(f"[FAIL] {type(e).__name__}, retry in {delay}s", flush=True)
        delay = min(delay * 2, max_delay)  # Exponential backoff
    time.sleep(delay)
