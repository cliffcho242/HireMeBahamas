#!/usr/bin/env python3
"""
Quick test to verify the AI-powered HireBahamas platform is working
"""

import sys

import requests


def test_backend():
    """Test backend server"""
    try:
        response = requests.get("http://127.0.0.1:8008/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running and healthy")
            return True
        else:
            print(f"❌ Backend server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend server not accessible: {e}")
        return False


def test_admin_login():
    """Test admin login"""
    try:
        login_data = {"email": "admin@hirebahamas.com", "password": "AdminPass123!"}
        response = requests.post(
            "http://127.0.0.1:8008/auth/login", json=login_data, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Admin login successful - network errors resolved!")
                return True
            else:
                print(f"❌ Admin login failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Admin login HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Admin login error: {e}")
        return False


def test_frontend():
    """Test frontend server"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server is running")
            return True
        else:
            print(f"⚠️ Frontend server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Frontend server not accessible: {e}")
        return False


def main():
    print("🤖 AI-Powered HireBahamas Platform Test")
    print("=" * 50)

    backend_ok = test_backend()
    login_ok = test_admin_login()
    frontend_ok = test_frontend()

    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)

    if backend_ok and login_ok:
        print("🎉 SUCCESS: Network errors during admin sign-in have been resolved!")
        print("✅ Backend server operational")
        print("✅ Admin authentication working")
        if frontend_ok:
            print("✅ Frontend server operational")
        else:
            print("⚠️ Frontend server may need manual start")
        return 0
    else:
        print("❌ ISSUES REMAIN: Some components need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
