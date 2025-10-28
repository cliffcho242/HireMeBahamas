#!/usr/bin/env python3
"""
Automated Login Test Script
Tests both backend and frontend login functionality
"""

import subprocess
import sys
import time
from pathlib import Path

import requests


def test_backend_login():
    """Test backend login directly"""
    print("🔧 Testing Backend Login...")
    try:
        r = requests.post(
            "http://127.0.0.1:8008/api/auth/login",
            json={"email": "admin@hirebahamas.com", "password": "AdminPass123!"},
            timeout=10,
        )
        if r.status_code == 200:
            print("✅ Backend login: SUCCESS")
            return True
        else:
            print(f"❌ Backend login: FAILED ({r.status_code}) - {r.text}")
            return False
    except Exception as e:
        print(f"❌ Backend login: ERROR - {e}")
        return False


def test_frontend_connection():
    """Test if frontend is accessible"""
    print("🌐 Testing Frontend Connection...")
    # Try both common ports
    for port in [3000, 3001]:
        try:
            r = requests.get(f"http://localhost:{port}", timeout=5)
            if r.status_code == 200:
                print(f"✅ Frontend connection: SUCCESS (port {port})")
                return True
        except Exception:
            continue
    print("❌ Frontend connection: FAILED - not found on ports 3000 or 3001")
    return False


def test_frontend_login_simulation():
    """Test frontend login by simulating the request it makes"""
    print("🔐 Testing Frontend Login Simulation...")
    try:
        # This simulates what the frontend sends
        r = requests.post(
            "http://127.0.0.1:8008/api/auth/login",
            json={"email": "admin@hirebahamas.com", "password": "AdminPass123!"},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if r.status_code == 200:
            response_data = r.json()
            if "token" in response_data and "user" in response_data:
                print("✅ Frontend login simulation: SUCCESS")
                print(f"   Token received: {response_data['token'][:50]}...")
                print(f"   User: {response_data['user']['email']}")
                return True
            else:
                print(
                    f"❌ Frontend login simulation: INVALID RESPONSE - {response_data}"
                )
                return False
        else:
            print(f"❌ Frontend login simulation: FAILED ({r.status_code}) - {r.text}")
            return False
    except Exception as e:
        print(f"❌ Frontend login simulation: ERROR - {e}")
        return False


def main():
    print("🚀 HireBahamas Login Test Suite")
    print("=" * 50)

    # Test backend
    backend_ok = test_backend_login()
    time.sleep(1)

    # Test frontend connection
    frontend_ok = test_frontend_connection()
    time.sleep(1)

    # Test frontend login simulation
    login_ok = test_frontend_login_simulation()

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Backend Login: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"   Frontend Connection: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"   Login Simulation: {'✅ PASS' if login_ok else '❌ FAIL'}")

    if backend_ok and frontend_ok and login_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("🔑 Login should work in the browser now!")
        print("   URL: http://localhost:3000")
        print("   Email: admin@hirebahamas.com")
        print("   Password: AdminPass123!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        if not backend_ok:
            print("   → Backend login issue - check if backend is running on port 8008")
        if not frontend_ok:
            print(
                "   → Frontend connection issue - check if frontend is running on port 3001"
            )
        if not login_ok:
            print("   → Login simulation failed - check credentials and API endpoint")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
