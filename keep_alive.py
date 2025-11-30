#!/usr/bin/env python3
"""
Optimal Render Keep-Alive: Mathematically optimal intervals for 100% uptime.

Rules:
1. Base interval = 55s (Render free tier sleeps after ~15 min = 900s → 900÷16 = 56.25s → 55s safest)
2. First 5 minutes after deploy → ping every 20s (covers cold-boot window)
3. After 5 minutes → switch to 55s forever
4. On any failed ping → immediately drop to 15s aggressive mode for 2 min, then back to normal
"""
import os
import time
import requests
from datetime import datetime, timedelta

# NEVER CHANGE THIS URL — HARDCODED FOR ZERO FAILURE
BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "https://hiremebahamas.onrender.com").rstrip("/")
HEALTH_URL = f"{BASE_URL}/health"

print(f"OPTIMAL KEEP-ALIVE STARTED → {HEALTH_URL}")

start_time = datetime.now()
aggressive_until = None  # type: ignore

while True:
    # Determine current interval - store current time once for efficiency
    now = datetime.now()
    uptime = now - start_time

    if aggressive_until and now < aggressive_until:
        interval = 15
        mode = "AGGRESSIVE 15s"
    elif uptime < timedelta(minutes=5):
        interval = 20
        mode = "WARMUP 20s"
    else:
        interval = 55
        mode = "NORMAL 55s"

    try:
        r = requests.get(HEALTH_URL, timeout=12, headers={"User-Agent": "OptimalKeepAlive/1.0"})
        if r.status_code == 200:
            print(f"PING OK — {mode}")
            aggressive_until = None  # reset on success
        else:
            print(f"PING WARN {r.status_code} — {mode} → switching to AGGRESSIVE 15s for 2 min")
            aggressive_until = datetime.now() + timedelta(minutes=2)
    except Exception as e:
        print(f"PING FAILED ({e}) → switching to AGGRESSIVE 15s for 2 min")
        aggressive_until = datetime.now() + timedelta(minutes=2)

    time.sleep(interval)
