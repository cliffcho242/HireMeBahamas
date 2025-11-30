#!/usr/bin/env python3
"""Keep-alive worker: pings https://hiremebahamas.onrender.com/health every 50s forever."""
import time, requests
URL = "https://hiremebahamas.onrender.com/health"
while True:
    try:
        r = requests.get(URL, timeout=30)
        print(f"Ping {URL}: {r.status_code}", flush=True)
    except Exception as e:
        print(f"Ping failed: {e}", flush=True)
    time.sleep(50)
