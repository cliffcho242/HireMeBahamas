#!/usr/bin/env python3
"""
Keep-Alive Background Worker for Render

This script runs as a background worker on Render to prevent the backend
from going to sleep due to inactivity. It pings multiple health endpoints
every 60 seconds.

Render's free tier sleeps services after 15 minutes of inactivity.
By pinging every 60 seconds, we ensure the service stays awake permanently.

Setup Instructions:
===================

1. ENVIRONMENT VARIABLE (set in Render Background Worker dashboard):
   Name:  RENDER_EXTERNAL_URL
   Value: https://hiremebahamas.onrender.com

2. BUILD COMMAND (in Render dashboard for the Background Worker):
   pip install requests

3. START COMMAND (in Render dashboard for the Background Worker):
   python keep_alive.py

4. Add to render.yaml as a background worker (already configured):
   - type: worker
     name: keep-alive
     runtime: python
     plan: free
     buildCommand: pip install requests
     startCommand: python keep_alive.py
     envVars:
       - key: RENDER_EXTERNAL_URL
         value: https://hiremebahamas.onrender.com

This costs $0 on Render's free tier for background workers.
"""
import os
import sys
import time
from datetime import datetime, timezone

import requests

# Configuration
PING_INTERVAL_SECONDS = 60  # Ping every 60 seconds to prevent sleep
REQUEST_TIMEOUT_SECONDS = 30  # Timeout for each request
MAX_CONSECUTIVE_FAILURES = 10  # Log warning after this many failures

# Endpoints to ping (in order of priority)
# /health/ping - Primary lightweight endpoint for keepalive
# /ping - Fallback lightweight endpoint
# /api/auth/ping - Bonus auth ping if it exists
ENDPOINTS = [
    "/health/ping",
    "/ping",
    "/api/auth/ping",
]


def log(message: str, is_error: bool = False) -> None:
    """Log a message with timestamp."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    prefix = "❌" if is_error else "✅"
    output = sys.stderr if is_error else sys.stdout
    print(f"[{timestamp}] {prefix} {message}", file=output, flush=True)


def ping_endpoint(base_url: str, endpoint: str) -> bool:
    """
    Ping a single endpoint and return success status.
    
    Args:
        base_url: The base URL of the service
        endpoint: The endpoint path to ping
        
    Returns:
        True if ping succeeded, False otherwise
    """
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code == 200:
            return True
        # 404 is acceptable for optional endpoints like /api/auth/ping
        if response.status_code == 404:
            return True  # Endpoint doesn't exist, but service is alive
        return False
    except requests.exceptions.Timeout:
        log(f"Timeout pinging {endpoint} (>{REQUEST_TIMEOUT_SECONDS}s)", is_error=True)
        return False
    except requests.exceptions.ConnectionError:
        log(f"Connection error pinging {endpoint}", is_error=True)
        return False
    except Exception as e:
        log(f"Error pinging {endpoint}: {type(e).__name__}: {e}", is_error=True)
        return False


def main() -> None:
    """Main keep-alive loop."""
    # Get the Render external URL from environment
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "").rstrip("/")
    
    if not base_url:
        log("ERROR: RENDER_EXTERNAL_URL environment variable is not set.", is_error=True)
        log("Please set RENDER_EXTERNAL_URL to your Render service URL", is_error=True)
        log("Example: RENDER_EXTERNAL_URL=https://hiremebahamas.onrender.com", is_error=True)
        sys.exit(1)
    
    log(f"Keep-alive worker started for {base_url}")
    log(f"Ping interval: {PING_INTERVAL_SECONDS} seconds")
    log(f"Endpoints to ping: {', '.join(ENDPOINTS)}")
    
    consecutive_failures = 0
    ping_count = 0
    
    while True:
        ping_count += 1
        any_success = False
        
        # Ping all endpoints
        for endpoint in ENDPOINTS:
            if ping_endpoint(base_url, endpoint):
                any_success = True
                # Log success every 10 pings (approximately every 10 minutes)
                if ping_count % 10 == 0:
                    log(f"Ping #{ping_count} successful - {endpoint}")
                break  # Stop on first successful ping
        
        if any_success:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            log(f"All endpoints failed (attempt {consecutive_failures})", is_error=True)
            
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                log(
                    f"WARNING: {MAX_CONSECUTIVE_FAILURES} consecutive failures. "
                    f"Service may be unhealthy at {base_url}",
                    is_error=True
                )
                # Reset counter to avoid spamming logs
                consecutive_failures = 0
        
        # Wait before next ping
        time.sleep(PING_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
