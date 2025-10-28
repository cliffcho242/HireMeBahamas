#!/usr/bin/env python3
"""Complete Solution Launcher"""

import os
import signal
import subprocess
import sys
import time
import webbrowser
from threading import Thread

import requests


class HireBahamasLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.base_dir = os.getcwd()

    def kill_existing_processes(self):
        """Kill any existing Python/Node processes"""
        print("🔄 Cleaning up existing processes...")
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe"],
                capture_output=True,
                check=False,
            )
            subprocess.run(
                ["taskkill", "/F", "/IM", "node.exe"], capture_output=True, check=False
            )
        except:
            pass
        time.sleep(2)

    def start_backend(self):
        """Start the backend server"""
        print("🚀 Starting backend...")
        python_exe = os.path.join(self.base_dir, ".venv", "Scripts", "python.exe")
        backend_file = os.path.join(self.base_dir, "working_backend_final.py")

        self.backend_process = subprocess.Popen(
            [python_exe, backend_file],
            cwd=self.base_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://127.0.0.1:8008/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Backend is running!")
                    return True
            except:
                time.sleep(1)

        print("❌ Backend failed to start")
        return False

    def start_frontend(self):
        """Start the frontend"""
        print("🌐 Starting frontend...")
        frontend_dir = os.path.join(self.base_dir, "frontend")

        self.frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

        print("⏳ Waiting for frontend to start...")
        time.sleep(10)  # Give frontend time to start

        # Try different ports
        for port in [3000, 3001, 3002, 3003, 3004, 3005]:
            try:
                response = requests.get(f"http://localhost:{port}", timeout=2)
                if response.status_code == 200:
                    print(f"✅ Frontend is running on port {port}!")
                    return port
            except:
                continue

        print("❌ Frontend may not be ready yet")
        return 3004  # Default port

    def test_login(self):
        """Test the login functionality"""
        print("🔑 Testing login...")
        try:
            response = requests.post(
                "http://127.0.0.1:8008/api/auth/login",
                json={"email": "admin@hirebahamas.com", "password": "admin123"},
                timeout=5,
            )

            if response.status_code == 200:
                print("✅ Login test successful!")
                data = response.json()
                print(f"   Token: {data.get('token', 'No token')[:20]}...")
                print(f"   User: {data.get('user', {}).get('email', 'No email')}")
                return True
            else:
                print(f"❌ Login test failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login test error: {e}")
            return False

    def launch(self):
        """Launch the complete application"""
        print("\n" + "=" * 60)
        print("🎯 HIREBAHAMAS COMPLETE LAUNCHER")
        print("=" * 60)

        # Step 1: Clean up
        self.kill_existing_processes()

        # Step 2: Start backend
        if not self.start_backend():
            print("❌ Failed to start backend. Exiting.")
            return False

        # Step 3: Test login
        if not self.test_login():
            print("❌ Login test failed. Exiting.")
            return False

        # Step 4: Start frontend
        frontend_port = self.start_frontend()

        # Step 5: Open browser
        frontend_url = f"http://localhost:{frontend_port}"
        print(f"\n🌐 Opening browser to: {frontend_url}")
        webbrowser.open(frontend_url)

        print("\n" + "=" * 60)
        print("✅ APPLICATION LAUNCHED SUCCESSFULLY!")
        print("=" * 60)
        print(f"🔗 Frontend: {frontend_url}")
        print(f"🔗 Backend: http://127.0.0.1:8008")
        print(f"🔑 Login: admin@hirebahamas.com / admin123")
        print("=" * 60)
        print("Press Ctrl+C to stop all services")

        try:
            # Keep the launcher running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.cleanup()

    def cleanup(self):
        """Clean up processes"""
        if self.backend_process:
            self.backend_process.terminate()
        if self.frontend_process:
            self.frontend_process.terminate()

        # Force kill any remaining processes
        subprocess.run(
            ["taskkill", "/F", "/IM", "python.exe"], capture_output=True, check=False
        )
        subprocess.run(
            ["taskkill", "/F", "/IM", "node.exe"], capture_output=True, check=False
        )


if __name__ == "__main__":
    launcher = HireBahamasLauncher()
    launcher.launch()
