#!/usr/bin/env python3
"""Direct Problem Identifier and Fixer"""

import subprocess
import time
from pathlib import Path

import requests


def main():
    print("🔍 DIRECT PROBLEM IDENTIFIER")
    print("=" * 50)

    base_dir = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
    python_exe = base_dir / ".venv" / "Scripts" / "python.exe"

    # Test 1: Check if clean_backend.py exists and works
    clean_backend = base_dir / "clean_backend.py"
    if clean_backend.exists():
        print("✅ clean_backend.py exists")

        # Start it
        print("🚀 Starting clean_backend.py...")
        process = subprocess.Popen(
            [str(python_exe), str(clean_backend)],
            cwd=str(base_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

        print(f"Backend PID: {process.pid}")

        # Wait for it to start
        print("⏳ Waiting for backend...")
        time.sleep(5)

        # Test health
        try:
            health_response = requests.get("http://127.0.0.1:8008/health", timeout=5)
            print(f"Health check: {health_response.status_code}")

            if health_response.status_code == 200:
                print("✅ Backend is responding")

                # Test login
                login_response = requests.post(
                    "http://127.0.0.1:8008/api/auth/login",
                    json={"email": "admin@hirebahamas.com", "password": "admin123"},
                    timeout=5,
                )

                print(f"Login test: {login_response.status_code}")
                print(f"Login response: {login_response.text}")

                if login_response.status_code == 200:
                    print("✅ LOGIN IS WORKING!")

                    # Now start frontend
                    print("🌐 Starting frontend...")
                    frontend_dir = base_dir / "frontend"

                    frontend_process = subprocess.Popen(
                        ["npm", "run", "dev"],
                        cwd=str(frontend_dir),
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                    )

                    print(f"Frontend PID: {frontend_process.pid}")
                    print("✅ Frontend started")

                    print("\n" + "=" * 50)
                    print("🎉 PROBLEM SOLVED!")
                    print("=" * 50)
                    print("✅ Backend: http://127.0.0.1:8008")
                    print("✅ Frontend: Check console for port")
                    print("✅ Login: admin@hirebahamas.com / admin123")
                    print("=" * 50)

                    return True
                else:
                    print(f"❌ Login failed: {login_response.status_code}")
                    print(f"   Response: {login_response.text}")
            else:
                print(f"❌ Backend health check failed: {health_response.status_code}")

        except Exception as e:
            print(f"❌ Backend test failed: {e}")
    else:
        print("❌ clean_backend.py not found")

    return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ALL ISSUES RESOLVED!")
        print("You can now use the login system!")
    else:
        print("\n❌ Issues remain. Need manual investigation.")

    input("Press Enter to exit...")
