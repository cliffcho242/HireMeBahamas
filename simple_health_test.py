"""
SIMPLE HEALTH TEST - Force start backend and test health endpoint
"""

import os
import subprocess
import sys
import time

import requests


def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8008/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend...")

    # Change to project directory
    os.chdir(r"C:\Users\Dell\OneDrive\Desktop\HireBahamas")

    # Try the fixed backend first
    if os.path.exists("ULTIMATE_BACKEND_FIXED.py"):
        print("   Using ULTIMATE_BACKEND_FIXED.py")
        process = subprocess.Popen([sys.executable, "ULTIMATE_BACKEND_FIXED.py"])
        return process
    elif os.path.exists("final_backend.py"):
        print("   Using final_backend.py")
        process = subprocess.Popen([sys.executable, "final_backend.py"])
        return process
    else:
        print("   ❌ No backend file found")
        return None


def main():
    print("🔍 Testing backend health...")

    # Test if backend is already running
    if test_health():
        print("✅ Backend is already running!")
        return True

    print("❌ Backend not responding, starting it...")

    # Kill any existing processes
    try:
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
    except:
        pass

    time.sleep(2)

    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend")
        return False

    print("⏳ Waiting for backend to start...")

    # Wait for backend to be ready
    for i in range(20):
        if test_health():
            print("✅ Backend is now running!")
            print("\n🌐 Health endpoint: http://127.0.0.1:8008/health")
            return True
        print(f"   Waiting... {i+1}/20")
        time.sleep(1)

    print("❌ Backend failed to start")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
