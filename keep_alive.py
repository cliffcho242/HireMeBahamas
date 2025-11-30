import time
import random
import requests

# THIS URL IS ETERNAL — HARDCODED
HEALTH_URL = "https://hiremebahamas.onrender.com/health"

print(f"ULTIMATE IMMORTAL KEEP-ALIVE STARTED → {HEALTH_URL}")

backoff = 0

while True:
    success = False
    for attempt in range(1, 4):
        try:
            r = requests.get(
                HEALTH_URL,
                timeout=(6, 20 + attempt * 10),  # connect 6s, read 30–50s
                headers={"User-Agent": "ImmortalKeepAlive/2025"}
            )
            if r.status_code == 200:
                print("✅ PING OK — Render stays alive forever")
                success = True
                break
            else:
                print(f"⚠️ PING WARN — HTTP {r.status_code} (attempt {attempt}/3)")
        except Exception as e:
            print(f"⏳ PING RETRY {attempt}/3 — {e}")
            if attempt < 3:
                time.sleep(2 ** attempt)  # 2s, 4s between retries

    if success:
        backoff = 0
        time.sleep(55)
    else:
        backoff = min(backoff + 1, 6)
        wait = (2 ** backoff) + random.uniform(0, 5)
        print(f"🔁 BACKOFF {backoff} — sleeping {wait:.1f}s before next cycle")
        time.sleep(wait)
