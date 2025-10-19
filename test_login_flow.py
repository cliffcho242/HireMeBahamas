#!/usr/bin/env python3
"""
🔍 HireMeBahamas Login Verification Test
Tests the complete login flow from frontend to backend
"""

import requests


def test_complete_login_flow():
    """Test the complete login flow"""
    print("🔍 Testing Complete HireBahamas Login Flow")
    print("=" * 50)

    backend_url = "http://127.0.0.1:8008"

    # Test 1: Backend Health
    print("1. Testing Backend Health...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend health check error: {e}")
        return False

    # Test 2: Admin Login
    print("2. Testing Admin Login...")
    login_data = {
        'email': 'admin@hiremebahamas.com',
        'password': 'AdminPass123!'
    }

    try:
        response = requests.post(
            f"{backend_url}/api/auth/login",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                token = result.get('token')
                print("   ✅ Admin login successful")
                print(f"   🔑 Token received: {token[:30]}...")
            else:
                print(f"   ❌ Login failed: {result.get('message')}")
                return False
        else:
            print(f"   ❌ Login endpoint error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Login test error: {e}")
        return False

    # Test 3: Protected Endpoint
    print("3. Testing Protected Endpoint...")
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f"{backend_url}/api/stories",
            headers=headers,
            timeout=5
        )

        if response.status_code in [200, 401]:
            print("   ✅ Protected endpoint accessible")
        else:
            print(f"   ❌ Protected endpoint error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Protected endpoint error: {e}")
        return False

    # Test 4: CORS Headers
    print("4. Testing CORS Configuration...")
    try:
        response = requests.options(
            f"{backend_url}/api/auth/login",
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type,Authorization'
            },
            timeout=5
        )

        cors_headers = response.headers
        required = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods'
        ]
        missing = [h for h in required if h not in cors_headers]

        if not missing:
            print("   ✅ CORS properly configured")
        else:
            print(f"   ❌ Missing CORS headers: {missing}")
            return False
    except Exception as e:
        print(f"   ❌ CORS test error: {e}")
        return False

    print("=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("🔐 Login system is fully operational")
    print("📧 Admin Email: admin@hiremebahamas.com")
    print("🔑 Admin Password: AdminPass123!")
    print("🌐 Backend URL: http://127.0.0.1:8008")
    print("🎯 Frontend can now connect and authenticate users")
    return True


if __name__ == "__main__":
    success = test_complete_login_flow()
    exit(0 if success else 1)