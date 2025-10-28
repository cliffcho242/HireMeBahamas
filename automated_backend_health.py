#!/usr/bin/env python3
"""
Automated Backend Health Check and Restart Script
Ensures backend is running and healthy, handles login and posts testing
"""

import subprocess
import sys
import time
from pathlib import Path

import requests


def kill_python_processes():
    """Kill any existing Python processes that might be blocking the port"""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", "python"], capture_output=True)
        print("✓ Killed existing Python processes")
        time.sleep(2)
    except Exception as e:
        print(f"⚠ Could not kill processes: {e}")


def start_backend():
    """Start the backend server"""
    try:
        backend_path = Path(__file__).parent / "ULTIMATE_BACKEND_FIXED.py"
        print(f"Starting backend: {backend_path}")
        # Start in background
        process = subprocess.Popen(
            [sys.executable, str(backend_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            ),
        )
        print(f"✓ Backend started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"✗ Failed to start backend: {e}")
        return None


def wait_for_backend(max_wait=30):
    """Wait for backend to be ready"""
    print("Waiting for backend to be ready...")
    for i in range(max_wait):
        try:
            r = requests.get("http://127.0.0.1:8008/health", timeout=2)
            if r.status_code == 200:
                print("✓ Backend is healthy")
                return True
        except Exception:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(f"  Still waiting... ({i+1}/{max_wait}s)")
    print("✗ Backend failed to start within timeout")
    return False


def test_login():
    """Test login functionality"""
    try:
        r = requests.post(
            "http://127.0.0.1:8008/api/auth/login",
            json={"email": "admin@hirebahamas.com", "password": "AdminPass123!"},
            timeout=5,
        )
        if r.status_code == 200:
            print("✓ Login test passed")
            return True
        else:
            print(f"✗ Login test failed: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"✗ Login test error: {e}")
        return False


def test_posts():
    """Test posts endpoint"""
    try:
        r = requests.get("http://127.0.0.1:8008/api/posts", timeout=5)
        if r.status_code == 200:
            print("✓ Posts test passed")
            return True
        else:
            print(f"✗ Posts test failed: {r.status_code} - {r.text}")
            return False
    except Exception as e:
        print(f"✗ Posts test error: {e}")
        return False


def main():
    print("🚀 Automated Backend Health Check & Restart")
    print("=" * 50)

    # Kill existing processes
    kill_python_processes()

    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("✗ Failed to start backend process")
        return False

    # Wait for backend to be ready
    if not wait_for_backend():
        print("✗ Backend not ready, terminating")
        backend_process.terminate()
        return False

    # Test endpoints
    login_ok = test_login()
    posts_ok = test_posts()

    if login_ok and posts_ok:
        print("\n🎉 All tests passed! Backend is fully operational.")
        print("📋 Admin credentials:")
        print("   Email: admin@hirebahamas.com")
        print("   Password: AdminPass123!")
        print("\n🔗 Endpoints:")
        print("   Health: http://127.0.0.1:8008/health")
        print("   Login: http://127.0.0.1:8008/api/auth/login")
        print("   Posts: http://127.0.0.1:8008/api/posts")
        return True
    else:
        print("\n❌ Some tests failed. Backend may need manual intervention.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
