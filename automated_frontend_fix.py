#!/usr/bin/env python3
"""
Automated Frontend Fix for HireBahamas
Handles Node.js/npm setup and frontend development server
"""

import os
import sys
import subprocess
import time
import signal
import threading

def run_command(cmd, cwd=None, shell=False):
    """Run a command and return the result"""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=300)
        else:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_nodejs():
    """Check if Node.js and npm are available"""
    print("Checking Node.js installation...")

    # Check node
    success, stdout, stderr = run_command("node --version")
    if success:
        print(f"Node.js found: {stdout.strip()}")
    else:
        print("Node.js not found")
        return False

    # Check npm - try multiple ways
    npm_paths = [
        "npm",
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd"
    ]

    for npm_path in npm_paths:
        success, stdout, stderr = run_command([npm_path, "--version"])
        if success:
            print(f"npm found: {stdout.strip()}")
            return True

    print("npm not found in PATH or common locations")
    print("Will try to use explicit npm path for commands")
    return True  # Node.js is available, we'll handle npm path issues in individual commands

def install_nodejs():
    """Install Node.js automatically"""
    print("Installing Node.js automatically...")

    # Run the Node.js installer script
    installer_script = os.path.join(os.path.dirname(__file__), "automate_nodejs_fix.py")
    if not os.path.exists(installer_script):
        print(f"Node.js installer not found: {installer_script}")
        return False

    success, stdout, stderr = run_command([sys.executable, installer_script])
    if success:
        print("Node.js installed successfully")
        return True
    else:
        print(f"Node.js installation failed: {stderr}")
        return False

def ensure_nodejs():
    """Ensure Node.js is installed and available"""
    if not check_nodejs():
        print("Node.js not found. Installing automatically...")
        if not install_nodejs():
            print("Failed to install Node.js automatically")
            print("Please install Node.js manually from https://nodejs.org")
            return False

        # Check again after installation
        if not check_nodejs():
            print("Node.js installation verification failed")
            return False

    return True

def check_frontend_setup():
    """Check if frontend is properly set up"""
    print("Checking frontend setup...")

    # Check if frontend directory exists
    if not os.path.exists('frontend'):
        print("frontend directory not found!")
        return False

    # Check if package.json exists in frontend directory
    frontend_package = os.path.join('frontend', 'package.json')
    if not os.path.exists(frontend_package):
        print("package.json not found in frontend directory!")
        return False

    print("Frontend directory and package.json found")
    return True

def install_dependencies():
    """Install npm dependencies"""
    print("Installing npm dependencies...")

    # Change to frontend directory
    frontend_dir = os.path.join(os.getcwd(), 'frontend')
    if not os.path.exists(frontend_dir):
        print("Frontend directory not found")
        return False

    # Try different npm paths
    npm_paths = [
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd",
        "npm"
    ]

    npm_cmd = None
    for path in npm_paths:
        if os.path.exists(path) or path == "npm":
            npm_cmd = path
            break

    if not npm_cmd:
        print("npm not found. Please install Node.js from https://nodejs.org")
        return False

    success, stdout, stderr = run_command([npm_cmd, 'install'], cwd=frontend_dir)
    if success:
        print("Dependencies installed successfully")
        return True
    else:
        print(f"Failed to install dependencies: {stderr}")
        return False

def start_frontend_server():
    """Start the frontend development server"""
    print("Starting frontend development server...")

    # Get frontend directory
    frontend_dir = os.path.join(os.getcwd(), 'frontend')
    if not os.path.exists(frontend_dir):
        print("Frontend directory not found")
        return False

    # Find npm command
    npm_paths = [
        r"C:\Program Files\nodejs\npm.cmd",
        r"C:\Program Files (x86)\nodejs\npm.cmd",
        "npm"
    ]

    npm_cmd = None
    for path in npm_paths:
        if os.path.exists(path) or path == "npm":
            npm_cmd = path
            break

    if not npm_cmd:
        print("npm not found. Please install Node.js")
        return False

    try:
        # Start npm run dev in background from frontend directory
        process = subprocess.Popen([npm_cmd, 'run', 'dev'],
                                 cwd=frontend_dir,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)

        print("Frontend server started successfully")
        print("Frontend should be available at: http://localhost:3000")
        print("Press Ctrl+C to stop the server")

        # Wait for the process
        process.wait()

    except KeyboardInterrupt:
        print("\nFrontend server stopped by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"Failed to start frontend server: {e}")
        return False

    return True

def start_backend_server():
    """Start the backend server"""
    print("Starting backend server...")

    # Go back to root directory
    root_dir = os.path.dirname(os.getcwd())
    os.chdir(root_dir)

    try:
        # Start backend in background
        backend_process = subprocess.Popen([sys.executable, 'final_backend.py'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True)

        print("Backend server started successfully")
        print("Backend API available at: http://127.0.0.1:8008")

        # Give backend time to start
        time.sleep(3)

        return backend_process

    except Exception as e:
        print(f"Failed to start backend server: {e}")
        return None

def main():
    """Main automated frontend fix function"""
    print("AUTOMATED FRONTEND FIX")
    print("=" * 30)

    # Ensure Node.js is installed
    if not ensure_nodejs():
        return 1

    # Store the root directory
    root_dir = os.getcwd()

    # Check if AUTOMATE argument is provided
    automate = len(sys.argv) > 1 and sys.argv[1].upper() == 'AUTOMATE'

    # Check frontend setup
    if not check_frontend_setup():
        return 1

    # Install dependencies
    if not install_dependencies():
        return 1

    if automate:
        print("AUTOMATE mode: Starting both frontend and backend...")

        # Start backend first (from root directory)
        os.chdir(root_dir)
        backend_process = start_backend_server()
        if not backend_process:
            return 1

        # Go back to frontend directory
        frontend_dir = os.path.join(root_dir, 'frontend')
        if os.path.exists(frontend_dir):
            os.chdir(frontend_dir)
        else:
            print(f"Frontend directory not found: {frontend_dir}")
            return 1

        # Start frontend
        try:
            start_frontend_server()
        finally:
            # Clean up backend process
            if backend_process:
                print("Stopping backend server...")
                backend_process.terminate()

    else:
        print("Starting frontend server only...")
        start_frontend_server()

    return 0


if __name__ == '__main__':
    sys.exit(main())
