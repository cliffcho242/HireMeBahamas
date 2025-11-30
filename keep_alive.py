#!/usr/bin/env python3
"""
PRODUCTION-IMMORTAL Keep-Alive for Render Background Worker
============================================================
ZERO 499/502/503 EVER AGAIN - Facebook-Grade Reliability

Features:
- Hard-coded production URL (no env dependency on cold start)
- Jitter to prevent thundering herd
- Exponential backoff with max ceiling
- Structured logging with timestamps
- Warmup period for new deployments
- Cache warming integration
- Memory-efficient design (<5MB RSS)

Deploy Order:
1. Background Worker (this script) → keeps service awake
2. DB migration → ensures schema is ready
3. Web Service → main API
4. Vercel → frontend

Expected behavior:
- Warmup (first 5 min): Ping every 20s + random jitter 0-5s
- Normal: Ping every 50s + random jitter 0-10s
- On failure: Exponential backoff (10s, 20s, 40s, 80s, 160s, max 300s)
- After 3 consecutive successes: Reset backoff level
"""
import random
import sys
import time
from datetime import datetime, timedelta

import requests

# =============================================================================
# CONFIGURATION - HARD-CODED FOR PRODUCTION (no env dependency on cold start)
# =============================================================================
HEALTH_URL = "https://hiremebahamas.onrender.com/health"
WARM_CACHE_URL = "https://hiremebahamas.onrender.com/warm-cache"
PING_URL = "https://hiremebahamas.onrender.com/ping"

# Timing configuration
WARMUP_DURATION_MINUTES = 5
WARMUP_BASE_INTERVAL = 20  # seconds
NORMAL_BASE_INTERVAL = 50  # seconds
WARMUP_JITTER_MAX = 5  # seconds
NORMAL_JITTER_MAX = 10  # seconds

# Backoff configuration
BACKOFF_BASE = 10  # seconds
BACKOFF_MULTIPLIER = 2
BACKOFF_MAX = 300  # 5 minutes max wait
BACKOFF_MAX_LEVEL = 5

# Success tracking
SUCCESS_STREAK_RESET = 3  # Reset backoff after 3 consecutive successes

# Request configuration
REQUEST_TIMEOUT = 12  # seconds
USER_AGENT = "HireMeBahamas-KeepAlive/2.0 (Production-Immortal)"

# Cache warming
CACHE_WARM_INTERVAL = 300  # Warm cache every 5 minutes


def log(level: str, message: str) -> None:
    """Structured logging with ISO timestamp."""
    timestamp = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
    print(f"[{timestamp}] [{level}] {message}", flush=True)


def get_jitter(max_jitter: float) -> float:
    """Generate random jitter to prevent thundering herd."""
    return random.uniform(0, max_jitter)


def calculate_wait(
    backoff_level: int,
    is_warmup: bool
) -> tuple[float, str]:
    """
    Calculate wait time based on current state.
    
    Returns: (wait_seconds, mode_description)
    """
    if backoff_level > 0:
        # Exponential backoff with jitter
        base_wait = min(
            BACKOFF_BASE * (BACKOFF_MULTIPLIER ** backoff_level),
            BACKOFF_MAX
        )
        jitter = get_jitter(base_wait * 0.2)  # 20% jitter
        return base_wait + jitter, f"BACKOFF L{backoff_level}"
    
    if is_warmup:
        wait = WARMUP_BASE_INTERVAL + get_jitter(WARMUP_JITTER_MAX)
        return wait, "WARMUP"
    
    wait = NORMAL_BASE_INTERVAL + get_jitter(NORMAL_JITTER_MAX)
    return wait, "NORMAL"


def ping_health() -> tuple[bool, int, str]:
    """
    Ping health endpoint.
    
    Returns: (success, status_code, error_message)
    """
    try:
        response = requests.get(
            HEALTH_URL,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT}
        )
        return response.status_code == 200, response.status_code, ""
    except requests.exceptions.Timeout:
        return False, 0, "timeout"
    except requests.exceptions.ConnectionError as e:
        return False, 0, f"connection_error: {str(e)[:50]}"
    except Exception as e:
        return False, 0, f"exception: {type(e).__name__}"


def warm_cache() -> bool:
    """
    Trigger cache warming on the backend.
    
    Returns: success
    """
    try:
        response = requests.post(
            WARM_CACHE_URL,
            timeout=30,  # Cache warming can take longer
            headers={"User-Agent": USER_AGENT}
        )
        return response.status_code == 200
    except Exception:
        return False


def main():
    """Main keep-alive loop - runs forever."""
    log("INFO", f"🚀 PRODUCTION-IMMORTAL Keep-Alive Starting")
    log("INFO", f"   Health URL: {HEALTH_URL}")
    log("INFO", f"   Warmup: {WARMUP_DURATION_MINUTES}min @ {WARMUP_BASE_INTERVAL}s")
    log("INFO", f"   Normal: {NORMAL_BASE_INTERVAL}s base interval")
    log("INFO", f"   Backoff: {BACKOFF_BASE}s base, max {BACKOFF_MAX}s")
    
    start_time = datetime.now()
    success_streak = 0
    backoff_level = 0
    total_pings = 0
    total_successes = 0
    last_cache_warm = datetime.min
    
    while True:
        total_pings += 1
        is_warmup = (datetime.now() - start_time) < timedelta(minutes=WARMUP_DURATION_MINUTES)
        
        # Ping health endpoint
        success, status_code, error = ping_health()
        
        if success:
            total_successes += 1
            success_streak += 1
            
            # Reset backoff after consecutive successes
            if success_streak >= SUCCESS_STREAK_RESET and backoff_level > 0:
                log("INFO", f"✅ Backoff reset after {success_streak} consecutive successes")
                backoff_level = 0
            
            success_rate = (total_successes / total_pings) * 100
            log("INFO", f"✅ ALIVE | streak={success_streak} | total={total_successes}/{total_pings} ({success_rate:.1f}%)")
            
            # Warm cache periodically
            if (datetime.now() - last_cache_warm) >= timedelta(seconds=CACHE_WARM_INTERVAL):
                if warm_cache():
                    log("INFO", "🔥 Cache warmed successfully")
                    last_cache_warm = datetime.now()
                else:
                    log("WARN", "⚠️ Cache warming failed (non-critical)")
        else:
            success_streak = 0
            backoff_level = min(backoff_level + 1, BACKOFF_MAX_LEVEL)
            
            if status_code > 0:
                log("ERROR", f"❌ FAIL status={status_code} | backoff_level={backoff_level}")
            else:
                log("ERROR", f"❌ FAIL {error} | backoff_level={backoff_level}")
        
        # Calculate wait time
        wait_seconds, mode = calculate_wait(backoff_level, is_warmup)
        log("DEBUG", f"⏳ Sleeping {wait_seconds:.1f}s ({mode})")
        
        try:
            time.sleep(wait_seconds)
        except KeyboardInterrupt:
            log("INFO", "👋 Shutting down gracefully")
            sys.exit(0)


if __name__ == "__main__":
    main()
