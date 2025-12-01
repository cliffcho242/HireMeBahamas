#!/usr/bin/env python3
"""
=============================================================================
NUCLEAR KEEP-ALIVE WORKER - 2025 IMMORTAL EDITION
=============================================================================
Pings /health every 45 seconds to prevent Render cold starts.

Deploy as Render Background Worker:
  - Name: keep-alive
  - Runtime: Python 3
  - Build Command: pip install requests
  - Start Command: python keep_alive.py

CRITICAL: NO ENVIRONMENT VARIABLES
  - URL is hardcoded - never fails due to missing env vars
  - Retries with exponential backoff and jitter
  - Never exits, never gives up, never dies

Cost: $0 on Render Free tier for Background Workers
Effect: Eliminates 502 Bad Gateway and 2+ minute cold starts
=============================================================================
"""
import random
import time

import requests

# =============================================================================
# HARDCODED CONFIGURATION - NO ENV VARS = NO FAILURES
# =============================================================================
HEALTH_URL = "https://hiremebahamas.onrender.com/health"
PING_INTERVAL_SECONDS = 45  # Keep service warm without overloading

# Retry configuration
MAX_RETRIES = 3  # Retries per ping cycle
BASE_BACKOFF_SECONDS = 2  # Base for exponential backoff
MAX_BACKOFF_LEVEL = 6  # Cap at 2^6 = 64 seconds

# =============================================================================
# STARTUP BANNER
# =============================================================================
print("=" * 60)
print("🔥 NUCLEAR KEEP-ALIVE WORKER - 2025 IMMORTAL EDITION")
print(f"   Target: {HEALTH_URL}")
print(f"   Interval: {PING_INTERVAL_SECONDS}s")
print(f"   Retries: {MAX_RETRIES} per cycle")
print("=" * 60)

# =============================================================================
# IMMORTAL PING LOOP
# =============================================================================
backoff = 0
consecutive_failures = 0

while True:
    success = False
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Increasing timeout per attempt (20s, 30s, 40s)
            # Handles cold starts which can take 30-60 seconds
            response = requests.get(
                HEALTH_URL,
                timeout=(6, 20 + attempt * 10),
                headers={"User-Agent": "ImmortalKeepAlive/2025"}
            )
            
            if response.status_code == 200:
                print(f"✅ [{time.strftime('%H:%M:%S')}] PING OK → {response.status_code} "
                      f"in {response.elapsed.total_seconds():.2f}s")
                success = True
                consecutive_failures = 0
                backoff = 0
                break
            else:
                print(f"⚠️ [{time.strftime('%H:%M:%S')}] HTTP {response.status_code} "
                      f"(attempt {attempt}/{MAX_RETRIES})")
                
        except requests.exceptions.Timeout as e:
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] TIMEOUT attempt {attempt}/{MAX_RETRIES}")
            if attempt < MAX_RETRIES:
                time.sleep(BASE_BACKOFF_SECONDS ** attempt)
                
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 [{time.strftime('%H:%M:%S')}] CONNECTION ERROR attempt {attempt}/{MAX_RETRIES}")
            if attempt < MAX_RETRIES:
                time.sleep(BASE_BACKOFF_SECONDS ** attempt)
                
        except Exception as e:
            print(f"❌ [{time.strftime('%H:%M:%S')}] ERROR attempt {attempt}/{MAX_RETRIES} — "
                  f"{type(e).__name__}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(BASE_BACKOFF_SECONDS ** attempt)

    if success:
        # Wait standard interval before next ping
        time.sleep(PING_INTERVAL_SECONDS)
    else:
        # All retries failed - use exponential backoff with jitter
        consecutive_failures += 1
        backoff = min(backoff + 1, MAX_BACKOFF_LEVEL)
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, 5)
        wait_time = (BASE_BACKOFF_SECONDS ** backoff) + jitter
        
        print(f"🔁 [{time.strftime('%H:%M:%S')}] BACKOFF level {backoff} — "
              f"waiting {wait_time:.1f}s (failures: {consecutive_failures})")
        
        # Alert on persistent failures
        if consecutive_failures >= 10:
            print(f"🚨 ALERT: {consecutive_failures} consecutive failures! "
                  "Service may be down.")
        
        time.sleep(wait_time)
