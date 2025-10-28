#!/usr/bin/env python3
"""
AI-Powered Permanent Network Error Resolution System
Continuously monitors and fixes network errors, authentication issues, and connection problems
"""

import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import psutil
import requests


class AIPermanentNetworkFixer:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8008"
        self.frontend_url = None
        self.frontend_port = None
        self.monitoring_active = False
        self.last_health_check = None
        self.error_count = 0
        self.max_errors_before_restart = 3

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            filename="ai_network_monitor.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger("AINetworkFixer")

    def run_command(self, cmd, shell=True, capture_output=True, timeout=30):
        """Run a command with proper error handling"""
        try:
            result = subprocess.run(
                cmd,
                shell=shell,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def check_port_availability(self, host, port):
        """Check if a port is available"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

    def detect_frontend_port(self):
        """Detect the actual frontend port being used"""
        possible_ports = [3000, 3001, 3002, 5173, 4173, 8080, 4000, 5000]

        for port in possible_ports:
            if self.check_port_availability("localhost", port):
                try:
                    response = requests.get(f"http://localhost:{port}", timeout=3)
                    if response.status_code == 200:
                        content = response.text.lower()
                        if any(
                            keyword in content
                            for keyword in ["html", "react", "vite", "hirebahamas"]
                        ):
                            self.frontend_port = port
                            self.frontend_url = f"http://localhost:{port}"
                            return True
                except:
                    continue
        return False

    def check_backend_health(self):
        """Check if backend server is running and healthy"""
        try:
            if not self.check_port_availability("127.0.0.1", 8008):
                return False

            response = requests.get(f"{self.backend_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def check_frontend_health(self):
        """Check if frontend server is running"""
        if not self.frontend_port and not self.detect_frontend_port():
            return False

        try:
            if not self.check_port_availability("localhost", self.frontend_port):
                return False

            response = requests.get(self.frontend_url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def test_admin_login(self):
        """Test admin login functionality"""
        try:
            login_data = {"email": "admin@hirebahamas.com", "password": "AdminPass123!"}
            response = requests.post(
                f"{self.backend_url}/auth/login", json=login_data, timeout=10
            )
            return response.status_code == 200 and response.json().get("success")
        except:
            return False

    def kill_process_on_port(self, port):
        """Kill any process running on a specific port"""
        try:
            # Find process using the port
            for proc in psutil.process_iter(["pid", "name", "connections"]):
                try:
                    if proc.info["connections"]:
                        for conn in proc.info["connections"]:
                            if hasattr(conn, "laddr") and conn.laddr.port == port:
                                proc.kill()
                                self.logger.info(
                                    f"Killed process {proc.info['pid']} on port {port}"
                                )
                                return True
                except:
                    continue
        except:
            pass
        return False

    def start_backend_server(self):
        """Start the backend server"""
        self.logger.info("Starting backend server...")

        # Kill any existing backend processes
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if "python" in proc.info["name"].lower():
                    cmdline = " ".join(proc.info["cmdline"])
                    if "final_backend.py" in cmdline:
                        proc.kill()
                        time.sleep(1)
            except:
                pass

        try:
            backend_process = subprocess.Popen(
                [sys.executable, "final_backend.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd(),
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            time.sleep(5)  # Wait for startup

            if self.check_backend_health():
                self.logger.info("Backend server started successfully")
                return True
            else:
                backend_process.terminate()
                return False
        except Exception as e:
            self.logger.error(f"Failed to start backend: {e}")
            return False

    def start_frontend_server(self):
        """Start the frontend server"""
        self.logger.info("Starting frontend server...")

        # Kill existing frontend processes
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if "node" in proc.info["name"].lower() or "npm" in " ".join(
                    proc.info["cmdline"]
                ):
                    cmdline = " ".join(proc.info["cmdline"])
                    if any(keyword in cmdline for keyword in ["vite", "npm", "react"]):
                        proc.kill()
                        time.sleep(1)
            except:
                pass

        frontend_dir = Path(__file__).parent / "frontend"
        if not frontend_dir.exists():
            self.logger.error("Frontend directory not found")
            return False

        try:
            npm_cmd = self.find_npm_command()
            if not npm_cmd:
                return False

            frontend_process = subprocess.Popen(
                [npm_cmd, "run", "dev"],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            # Wait for startup and detect port
            time.sleep(10)

            if self.detect_frontend_port() and self.check_frontend_health():
                self.logger.info(
                    f"Frontend server started successfully on port {self.frontend_port}"
                )
                return True
            else:
                frontend_process.terminate()
                return False
        except Exception as e:
            self.logger.error(f"Failed to start frontend: {e}")
            return False

    def find_npm_command(self):
        """Find the npm command path"""
        npm_paths = [
            "npm.cmd",
            "npm",
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
        ]

        for path in npm_paths:
            try:
                success, _, _ = self.run_command([path, "--version"])
                if success:
                    return path
            except:
                continue
        return None

    def comprehensive_health_check(self):
        """Perform comprehensive health check"""
        self.logger.info("Performing comprehensive health check...")

        issues = []
        backend_ok = self.check_backend_health()
        frontend_ok = self.check_frontend_health()
        login_ok = self.test_admin_login()

        if not backend_ok:
            issues.append("Backend server down")
        if not frontend_ok:
            issues.append("Frontend server down")
        if not login_ok:
            issues.append("Admin login failing")

        self.last_health_check = time.time()

        if issues:
            self.logger.warning(f"Health check found issues: {', '.join(issues)}")
            self.error_count += 1
            return False, issues
        else:
            self.logger.info("All systems healthy")
            self.error_count = 0  # Reset error count on success
            return True, []

    def emergency_restart(self):
        """Perform emergency restart of all services"""
        self.logger.warning("Performing emergency restart of all services")

        # Kill all related processes
        self.kill_process_on_port(8008)  # Backend
        if self.frontend_port:
            self.kill_process_on_port(self.frontend_port)  # Frontend

        time.sleep(2)

        # Restart services
        backend_started = self.start_backend_server()
        frontend_started = self.start_frontend_server()

        if backend_started and frontend_started:
            self.logger.info("Emergency restart successful")
            self.error_count = 0
            return True
        else:
            self.logger.error("Emergency restart failed")
            return False

    def continuous_monitoring_loop(self):
        """Main monitoring loop without external dependencies"""
        self.logger.info("Starting continuous network monitoring...")

        while self.monitoring_active:
            try:
                # Perform health check
                healthy, issues = self.comprehensive_health_check()

                if not healthy:
                    self.logger.warning(f"Issues detected: {issues}")

                    if self.error_count >= self.max_errors_before_restart:
                        self.logger.warning(
                            "Too many errors, performing emergency restart"
                        )
                        self.emergency_restart()
                    else:
                        # Try to fix individual issues
                        for issue in issues:
                            if "Backend" in issue:
                                self.start_backend_server()
                            elif "Frontend" in issue:
                                self.start_frontend_server()

                # Wait 30 seconds before next check
                time.sleep(30)

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(30)

    def start_monitoring(self):
        """Start the continuous monitoring system"""
        print("🤖 AI Permanent Network Fixer - Starting Continuous Monitoring")
        print("=" * 60)

        # Initial health check and fixes
        print("Performing initial system check...")
        healthy, issues = self.comprehensive_health_check()

        if not healthy:
            print(f"Initial issues found: {issues}")
            print("Applying fixes...")
            self.emergency_restart()

        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self.continuous_monitoring_loop, daemon=True
        )
        monitor_thread.start()

        print("✅ Continuous monitoring started!")
        print("The AI system will now monitor and fix network errors permanently.")
        print("Press Ctrl+C to stop monitoring.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping AI network monitoring...")
            self.monitoring_active = False
            time.sleep(2)
            print("✅ Monitoring stopped.")

    def run_diagnostic_mode(self):
        """Run one-time diagnostic and fix"""
        print("🤖 AI Permanent Network Fixer - Diagnostic Mode")
        print("=" * 50)

        healthy, issues = self.comprehensive_health_check()

        if healthy:
            print("✅ All systems are healthy!")
            return True

        print(f"❌ Issues found: {issues}")
        print("🔧 Applying fixes...")

        success = self.emergency_restart()

        if success:
            print("✅ All issues resolved!")
            return True
        else:
            print("❌ Some issues could not be resolved automatically")
            return False


def main():
    """Main function"""
    try:
        import psutil
        import requests
    except ImportError:
        print("Installing required packages...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "psutil", "requests"], check=True
        )

    fixer = AIPermanentNetworkFixer()

    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        fixer.start_monitoring()
    else:
        success = fixer.run_diagnostic_mode()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
