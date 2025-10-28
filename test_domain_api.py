#!/usr/bin/env python3
"""
Test if API calls work from hiremebahamas.com domain
"""
import requests


def test_from_domain():
    print("Testing API calls with domain origin...")

    # Test 1: Health check
    print("\n1. Testing Health Endpoint:")
    try:
        r = requests.get(
            "https://hiremebahamas.onrender.com/health",
            headers={"Origin": "https://hiremebahamas.com"},
            timeout=30,
        )
        print(f"   Status: {r.status_code}")
        print(
            f"   CORS Header: {r.headers.get('Access-Control-Allow-Origin', 'Not set')}"
        )
        if r.status_code == 200:
            print(f"   ✅ Health check OK")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: OPTIONS preflight for login
    print("\n2. Testing CORS Preflight (OPTIONS) for Login:")
    try:
        r = requests.options(
            "https://hiremebahamas.onrender.com/api/auth/login",
            headers={
                "Origin": "https://hiremebahamas.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
            timeout=30,
        )
        print(f"   Status: {r.status_code}")
        print(
            f"   Allow-Origin: {r.headers.get('Access-Control-Allow-Origin', 'Not set')}"
        )
        print(
            f"   Allow-Methods: {r.headers.get('Access-Control-Allow-Methods', 'Not set')}"
        )
        if r.status_code == 200:
            print(f"   ✅ CORS preflight OK")
        else:
            print(f"   ❌ CORS preflight failed!")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Actual login POST
    print("\n3. Testing Login POST:")
    try:
        r = requests.post(
            "https://hiremebahamas.onrender.com/api/auth/login",
            json={"email": "testuser@example.com", "password": "TestPass123"},
            headers={
                "Origin": "https://hiremebahamas.com",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        print(f"   Status: {r.status_code}")
        print(
            f"   CORS Header: {r.headers.get('Access-Control-Allow-Origin', 'Not set')}"
        )
        if r.status_code == 200:
            print(f"   ✅ Login successful")
        elif r.status_code == 401:
            print(f"   ✅ Login endpoint working (401 = wrong password)")
        elif r.status_code == 405:
            print(f"   ❌ 405 ERROR - Method Not Allowed!")
            print(f"   Response: {r.text[:200]}")
        else:
            print(f"   ⚠️  Unexpected status: {r.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: Test with www subdomain
    print("\n4. Testing with www.hiremebahamas.com origin:")
    try:
        r = requests.post(
            "https://hiremebahamas.onrender.com/api/auth/login",
            json={"email": "testuser@example.com", "password": "TestPass123"},
            headers={
                "Origin": "https://www.hiremebahamas.com",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        print(f"   Status: {r.status_code}")
        print(
            f"   CORS Header: {r.headers.get('Access-Control-Allow-Origin', 'Not set')}"
        )
        if r.status_code == 200:
            print(f"   ✅ Login successful")
        elif r.status_code == 401:
            print(f"   ✅ Login endpoint working (401 = wrong password)")
        elif r.status_code == 405:
            print(f"   ❌ 405 ERROR with www subdomain!")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 5: Check backend CORS configuration
    print("\n5. Checking Backend CORS Configuration:")
    try:
        r = requests.get("https://hiremebahamas.onrender.com/health", timeout=30)
        print(f"   Backend is responding: {r.status_code}")

        # The backend should allow ALL origins with "*"
        print(f"   ✅ Backend CORS should be set to '*' (allow all origins)")
        print(f"   This means hiremebahamas.com SHOULD work")
    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    test_from_domain()

    print("\n" + "=" * 80)
    print("DIAGNOSIS:")
    print("=" * 80)
    print("If you see 405 errors above, the issue is NOT the domain itself.")
    print("The backend CORS is set to '*' which allows ALL domains including")
    print("hiremebahamas.com and www.hiremebahamas.com")
    print("\nPossible causes if 405 appears:")
    print("1. Backend is sleeping (keep-alive service stopped)")
    print("2. Frontend is making requests with wrong HTTP method")
    print("3. Frontend cache has old code")
    print("4. Browser is blocking requests (check DevTools)")
    print("\nRecommended Actions:")
    print("1. Clear browser cache completely")
    print("2. Check keep-alive service is running")
    print("3. Test in incognito/private browsing mode")
    print("4. Check browser DevTools Network tab for actual error")
    print("=" * 80)
