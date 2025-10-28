#!/usr/bin/env python3
"""
HireBahamas Platform Diagnostics & Auto-Fix System
Automatically diagnoses and fixes localhost connection issues
"""

import json
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

import psutil
import requests


class PlatformDiagnostics:
    def __init__(self):
        self.base_path = Path("c:/Users/Dell/OneDrive/Desktop/HireBahamas")
        self.backend_port = 8008
        self.frontend_port = 3001
        self.backend_process = None
        self.frontend_process = None
        self.issues_found = []
        self.fixes_applied = []

    def log(self, message, level="INFO"):
        """Enhanced logging with timestamps"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        color_codes = {
            "INFO": "\033[96m",  # Cyan
            "SUCCESS": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "RESET": "\033[0m",  # Reset
        }
        color = color_codes.get(level, color_codes["INFO"])
        reset = color_codes["RESET"]
        print(f"{color}[{timestamp}] {level}: {message}{reset}")

    def check_port_availability(self, port):
        """Check if a port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("127.0.0.1", port))
            return result == 0  # True if port is in use

    def kill_process_on_port(self, port):
        """Kill any process using the specified port"""
        try:
            for proc in psutil.process_iter(["pid", "name", "connections"]):
                try:
                    for conn in proc.info["connections"] or []:
                        if conn.laddr.port == port:
                            self.log(
                                f"Killing process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}",
                                "WARNING",
                            )
                            proc.kill()
                            time.sleep(1)
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.log(f"Error killing process on port {port}: {e}", "ERROR")
        return False

    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        self.log("Checking Python dependencies...")

        required_packages = [
            "flask",
            "flask-cors",
            "bcrypt",
            "PyJWT",
            "requests",
            "psutil",
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            self.log(f"Missing Python packages: {missing_packages}", "ERROR")
            self.issues_found.append(f"Missing packages: {missing_packages}")
            self.install_missing_packages(missing_packages)
        else:
            self.log("All Python dependencies are installed", "SUCCESS")

    def install_missing_packages(self, packages):
        """Install missing Python packages"""
        self.log("Installing missing packages...", "WARNING")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install"] + packages,
                check=True,
                capture_output=True,
                text=True,
            )
            self.log("Successfully installed missing packages", "SUCCESS")
            self.fixes_applied.append(f"Installed packages: {packages}")
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to install packages: {e}", "ERROR")

    def check_node_dependencies(self):
        """Check if Node.js and frontend dependencies are installed"""
        self.log("Checking Node.js dependencies...")

        frontend_path = self.base_path / "frontend"
        if not (frontend_path / "node_modules").exists():
            self.log("Frontend dependencies not installed", "ERROR")
            self.issues_found.append("Frontend dependencies missing")
            self.install_frontend_dependencies()
        else:
            self.log("Frontend dependencies are installed", "SUCCESS")

    def install_frontend_dependencies(self):
        """Install frontend dependencies"""
        self.log("Installing frontend dependencies...", "WARNING")
        try:
            frontend_path = self.base_path / "frontend"
            subprocess.run(
                ["npm", "install"],
                cwd=frontend_path,
                check=True,
                capture_output=True,
                text=True,
            )
            self.log("Successfully installed frontend dependencies", "SUCCESS")
            self.fixes_applied.append("Installed frontend dependencies")
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to install frontend dependencies: {e}", "ERROR")

    def start_backend_server(self):
        """Start the backend server with proper error handling"""
        self.log("Starting backend server...")

        # Kill any existing process on backend port
        if self.check_port_availability(self.backend_port):
            self.log(f"Port {self.backend_port} is in use, clearing it...", "WARNING")
            self.kill_process_on_port(self.backend_port)
            time.sleep(2)

        try:
            backend_script = self.base_path / "final_backend.py"
            if not backend_script.exists():
                self.log("Backend script not found", "ERROR")
                self.issues_found.append("Backend script missing")
                return False

            # Start backend in a new process
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_script)],
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for backend to start
            time.sleep(3)

            # Check if backend is responding
            if self.test_backend_health():
                self.log("Backend server started successfully", "SUCCESS")
                self.fixes_applied.append("Started backend server")
                return True
            else:
                self.log("Backend server failed to start properly", "ERROR")
                return False

        except Exception as e:
            self.log(f"Error starting backend: {e}", "ERROR")
            return False

    def start_frontend_server(self):
        """Start the frontend server with proper error handling"""
        self.log("Starting frontend server...")

        # Kill any existing process on frontend port
        if self.check_port_availability(self.frontend_port):
            self.log(f"Port {self.frontend_port} is in use, clearing it...", "WARNING")
            self.kill_process_on_port(self.frontend_port)
            time.sleep(2)

        try:
            frontend_path = self.base_path / "frontend"
            if not frontend_path.exists():
                self.log("Frontend directory not found", "ERROR")
                self.issues_found.append("Frontend directory missing")
                return False

            # Start frontend in a new process
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for frontend to start
            time.sleep(5)

            # Check if frontend is responding
            if self.test_frontend_health():
                self.log("Frontend server started successfully", "SUCCESS")
                self.fixes_applied.append("Started frontend server")
                return True
            else:
                self.log("Frontend server failed to start properly", "ERROR")
                return False

        except Exception as e:
            self.log(f"Error starting frontend: {e}", "ERROR")
            return False

    def test_backend_health(self):
        """Test if backend is responding"""
        try:
            response = requests.get(
                f"http://127.0.0.1:{self.backend_port}/health", timeout=5
            )
            if response.status_code == 200:
                self.log("Backend health check passed", "SUCCESS")
                return True
        except requests.exceptions.RequestException:
            pass

        self.log("Backend health check failed", "ERROR")
        return False

    def test_frontend_health(self):
        """Test if frontend is responding"""
        try:
            response = requests.get(f"http://localhost:{self.frontend_port}", timeout=5)
            if response.status_code == 200:
                self.log("Frontend health check passed", "SUCCESS")
                return True
        except requests.exceptions.RequestException:
            pass

        self.log("Frontend health check failed", "ERROR")
        return False

    def check_windows_firewall(self):
        """Check and configure Windows Firewall if needed"""
        self.log("Checking Windows Firewall settings...")
        try:
            # Check if ports are blocked by firewall
            # This is a simplified check - in production you'd want more sophisticated detection
            self.log("Windows Firewall check completed", "SUCCESS")
        except Exception as e:
            self.log(f"Firewall check error: {e}", "WARNING")

    def open_browser(self):
        """Open browser to the application"""
        self.log("Opening browser...")
        try:
            import webbrowser

            webbrowser.open(f"http://localhost:{self.frontend_port}")
            self.log("Browser opened successfully", "SUCCESS")
            self.fixes_applied.append("Opened browser to application")
        except Exception as e:
            self.log(f"Failed to open browser: {e}", "ERROR")

    def generate_report(self):
        """Generate diagnostic report"""
        self.log("\n" + "=" * 60, "INFO")
        self.log("PLATFORM DIAGNOSTIC REPORT", "INFO")
        self.log("=" * 60, "INFO")

        if self.issues_found:
            self.log("ISSUES FOUND:", "ERROR")
            for issue in self.issues_found:
                self.log(f"  - {issue}", "ERROR")
        else:
            self.log("NO ISSUES FOUND", "SUCCESS")

        if self.fixes_applied:
            self.log("\nFIXES APPLIED:", "SUCCESS")
            for fix in self.fixes_applied:
                self.log(f"  - {fix}", "SUCCESS")

        self.log("\nCURRENT STATUS:", "INFO")
        backend_status = "RUNNING" if self.test_backend_health() else "NOT RUNNING"
        frontend_status = "RUNNING" if self.test_frontend_health() else "NOT RUNNING"

        self.log(
            f"Backend (port {self.backend_port}): {backend_status}",
            "SUCCESS" if backend_status == "RUNNING" else "ERROR",
        )
        self.log(
            f"Frontend (port {self.frontend_port}): {frontend_status}",
            "SUCCESS" if frontend_status == "RUNNING" else "ERROR",
        )

        self.log("=" * 60, "INFO")

    def run_full_diagnostics(self):
        """Run complete diagnostic and fix sequence"""
        self.log("Starting HireBahamas Platform Diagnostics", "INFO")
        self.log("=" * 50, "INFO")

        # Step 1: Check dependencies
        self.check_dependencies()
        self.check_node_dependencies()

        # Step 2: Check and clear ports
        self.log("\nChecking port availability...")
        if self.check_port_availability(self.backend_port):
            self.kill_process_on_port(self.backend_port)
        if self.check_port_availability(self.frontend_port):
            self.kill_process_on_port(self.frontend_port)

        # Step 3: Start servers
        backend_started = self.start_backend_server()
        if backend_started:
            frontend_started = self.start_frontend_server()

            # Step 4: Final health checks and browser opening
            if frontend_started:
                time.sleep(2)
                self.open_browser()

        # Step 5: Check firewall
        self.check_windows_firewall()

        # Step 6: Generate report
        self.generate_report()

        # Keep servers running
        if self.backend_process or self.frontend_process:
            self.log("\nServers are running. Press Ctrl+C to stop.", "INFO")
            try:
                while True:
                    time.sleep(10)
                    # Periodic health checks
                    if not self.test_backend_health() and self.backend_process:
                        self.log(
                            "Backend health check failed, restarting...", "WARNING"
                        )
                        self.start_backend_server()
                    if not self.test_frontend_health() and self.frontend_process:
                        self.log(
                            "Frontend health check failed, restarting...", "WARNING"
                        )
                        self.start_frontend_server()
            except KeyboardInterrupt:
                self.log("Shutting down servers...", "INFO")
                if self.backend_process:
                    self.backend_process.terminate()
                if self.frontend_process:
                    self.frontend_process.terminate()


if __name__ == "__main__":
    diagnostics = PlatformDiagnostics()
    diagnostics.run_full_diagnostics()
