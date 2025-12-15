#!/usr/bin/env python3
"""
Permanent Backend Keep-Alive Service
Keeps Render backend awake 24/7 by pinging it every 10 minutes
Runs in background and auto-restarts on failure
"""
import logging
import os
import sys
import time
from datetime import datetime

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backend_keepalive.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

BACKEND_URL = "https://hiremebahamas.onrender.com"
PING_INTERVAL = 600  # 10 minutes (Render sleeps after 15 min inactivity)
HEALTH_ENDPOINT = f"{BACKEND_URL}/api/health"


def ping_backend():
    """Ping the backend to keep it awake"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=30)
        if response.status_code == 200:
            data = response.json()
            logging.info(
                f"[OK] Backend alive - Status: {data.get('status', 'unknown')}"
            )
            return True
        else:
            logging.warning(
                f"[WARN] Backend responded with status {response.status_code}"
            )
            return False
    except requests.exceptions.Timeout:
        logging.error("[ERROR] Backend ping timeout (might be waking up)")
        return False
    except requests.exceptions.ConnectionError:
        logging.error("[ERROR] Backend connection error")
        return False
    except Exception as e:
        logging.error(f"[ERROR] Unexpected error: {e}")
        return False


def main():
    """Main keep-alive loop"""
    logging.info("=" * 70)
    logging.info("Backend Keep-Alive Service Started")
    logging.info(f"   Backend: {BACKEND_URL}")
    logging.info(
        f"   Ping Interval: {PING_INTERVAL} seconds ({PING_INTERVAL/60} minutes)"
    )
    logging.info("=" * 70)

    consecutive_failures = 0

    while True:
        try:
            success = ping_backend()

            if success:
                consecutive_failures = 0
            else:
                consecutive_failures += 1

            if consecutive_failures >= 3:
                logging.error(f"[ALERT] {consecutive_failures} consecutive failures!")
                # Try to wake it up with longer timeout
                try:
                    logging.info("Attempting emergency wake-up with 60s timeout...")
                    response = requests.get(HEALTH_ENDPOINT, timeout=60)
                    if response.status_code == 200:
                        logging.info("[OK] Emergency wake-up successful!")
                        consecutive_failures = 0
                except Exception as e:
                    logging.error(f"Emergency wake-up failed: {e}")

            # Wait for next ping
            logging.info(f"[WAIT] Next ping in {PING_INTERVAL} seconds...")
            time.sleep(PING_INTERVAL)

        except KeyboardInterrupt:
            logging.info("\nKeep-alive service stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            time.sleep(60)  # Wait 1 minute before retrying


if __name__ == "__main__":
    main()
