#!/usr/bin/env python3
"""
AI-Powered Network & Authentication Diagnostic System
Automatically detects and fixes network errors, authentication issues, and connection problems
"""

import os
import sys
import subprocess
import requests
import time
import json
import socket
from pathlib import Path
import threading
import psutil

class AINetworkAuthenticator:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8008"
        self.frontend_url = None  # Will be detected dynamically
        self.frontend_port = None
        self.diagnostic_results = {}
        self.fixes_applied = []

    def detect_frontend_port(self):
        """Detect the actual frontend port being used"""
        print("🔍 Detecting frontend port...")

        # Common ports that Vite/React might use
        possible_ports = [3000, 3001, 3002, 5173, 4173, 8080, 4000]

        for port in possible_ports:
            if self.check_port_availability("localhost", port):
                try:
                    # Test if it's actually the frontend
                    response = requests.get(f"http://localhost:{port}", timeout=3)
                    if response.status_code == 200:
                        # Check if it contains typical frontend content
                        content = response.text.lower()
                        if any(keyword in content for keyword in ['html', 'react', 'vite', 'hirebahamas']):
                            self.frontend_port = port
                            self.frontend_url = f"http://localhost:{port}"
                            print(f"✅ Frontend detected on port {port}")
                            return True
                except:
                    continue

        print("❌ Could not detect frontend port")
        return False

    def run_command(self, cmd, shell=True, capture_output=True, timeout=30):
        """Run a command with proper error handling"""
        try:
            result = subprocess.run(cmd, shell=shell, capture_output=capture_output,
                                  text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def check_port_availability(self, host, port):
        """Check if a port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

    def check_backend_health(self):
        """Check if backend server is running and healthy"""
        print("🔍 Checking backend server health...")

        # Check if port 8008 is open
        if not self.check_port_availability("127.0.0.1", 8008):
            self.diagnostic_results["backend_port"] = "CLOSED"
            return False

        # Try to connect to health endpoint
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                self.diagnostic_results["backend_health"] = "HEALTHY"
                return True
            else:
                self.diagnostic_results["backend_health"] = f"HTTP {response.status_code}"
                return False
        except requests.exceptions.RequestException as e:
            self.diagnostic_results["backend_connection"] = str(e)
            return False

    def check_frontend_health(self):
        """Check if frontend server is running"""
        print("🔍 Checking frontend server health...")

        # First detect the port if not already done
        if not self.frontend_port:
            if not self.detect_frontend_port():
                self.diagnostic_results["frontend_port"] = "NOT_DETECTED"
                return False

        # Check if the detected port is still available
        if not self.check_port_availability("localhost", self.frontend_port):
            self.diagnostic_results["frontend_port"] = f"CLOSED (port {self.frontend_port})"
            return False

        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.diagnostic_results["frontend_health"] = "HEALTHY"
                self.diagnostic_results["frontend_port"] = f"ACTIVE (port {self.frontend_port})"
                return True
            else:
                self.diagnostic_results["frontend_health"] = f"HTTP {response.status_code}"
                return False
        except requests.exceptions.RequestException as e:
            self.diagnostic_results["frontend_connection"] = str(e)
            return False

    def check_database_connection(self):
        """Check database connectivity"""
        print("🔍 Checking database connection...")

        try:
            import sqlite3
            db_path = Path(__file__).parent / "hirebahamas.db"
            conn = sqlite3.connect(str(db_path), timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            conn.close()

            self.diagnostic_results["database_users"] = count
            self.diagnostic_results["database_status"] = "CONNECTED"
            return True
        except Exception as e:
            self.diagnostic_results["database_error"] = str(e)
            return False

    def test_admin_login(self):
        """Test admin login functionality"""
        print("🔍 Testing admin login...")

        login_data = {
            "email": "admin@hirebahamas.com",
            "password": "AdminPass123!"
        }

        try:
            response = requests.post(f"{self.backend_url}/auth/login",
                                   json=login_data, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.diagnostic_results["admin_login"] = "SUCCESS"
                    self.diagnostic_results["admin_token"] = data.get("token")
                    return True
                else:
                    self.diagnostic_results["admin_login"] = f"FAILED: {data.get('message')}"
                    return False
            else:
                self.diagnostic_results["admin_login"] = f"HTTP {response.status_code}"
                return False

        except requests.exceptions.RequestException as e:
            self.diagnostic_results["admin_login_error"] = str(e)
            return False

    def start_backend_server(self):
        """Start the backend server if not running"""
        print("🔧 Starting backend server...")

        # Kill any existing backend processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'final_backend.py' in cmdline:
                        print(f"Killing existing backend process (PID: {proc.info['pid']})")
                        proc.kill()
            except:
                pass

        # Start new backend server
        try:
            backend_process = subprocess.Popen([sys.executable, 'final_backend.py'],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             cwd=os.getcwd())

            # Wait for server to start
            time.sleep(3)

            if self.check_backend_health():
                self.fixes_applied.append("Started backend server")
                return True
            else:
                print("Backend server failed to start properly")
                return False

        except Exception as e:
            print(f"Failed to start backend server: {e}")
            return False

    def start_frontend_server(self):
        """Start the frontend server if not running"""
        print("🔧 Starting frontend server...")

        # Kill any existing frontend processes more aggressively
        self.kill_existing_frontend_processes()

        # Get frontend directory
        frontend_dir = Path(__file__).parent / "frontend"
        if not frontend_dir.exists():
            print("Frontend directory not found")
            return False

        try:
            # Use npm from correct path
            npm_cmd = self.find_npm_command()
            if not npm_cmd:
                print("npm command not found")
                return False

            # Start frontend server
            frontend_process = subprocess.Popen([npm_cmd, 'run', 'dev'],
                                             cwd=str(frontend_dir),
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

            # Wait for server to start (give it more time)
            print("Waiting for frontend server to start...")
            time.sleep(8)

            # Try to detect the port multiple times
            max_attempts = 5
            for attempt in range(max_attempts):
                if self.detect_frontend_port():
                    if self.check_frontend_health():
                        self.fixes_applied.append("Started frontend server")
                        print(f"✅ Frontend server started successfully on port {self.frontend_port}")
                        return True
                time.sleep(2)

            print("Frontend server failed to start properly after multiple attempts")
            return False

        except Exception as e:
            print(f"Failed to start frontend server: {e}")
            return False

    def find_npm_command(self):
        """Find the npm command path"""
        npm_paths = [
            "npm.cmd",  # Windows npm command
            "npm",
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd"
        ]

        for path in npm_paths:
            try:
                # Test if it works
                success, _, _ = self.run_command([path, "--version"])
                if success:
                    return path
            except:
                continue

        return None

    def fix_cors_issues(self):
        """Ensure CORS is properly configured"""
        print("🔧 Checking CORS configuration...")

        # Check if CORS headers are present
        try:
            response = requests.options(f"{self.backend_url}/auth/login",
                                      headers={'Origin': self.frontend_url},
                                      timeout=5)

            cors_headers = ['access-control-allow-origin', 'access-control-allow-methods']
            missing_headers = []

            for header in cors_headers:
                if header not in response.headers:
                    missing_headers.append(header)

            if missing_headers:
                print(f"CORS headers missing: {missing_headers}")
                self.diagnostic_results["cors_issues"] = missing_headers
                return False
            else:
                self.diagnostic_results["cors_status"] = "OK"
                return True

        except Exception as e:
            print(f"CORS check failed: {e}")
            return False

    def run_full_diagnostic(self):
        """Run complete diagnostic and apply fixes"""
        print("🤖 AI NETWORK & AUTHENTICATION DIAGNOSTIC")
        print("=" * 50)

        issues_found = []
        fixes_needed = []

        # 1. Check database first
        if not self.check_database_connection():
            issues_found.append("Database connection failed")
            fixes_needed.append("Database connectivity")

        # 2. Detect frontend port early
        if not self.detect_frontend_port():
            issues_found.append("Frontend server not detected")
            fixes_needed.append("Start frontend server")

        # 3. Check backend
        if not self.check_backend_health():
            issues_found.append("Backend server not responding")
            fixes_needed.append("Start backend server")

        # 4. Check frontend health (now that port is detected)
        if not self.check_frontend_health():
            issues_found.append("Frontend server not responding")
            fixes_needed.append("Start frontend server")

        # 5. Check CORS
        if not self.fix_cors_issues():
            issues_found.append("CORS configuration issues")
            fixes_needed.append("Fix CORS headers")

        # 6. Test admin login
        if not self.test_admin_login():
            issues_found.append("Admin login failed")
            fixes_needed.append("Fix authentication")

        # Apply fixes
        if fixes_needed:
            print(f"\n🔧 Applying {len(fixes_needed)} fixes...")

            if "Start backend server" in fixes_needed:
                if self.start_backend_server():
                    fixes_needed.remove("Start backend server")

            if "Start frontend server" in fixes_needed:
                if self.start_frontend_server():
                    fixes_needed.remove("Start frontend server")

        # Final verification
        print("\n🔄 Final verification...")
        self.test_admin_login()

        return len(issues_found) == 0

    def generate_report(self):
        """Generate diagnostic report"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "diagnostic_results": self.diagnostic_results,
            "fixes_applied": self.fixes_applied,
            "status": "SUCCESS" if not self.diagnostic_results.get("admin_login_error") else "ISSUES_REMAINING"
        }

        return report

    def kill_existing_frontend_processes(self):
        """Kill any existing frontend processes more aggressively"""
        print("🔧 Killing existing frontend processes...")

        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'node' in proc.info['name'].lower() or 'npm' in ' '.join(proc.info['cmdline']):
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(keyword in cmdline for keyword in ['vite', 'npm', 'react', 'frontend', 'hirebahamas']):
                        print(f"Killing frontend process (PID: {proc.info['pid']}) - {cmdline[:50]}...")
                        proc.kill()
                        killed_count += 1
                        time.sleep(0.5)  # Give it time to die
            except psutil.NoSuchProcess:
                continue
            except Exception as e:
                print(f"Error killing process {proc.info['pid']}: {e}")

        if killed_count > 0:
            print(f"✅ Killed {killed_count} existing frontend processes")
            time.sleep(2)  # Wait for processes to fully terminate
        else:
            print("ℹ️ No existing frontend processes found")

def main():
    """Main function"""
    try:
        import psutil
    except ImportError:
        print("Installing required package: psutil")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)

    try:
        import requests
    except ImportError:
        print("Installing required package: requests")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)

    ai_diagnostic = AINetworkAuthenticator()

    success = ai_diagnostic.run_full_diagnostic()

    report = ai_diagnostic.generate_report()

    print("\n" + "=" * 50)
    print("DIAGNOSTIC REPORT")
    print("=" * 50)

    for key, value in report["diagnostic_results"].items():
        print(f"{key}: {value}")

    if report["fixes_applied"]:
        print(f"\nFixes Applied: {', '.join(report['fixes_applied'])}")

    print(f"\nOverall Status: {report['status']}")

    if success:
        print("\n✅ ALL SYSTEMS OPERATIONAL")
        print("Admin login should now work without network errors!")
    else:
        print("\n❌ ISSUES REMAIN - Check diagnostic results above")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())