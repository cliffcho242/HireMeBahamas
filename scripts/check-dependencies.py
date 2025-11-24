#!/usr/bin/env python3
"""
Comprehensive Dependency Installation and Verification Script
for HireMeBahamas Platform

This script:
1. Checks for missing dependencies (Python and Node.js)
2. Installs missing dependencies automatically
3. Verifies critical package imports
4. Generates a detailed dependency report

Usage:
    python3 scripts/check-dependencies.py [--backend-only|--frontend-only|--install]
"""

import sys
import subprocess
import os
import json
from pathlib import Path
from typing import List, Tuple, Dict

# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_status(status: str, message: str):
    """Print colored status message"""
    if status == "success":
        print(f"{Colors.GREEN}✓{Colors.NC} {message}")
    elif status == "error":
        print(f"{Colors.RED}✗{Colors.NC} {message}")
    elif status == "info":
        print(f"{Colors.CYAN}ℹ{Colors.NC} {message}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")

def run_command(cmd: List[str], cwd: str = None) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_python_dependencies() -> Dict[str, bool]:
    """Check if critical Python packages are available"""
    print(f"\n{Colors.YELLOW}Checking Python Dependencies...{Colors.NC}")
    
    packages = {
        'fastapi': 'FastAPI',
        'sqlalchemy': 'SQLAlchemy',
        'psycopg2': 'psycopg2-binary',
        'jose': 'python-jose',
        'passlib': 'passlib',
        'pydantic': 'Pydantic',
        'asyncpg': 'asyncpg',
        'aiosqlite': 'aiosqlite',
        'google.oauth2': 'google-auth',
        'jwt': 'PyJWT',
    }
    
    results = {}
    for module, name in packages.items():
        try:
            __import__(module)
            print_status("success", f"{name} available")
            results[name] = True
        except ImportError:
            print_status("error", f"{name} missing")
            results[name] = False
    
    return results

def check_backend_modules() -> bool:
    """Check if backend modules can be imported"""
    print(f"\n{Colors.YELLOW}Checking Backend Modules...{Colors.NC}")
    
    # Add backend to path
    backend_path = Path(__file__).parent.parent / 'backend'
    sys.path.insert(0, str(backend_path))
    
    try:
        from app.core.security import create_access_token, verify_password, get_password_hash
        print_status("success", "Security module loaded")
        
        from app.models import User, Job
        print_status("success", "Models loaded")
        
        from app.api.auth import router
        print_status("success", "Auth API loaded")
        
        return True
    except ImportError as e:
        print_status("error", f"Failed to load backend modules: {e}")
        return False

def check_frontend_dependencies() -> bool:
    """Check if frontend dependencies are installed"""
    print(f"\n{Colors.YELLOW}Checking Frontend Dependencies...{Colors.NC}")
    
    frontend_path = Path(__file__).parent.parent / 'frontend'
    package_json = frontend_path / 'package.json'
    node_modules = frontend_path / 'node_modules'
    
    if not package_json.exists():
        print_status("error", "package.json not found")
        return False
    
    print_status("success", "package.json found")
    
    if not node_modules.exists():
        print_status("warning", "node_modules not found - dependencies not installed")
        return False
    
    print_status("success", "node_modules found")
    
    # Check for critical packages
    with open(package_json, 'r') as f:
        pkg_data = json.load(f)
    
    required_packages = [
        'react',
        'react-dom',
        'react-router-dom',
        'axios',
        'react-hook-form',
        'react-hot-toast',
        '@react-oauth/google',
        'react-apple-signin-auth',
        'vite',
        'typescript'
    ]
    
    deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
    
    all_found = True
    for pkg in required_packages:
        if pkg in deps:
            print_status("success", f"{pkg} defined")
        else:
            print_status("error", f"{pkg} missing")
            all_found = False
    
    return all_found

