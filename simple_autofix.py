import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import requests


def check_port(host, port):
    """Check if a port is available and responding"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            return result == 0
    except:
        return False


def test_http_endpoint(url):
    """Test HTTP endpoint with timeout"""
    try:
        response = requests.get(url, timeout=5)
        return {
            "status": "healthy" if response.status_code == 200 else "error",
            "code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
        }
    except requests.exceptions.ConnectionError:
        return {"status": "connection_refused", "code": None, "response_time": None}
    except requests.exceptions.Timeout:
        return {"status": "timeout", "code": None, "response_time": None}
    except Exception as e:
        return {"status": "error", "code": None, "response_time": None, "error": str(e)}
        color = colors.get(status, colors["INFO"])
        reset = colors["RESET"]
        timestamp = time.strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {status}: {message}{reset}")

    def check_port(self, port):
        """Check if port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(("127.0.0.1", port))
            return result == 0

    def kill_port_process(self, port):
        """Kill process using specific port (Windows)"""
        try:
            # Use Windows netstat and taskkill
            result = subprocess.run(
                f'netstat -ano | findstr ":{port}" | findstr "LISTENING"',
                shell=True,
                capture_output=True,
                text=True,
            )

            if result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        self.log(f"Killing process {pid} on port {port}", "WARNING")
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                        time.sleep(1)
                        return True
        except Exception as e:
            self.log(f"Error killing process on port {port}: {e}", "ERROR")
        return False

    def start_backend(self):
        """Start backend server"""
        self.log("Starting backend server...", "INFO")

        # Clear port if occupied
        if self.check_port(self.backend_port):
            self.log(f"Port {self.backend_port} is occupied, clearing...", "WARNING")
            self.kill_port_process(self.backend_port)
            time.sleep(2)

        try:
            backend_script = self.base_path / "final_backend.py"
            if not backend_script.exists():
                self.log("Backend script not found!", "ERROR")
                return False

            # Start backend in new window
            cmd = f'start "HireBahamas Backend" cmd /k "cd /d {self.base_path} && {self.python_exe} final_backend.py"'
            subprocess.run(cmd, shell=True)

            # Wait and test
            time.sleep(4)
            return self.test_backend()

        except Exception as e:
            self.log(f"Backend start error: {e}", "ERROR")
            return False

    def start_frontend(self):
        """Start frontend server"""
        self.log("Starting frontend server...", "INFO")

        # Clear port if occupied
        if self.check_port(self.frontend_port):
            self.log(f"Port {self.frontend_port} is occupied, clearing...", "WARNING")
            self.kill_port_process(self.frontend_port)
            time.sleep(2)

        try:
            frontend_path = self.base_path / "frontend"
            if not frontend_path.exists():
                self.log("Frontend directory not found!", "ERROR")
                return False

            # Check if node_modules exists
            if not (frontend_path / "node_modules").exists():
                self.log("Installing frontend dependencies...", "WARNING")
                subprocess.run("npm install", cwd=frontend_path, shell=True)

            # Start frontend in new window
            cmd = f'start "HireBahamas Frontend" cmd /k "cd /d {frontend_path} && npm run dev"'
            subprocess.run(cmd, shell=True)

            # Wait and test
            time.sleep(6)
            return self.test_frontend()

        except Exception as e:
            self.log(f"Frontend start error: {e}", "ERROR")
            return False

    def test_backend(self):
        """Test backend health"""
        try:
            import urllib.request

            url = f"http://127.0.0.1:{self.backend_port}/health"
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.getcode() == 200:
                    self.log("Backend health check: PASSED", "SUCCESS")
                    return True
        except Exception:
            pass

        self.log("Backend health check: FAILED", "ERROR")
        return False

    def test_frontend(self):
        """Test frontend availability"""
        try:
            import urllib.request

            url = f"http://localhost:{self.frontend_port}"
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.getcode() == 200:
                    self.log("Frontend health check: PASSED", "SUCCESS")
                    return True
        except Exception:
            pass

        self.log("Frontend health check: FAILED", "ERROR")
        return False

    def open_browser(self):
        """Open browser to application"""
        self.log("Opening browser...", "INFO")
        try:
            url = f"http://localhost:{self.frontend_port}"
            webbrowser.open(url)
            self.log("Browser opened successfully", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Browser open failed: {e}", "ERROR")
            return False

    def show_status(self):
        """Show current status"""
        self.log("=== PLATFORM STATUS ===", "INFO")

        backend_ok = self.test_backend()
        frontend_ok = self.test_frontend()

        backend_status = "RUNNING" if backend_ok else "NOT RUNNING"
        frontend_status = "RUNNING" if frontend_ok else "NOT RUNNING"

        self.log(
            f"Backend (:{self.backend_port}): {backend_status}",
            "SUCCESS" if backend_ok else "ERROR",
        )
        self.log(
            f"Frontend (:{self.frontend_port}): {frontend_status}",
            "SUCCESS" if frontend_ok else "ERROR",
        )

        if backend_ok and frontend_ok:
            self.log("All services are running!", "SUCCESS")
            self.log(
                f"Access your app at: http://localhost:{self.frontend_port}", "INFO"
            )
            self.log("Admin: admin@hirebahamas.com / AdminPass123!", "INFO")
        else:
            self.log("Some services failed to start", "WARNING")

        return backend_ok and frontend_ok

    def run_auto_fix(self):
        """Run complete auto-fix sequence"""
        self.log("HireBahamas Auto-Fix System Starting...", "INFO")
        self.log("=" * 50, "INFO")

        # Step 1: Start backend
        backend_started = self.start_backend()

        # Step 2: Start frontend (only if backend is running)
        frontend_started = False
        if backend_started:
            frontend_started = self.start_frontend()

        # Step 3: Open browser if both are running
        if backend_started and frontend_started:
            time.sleep(2)
            self.open_browser()

        # Step 4: Show final status
        self.show_status()

        # Step 5: Keep monitoring
        if backend_started or frontend_started:
            self.log("System is running. Monitoring for issues...", "INFO")
            self.log("Press Ctrl+C to stop monitoring", "INFO")

            try:
                monitor_count = 0
                while monitor_count < 60:  # Monitor for 10 minutes
                    time.sleep(10)
                    monitor_count += 1

                    # Quick health checks
                    if not self.test_backend():
                        self.log("Backend went down! Restarting...", "WARNING")
                        self.start_backend()

                    if not self.test_frontend():
                        self.log("Frontend went down! Restarting...", "WARNING")
                        self.start_frontend()

            except KeyboardInterrupt:
                self.log("Monitoring stopped by user", "INFO")

        self.log("Auto-fix complete!", "SUCCESS")


if __name__ == "__main__":
    autofix = SimpleAutoFix()
    autofix.run_auto_fix()
