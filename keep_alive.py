"""
=============================================================================
UNBREAKABLE KEEP-ALIVE WORKER FOR RENDER BACKGROUND SERVICE (2025 EDITION)
=============================================================================
This worker pings the web service every 45 seconds to prevent cold starts.

Deploy as Render Background Worker:
  - Name: keep-alive
  - Runtime: Python 3
  - Build Command: pip install requests
  - Start Command: python keep_alive.py
  - Environment: RENDER_EXTERNAL_URL=https://hiremebahamas.onrender.com

Cost: $0 on Render Free tier for Background Workers
Effect: Eliminates 502 Bad Gateway and 2+ minute cold starts
=============================================================================
"""
import os
import time
import random
import requests

# HARDCODED URL — NEVER FAILS
# Falls back to env var for flexibility in other deployments
DEFAULT_URL = "https://hiremebahamas.onrender.com"
_base_url = os.getenv("RENDER_EXTERNAL_URL", "").strip()

# Validate URL: must be non-empty and have a valid scheme (http/https)
if not _base_url or not _base_url.startswith(("http://", "https://")):
    _base_url = DEFAULT_URL

HEALTH_URL = _base_url + "/health"

# Ping interval: 45 seconds keeps service warm without overloading
PING_INTERVAL_SECONDS = 45

# Retry configuration
MAX_RETRIES = 5
CONNECT_TIMEOUT = 10  # seconds
READ_TIMEOUT = 30  # seconds (generous for cold start)

print("=" * 60)
print("🔥 UNBREAKABLE KEEP-ALIVE WORKER STARTED")
print(f"   Target: {HEALTH_URL}")
print(f"   Interval: {PING_INTERVAL_SECONDS}s")
print("=" * 60)

backoff = 0
consecutive_failures = 0

while True:
    success = False
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Fixed timeout to avoid blocking the keep-alive loop for too long
            # connect: 10s, read: 45s - handles cold starts without excessive delays
            response = requests.get(
                HEALTH_URL,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT + 15),  # (10s, 45s) max
                headers={
                    "User-Agent": "KeepAlive-Worker/2025",
                    "Accept": "application/json",
                }
            )
            
            if response.status_code == 200:
                print(f"✅ [{time.strftime('%H:%M:%S')}] PING OK → {response.status_code} in {response.elapsed.total_seconds():.2f}s")
                success = True
                consecutive_failures = 0
                break
            else:
                print(f"⚠️ [{time.strftime('%H:%M:%S')}] HTTP {response.status_code} (attempt {attempt}/{MAX_RETRIES})")
                
        except requests.exceptions.Timeout as e:
            print(f"⏱️ [{time.strftime('%H:%M:%S')}] TIMEOUT attempt {attempt}/{MAX_RETRIES} — {e}")
            if attempt < MAX_RETRIES:
                # Short delay between retries
                time.sleep(2 ** attempt)
                
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 [{time.strftime('%H:%M:%S')}] CONNECTION ERROR attempt {attempt}/{MAX_RETRIES} — {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)
                
        except Exception as e:
            print(f"❌ [{time.strftime('%H:%M:%S')}] ERROR attempt {attempt}/{MAX_RETRIES} — {type(e).__name__}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)

    if success:
        backoff = 0
        # Wait 45 seconds before next ping
        time.sleep(PING_INTERVAL_SECONDS)
    else:
        # Exponential backoff on complete failure (all retries exhausted)
        consecutive_failures += 1
        backoff = min(backoff + 1, 6)  # Cap at 2^6 = 64 seconds base
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, 5)
        wait_time = (2 ** backoff) + jitter
        
        print(f"🔁 [{time.strftime('%H:%M:%S')}] BACKOFF level {backoff} — "
              f"waiting {wait_time:.1f}s (consecutive failures: {consecutive_failures})")
        
        # If too many consecutive failures, alert but keep trying
        if consecutive_failures >= 10:
            print(f"🚨 ALERT: {consecutive_failures} consecutive failures! Service may be down.")
        
        time.sleep(wait_time)
