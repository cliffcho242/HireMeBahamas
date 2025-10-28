#!/usr/bin/env python3
"""System Status Checker"""

import subprocess
import time

import requests


def check_backend():
    """Check backend status"""
    try:
        # Health check
        response = requests.get("http://127.0.0.1:8008/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend: RUNNING")

            # Test login
            login_response = requests.post(
                "http://127.0.0.1:8008/api/auth/login",
                json={"email": "admin@hirebahamas.com", "password": "admin123"},
                timeout=3,
            )

            if login_response.status_code == 200:
                print("✅ Login API: WORKING")
                return True
            else:
                print(f"❌ Login API: FAILED ({login_response.status_code})")
                return False
        else:
            print(f"❌ Backend: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend: NOT RESPONDING ({e})")
        return False


def check_frontend():
    """Check frontend status"""
    ports = [3000, 3001, 3002, 3003, 3004]

    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=3)
            if response.status_code == 200:
                print(f"✅ Frontend: RUNNING on port {port}")
                return port
        except:
            continue

    print("❌ Frontend: NOT RESPONDING")
    return None


def main():
    print("🔍 HIREBAHAMAS SYSTEM STATUS CHECK")
    print("=" * 50)
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    backend_ok = check_backend()
    frontend_port = check_frontend()

    print()
    print("=" * 50)

    if backend_ok and frontend_port:
        print("🎉 SYSTEM STATUS: ALL GOOD!")
        print(f"🔗 Backend: http://127.0.0.1:8008")
        print(f"🔗 Frontend: http://localhost:{frontend_port}")
        print(f"🔑 Login: admin@hirebahamas.com / admin123")
        print()
        print("✅ You can now use the application successfully!")
    else:
        print("❌ SYSTEM STATUS: ISSUES DETECTED")
        if not backend_ok:
            print("   - Backend needs to be started")
        if not frontend_port:
            print("   - Frontend needs to be started")


if __name__ == "__main__":
    main()
