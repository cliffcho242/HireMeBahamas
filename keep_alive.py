import time
import requests

# THIS IS THE ONLY TRUTH — HARD-CODED FOREVER
HEALTH_URL = "https://hiremebahamas.onrender.com/health"

print(f"FINAL KEEP-ALIVE ACTIVE → {HEALTH_URL}")

while True:
    try:
        r = requests.get(
            HEALTH_URL,
            timeout=15,
            headers={"User-Agent": "ImmortalKeepAlive/2025"}
        )
        if r.status_code == 200:
            print("PING OK — Render is immortal")
        else:
            print(f"PING WARN — HTTP {r.status_code}")
    except Exception as e:
        print(f"PING FAILED — {e}")

    time.sleep(55)
