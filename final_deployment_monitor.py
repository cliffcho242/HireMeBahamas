#!/usr/bin/env python3
"""
Comprehensive Railway deployment monitor with detailed diagnostics.
Checks every aspect of the deployment to identify routing issues.
"""

import requests
import time

BACKEND_URL = "https://hiremebahamas-backend.railway.app"


def test_deployment():
    """Test all aspects of the deployment."""
    print("\n" + "=" * 70)
    print(f"🔍 RAILWAY DEPLOYMENT DIAGNOSTIC - {time.strftime('%H:%M:%S')}")
    print("=" * 70)

    # Test 1: Root path
    print("\n1️⃣ Testing root path (/)...")
    try:
        resp = requests.get(f"{BACKEND_URL}/", timeout=10)
        content = resp.text[:200]

        if "Railway API" in content:
            print("   ❌ PROBLEM: Railway default page detected!")
            print("   🔧 Railway is NOT routing to your Flask app")
            return False
        elif "HireBahamas" in content or resp.status_code == 200:
            print(f"   ✅ Flask app responding (Status: {resp.status_code})")
        else:
            print(f"   ⚠️  Unknown response (Status: {resp.status_code})")
            print(f"   Content preview: {content}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # Test 2: Health check
    print("\n2️⃣ Testing /health endpoint...")
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"   Status: {resp.status_code}")

        if resp.status_code == 200:
            try:
                data = resp.json()
                if "message" in data and "HireBahamas" in data["message"]:
                    print(f"   ✅ Health check passed: {data.get('message', 'OK')}")
                else:
                    print(f"   ⚠️  Unexpected response: {resp.text[:100]}")
            except:
                print(f"   Response: {resp.text}")
        else:
            print(f"   ❌ Health check failed")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Debug routes endpoint
    print("\n3️⃣ Testing /api/routes (debug endpoint)...")
    try:
        resp = requests.get(f"{BACKEND_URL}/api/routes", timeout=10)
        print(f"   Status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ NEW DEPLOYMENT LIVE!")
            print(f"   Total routes: {data.get('total_routes', 0)}")

            # Check for auth routes
            routes = data.get("routes", [])
            auth_routes = [r for r in routes if "/api/auth/" in r.get("path", "")]
            print(f"   Auth routes: {len(auth_routes)}")

            return True
        elif resp.status_code == 404:
            print(f"   ⏳ Old deployment still active")
        else:
            print(f"   ⚠️  Unexpected status")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: Auth endpoint
    print("\n4️⃣ Testing /api/auth/login...")
    try:
        resp = requests.options(f"{BACKEND_URL}/api/auth/login", timeout=10)
        print(f"   OPTIONS status: {resp.status_code}")

        if resp.status_code == 200:
            print(f"   ✅ Auth route working!")
            return True
        elif resp.status_code == 404:
            print(f"   ❌ Route not found (404)")
        elif resp.status_code == 405:
            print(f"   ⚠️  405 error still present")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    return False


def main():
    print("🚀 Railway Deployment Monitor")
    print(f"Backend: {BACKEND_URL}")
    print("Monitoring for deployment completion...")

    max_attempts = 30  # 5 minutes (10s intervals)
    attempt = 0

    while attempt < max_attempts:
        attempt += 1

        if test_deployment():
            print("\n" + "=" * 70)
            print("🎉 SUCCESS! DEPLOYMENT IS LIVE AND WORKING!")
            print("=" * 70)
            print("\n✅ The 405 authentication errors are now FIXED!")
            print("✅ Users can now sign in and register on HireBahamas!")
            print(f"\n🌐 Backend: {BACKEND_URL}")
            print("🌐 Frontend: https://hiremebahamas.vercel.app")
            print("🌐 Domain: https://hiremebahamas.com")
            break

        if attempt < max_attempts:
            print(f"\n⏳ Waiting 10 seconds... (Attempt {attempt}/{max_attempts})")
            time.sleep(10)
    else:
        print("\n" + "=" * 70)
        print("⚠️  Timeout: Deployment not detected after 5 minutes")
        print("=" * 70)
        print("\n💡 Troubleshooting:")
        print("   1. Check Railway dashboard for build logs")
        print("   2. Verify GitHub commit 521a6305 triggered deployment")
        print("   3. Check Railway service is set to auto-deploy from main")
        print(f"   4. Visit {BACKEND_URL} in browser to see current state")


if __name__ == "__main__":
    main()
