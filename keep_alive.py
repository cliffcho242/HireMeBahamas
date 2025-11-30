#!/usr/bin/env python3
"""
Keep-alive worker: pings the Render web service to prevent sleeping.

This background worker runs on Render's free tier and pings the web service
every 70 seconds to prevent it from sleeping due to inactivity.

Requirements:
- Set RENDER_EXTERNAL_URL environment variable to your service URL
  (e.g., https://hiremebahamas.onrender.com)

Render Dashboard Setup:
1. Go to Render Dashboard → New → Background Worker
2. Connect your GitHub repository
3. Set the following:
   - Service Type: Background Worker
   - Name: keep-alive
   - Runtime: Python 3
   - Build Command: pip install requests
   - Start Command: python keep_alive.py
4. Add environment variable:
   - Key: RENDER_EXTERNAL_URL
   - Value: https://your-service.onrender.com
5. Deploy!
"""
import os
import sys
import time

import requests

# Get the service URL from environment variable
url = os.environ.get("RENDER_EXTERNAL_URL")
if not url:
    print("Error: RENDER_EXTERNAL_URL environment variable is not set.")
    print("Please set it to your Render web service URL.")
    print("Example: https://hiremebahamas.onrender.com")
    sys.exit(1)

# Use the /health/ping endpoint for minimal overhead
ping_url = f"{url}/health/ping"

print(f"Keep-alive worker started. Pinging {ping_url} every 70 seconds.")

while True:
    try:
        response = requests.get(ping_url, timeout=10)
        print(f"Ping {ping_url}: {response.status_code}", flush=True)
    except requests.exceptions.Timeout:
        print(f"Ping timeout after 10 seconds", flush=True)
    except requests.exceptions.ConnectionError:
        print(f"Connection error - service may be starting up", flush=True)
    except Exception as e:
        print(f"Ping failed: {e}", flush=True)
    
    # Sleep for 70 seconds between pings
    # Render free tier sleeps after 15 minutes of inactivity
    # Pinging every 70 seconds keeps the service responsive
    time.sleep(70)
