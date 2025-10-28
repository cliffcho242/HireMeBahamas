#!/usr/bin/env python3
"""
Service Verification Script
Checks if HireBahamas services are running properly
"""

import sys
import time

import requests


def check_services():
    print("🔍 Checking HireBahamas services...")
    time.sleep(2)

    backend_ok = False
    frontend_ok = False

    # Check backend
    try:
        print("Checking backend (port 8008)...")
        r = requests.get("http://127.0.0.1:8008/health", timeout=10)
        if r.status_code == 200:
            backend_ok = True
            print("✅ Backend: OK (port 8008)")
        else:
            print(f"❌ Backend: FAILED (status {r.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend: NOT RESPONDING - {str(e)}")
    except Exception as e:
        print(f"❌ Backend: ERROR - {str(e)}")

    # Check frontend
    try:
        print("Checking frontend (port 3000)...")
        r = requests.get("http://127.0.0.1:3000", timeout=10)
        if r.status_code == 200:
            frontend_ok = True
            print("✅ Frontend: OK (port 3000)")
        else:
            print(f"❌ Frontend: FAILED (status {r.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend: NOT RESPONDING - {str(e)}")
    except Exception as e:
        print(f"❌ Frontend: ERROR - {str(e)}")

    print()
    if backend_ok and frontend_ok:
        print("🎉 ALL SERVICES RUNNING SUCCESSFULLY!")
        return True
    elif backend_ok:
        print("⚠️  Backend OK, Frontend needs attention")
        return False
    elif frontend_ok:
        print("⚠️  Frontend OK, Backend needs attention")
        return False
    else:
        print("❌ NO SERVICES RESPONDING")
        return False


if __name__ == "__main__":
    success = check_services()
    sys.exit(0 if success else 1)
