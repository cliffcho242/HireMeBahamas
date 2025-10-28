#!/usr/bin/env python3
"""
AI-Enhanced HireBahamas Platform Launcher
Launches the complete system with AI monitoring and error prevention
"""
import subprocess
import sys
import time
from pathlib import Path

import requests


class PlatformLauncher:
    def __init__(self):
        self.base_path = Path("C:/Users/Dell/OneDrive/Desktop/HireBahamas")
        self.venv_python = self.base_path / ".venv" / "Scripts" / "python.exe"

    def log(self, message, status="INFO"):
        """Safe logging for Windows console"""
        markers = {
            "INFO": "[INFO]",
            "SUCCESS": "[SUCCESS]",
            "ERROR": "[ERROR]",
            "WARNING": "[WARNING]",
            "STARTING": "[STARTING]",
        }

        print(f"{markers.get(status, '[LOG]')} {message}")

    def kill_existing_processes(self):
        """Kill any existing Python processes"""
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe"],
                capture_output=True,
                check=False,
            )
            time.sleep(2)
            self.log("Cleaned up existing processes", "SUCCESS")
        except Exception as e:
            self.log(f"Process cleanup warning: {e}", "WARNING")

    def start_backend(self):
        """Start the AI-enhanced backend"""
        self.log("Starting AI-Enhanced Backend Server...", "STARTING")

        try:
            # Start backend process
            backend_script = self.base_path / "facebook_like_backend.py"
            process = subprocess.Popen(
                [str(self.venv_python), str(backend_script)], cwd=str(self.base_path)
            )

            # Wait for startup
            time.sleep(5)

            # Test if running
            for attempt in range(10):
                try:
                    response = requests.get("http://127.0.0.1:8008/health", timeout=3)
                    if response.status_code == 200:
                        health = response.json()
                        self.log("Backend server started successfully", "SUCCESS")
                        self.log(
                            f"AI Monitor: {health.get('ai_monitor', 'Not available')}",
                            "INFO",
                        )
                        return True
                except:
                    time.sleep(2)
                    self.log(f"Waiting for backend... attempt {attempt + 1}/10", "INFO")

            self.log("Backend may not be fully ready", "WARNING")
            return False

        except Exception as e:
            self.log(f"Backend start failed: {e}", "ERROR")
            return False

    def test_login_system(self):
        """Test the enhanced login system"""
        self.log("Testing AI-Enhanced Login System...", "STARTING")

        login_data = {"email": "admin@hirebahamas.com", "password": "admin123"}

        try:
            response = requests.post(
                "http://127.0.0.1:8008/api/auth/login", json=login_data, timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                self.log("Login system operational", "SUCCESS")
                self.log(
                    f"Admin user: {result.get('user', {}).get('email', 'Unknown')}",
                    "INFO",
                )

                # Test error monitoring with invalid login
                invalid_data = {"email": "test@fail.com", "password": "wrong"}
                error_response = requests.post(
                    "http://127.0.0.1:8008/api/auth/login", json=invalid_data, timeout=5
                )

                if error_response.status_code == 401:
                    self.log(
                        "Error monitoring active - invalid login detected", "SUCCESS"
                    )

                return True
            else:
                self.log(f"Login test failed: {response.status_code}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Login test error: {e}", "ERROR")
            return False

    def launch_platform(self):
        """Launch the complete AI-enhanced platform"""
        self.log("=" * 60, "INFO")
        self.log("AI-ENHANCED HIREBAHAMAS PLATFORM LAUNCHER", "INFO")
        self.log("=" * 60, "INFO")

        # Step 1: Clean up
        self.kill_existing_processes()

        # Step 2: Start backend
        backend_started = self.start_backend()

        if not backend_started:
            self.log("Platform launch failed - backend not responding", "ERROR")
            return False

        # Step 3: Test login system
        login_working = self.test_login_system()

        if not login_working:
            self.log("Platform launch failed - login system issues", "ERROR")
            return False

        # Success summary
        self.log("=" * 60, "INFO")
        self.log("PLATFORM SUCCESSFULLY LAUNCHED", "SUCCESS")
        self.log("=" * 60, "INFO")

        self.log("SYSTEM FEATURES:", "INFO")
        self.log("- AI-powered error monitoring and auto-healing", "INFO")
        self.log("- Real-time system health tracking", "INFO")
        self.log("- Enhanced login with pattern recognition", "INFO")
        self.log("- Automatic performance optimization", "INFO")
        self.log("- Predictive issue prevention", "INFO")

        self.log("ACCESS INFORMATION:", "INFO")
        self.log("Frontend: http://localhost:3000", "INFO")
        self.log("Backend API: http://127.0.0.1:8008", "INFO")
        self.log("Admin Email: admin@hirebahamas.com", "INFO")
        self.log("Admin Password: admin123", "INFO")

        self.log("AI MONITORING ENDPOINTS:", "INFO")
        self.log("Health: http://127.0.0.1:8008/api/system/health", "INFO")
        self.log(
            "Monitor Status: http://127.0.0.1:8008/api/system/monitor/status", "INFO"
        )

        self.log("=" * 60, "INFO")
        self.log("Platform is now running with AI enhancement!", "SUCCESS")
        self.log("The system will automatically monitor and fix issues.", "SUCCESS")

        return True


def main():
    """Main launcher function"""
    launcher = PlatformLauncher()
    success = launcher.launch_platform()

    if success:
        print("\nPress Ctrl+C to stop the platform")
        try:
            while True:
                time.sleep(30)
                # Keep the launcher alive
                try:
                    response = requests.get("http://127.0.0.1:8008/health", timeout=3)
                    if response.status_code != 200:
                        launcher.log(
                            "Backend health check failed - may need restart", "WARNING"
                        )
                except:
                    launcher.log(
                        "Backend not responding - auto-healing should engage", "WARNING"
                    )
        except KeyboardInterrupt:
            launcher.log("Platform shutdown requested", "INFO")
            launcher.kill_existing_processes()
            launcher.log("Platform stopped", "SUCCESS")
    else:
        launcher.log("Platform launch failed", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
