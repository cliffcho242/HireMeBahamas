#!/usr/bin/env python3
"""
HireMeBahamas - Application Operational Test Suite
This script tests that all dependencies are installed and the app is operational.
"""

import subprocess
import sys
import importlib
from pathlib import Path

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_section(message):
    """Print a section header"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{message:^60}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")


def print_success(message):
    """Print a success message"""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print an error message"""
    print(f"{RED}✗ {message}{RESET}")


def print_warning(message):
    """Print a warning message"""
    print(f"{YELLOW}⚠ {message}{RESET}")


def check_python_package(package_name):
    """Check if a Python package is installed"""
    try:
        importlib.import_module(package_name.replace("-", "_"))
        return True
    except ImportError:
        return False


def test_system_commands():
    """Test that required system commands are available"""
    print_section("Testing System Commands")
    
    commands = {
        "python3": "Python 3",
        "pip": "pip package manager",
        "node": "Node.js",
        "npm": "npm package manager",
        "git": "Git version control",
        "psql": "PostgreSQL client",
        "redis-cli": "Redis client",
    }
    
    all_passed = True
    for cmd, description in commands.items():
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                print_success(f"{description}: {version}")
            else:
                print_error(f"{description} not found")
                all_passed = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print_error(f"{description} not found")
            all_passed = False
    
    return all_passed


def test_python_dependencies():
    """Test that all required Python packages are installed"""
    print_section("Testing Python Dependencies")
    
    # Core packages from requirements.txt
    packages = [
        ("flask", "Flask web framework"),
        ("flask_cors", "Flask-CORS"),
        ("flask_limiter", "Flask-Limiter"),
        ("flask_caching", "Flask-Caching"),
        ("werkzeug", "Werkzeug"),
        ("jwt", "PyJWT"),
        ("bcrypt", "bcrypt"),
        ("flask_talisman", "flask-talisman"),
        ("cryptography", "cryptography"),
        ("psycopg2", "psycopg2-binary"),
        ("aiosqlite", "aiosqlite"),
        ("flask_sqlalchemy", "Flask-SQLAlchemy"),
        ("flask_migrate", "Flask-Migrate"),
        ("sentry_sdk", "sentry-sdk"),
        ("flask_compress", "flask-compress"),
        ("redis", "redis"),
        ("flask_socketio", "flask-socketio"),
        ("socketio", "python-socketio"),
        ("engineio", "python-engineio"),
        ("marshmallow", "marshmallow"),
        ("email_validator", "email-validator"),
        ("celery", "celery"),
        ("flower", "flower"),
        ("dotenv", "python-dotenv"),
        ("gunicorn", "gunicorn"),
        ("waitress", "waitress"),
        ("requests", "requests"),
        ("gevent", "gevent"),
    ]
    
    all_passed = True
    for package, description in packages:
        if check_python_package(package):
            print_success(f"{description}")
        else:
            print_error(f"{description} not installed")
            all_passed = False
    
    return all_passed


def test_frontend_dependencies():
    """Test that frontend dependencies are installed"""
    print_section("Testing Frontend Dependencies")
    
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print_error("Frontend directory not found")
        return False
    
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print_error("node_modules not found - run 'npm install' in frontend directory")
        return False
    
    print_success("node_modules directory exists")
    
    # Check for key packages
    key_packages = [
        "react",
        "react-dom",
        "react-router-dom",
        "axios",
        "vite",
        "typescript",
        "tailwindcss",
    ]
    
    all_passed = True
    for package in key_packages:
        package_dir = node_modules / package
        if package_dir.exists():
            print_success(f"{package}")
        else:
            print_error(f"{package} not installed")
            all_passed = False
    
    return all_passed


def test_backend_import():
    """Test that the backend can be imported"""
    print_section("Testing Backend Import")
    
    try:
        # Try to import the main backend module
        import final_backend_postgresql
        print_success("Backend module imports successfully")
        print_success("Flask app initialized")
        return True
    except Exception as e:
        print_error(f"Backend import failed: {e}")
        return False


def test_frontend_build():
    """Test that the frontend can be built"""
    print_section("Testing Frontend Build")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_error("Frontend directory not found")
        return False
    
    try:
        # Check if we can run the TypeScript compiler
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print_success("Frontend builds successfully")
            dist_dir = frontend_dir / "dist"
            if dist_dir.exists():
                print_success(f"Build output created in {dist_dir}")
            return True
        else:
            print_error("Frontend build failed")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print_error("Frontend build timed out")
        return False
    except Exception as e:
        print_error(f"Frontend build test failed: {e}")
        return False


def test_database_connectivity():
    """Test database connectivity"""
    print_section("Testing Database Connectivity")
    
    # Test SQLite (development)
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()
        if result[0] == 1:
            print_success("SQLite connectivity OK")
    except Exception as e:
        print_error(f"SQLite test failed: {e}")
        return False
    
    # Test PostgreSQL availability (optional)
    try:
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("PostgreSQL client available")
    except Exception:
        print_warning("PostgreSQL client not available (optional)")
    
    # Test Redis availability (optional)
    try:
        result = subprocess.run(
            ["redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "PONG" in result.stdout:
            print_success("Redis server responding")
        else:
            print_warning("Redis server not responding (optional for development)")
    except Exception:
        print_warning("Redis not available (optional for development)")
    
    return True


def main():
    """Run all tests"""
    print_section("HireMeBahamas - Application Operational Test")
    print("Testing all dependencies and functionality...\n")
    
    results = {
        "System Commands": test_system_commands(),
        "Python Dependencies": test_python_dependencies(),
        "Frontend Dependencies": test_frontend_dependencies(),
        "Backend Import": test_backend_import(),
        "Database Connectivity": test_database_connectivity(),
    }
    
    # Note: Frontend build test is slow, so it's optional
    print("\n" + "=" * 60)
    print(f"\n{BLUE}Optional Tests (may take time):{RESET}\n")
    print("Run 'npm run build' in frontend directory to test frontend build")
    
    # Print summary
    print_section("Test Summary")
    
    all_passed = True
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            all_passed = False
    
    print("\n" + "=" * 60 + "\n")
    
    if all_passed:
        print(f"{GREEN}✓ All tests passed! Application is ready to run.{RESET}\n")
        print("Next steps:")
        print("  1. Copy .env.example to .env and configure")
        print("  2. Start backend: python final_backend_postgresql.py")
        print("  3. Start frontend: cd frontend && npm run dev")
        print("  4. Open http://localhost:3000 in your browser\n")
        return 0
    else:
        print(f"{RED}✗ Some tests failed. Please review the errors above.{RESET}\n")
        print("To install dependencies, run:")
        print("  ./install_dependencies.sh\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
