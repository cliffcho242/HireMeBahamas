#!/usr/bin/env python3
"""Render Keep-Alive: Pings /health every 40s with retry + exponential backoff."""
import os, time, requests
url, delay, max_delay = os.getenv("RENDER_EXTERNAL_URL", os.getenv("APP_URL", "https://hiremebahamas.onrender.com")), 40, 300
print(f"Keep-alive: {url}/health every {delay}s", flush=True)
while True:
    try:
        r = requests.get(f"{url}/health", timeout=10)
        print(f"[OK] {r.status_code} {r.elapsed.total_seconds()*1000:.0f}ms", flush=True); delay = 40
    except Exception as e:
        print(f"[FAIL] {type(e).__name__} retry:{delay}s", flush=True); delay = min(delay * 2, max_delay)
    time.sleep(delay)
