#!/usr/bin/env python3
"""Pings /health every 40s with retry logic to keep Render always-on."""
import os, sys, time, requests
url = os.environ.get("APP_URL") or os.environ.get("RENDER_EXTERNAL_URL")
if not url: print("ERROR: APP_URL not set", flush=True); sys.exit(1)
ping_url, delay, max_delay = f"{url}/health", 40, 300
print(f"Keep-alive: {ping_url} every {delay}s", flush=True)
while True:
    try: r = requests.get(ping_url, timeout=10); print(f"[OK] {r.status_code} {r.elapsed.total_seconds()*1000:.0f}ms", flush=True); delay = 40
    except Exception as e: print(f"[FAIL] {type(e).__name__}, retry {delay}s", flush=True); delay = min(delay * 2, max_delay)
    time.sleep(delay)
