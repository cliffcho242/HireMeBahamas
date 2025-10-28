#!/usr/bin/env python3
"""
HireBahamas Backend Auto-Health-Check
Automatically starts backend if needed and runs health checks
"""

import os
import subprocess
import sys
import time

import requests


def check_backend_health():
    """Check if backend is running and healthy"""
    try:
        response = requests.get("http://127.0.0.1:8008/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Backend: {response.status_code}")
            print(f"Service: {data.get('service', 'Unknown')}")
            print(f"Status: {data.get('status', 'Unknown')}")
            return True
        else:
            print(f"Backend: {response.status_code} (Unhealthy)")
            return False
    except Exception as e:
        print(f"Backend: NOT RUNNING - {str(e)[:50]}")
        return False


def start_backend():
    """Start the backend server"""
    print("Starting backend server...")

    # Kill any existing Python processes
    try:
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
        time.sleep(2)
    except:
        pass

    # Start the backend
    try:
        backend_cmd = [sys.executable, "ULTIMATE_BACKEND_FIXED.py"]
        subprocess.Popen(backend_cmd, cwd=os.getcwd())
        print("Backend server started")
        time.sleep(5)  # Wait for startup
        return True
    except Exception as e:
        print(f"Failed to start backend: {e}")
        return False


def main():
    print("🤖 HireBahamas Backend Auto-Health-Check")
    print("=" * 45)

    # First check
    if check_backend_health():
        print("✅ Backend is already running and healthy!")
        return

    # Try to start backend
    print("\n🔄 Backend not running - Auto-starting...")
    if start_backend():
        print("⏳ Waiting for backend to initialize...")
        time.sleep(3)

        # Final check
        if check_backend_health():
            print("✅ Backend successfully started and is healthy!")
        else:
            print("❌ Backend failed to start properly")
    else:
        print("❌ Failed to start backend server")


if __name__ == "__main__":
    main()
