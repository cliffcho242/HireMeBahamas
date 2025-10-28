#!/usr/bin/env python3
"""
PREMIUM FRONTEND FIX - Ultimate npm Directory Resolution
Automatically detects and fixes npm directory issues
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_package_json(root_dir):
    """Find package.json in the project"""
    frontend_dir = os.path.join(root_dir, "frontend")
    if os.path.exists(os.path.join(frontend_dir, "package.json")):
        return frontend_dir
    return None


def check_node_npm():
    """Check if Node.js and npm are installed"""
    npm_paths = [
        "C:\\Program Files\\nodejs\\npm.cmd",
        "C:\\Program Files (x86)\\nodejs\\npm.cmd",
        os.path.join(os.environ.get("APPDATA", ""), "npm\\npm.cmd"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "nodejs\\npm.cmd"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "nodejs\\npm.cmd"),
        "npm",  # In PATH as last resort
        "npm.cmd",  # In PATH as last resort
    ]

    npm_exe = None
    for npm_path in npm_paths:
        try:
            if os.path.exists(npm_path):
                # Test if it's actually executable
                result = subprocess.run(
                    [npm_path, "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    npm_exe = npm_path
                    print(f"✅ npm found at: {npm_exe}")
                    print(f"✅ npm version: {result.stdout.strip()}")
                    break
        except (
            FileNotFoundError,
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
        ):
            continue

    if not npm_exe:
        print("❌ npm not found or not working")
        return None

    return npm_exe


def install_dependencies(frontend_dir, npm_exe):
    """Install npm dependencies"""
    print("📦 Installing npm dependencies...")
    os.chdir(frontend_dir)

    try:
        result = subprocess.run([npm_exe, "install"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def run_npm_command(command, frontend_dir, npm_exe):
    """Run npm command from correct directory"""
    print(f"🚀 Running: {npm_exe} {command}")
    os.chdir(frontend_dir)

    try:
        # Run in background for dev server
        if command == "run dev":
            process = subprocess.Popen([npm_exe, "run", "dev"])
            print("✅ Frontend development server started")
            print("🌐 Frontend should be available at: http://localhost:3000")
            print("📝 Press Ctrl+C to stop the server")
            process.wait()
        else:
            result = subprocess.run(
                [npm_exe] + command.split(), capture_output=True, text=True
            )
            if result.returncode == 0:
                print("✅ Command executed successfully")
                return True
            else:
                print(f"❌ Command failed: {result.stderr}")
                return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def main():
    """Main premium frontend fix function"""
    print("💎 PREMIUM FRONTEND FIX")
    print("=" * 30)

    # Get current directory
    current_dir = os.getcwd()
    print(f"📍 Current directory: {current_dir}")

    # Find package.json
    frontend_dir = find_package_json(current_dir)
    if not frontend_dir:
        print("❌ Could not find package.json in frontend directory")
        print("Please ensure you're in the HireBahamas project root")
        return 1

    print(f"✅ Found frontend directory: {frontend_dir}")

    # Check Node.js and npm
    npm_exe = check_node_npm()
    if not npm_exe:
        print("❌ Node.js/npm setup required")
        return 1

    # Install dependencies if needed
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        if not install_dependencies(frontend_dir, npm_exe):
            return 1
    else:
        print("✅ Dependencies already installed")

    # Get command from arguments
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        command = "run dev"

    # Run the command
    if run_npm_command(command, frontend_dir, npm_exe):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
