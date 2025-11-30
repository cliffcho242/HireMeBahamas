import time
import requests

# THIS IS THE ONLY TRUTH – HARDCODED FOREVER – CAN NEVER BE WRONG
HEALTH_URL = "https://hiremebahamas.onrender.com/health"

print(f"ULTIMATE IMMORTAL KEEP-ALIVE STARTED → {HEALTH_URL}")

while True:
    try:
        response = requests.get(
            HEALTH_URL,
            timeout=12,
            headers={"User-Agent": "ImmortalKeepAlive/2025"}
        )
        if response.status_code == 200:
            print("PING OK — Render stays alive forever")
        else:
            print(f"PING WARN — HTTP {response.status_code}")
    except Exception as e:
        print(f"PING FAILED — {e}")

    time.sleep(55)
