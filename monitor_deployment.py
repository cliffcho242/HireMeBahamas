#!/usr/bin/env python3
"""Monitor Render deployment and test when new version is live."""

import requests
import time

BACKEND_URL = "https://hiremebahamas-backend.render.app"
CHECK_INTERVAL = 10  # seconds
MAX_WAIT = 300  # 5 minutes

print("🚀 Monitoring Render Deployment")
print("=" * 70)
print(f"Backend: {BACKEND_URL}")
print(f"Checking every {CHECK_INTERVAL} seconds...")
print("=" * 70)

start_time = time.time()
attempt = 0

while (time.time() - start_time) < MAX_WAIT:
    attempt += 1
    elapsed = int(time.time() - start_time)

    print(f"\n⏱️  Attempt {attempt} ({elapsed}s elapsed)")

    try:
        # Test the new debug endpoint
        response = requests.get(f"{BACKEND_URL}/api/routes", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ NEW VERSION IS LIVE!")
            print(f"   Total routes: {data['total_routes']}")

            # Check for auth routes
            auth_routes = [r for r in data["routes"] if "/api/auth/" in r["path"]]
            print(f"\n🔐 Authentication routes found: {len(auth_routes)}")
            for route in auth_routes:
                print(f"   {route['path']}: {', '.join(route['methods'])}")

            # Test one auth route
            print(f"\n🧪 Testing /api/auth/login...")
            test_resp = requests.options(f"{BACKEND_URL}/api/auth/login", timeout=5)
            print(f"   OPTIONS /api/auth/login: {test_resp.status_code}")

            if test_resp.status_code == 200:
                print(f"\n🎉 SUCCESS! 405 errors are FIXED!")
                print(f"   Users can now sign in and register!")
                break
            else:
                print(f"   ⚠️  Still returning {test_resp.status_code}")

        elif response.status_code == 404:
            print(f"   ⏳ Old version still running (404 on /api/routes)")
            print(f"   Waiting {CHECK_INTERVAL}s...")

        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")

    time.sleep(CHECK_INTERVAL)

else:
    print(f"\n⚠️  Timeout after {MAX_WAIT}s")
    print(f"   Check Render dashboard for deployment status")

print("\n" + "=" * 70)
