import os
import time
import requests

# MASTER FIX – hard-coded full URL + env fallback
BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "https://hiremebahamas.onrender.com")
HEALTH_URL = f"{BASE_URL.rstrip('/')}/health"

print(f"Keep-alive started → pinging {HEALTH_URL} every 40s")

while True:
    try:
        resp = requests.get(HEALTH_URL, timeout=15, headers={"User-Agent": "KeepAliveBot/1.0"})
        if resp.status_code == 200:
            print("PING OK – Render is awake")
        else:
            print(f"PING FAILED – status {resp.status_code}")
    except Exception as e:
        print(f"PING FAILED – {e}")
    
    time.sleep(40)
