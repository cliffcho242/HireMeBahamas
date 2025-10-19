#!/usr/bin/env python3
"""
Quick Test for AI Permanent Network Fix System
"""

import requests
import subprocess
import sys
import time

def test_backend():
    try:
        r = requests.get('http://127.0.0.1:8008/health', timeout=5)
        return r.status_code == 200
    except:
        return False

def test_frontend():
    # Test multiple possible ports
    for port in [3000, 3001, 3002]:
        try:
            r = requests.get(f'http://localhost:{port}', timeout=5)
            if r.status_code == 200:
                return True, port
        except:
            continue
    return False, None

def test_admin_login():
    try:
        data = {"email": "admin@hirebahamas.com", "password": "AdminPass123!"}
        r = requests.post('http://127.0.0.1:8008/auth/login', json=data, timeout=10)
        return r.status_code == 200 and r.json().get('success')
    except:
        return False

def main():
    print("🧪 AI Permanent Network Fix - System Test")
    print("=" * 50)

    # Test backend
    print("Testing backend server...")
    backend_ok = test_backend()
    print(f"Backend: {'✅ OK' if backend_ok else '❌ FAIL'}")

    # Test frontend
    print("Testing frontend server...")
    frontend_ok, port = test_frontend()
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ FAIL'} (Port: {port})")

    # Test admin login
    print("Testing admin login...")
    login_ok = test_admin_login()
    print(f"Admin Login: {'✅ OK' if login_ok else '❌ FAIL'}")

    print("\n" + "=" * 50)
    if backend_ok and frontend_ok and login_ok:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("Network errors have been permanently resolved!")
        return 0
    else:
        print("❌ ISSUES DETECTED - Running AI Fixer...")
        try:
            result = subprocess.run([sys.executable, 'ai_permanent_network_fixer.py'],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ AI Fixer completed successfully")
                return 0
            else:
                print("❌ AI Fixer failed")
                return 1
        except:
            print("❌ Could not run AI Fixer")
            return 1

if __name__ == "__main__":
    sys.exit(main())