def install_python_dependencies() -> bool:
    """Install Python dependencies"""
    print(f"\n{Colors.YELLOW}Installing Python Dependencies...{Colors.NC}")
    
    # Upgrade pip
    print_status("info", "Upgrading pip...")
    success, output = run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
    if not success:
        print_status("error", "Failed to upgrade pip")
        return False
    
    # Install test dependencies
    print_status("info", "Installing test dependencies...")
    success, output = run_command([sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-flask', 'pytest-asyncio'])
    if not success:
        print_status("warning", "Failed to install test dependencies")
    
    # Install requirements.txt
    requirements_file = Path(__file__).parent.parent / 'requirements.txt'
    if requirements_file.exists():
        print_status("info", "Installing from requirements.txt...")
        success, output = run_command([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)])
        if not success:
            print_status("error", f"Failed to install requirements.txt: {output}")
            return False
        print_status("success", "Installed requirements.txt")
    
    # Install backend requirements.txt
    backend_requirements = Path(__file__).parent.parent / 'backend' / 'requirements.txt'
    if backend_requirements.exists():
        print_status("info", "Installing from backend/requirements.txt...")
        success, output = run_command([sys.executable, '-m', 'pip', 'install', '-r', str(backend_requirements)])
        if not success:
            print_status("error", f"Failed to install backend/requirements.txt: {output}")
            return False
        print_status("success", "Installed backend/requirements.txt")
    
    return True

def install_frontend_dependencies() -> bool:
    """Install frontend Node.js dependencies"""
    print(f"\n{Colors.YELLOW}Installing Frontend Dependencies...{Colors.NC}")
    
    frontend_path = Path(__file__).parent.parent / 'frontend'
    package_lock = frontend_path / 'package-lock.json'
    
    if package_lock.exists():
        print_status("info", "Using npm ci (clean install)...")
        success, output = run_command(['npm', 'ci'], cwd=str(frontend_path))
        if not success:
            print_status("warning", "npm ci failed, trying npm install...")
            success, output = run_command(['npm', 'install'], cwd=str(frontend_path))
    else:
        print_status("info", "Using npm install...")
        success, output = run_command(['npm', 'install'], cwd=str(frontend_path))
    
    if not success:
        print_status("error", f"Failed to install frontend dependencies: {output}")
        return False
    
    print_status("success", "Frontend dependencies installed")
    return True

def generate_report(backend_ok: bool, frontend_ok: bool):
    """Generate a dependency status report"""
    print(f"\n{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.BLUE}Dependency Status Report{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}\n")
    
    print(f"Backend Dependencies: {Colors.GREEN + '✓ OK' + Colors.NC if backend_ok else Colors.RED + '✗ ISSUES' + Colors.NC}")
    print(f"Frontend Dependencies: {Colors.GREEN + '✓ OK' + Colors.NC if frontend_ok else Colors.RED + '✗ ISSUES' + Colors.NC}")
    
    if backend_ok and frontend_ok:
        print(f"\n{Colors.GREEN}{'='*50}{Colors.NC}")
        print(f"{Colors.GREEN}✓ All dependencies are satisfied!{Colors.NC}")
        print(f"{Colors.GREEN}{'='*50}{Colors.NC}\n")
    else:
        print(f"\n{Colors.RED}{'='*50}{Colors.NC}")
        print(f"{Colors.RED}✗ Some dependencies are missing or have issues{Colors.NC}")
        print(f"{Colors.RED}{'='*50}{Colors.NC}\n")
        print("Run with --install flag to attempt automatic installation:")
        print(f"  {sys.executable} {__file__} --install")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check and install HireMeBahamas dependencies')
    parser.add_argument('--backend-only', action='store_true', help='Check only backend dependencies')
    parser.add_argument('--frontend-only', action='store_true', help='Check only frontend dependencies')
    parser.add_argument('--install', action='store_true', help='Automatically install missing dependencies')
    
    args = parser.parse_args()
    
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    print(f"{Colors.BLUE}HireMeBahamas - Dependency Checker{Colors.NC}")
    print(f"{Colors.BLUE}{'='*50}{Colors.NC}")
    
    backend_ok = True
    frontend_ok = True
    
    # Check backend
    if not args.frontend_only:
        backend_deps_ok = all(check_python_dependencies().values())
        backend_modules_ok = check_backend_modules()
        backend_ok = backend_deps_ok and backend_modules_ok
        
        if not backend_ok and args.install:
            print_status("info", "Attempting to install backend dependencies...")
            install_python_dependencies()
            # Recheck after installation
            backend_deps_ok = all(check_python_dependencies().values())
            backend_modules_ok = check_backend_modules()
            backend_ok = backend_deps_ok and backend_modules_ok
    
    # Check frontend
    if not args.backend_only:
        frontend_ok = check_frontend_dependencies()
        
        if not frontend_ok and args.install:
            print_status("info", "Attempting to install frontend dependencies...")
            install_frontend_dependencies()
            # Recheck after installation
            frontend_ok = check_frontend_dependencies()
    
    # Generate report
    generate_report(backend_ok, frontend_ok)
    
    # Exit with appropriate code
    sys.exit(0 if (backend_ok and frontend_ok) else 1)

if __name__ == '__main__':
    main()
