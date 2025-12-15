import os
import time

import requests

# Get base URL from environment or default to localhost for local dev
BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000")

print("Testing Admin Backend API...")

# Give backend time to start if just started
time.sleep(1)

try:
    # Test 1: Health endpoint
    print("\n1. Testing Health Endpoint:")
    r = requests.get(f"{BASE_URL}/admin/health", timeout=5)
    if r.status_code == 200:
        print("   [OK] Admin backend health check passed")
        print(f"   Response: {r.json()}")
    else:
        print(f"   [WARN] Health check returned: {r.status_code}")

    # Test 2: Login
    print("\n2. Testing Admin Login:")
    r = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={"email": "admin@hiremebahamas.com", "password": "Admin123456!"},
        timeout=5,
    )
    if r.status_code == 200:
        print("   [OK] Admin login successful")
        data = r.json()
        token = data.get("access_token", "")
        print(f"   Token: {token[:50]}...")

        # Test 3: Get admin info
        print("\n3. Testing Get Admin Info:")
        r = requests.get(
            f"{BASE_URL}/admin/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if r.status_code == 200:
            print("   [OK] Admin info retrieved")
            print(f"   Admin: {r.json()}")
        else:
            print(f"   [WARN] Get admin info returned: {r.status_code}")
    else:
        print(f"   [ERROR] Login failed: {r.status_code}")
        print(f"   Response: {r.text[:200]}")

    print("\n[SUCCESS] Admin backend is working!")

except requests.exceptions.ConnectionError:
    print("\n[ERROR] Admin backend not running")
    print("   Start it with: python admin_backend.py")
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
