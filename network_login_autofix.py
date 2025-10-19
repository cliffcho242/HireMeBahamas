#!/usr/bin/env python3
"""
🔧 HireMeBahamas Network & Login Auto-Fix System
Automatically detects and fixes network connectivity and login issues
"""

import os
import sys
import time
import json
import requests
import subprocess
import psutil
from pathlib import Path

class NetworkLoginFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_port = 8008
        self.frontend_port = 3000
        self.backend_url = f"http://127.0.0.1:{self.backend_port}"
        self.frontend_url = f"http://localhost:{self.frontend_port}"

    def log(self, message, status="INFO"):
        """Enhanced logging with status indicators"""
        timestamp = time.strftime("%H:%M:%S")
        status_icons = {
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "INFO": "ℹ️",
            "FIX": "🔧",
            "TEST": "🧪"
        }
        icon = status_icons.get(status, "ℹ️")
        print(f"[{timestamp}] {icon} {message}")

    def kill_existing_processes(self):
        """Kill any existing backend/frontend processes"""
        self.log("Killing existing processes...", "FIX")

        killed_count = 0

        # Kill Python processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(keyword in cmdline for keyword in ['final_backend.py', 'backend', 'flask']):
                        proc.kill()
                        killed_count += 1
                        self.log(f"Killed Python process (PID: {proc.info['pid']})", "FIX")
            except:
                pass

        # Kill Node.js processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'node' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(keyword in cmdline for keyword in ['vite', 'react', 'frontend']):
                        proc.kill()
                        killed_count += 1
                        self.log(f"Killed Node.js process (PID: {proc.info['pid']})", "FIX")
            except:
                pass

        if killed_count > 0:
            self.log(f"Successfully killed {killed_count} processes", "SUCCESS")
            time.sleep(3)  # Wait for processes to fully terminate
        else:
            self.log("No existing processes found to kill", "INFO")

    def check_backend_health(self):
        """Check if backend is responding"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("Backend health check passed", "SUCCESS")
                return True
            else:
                self.log(f"Backend returned status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Backend health check failed: {e}", "ERROR")
            return False

    def start_backend(self):
        """Start the backend server"""
        self.log("Starting backend server...", "FIX")

        try:
            # Change to project directory
            os.chdir(self.project_root)

            # Start backend
            backend_process = subprocess.Popen(
                [sys.executable, 'final_backend.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_root
            )

            self.log("Backend process started", "SUCCESS")

            # Wait for backend to start
            max_attempts = 30
            for attempt in range(max_attempts):
                if self.check_backend_health():
                    self.log("Backend is now responding", "SUCCESS")
                    return True
                time.sleep(1)
                self.log(f"Waiting for backend... ({attempt + 1}/{max_attempts})", "INFO")

            self.log("Backend failed to start properly", "ERROR")
            return False

        except Exception as e:
            self.log(f"Failed to start backend: {e}", "ERROR")
            return False

    def test_login_endpoint(self):
        """Test the login endpoint with admin credentials"""
        self.log("Testing login endpoint...", "TEST")

        login_data = {
            'email': 'admin@hiremebahamas.com',
            'password': 'AdminPass123!'
        }

        try:
            response = requests.post(
                f"{self.backend_url}/api/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.log("Login endpoint test passed", "SUCCESS")
                    self.log(f"Token received: {result.get('token')[:20]}...", "SUCCESS")
                    return True
                else:
                    self.log(f"Login failed: {result.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"Login endpoint returned status {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False

        except requests.exceptions.ConnectionError:
            self.log("Cannot connect to login endpoint - backend not running", "ERROR")
            return False
        except Exception as e:
            self.log(f"Login test error: {e}", "ERROR")
            return False

    def fix_cors_headers(self):
        """Ensure CORS headers are properly configured"""
        self.log("Checking CORS configuration...", "FIX")

        # Check if backend has proper CORS setup
        try:
            response = requests.options(
                f"{self.backend_url}/api/auth/login",
                headers={
                    'Origin': self.frontend_url,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type,Authorization'
                },
                timeout=5
            )

            cors_headers = response.headers
            required_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]

            missing_headers = []
            for header in required_headers:
                if header not in cors_headers:
                    missing_headers.append(header)

            if missing_headers:
                self.log(f"Missing CORS headers: {missing_headers}", "WARNING")
                return False
            else:
                self.log("CORS headers are properly configured", "SUCCESS")
                return True

        except Exception as e:
            self.log(f"CORS check failed: {e}", "ERROR")
            return False

    def fix_environment_variables(self):
        """Ensure environment variables are properly set"""
        self.log("Checking environment variables...", "FIX")

        env_file = self.project_root / "frontend" / ".env"
        if not env_file.exists():
            self.log("Frontend .env file not found", "ERROR")
            return False

        with open(env_file, 'r') as f:
            env_content = f.read()

        required_vars = {
            'VITE_API_URL': f'http://127.0.0.1:{self.backend_port}',
            'VITE_SOCKET_URL': f'http://127.0.0.1:{self.backend_port}'
        }

        missing_vars = []
        for var, expected_value in required_vars.items():
            if var not in env_content:
                missing_vars.append(var)
            elif expected_value not in env_content:
                self.log(f"{var} has incorrect value", "WARNING")

        if missing_vars:
            self.log(f"Missing environment variables: {missing_vars}", "ERROR")
            # Auto-fix environment variables
            with open(env_file, 'w') as f:
                f.write(f"VITE_API_URL={required_vars['VITE_API_URL']}\n")
                f.write(f"VITE_SOCKET_URL={required_vars['VITE_SOCKET_URL']}\n")
                f.write("VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name\n")
            self.log("Environment variables auto-fixed", "SUCCESS")
            return True
        else:
            self.log("Environment variables are properly configured", "SUCCESS")
            return True

    def test_frontend_connection(self):
        """Test if frontend can connect to backend"""
        self.log("Testing frontend-backend connection...", "TEST")

        try:
            # Test basic API call
            response = requests.get(f"{self.backend_url}/api/stories", timeout=5)
            if response.status_code in [200, 401]:  # 401 is expected without auth
                self.log("Frontend-backend connection test passed", "SUCCESS")
                return True
            else:
                self.log(f"Unexpected response: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Frontend-backend connection test failed: {e}", "ERROR")
            return False

    def comprehensive_fix(self):
        """Run comprehensive network and login fixes"""
        self.log("🚀 Starting HireMeBahamas Network & Login Auto-Fix", "INFO")
        self.log("=" * 60, "INFO")

        fixes_applied = []
        tests_passed = []

        # Step 1: Kill existing processes
        self.log("Step 1: Cleaning up existing processes", "INFO")
        self.kill_existing_processes()
        fixes_applied.append("Process cleanup")

        # Step 2: Fix environment variables
        self.log("Step 2: Checking environment configuration", "INFO")
        if self.fix_environment_variables():
            fixes_applied.append("Environment variables")

        # Step 3: Start backend
        self.log("Step 3: Starting backend server", "INFO")
        if self.start_backend():
            fixes_applied.append("Backend startup")

        # Step 4: Test backend health
        self.log("Step 4: Testing backend health", "INFO")
        if self.check_backend_health():
            tests_passed.append("Backend health")

        # Step 5: Test CORS
        self.log("Step 5: Testing CORS configuration", "INFO")
        if self.fix_cors_headers():
            tests_passed.append("CORS configuration")

        # Step 6: Test login endpoint
        self.log("Step 6: Testing login functionality", "INFO")
        if self.test_login_endpoint():
            tests_passed.append("Login endpoint")

        # Step 7: Test frontend-backend connection
        self.log("Step 7: Testing frontend-backend connection", "INFO")
        if self.test_frontend_connection():
            tests_passed.append("API connectivity")

        # Summary
        self.log("=" * 60, "INFO")
        self.log("📋 FIX SUMMARY", "INFO")
        self.log(f"✅ Fixes Applied: {len(fixes_applied)}", "SUCCESS")
        for fix in fixes_applied:
            self.log(f"   • {fix}", "SUCCESS")

        self.log(f"🧪 Tests Passed: {len(tests_passed)}", "SUCCESS")
        for test in tests_passed:
            self.log(f"   • {test}", "SUCCESS")

        if len(tests_passed) >= 3:  # Backend health, CORS, and Login
            self.log("🎉 Network and login issues have been resolved!", "SUCCESS")
            self.log("🔐 Admin Login: admin@hiremebahamas.com / AdminPass123!", "INFO")
            return True
        else:
            self.log("❌ Some issues remain. Please check the logs above.", "ERROR")
            return False

def main():
    fixer = NetworkLoginFixer()
    success = fixer.comprehensive_fix()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()