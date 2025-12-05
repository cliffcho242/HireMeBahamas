"""
=============================================================================
DEPRECATED: KEEP-ALIVE WORKER (No longer needed after Vercel + Railway migration)
=============================================================================
This file was used for Render Background Service to prevent cold starts.

After migrating to Vercel + Railway:
- Vercel Edge: No cold starts (edge functions are always warm)
- Railway: Use GitHub Actions workflows for keepalive (keep-database-awake.yml)

This file is kept for historical reference only.

For Railway keepalive, use:
- .github/workflows/keep-database-awake.yml (runs every 2 minutes)
- .github/workflows/scheduled-ping.yml (runs every 10 minutes)

For external monitoring services:
  1. UptimeRobot (free monitoring + pings)
  2. Cron-job.org (free scheduled pings)
  3. Railway built-in health checks
=============================================================================
"""
import os
import time
import random
import requests

# Get backend URL from environment variable
_base_url = os.getenv("BACKEND_URL", "").strip()

# Fallback to localhost if no URL provided
if not _base_url or not _base_url.startswith(("http://", "https://")):
    print("⚠️ WARNING: BACKEND_URL not set. This script is deprecated.")
    print("   Use GitHub Actions workflows instead:")
    print("   - .github/workflows/keep-database-awake.yml")
    print("   - .github/workflows/scheduled-ping.yml")
    _base_url = "http://localhost:8000"

HEALTH_URL = _base_url + "/health"

# Ping interval: 45 seconds keeps service warm without overloading
PING_INTERVAL_SECONDS = 45

# Retry configuration - NUCLEAR SETTINGS
MAX_RETRIES = 5
CONNECT_TIMEOUT = 10  # seconds - connection establishment
READ_TIMEOUT = 30     # seconds - response read (30s as specified)

print("=" * 60)
print("🔥 UNBREAKABLE KEEP-ALIVE WORKER STARTED")
print(f"   Target: {HEALTH_URL}")
print(f"   Interval: {PING_INTERVAL_SECONDS}s")
print(f"   Timeout: ({CONNECT_TIMEOUT}s connect, {READ_TIMEOUT}s read)")
print(f"   Retries: {MAX_RETRIES}")
print("=" * 60)

backoff = 0
consecutive_failures = 0

while True:
    success = False
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # NUCLEAR TIMEOUT: (10s connect, 30s read) as specified
            # This handles cold starts without blocking the keep-alive loop too long
            response = requests.get(
                HEALTH_URL,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
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
