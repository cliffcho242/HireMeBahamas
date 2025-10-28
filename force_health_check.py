#!/usr/bin/env python3
"""
HireBahamas Force Health Check - Automated Backend Management
Forces backend to start if needed and runs health checks
"""

import os
import signal
import subprocess
import sys
import time

import requests


def kill_existing_processes():
    """Kill any existing Python processes that might be running the backend"""
    try:
        # Kill Python processes
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
        else:
            subprocess.run(["pkill", "-f", "python"], capture_output=True)
        time.sleep(2)
        print("🧹 Killed existing Python processes")
    except:
        pass


def start_backend():
    """Start the backend server"""
    print("🚀 Starting HireBahamas backend...")

    # Kill existing processes first
    kill_existing_processes()

    try:
        # Start the backend
        backend_cmd = [sys.executable, "ULTIMATE_BACKEND_FIXED.py"]
        process = subprocess.Popen(
            backend_cmd,
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
            ),
        )

        print(f"📍 Backend process started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None


def check_backend_health(max_attempts=10):
    """Check if backend is healthy, with retries"""
    for attempt in range(max_attempts):
        try:
            print(f"🔍 Health check attempt {attempt + 1}/{max_attempts}...")
            response = requests.get("http://127.0.0.1:8008/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                print("✅ Backend is healthy!")
                print(f"   Service: {data.get('service', 'Unknown')}")
                print(f"   Status: {data.get('status', 'Unknown')}")
                return True
            else:
                print(f"⚠️  Backend responded with status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"⏳ Backend not ready yet: {str(e)[:50]}")

        if attempt < max_attempts - 1:
            print("⏳ Waiting 3 seconds before retry...")
            time.sleep(3)

    return False


def run_health_check_command():
    """Run the exact health check command the user requested"""
    print("\n🔍 Running automated health check:")
    print(
        "python -c \"import requests; r=requests.get('http://127.0.0.1:8008/health'); print('Backend:', r.status_code)\""
    )
    print()

    try:
        # Run the exact command
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import requests; r=requests.get('http://127.0.0.1:8008/health'); print('Backend:', r.status_code)",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        print(result.stdout.strip())
        if result.stderr:
            print(f"Errors: {result.stderr.strip()}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("❌ Health check command timed out")
        return False
    except Exception as e:
        print(f"❌ Health check command failed: {e}")
        return False


def main():
    print("🤖 HireBahamas Force Health Check")
    print("=" * 40)
    print("Automated backend management and health monitoring")
    print()

    # Check current directory
    print(f"📍 Working directory: {os.getcwd()}")

    # First check if backend is already running
    print("\n🔍 Checking current backend status...")
    if check_backend_health(3):  # Quick check with fewer attempts
        print("✅ Backend is already running and healthy!")
        success = run_health_check_command()
        if success:
            print("\n🎉 Health check completed successfully!")
        return

    # Backend not running, start it
    print("\n❌ Backend not running - Force starting...")
    backend_process = start_backend()

    if backend_process is None:
        print("❌ Failed to start backend process")
        return

    # Wait for backend to start and check health
    print("\n⏳ Waiting for backend to initialize...")
    if check_backend_health(15):  # More attempts for startup
        print("\n✅ Backend started successfully!")

        # Run the health check command
        success = run_health_check_command()

        if success:
            print("\n🎉 Force health check completed successfully!")
            print("✅ Backend is running and healthy!")
        else:
            print("\n⚠️  Backend started but health check had issues")

    else:
        print("\n❌ Backend failed to start properly")
        print("📋 Check for error messages above")

        # Try to terminate the process if it exists
        try:
            if sys.platform == "win32":
                backend_process.terminate()
            else:
                os.killpg(os.getpgid(backend_process.pid), signal.SIGTERM)
        except:
            pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        print("\n🤖 Force health check automation complete")
