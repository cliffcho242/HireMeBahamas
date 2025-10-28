#!/usr/bin/env python3
"""Stable Backend Launcher"""

import os
import subprocess
import sys
import time
from pathlib import Path


def start_backend():
    """Start backend in a new window"""

    base_dir = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
    python_exe = base_dir / ".venv" / "Scripts" / "python.exe"
    backend_file = base_dir / "clean_backend.py"

    print("Starting backend in new window...")

    # Start backend in new console window
    process = subprocess.Popen(
        [str(python_exe), str(backend_file)],
        cwd=str(base_dir),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    print(f"Backend process started with PID: {process.pid}")

    # Wait for it to start
    print("Waiting for backend to be ready...")
    for i in range(15):
        try:
            import requests

            response = requests.get("http://127.0.0.1:8008/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Backend is ready! (attempt {i+1})")
                return True
        except:
            pass
        time.sleep(1)

    print("❌ Backend failed to start or not responding")
    return False


def test_login():
    """Test login functionality"""
    try:
        import requests

        print("Testing login...")
        response = requests.post(
            "http://127.0.0.1:8008/api/auth/login",
            json={"email": "admin@hirebahamas.com", "password": "admin123"},
            timeout=5,
        )

        if response.status_code == 200:
            print("✅ Login test successful!")
            data = response.json()
            print(f"   Token: {data.get('token', 'No token')[:30]}...")
            print(f"   User: {data.get('user', {}).get('email', 'No email')}")
            return True
        else:
            print(f"❌ Login test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False


def start_frontend():
    """Start frontend"""
    print("Starting frontend...")

    frontend_dir = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas/frontend")

    process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(frontend_dir),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    print(f"Frontend process started with PID: {process.pid}")
    print(
        "Frontend should be available at http://localhost:3000 (or next available port)"
    )

    return True


if __name__ == "__main__":
    print("🚀 HIREBAHAMAS LAUNCHER")
    print("=" * 50)

    # Step 1: Start backend
    if start_backend():
        # Step 2: Test login
        if test_login():
            # Step 3: Start frontend
            start_frontend()

            print("\n✅ ALL SERVICES STARTED!")
            print("=" * 50)
            print("🔗 Backend: http://127.0.0.1:8008")
            print("🔗 Frontend: http://localhost:3000 (or check console)")
            print("🔑 Login: admin@hirebahamas.com / admin123")
            print("=" * 50)

            input("Press Enter to exit...")
        else:
            print("❌ Login test failed!")
            input("Press Enter to exit...")
    else:
        print("❌ Backend failed to start!")
        input("Press Enter to exit...")
