"""
Test ALL possible Render URL patterns
"""

import requests
import time

# All possible URL patterns for Render
urls_to_test = [
    "https://hiremebahamas-backend.render.app",
    "https://hiremebahamas-backend-production.up.render.app",
    "https://web-production.up.render.app",
    "https://api.hiremebahamas.com",
]

print("=" * 70)
print("TESTING ALL RAILWAY URL PATTERNS")
print("=" * 70)

for url in urls_to_test:
    print(f"\n🔍 Testing: {url}")
    print("-" * 70)

    # Test /health
    try:
        resp = requests.get(
            f"{url}/health",
            timeout=5,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
        print(f"   /health → {resp.status_code} ({len(resp.text)} bytes)")

        if len(resp.text) > 50:
            try:
                data = resp.json()
                print(f"   ✅ JSON Response: {list(data.keys())}")
            except:
                print(f"   Body: {resp.text[:100]}")
    except Exception as e:
        print(f"   /health → Error: {str(e)[:60]}")

    # Test /api/users/1
    try:
        resp = requests.get(
            f"{url}/api/users/1", timeout=5, headers={"Cache-Control": "no-cache"}
        )
        print(f"   /api/users/1 → {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ USER FOUND! Email: {data.get('email')}")
    except Exception as e:
        print(f"   /api/users/1 → Error: {str(e)[:60]}")

    # Test /api/routes
    try:
        resp = requests.get(
            f"{url}/api/routes", timeout=5, headers={"Cache-Control": "no-cache"}
        )
        print(f"   /api/routes → {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ ROUTES FOUND! Count: {len(data.get('routes', []))}")
    except Exception as e:
        print(f"   /api/routes → Error: {str(e)[:60]}")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)
print(
    """
If all URLs show 404 or 'OK' (2 bytes), but Render logs show 209 bytes:
→ Render's CDN is caching old responses

SOLUTION:
1. Go to Render Dashboard: https://render.app/dashboard
2. Click your backend service
3. Settings → Networking → Click "Generate Domain" 
4. Get the NEW domain and test with that
5. Or: Deployments → ... menu → "Restart"
"""
)
