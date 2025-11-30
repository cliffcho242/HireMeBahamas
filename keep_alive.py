#!/usr/bin/env python3
"""ULTIMATE Render Keep-Alive: Exponential backoff + warmup for 100% uptime."""
import os, time, requests
from datetime import datetime, timedelta

URL = os.getenv("RENDER_EXTERNAL_URL", "https://hiremebahamas.onrender.com").rstrip("/") + "/health"
print(f"ULTIMATE KEEP-ALIVE → {URL}")
start, ok, lvl = datetime.now(), 0, 0

while True:
    base = 20 if datetime.now() - start < timedelta(minutes=5) else 55
    mode, wait = ("WARMUP" if base == 20 else "NORMAL") + f" {base}s", min(10 * 2**lvl, 300) if lvl else base
    try:
        if requests.get(URL, timeout=12, headers={"User-Agent": "KeepAlive/1.0"}).status_code == 200:
            ok += 1
            if ok >= 3: lvl, ok = 0, 0
            print(f"OK — {mode} | lvl={lvl} | streak={ok}")
        else: ok, lvl = 0, min(lvl + 1, 5); print(f"FAIL — {mode} | lvl={lvl} | wait={wait}s")
    except Exception as e: ok, lvl = 0, min(lvl + 1, 5); print(f"FAIL ({e}) — {mode} | lvl={lvl} | wait={wait}s")
    time.sleep(wait)
