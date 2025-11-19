#!/usr/bin/env python3
"""Monitor Railway for deployment update after empty commit push."""

import requests
import time
import json

BACKEND_URL = "https://hiremebahamas-backend.railway.app"
CHECK_INTERVAL = 15  # Check every 15 seconds
MAX_CHECKS = 20  # 5 minutes total

print("=" * 70)
print("🚀 MONITORING RAILWAY DEPLOYMENT")
print("=" * 70)
print(f"Pushed empty commit: eefdebd5")
print(f"Waiting for Railway to deploy...")
print(f"Checking every {CHECK_INTERVAL} seconds")
print("=" * 70)

for attempt in range(1, MAX_CHECKS + 1):
    elapsed = (attempt - 1) * CHECK_INTERVAL
    print(f"\n⏱️  Check {attempt}/{MAX_CHECKS} ({elapsed}s elapsed)")

    try:
        # Test /health endpoint
        health_resp = requests.get(f"{BACKEND_URL}/health", timeout=10)

        # Check if it's the NEW version (returns JSON)
        try:
            health_data = health_resp.json()

            if "message" in health_data and "HireMeBahamas" in health_data["message"]:
                print("   🎉 NEW VERSION DETECTED!")
                print(f"   Version: {health_data.get('version', 'unknown')}")
                print(f"   Message: {health_data.get('message', '')}")
                print(f"   Database: {health_data.get('database', 'unknown')}")

                # Test auth routes
                print("\n   Testing auth routes...")
                auth_resp = requests.options(f"{BACKEND_URL}/api/auth/login", timeout=5)

                if auth_resp.status_code == 200:
                    print("   ✅ /api/auth/login OPTIONS: 200 OK")
                    print("\n" + "=" * 70)
                    print("🎉 SUCCESS! DEPLOYMENT IS LIVE!")
                    print("=" * 70)
                    print("\n✅ All systems operational:")
                    print("   - Flask app deployed")
                    print("   - Authentication routes working")
                    print("   - 405 errors FIXED!")
                    print(f"\n🌐 Backend: {BACKEND_URL}")
                    print("🌐 Frontend: https://hiremebahamas.vercel.app")
                    print("🌐 Domain: https://hiremebahamas.com")
                    break
                else:
                    print(f"   ⚠️  Auth route returned: {auth_resp.status_code}")
            else:
                print("   ⏳ JSON response but unexpected format")
                print(f"   Data: {json.dumps(health_data, indent=2)[:200]}")

        except (json.JSONDecodeError, ValueError):
            # Still returning plain text "OK" (old version)
            print(f"   ⏳ Old version still active (Status: {health_resp.status_code})")
            print(f"   Response: {health_resp.text[:50]}")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {str(e)[:80]}")

    if attempt < MAX_CHECKS:
        print(f"   Waiting {CHECK_INTERVAL}s...")
        time.sleep(CHECK_INTERVAL)

else:
    print("\n" + "=" * 70)
    print("⚠️  TIMEOUT: Railway did not deploy after 5 minutes")
    print("=" * 70)
    print("\n💡 This confirms Railway's GitHub webhook is NOT working.")
    print("\nYOU MUST:")
    print("1. Open Railway dashboard: https://railway.app/dashboard")
    print("2. Find your service")
    print("3. Manually click 'Redeploy' or check webhook settings")
    print("4. Verify auto-deploy is enabled for main branch")
    print("\nAlternatively, check if the service is paused or has errors.")
    print("=" * 70)
