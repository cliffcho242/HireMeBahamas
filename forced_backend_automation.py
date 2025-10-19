#!/usr/bin/env python3
"""
FORCED BACKEND AUTOMATION - Guaranteed to start and keep backend running
Kills conflicts, forces startup, monitors health, auto-restarts on failure
"""

import subprocess
import time
import requests
import os
import sys
import signal
import psutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('forced_backend.log')
    ]
)
logger = logging.getLogger(__name__)

class ForcedBackendManager:
    def __init__(self):
        self.backend_process = None
        self.project_dir = Path(__file__).parent
        self.backend_file = self.project_dir / "ULTIMATE_BACKEND_FIXED.py"
        self.health_url = "http://127.0.0.1:8008/health"

    def kill_python_processes(self):
        """Force kill all Python processes"""
        logger.info("🔪 Killing all Python processes...")
        try:
            # Kill by name
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True)
            subprocess.run(['taskkill', '/F', '/IM', 'python3.exe'], capture_output=True)

            # Kill by port
            try:
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if ':8008' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
            except:
                pass

            time.sleep(2)
            logger.info("✅ All Python processes killed")
        except Exception as e:
            logger.warning(f"Process killing warning: {e}")

    def clear_port(self):
        """Clear port 8008 if occupied"""
        logger.info("🧹 Clearing port 8008...")
        try:
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if ':8008' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        logger.info(f"Killing process {pid} using port 8008")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Port clearing warning: {e}")

    def test_health(self):
        """Test health endpoint"""
        try:
            response = requests.get(self.health_url, timeout=3)
            return response.status_code == 200
        except:
            return False

    def start_backend(self):
        """Start the backend server"""
        logger.info("🚀 Starting backend...")

        if not self.backend_file.exists():
            logger.error(f"❌ Backend file not found: {self.backend_file}")
            return False

        try:
            # Change to project directory
            os.chdir(self.project_dir)

            # Start backend
            self.backend_process = subprocess.Popen(
                [sys.executable, str(self.backend_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            logger.info(f"✅ Backend started with PID: {self.backend_process.pid}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start backend: {e}")
            return False

    def monitor_backend(self):
        """Monitor backend process and health"""
        logger.info("👀 Monitoring backend...")

        consecutive_failures = 0
        max_failures = 5

        while True:
            try:
                # Check if process is still running
                if self.backend_process and self.backend_process.poll() is not None:
                    logger.error("❌ Backend process died")
                    return False

                # Test health endpoint
                if self.test_health():
                    consecutive_failures = 0
                    logger.info("✅ Backend healthy")
                else:
                    consecutive_failures += 1
                    logger.warning(f"⚠️  Health check failed ({consecutive_failures}/{max_failures})")

                    if consecutive_failures >= max_failures:
                        logger.error("❌ Too many health failures, restarting...")
                        return False

                time.sleep(5)

            except KeyboardInterrupt:
                logger.info("🛑 Monitoring interrupted")
                return True
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                consecutive_failures += 1
                time.sleep(5)

    def run(self):
        """Main execution loop"""
        logger.info("🔥 FORCED BACKEND AUTOMATION STARTED")
        logger.info("=" * 50)

        while True:
            try:
                # Kill conflicts
                self.kill_python_processes()
                self.clear_port()

                # Start backend
                if not self.start_backend():
                    logger.error("❌ Failed to start backend, retrying in 5 seconds...")
                    time.sleep(5)
                    continue

                # Wait for startup
                logger.info("⏳ Waiting for backend to initialize...")
                time.sleep(3)

                # Monitor
                if not self.monitor_backend():
                    logger.warning("🔄 Backend failed, restarting...")
                    time.sleep(2)
                    continue

            except KeyboardInterrupt:
                logger.info("🛑 Forced automation stopped by user")
                self.cleanup()
                break
            except Exception as e:
                logger.error(f"❌ Automation error: {e}")
                time.sleep(5)

    def cleanup(self):
        """Clean up processes"""
        logger.info("🧹 Cleaning up...")
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                try:
                    self.backend_process.kill()
                except:
                    pass

def main():
    manager = ForcedBackendManager()
    try:
        manager.run()
    except KeyboardInterrupt:
        manager.cleanup()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        manager.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()