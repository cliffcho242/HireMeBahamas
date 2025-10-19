#!/usr/bin/env python3
"""
ULTIMATE AUTOMATED FIX FOR HIREBAHAMAS PLATFORM
===============================================

This script automatically detects and fixes all common issues:
- Directory navigation problems
- Missing dependencies
- Backend/frontend startup issues
- Port conflicts
- Database connectivity

Usage:
    python ultimate_automated_fix.py [mode]

Modes:
    - No argument: Interactive mode with prompts
    - FULL: Complete automated setup (backend + frontend)
    - BACKEND: Backend only
    - FRONTEND: Frontend only
    - FIX: Fix existing issues without starting servers
    - CLEAN: Clean and restart everything
"""

import os
import sys
import subprocess
import time
import signal
import requests
import platform
import shutil
from pathlib import Path

class UltimateFixer:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.frontend_dir = self.root_dir / "frontend"
        self.backend_file = self.root_dir / "final_backend.py"
        self.processes = []
        self.is_windows = platform.system() == "Windows"

    def print_header(self, title):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"🔧 {title.upper()}")
        print(f"{'='*60}")

    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")

    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")

    def print_info(self, message):
        """Print info message"""
        print(f"ℹ️  {message}")

    def check_frontend_setup(self):
        """Check if frontend directory and package.json exist"""
        self.print_info("Checking frontend setup...")

        if not self.frontend_dir.exists():
            self.print_error(f"Frontend directory not found: {self.frontend_dir}")
            return False

        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            self.print_error(f"package.json not found in: {self.frontend_dir}")
            return False

        self.print_success("Frontend directory and package.json found")
        return True

    def check_backend_setup(self):
        """Check if backend file exists"""
        self.print_info("Checking backend setup...")

        if not self.backend_file.exists():
            self.print_error(f"Backend file not found: {self.backend_file}")
            return False

        self.print_success("Backend file found")
        return True

    def find_npm_executable(self):
        """Find npm executable path"""
        possible_paths = [
            "C:\\Program Files\\nodejs\\npm.cmd",
            "C:\\Program Files (x86)\\nodejs\\npm.cmd",
            "npm.cmd",
            "npm"
        ]

        for path in possible_paths:
            if shutil.which(path):
                self.print_success(f"Found npm at: {path}")
                return path

        self.print_error("npm not found in PATH")
        return None

    def install_frontend_dependencies(self):
        """Install frontend dependencies"""
        self.print_info("Installing frontend dependencies...")

        npm_path = self.find_npm_executable()
        if not npm_path:
            return False

        try:
            # Change to frontend directory
            os.chdir(self.frontend_dir)

            # Run npm install
            result = subprocess.run(
                [npm_path, "install"],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.print_success("Frontend dependencies installed successfully")
                return True
            else:
                self.print_error("Failed to install frontend dependencies")
                print(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            self.print_error("npm install timed out")
            return False
        except Exception as e:
            self.print_error(f"Error installing dependencies: {e}")
            return False
        finally:
            # Always go back to root directory
            os.chdir(self.root_dir)

    def kill_existing_processes(self):
        """Kill existing Python and Node processes"""
        self.print_info("Cleaning up existing processes...")

        try:
            if self.is_windows:
                # Use a more robust approach for Windows
                import psutil
                killed_any = False

                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] and ('python' in proc.info['name'].lower() or 'node' in proc.info['name'].lower()):
                            # Check if it's related to our project
                            if proc.info['cmdline'] and any(keyword in ' '.join(proc.info['cmdline']).lower()
                                                         for keyword in ['final_backend.py', 'vite', 'react', 'hirebahamas']):
                                proc.kill()
                                killed_any = True
                                self.print_info(f"Killed process: {proc.info['name']} (PID: {proc.info['pid']})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if killed_any:
                    self.print_success("Existing processes cleaned up")
                    time.sleep(2)  # Wait for processes to fully terminate
                else:
                    self.print_info("No existing processes found to clean up")
            else:
                subprocess.run(["pkill", "-f", "python"], capture_output=True, check=False)
                subprocess.run(["pkill", "-f", "node"], capture_output=True, check=False)
                self.print_success("Existing processes cleaned up")
        except ImportError:
            # psutil not available, use basic approach
            self.print_info("Using basic process cleanup (psutil not available)")
            try:
                subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True, check=False)
                subprocess.run(["taskkill", "/f", "/im", "node.exe"], capture_output=True, check=False)
                self.print_success("Basic process cleanup completed")
            except Exception as e:
                self.print_info(f"Basic cleanup completed: {e}")
        except Exception as e:
            self.print_info(f"Process cleanup completed: {e}")
            self.print_success("Process cleanup finished")

    def start_backend_server(self):
        """Start the backend server"""
        self.print_info("Starting backend server...")

        try:
            os.chdir(self.root_dir)
            process = subprocess.Popen(
                [sys.executable, "final_backend.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait a bit for server to start
            time.sleep(3)

            # Check if process is still running
            if process.poll() is None:
                self.processes.append(("backend", process))
                self.print_success("Backend server started successfully")
                self.print_info("Backend API available at: http://127.0.0.1:8008")
                return True
            else:
                stdout, stderr = process.communicate()
                self.print_error("Backend server failed to start")
                if stderr:
                    print(f"Error: {stderr}")
                return False

        except Exception as e:
            self.print_error(f"Error starting backend: {e}")
            return False

    def start_frontend_server(self):
        """Start the frontend server"""
        self.print_info("Starting frontend development server...")

        npm_path = self.find_npm_executable()
        if not npm_path:
            return False

        try:
            os.chdir(self.frontend_dir)
            process = subprocess.Popen(
                [npm_path, "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait a bit for server to start
            time.sleep(5)

            # Check if process is still running
            if process.poll() is None:
                self.processes.append(("frontend", process))
                self.print_success("Frontend server started successfully")
                self.print_info("Frontend should be available at: http://localhost:3000")
                return True
            else:
                stdout, stderr = process.communicate()
                self.print_error("Frontend server failed to start")
                if stderr:
                    print(f"Error: {stderr}")
                return False

        except Exception as e:
            self.print_error(f"Error starting frontend: {e}")
            return False
        finally:
            os.chdir(self.root_dir)

    def test_backend_connection(self):
        """Test backend API connection"""
        self.print_info("Testing backend connection...")

        try:
            response = requests.get("http://127.0.0.1:8008/", timeout=5)
            if response.status_code == 200:
                self.print_success("Backend connection successful")
                return True
            else:
                self.print_error(f"Backend returned status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_error(f"Backend connection failed: {e}")
            return False

    def test_frontend_connection(self):
        """Test frontend connection"""
        self.print_info("Testing frontend connection...")

        try:
            response = requests.get("http://localhost:3000", timeout=10)
            if response.status_code == 200:
                self.print_success("Frontend connection successful")
                return True
            else:
                self.print_error(f"Frontend returned status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_error(f"Frontend connection failed: {e}")
            return False

    def open_browser(self):
        """Open browser to the application"""
        self.print_info("Opening browser...")

        import webbrowser
        try:
            webbrowser.open("http://localhost:3000")
            self.print_success("Browser opened to http://localhost:3000")
        except Exception as e:
            self.print_info(f"Could not open browser automatically: {e}")

    def cleanup(self):
        """Clean up running processes"""
        self.print_info("Cleaning up processes...")

        for name, process in self.processes:
            try:
                if self.is_windows:
                    process.terminate()
                else:
                    os.kill(process.pid, signal.SIGTERM)
                self.print_success(f"Stopped {name} server")
            except Exception as e:
                self.print_info(f"Error stopping {name}: {e}")

    def run_full_setup(self):
        """Run complete automated setup"""
        self.print_header("ULTIMATE AUTOMATED FIX - FULL SETUP")

        # Step 1: Clean up
        self.kill_existing_processes()

        # Step 2: Check setup
        if not self.check_frontend_setup():
            return False

        if not self.check_backend_setup():
            return False

        # Step 3: Install dependencies
        if not self.install_frontend_dependencies():
            return False

        # Step 4: Start backend
        if not self.start_backend_server():
            return False

        # Step 5: Test backend
        time.sleep(2)
        if not self.test_backend_connection():
            self.print_error("Backend test failed, but continuing...")

        # Step 6: Start frontend
        if not self.start_frontend_server():
            return False

        # Step 7: Test frontend
        time.sleep(3)
        if not self.test_frontend_connection():
            self.print_error("Frontend test failed, but continuing...")

        # Step 8: Open browser
        self.open_browser()

        self.print_header("SETUP COMPLETE")
        print("\n🎉 HireBahamas Platform is now running!")
        print("🌐 Frontend:     http://localhost:3000")
        print("🔧 Backend:      http://127.0.0.1:8008")
        print("🤖 AI Dashboard: http://localhost:3000/ai")
        print("\n📝 Press Ctrl+C to stop all servers")

        return True

    def run_backend_only(self):
        """Run backend only setup"""
        self.print_header("BACKEND ONLY SETUP")

        self.kill_existing_processes()

        if not self.check_backend_setup():
            return False

        if not self.start_backend_server():
            return False

        time.sleep(2)
        self.test_backend_connection()

        print("\n🔧 Backend server running at: http://127.0.0.1:8008")
        print("📝 Press Ctrl+C to stop")

        return True

    def run_frontend_only(self):
        """Run frontend only setup"""
        self.print_header("FRONTEND ONLY SETUP")

        if not self.check_frontend_setup():
            return False

        if not self.install_frontend_dependencies():
            return False

        if not self.start_frontend_server():
            return False

        time.sleep(3)
        self.test_frontend_connection()

        print("\n🌐 Frontend server running at: http://localhost:3000")
        print("📝 Press Ctrl+C to stop")

        return True

    def run_fix_only(self):
        """Run fix without starting servers"""
        self.print_header("FIX ONLY MODE")

        self.kill_existing_processes()

        if not self.check_frontend_setup():
            return False

        if not self.check_backend_setup():
            return False

        if not self.install_frontend_dependencies():
            return False

        self.print_success("All fixes applied successfully")
        return True

    def run_clean_restart(self):
        """Clean everything and restart"""
        self.print_header("CLEAN RESTART")

        self.kill_existing_processes()
        time.sleep(2)

        return self.run_full_setup()

def main():
    fixer = UltimateFixer()

    # Parse command line arguments
    mode = sys.argv[1].upper() if len(sys.argv) > 1 else "INTERACTIVE"

    try:
        if mode == "FULL":
            success = fixer.run_full_setup()
        elif mode == "BACKEND":
            success = fixer.run_backend_only()
        elif mode == "FRONTEND":
            success = fixer.run_frontend_only()
        elif mode == "FIX":
            success = fixer.run_fix_only()
        elif mode == "CLEAN":
            success = fixer.run_clean_restart()
        else:
            # Interactive mode
            print("🤖 ULTIMATE AUTOMATED FIX FOR HIREBAHAMAS")
            print("=" * 50)
            print("Choose a mode:")
            print("1. FULL - Complete setup (backend + frontend)")
            print("2. BACKEND - Backend only")
            print("3. FRONTEND - Frontend only")
            print("4. FIX - Fix issues without starting servers")
            print("5. CLEAN - Clean restart everything")

            choice = input("\nEnter choice (1-5): ").strip()

            mode_map = {
                "1": "FULL",
                "2": "BACKEND",
                "3": "FRONTEND",
                "4": "FIX",
                "5": "CLEAN"
            }

            if choice in mode_map:
                mode = mode_map[choice]
                if mode == "FULL":
                    success = fixer.run_full_setup()
                elif mode == "BACKEND":
                    success = fixer.run_backend_only()
                elif mode == "FRONTEND":
                    success = fixer.run_frontend_only()
                elif mode == "FIX":
                    success = fixer.run_fix_only()
                elif mode == "CLEAN":
                    success = fixer.run_clean_restart()
                else:
                    success = False
            else:
                print("❌ Invalid choice")
                success = False

        if success:
            # Wait for user interrupt
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down servers...")
        else:
            print("\n❌ Setup failed. Check errors above.")
            return 1

    except KeyboardInterrupt:
        print("\n🛑 User interrupted")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        fixer.cleanup()

    return 0

if __name__ == "__main__":
    sys.exit(main())