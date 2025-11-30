#!/usr/bin/env python3
"""
NUCLEAR-GRADE Render Keep-Alive with jitter — Deploy once, win forever.

Rules:
1. First 5 min after deploy → 20s ± 5s jitter (covers cold-boot window)
2. Normal mode → 55s ± 10s jitter
3. On failure → exponential backoff (10→20→40→80→160→300s) + ±20s jitter
4. Reset backoff only after 3 consecutive successes
5. Never sleep below 5s
"""
import os
import time
import random
import requests
from datetime import datetime, timedelta

# BULLETPROOF — CAN NEVER BE WRONG
BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "https://hiremebahamas.onrender.com").rstrip("/")
HEALTH_URL = f"{BASE_URL}/health"

print(f"NUCLEAR KEEP-ALIVE STARTED → {HEALTH_URL}")

start_time = datetime.now()
consecutive_success = 0
backoff_level = 0

while True:
    uptime = datetime.now() - start_time

    # Base interval + jitter
    if uptime < timedelta(minutes=5):
        base = 20
        jitter_sec = random.randint(-5, 5)
        mode = "WARMUP"
    else:
        base = 55
        jitter_sec = random.randint(-10, 10)
        mode = "NORMAL"

    # Apply backoff if failing
    if consecutive_success < 3 and backoff_level > 0:
        base = min(10 * (2 ** (backoff_level - 1)), 300)
        jitter_sec = random.randint(-20, 20)
        mode = f"BACKOFF L{backoff_level}"

    sleep_time = max(5, base + jitter_sec)  # never below 5s

    try:
        r = requests.get(
            HEALTH_URL,
            timeout=15,
            headers={"User-Agent": "NuclearKeepAlive/1.0"}
        )
        if r.status_code == 200:
            print(f"PING OK — {mode} → sleep {sleep_time}s")
            consecutive_success = min(consecutive_success + 1, 3)
            if consecutive_success >= 3:
                backoff_level = 0
                consecutive_success = 0
        else:
            raise Exception(f"HTTP {r.status_code}")
    except Exception as e:
        consecutive_success = 0
        backoff_level = min(backoff_level + 1, 6)  # Cap at level 6 (300s max)
        print(f"PING FAILED ({e}) → BACKOFF ↑ L{backoff_level} → sleep {sleep_time}s")

    time.sleep(sleep_time)
