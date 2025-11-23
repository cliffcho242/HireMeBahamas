#!/usr/bin/env python3
"""
Automated Fix for "Failed to load user profile" Error

This script automatically installs all system dependencies (apt-get) needed 
for HireMeBahamas backend and frontend to run properly, particularly fixing 
the user profile loading issue.

Installs:
- Backend dependencies: Python, PostgreSQL, Redis, build tools, libraries
- Frontend dependencies: Node.js, npm, image optimization libraries

Usage: 
    sudo python3 automated_dependency_fix.py
    
Or run the full setup with Python dependencies:
    sudo python3 automated_dependency_fix.py --install-python-deps
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_colored(message, color=Colors.NC):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.NC}")


def run_command(command, error_message="Command failed", check=True):
    """Run a shell command and handle errors"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print_colored(f"ERROR: {error_message}", Colors.RED)
        print_colored(f"Details: {e.stderr}", Colors.RED)
        return False


def check_root():
    """Check if script is running as root"""
    if os.geteuid() != 0:
        print_colored("ERROR: This script must be run as root or with sudo", Colors.RED)
        print("Usage: sudo python3 automated_dependency_fix.py")
        sys.exit(1)


def install_system_dependencies():
    """Install all required system dependencies"""
    print_colored("=" * 60, Colors.BLUE)
    print_colored("HireMeBahamas - Automated Dependency Fix", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    print()
    
    # Update package lists
    print_colored("[1/6] Updating package lists...", Colors.YELLOW)
    if not run_command("apt-get update -y", "Failed to update package lists"):
        sys.exit(1)
    
    # Install build tools
    print()
    print_colored("[2/6] Installing build tools and Python development packages...", Colors.YELLOW)
    build_tools = [
        "build-essential",
        "gcc",
        "g++",
        "make",
        "pkg-config",
        "python3",
        "python3-pip",
        "python3-dev",
        "python3-venv",
        "python3-setuptools",
        "python3-wheel"
    ]
    if not run_command(f"apt-get install -y {' '.join(build_tools)}", "Failed to install build tools"):
        sys.exit(1)
    
    # Install database and cache
    print()
    print_colored("[3/6] Installing database and cache dependencies...", Colors.YELLOW)
    database_tools = [
        "postgresql",
        "postgresql-contrib",
        "postgresql-client",
        "libpq-dev",
        "redis-server",
        "redis-tools"
    ]
    if not run_command(f"apt-get install -y {' '.join(database_tools)}", "Failed to install database dependencies"):
        sys.exit(1)
    
    # Install security libraries
    print()
    print_colored("[4/6] Installing cryptography and security libraries...", Colors.YELLOW)
    security_libs = [
        "libssl-dev",
        "libffi-dev",
        "ca-certificates"
    ]
    if not run_command(f"apt-get install -y {' '.join(security_libs)}", "Failed to install security libraries"):
        sys.exit(1)
    
    # Install image processing libraries
    print()
    print_colored("[5/6] Installing image processing and event libraries...", Colors.YELLOW)
    image_libs = [
        "libjpeg-dev",
        "libpng-dev",
        "libtiff-dev",
        "libwebp-dev",
        "libopenjp2-7-dev",
        "zlib1g-dev",
        "libevent-dev",
        "libxml2-dev",
        "libxslt1-dev"
    ]
    if not run_command(f"apt-get install -y {' '.join(image_libs)}", "Failed to install image processing libraries"):
        sys.exit(1)
    
    # Install utilities
    print()
    print_colored("[6/8] Installing additional utilities...", Colors.YELLOW)
    utilities = [
        "curl",
        "wget",
        "git",
        "htop",
        "vim",
        "unzip"
    ]
    if not run_command(f"apt-get install -y {' '.join(utilities)}", "Failed to install utilities"):
        sys.exit(1)
    
    # Install Node.js for frontend
    print()
    print_colored("[7/8] Installing Node.js (for frontend)...", Colors.YELLOW)
    
    # Check if Node.js is already installed
    node_check = subprocess.run("command -v node", shell=True, capture_output=True)
    if node_check.returncode == 0:
        node_version = subprocess.run("node --version", shell=True, capture_output=True, text=True)
        print_colored(f"Node.js is already installed: {node_version.stdout.strip()}", Colors.GREEN)
    else:
        print_colored("Installing Node.js 18.x LTS...", Colors.YELLOW)
        # Download and run NodeSource setup script
        if not run_command("curl -fsSL https://deb.nodesource.com/setup_18.x | bash -", "Failed to setup Node.js repository"):
            print_colored("Warning: Could not setup Node.js repository", Colors.YELLOW)
        else:
            if run_command("apt-get install -y nodejs", "Failed to install Node.js"):
                node_version = subprocess.run("node --version", shell=True, capture_output=True, text=True)
                print_colored(f"Node.js installed successfully: {node_version.stdout.strip()}", Colors.GREEN)
    
    # Install frontend build dependencies (optional image optimization libraries)
    print()
    print_colored("[8/8] Installing frontend build dependencies...", Colors.YELLOW)
    frontend_libs = [
        "libvips-dev",
        "libwebp-dev",
        "libheif-dev",
        "libavif-dev"
    ]
    if not run_command(f"apt-get install -y {' '.join(frontend_libs)}", check=False):
        print_colored("Note: Some optional frontend image optimization libraries may not be available", Colors.YELLOW)
    
    print()
    print_colored("=" * 60, Colors.GREEN)
    print_colored("✅ System dependencies installed successfully!", Colors.GREEN)
    print_colored("=" * 60, Colors.GREEN)
    print()


def start_services():
    """Start PostgreSQL and Redis services"""
    print_colored("Starting PostgreSQL and Redis services...", Colors.YELLOW)
    
    # Try systemctl first, then fall back to service command
    run_command("systemctl start postgresql 2>/dev/null || service postgresql start 2>/dev/null", check=False)
    run_command("systemctl start redis-server 2>/dev/null || service redis-server start 2>/dev/null", check=False)
    
    # Enable services on boot
    print_colored("Enabling services to start on boot...", Colors.YELLOW)
    run_command("systemctl enable postgresql 2>/dev/null", check=False)
    run_command("systemctl enable redis-server 2>/dev/null", check=False)


def install_python_dependencies():
    """Install Python dependencies from requirements.txt"""
    print()
    print_colored("=" * 60, Colors.BLUE)
    print_colored("Installing Python Dependencies", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    print()
    
    repo_root = Path(__file__).parent
    
    # Upgrade pip first
    print_colored("Upgrading pip...", Colors.YELLOW)
    run_command("pip3 install --upgrade pip", check=False)
    
    # Install root requirements.txt with --ignore-installed for problematic packages
    requirements_file = repo_root / "requirements.txt"
    if requirements_file.exists():
        print_colored(f"Installing dependencies from {requirements_file}...", Colors.YELLOW)
        if not run_command(f"pip3 install --ignore-installed typing_extensions -r {requirements_file}"):
            print_colored(f"Warning: Failed to install some dependencies from {requirements_file}", Colors.YELLOW)
            print_colored("Trying with --no-deps flag for problematic packages...", Colors.YELLOW)
            run_command(f"pip3 install --no-deps -r {requirements_file}", check=False)
    
    # Install backend requirements.txt with --ignore-installed for problematic packages
    backend_requirements = repo_root / "backend" / "requirements.txt"
    if backend_requirements.exists():
        print_colored(f"Installing dependencies from {backend_requirements}...", Colors.YELLOW)
        if not run_command(f"pip3 install --ignore-installed typing_extensions -r {backend_requirements}"):
            print_colored(f"Warning: Failed to install some dependencies from {backend_requirements}", Colors.YELLOW)
            print_colored("Trying with --no-deps flag for problematic packages...", Colors.YELLOW)
            run_command(f"pip3 install --no-deps -r {backend_requirements}", check=False)
    
    print()
    print_colored("✅ Python dependencies installation completed!", Colors.GREEN)
    print()


def verify_installations():
    """Verify that key tools are installed"""
    print()
    print_colored("Verifying installations...", Colors.GREEN)
    
    # Check Python
    result = subprocess.run("python3 --version", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Python version: {result.stdout.strip()}")
    
    # Check Node.js
    result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Node.js version: {result.stdout.strip()}")
    
    # Check npm
    result = subprocess.run("npm --version", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"npm version: {result.stdout.strip()}")


def print_next_steps():
    """Print next steps for the user"""
    print()
    print_colored("=" * 60, Colors.BLUE)
    print_colored("Next Steps:", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    print()
    print("To complete the setup, run these commands:")
    print()
    print("1. Install Python dependencies:")
    print("   pip3 install -r requirements.txt")
    print("   cd backend && pip3 install -r requirements.txt")
    print()
    print("2. Install frontend Node.js dependencies:")
    print("   cd frontend && npm install")
    print()
    print("3. Configure environment variables:")
    print("   cp .env.example .env")
    print("   # Edit .env with your settings")
    print()
    print("4. Start the backend server:")
    print("   cd backend && python3 -m app.main")
    print()
    print("5. Start the frontend development server:")
    print("   cd frontend && npm run dev")
    print()
    print("6. Test the user profile endpoint:")
    print("   python3 test_user_profile_fix.py")
    print()
    print_colored("✅ All system dependencies (apt-get) installed for backend and frontend!", Colors.GREEN)
    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Automated fix for HireMeBahamas dependencies"
    )
    parser.add_argument(
        "--install-python-deps",
        action="store_true",
        help="Also install Python dependencies from requirements.txt"
    )
    parser.add_argument(
        "--skip-services",
        action="store_true",
        help="Skip starting PostgreSQL and Redis services"
    )
    
    args = parser.parse_args()
    
    # Check if running as root
    check_root()
    
    # Install system dependencies
    install_system_dependencies()
    
    # Start services
    if not args.skip_services:
        start_services()
    
    # Install Python dependencies if requested
    if args.install_python_deps:
        install_python_dependencies()
    
    # Verify installations
    verify_installations()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
