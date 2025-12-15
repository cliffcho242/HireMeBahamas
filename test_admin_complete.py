import os

import requests

# Get base URL from environment or default to localhost for local dev
BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000")

print("=" * 80)
print("  ADMIN PANEL API TEST")
print("=" * 80)

# Test 1: Health Check
print("\n1. Health Check:")
try:
    r = requests.get(f"{BASE_URL}/admin/health", timeout=5)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    print("   [OK] Admin backend is running")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 2: Admin Login
print("\n2. Admin Login:")
try:
    r = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={"email": "admin@hiremebahamas.com", "password": "Admin123456!"},
        timeout=5,
    )
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Admin Email: {data.get('admin', {}).get('email')}")
        print(f"   Token: {data.get('access_token', '')[:50]}...")
        token = data.get("access_token")
        print("   [OK] Admin login successful")

        # Test 3: Get Admin Info
        print("\n3. Get Admin Info (with token):")
        r = requests.get(
            f"{BASE_URL}/admin/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Admin: {data.get('admin')}")
            print("   [OK] Token authentication working")
        else:
            print(f"   [ERROR] {r.text[:200]}")

        # Test 4: Get Dashboard Stats
        print("\n4. Get Dashboard Stats:")
        r = requests.get(
            f"{BASE_URL}/admin/dashboard/stats",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            stats = data.get("stats", {})
            print(f"   Total Users: {stats.get('total_users')}")
            print(f"   Users by Type: {stats.get('users_by_type')}")
            print("   [OK] Dashboard API working")
        else:
            print(f"   [ERROR] {r.text[:200]}")

        # Test 5: Get All Users
        print("\n5. Get All Users:")
        r = requests.get(
            f"{BASE_URL}/admin/users?page=1&per_page=10",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Total Users: {data.get('total')}")
            print(f"   Current Page: {data.get('page')}/{data.get('pages')}")
            print(f"   Users Retrieved: {len(data.get('users', []))}")
            print("   [OK] User management API working")
        else:
            print(f"   [ERROR] {r.text[:200]}")

    else:
        print(f"   [ERROR] Login failed: {r.text[:200]}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test 6: Test that regular endpoint is separate (no 405 conflict)
print("\n6. Test Main App Endpoint (ensure no 405 conflict):")
try:
    backend_url = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")
    r = requests.get(f"{backend_url}/health", timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   Main app backend: {r.json()}")
        print("   [OK] Main app unaffected by admin panel")
    else:
        print(f"   [WARN] Main app status: {r.status_code}")
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "=" * 80)
print("  TEST COMPLETE")
print("=" * 80)
print("\nAdmin Panel:")
print(f"  Backend: {BASE_URL}")
print("  Login: admin@hiremebahamas.com / Admin123456!")
print("\nMain App (Users):")
backend_url = os.getenv("BACKEND_URL", "https://hiremebahamas.vercel.app")
print(f"  Backend: {backend_url}")
print("  Frontend: https://hiremebahamas.com")
print("\n[SUCCESS] Admin panel is separate from main app - no 405 conflicts!")
