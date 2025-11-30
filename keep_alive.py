#!/usr/bin/env python3
"""Render Keep-Alive: Pings /health every 40s with exponential backoff."""
import os, time, requests

APP_URL = os.getenv("RENDER_EXTERNAL_URL", "https://hiremebahamas.onrender.com")
delay, max_delay = 40, 300

while True:
    try:
        r = requests.get(f"{APP_URL}/health", timeout=10, headers={"User-Agent": "KeepAlive/1.0"})
        if r.status_code == 200:
            print("PING OK – Render awake", flush=True)
            delay = 40
        else:
            print(f"PING FAILED {r.status_code}", flush=True)
            delay = min(delay * 2, max_delay)
    except Exception as e:
        print(f"PING FAILED – {e}", flush=True)
        delay = min(delay * 2, max_delay)
    time.sleep(delay)
