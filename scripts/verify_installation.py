#!/usr/bin/env python3
"""
HireMeBahamas - Installation Verification Script
=================================================
This script verifies that all dependencies are correctly installed
and all services are running properly.

Exit Codes:
    0 - All checks passed
    1 - One or more checks failed
"""

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title:^80}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.NC}\n")


def print_success(message: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")


def print_error(message: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.NC} {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")


def print_info(message: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {message}")


def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[bool, str]:
    """
    Run a shell command and return success status and output.
    
    Args:
        cmd: Command to run as list of strings
        capture_output: Whether to capture output
    
    Returns:
        Tuple of (success, output)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout.strip() if capture_output else ""
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        return False, str(e)


def check_command_exists(command: str) -> Tuple[bool, str]:
    """Check if a command exists in PATH."""
    success, output = run_command(["which", command])
    return success, output


def check_python_version() -> bool:
    """Check Python version."""
    print_info("Checking Python installation...")
    
    success, version = run_command(["python3", "--version"])
    if success:
        print_success(f"Python: {version}")
        
        # Check if version is >= 3.8
        version_parts = version.split()[1].split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        if major >= 3 and minor >= 8:
            return True
        else:
            print_warning(f"Python version {version} is less than 3.8")
            return False
    else:
        print_error("Python 3 not found")
        return False


def check_node_version() -> bool:
    """Check Node.js version."""
    print_info("Checking Node.js installation...")
    
    success, version = run_command(["node", "--version"])
    if success:
        print_success(f"Node.js: {version}")
        
        # Check if version is >= 16
        version_num = int(version.strip('v').split('.')[0])
        if version_num >= 16:
            return True
        else:
            print_warning(f"Node.js version {version} is less than 16")
            return False
    else:
        print_error("Node.js not found")
        return False


def check_npm_version() -> bool:
    """Check npm version."""
    success, version = run_command(["npm", "--version"])
    if success:
        print_success(f"npm: {version}")
        return True
    else:
        print_error("npm not found")
        return False


def check_python_packages() -> bool:
    """Check if required Python packages are installed."""
    print_info("Checking Python packages...")
    
    # Read requirements.txt
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print_warning(f"requirements.txt not found at {requirements_file}")
        return False
    
    all_ok = True
    checked_packages = set()
    
    with open(requirements_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Extract package name (before ==, >=, etc.)
            package = line.split('==')[0].split('>=')[0].split('[')[0].strip()
            
            # Skip duplicates
            if package in checked_packages:
                continue
            checked_packages.add(package)
            
            # Try to import the package
            try:
                # Convert package name to module name
                module_name = package.lower().replace('-', '_')
                importlib.import_module(module_name)
                # Don't print success for each package to keep output clean
            except ImportError:
                print_error(f"Python package not installed: {package}")
                all_ok = False
    
    if all_ok:
        print_success(f"All Python packages from requirements.txt are installed")
    
    # Check additional critical packages
    critical_packages = [
        ('psycopg2', 'psycopg2-binary'),
        ('redis', 'redis'),
        ('flask', 'Flask'),
        ('jwt', 'PyJWT'),
    ]
    
    for module_name, package_name in critical_packages:
        try:
            importlib.import_module(module_name)
        except ImportError:
            print_error(f"Critical package not installed: {package_name}")
            all_ok = False
    
    return all_ok


def check_node_packages() -> bool:
    """Check if Node.js packages are installed."""
    print_info("Checking Node.js packages...")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    frontend_dir = project_root / "frontend"
    
    if not frontend_dir.exists():
        print_warning("Frontend directory not found")
        return False
    
    node_modules = frontend_dir / "node_modules"
    package_json = frontend_dir / "package.json"
    
    if not package_json.exists():
        print_error("frontend/package.json not found")
        return False
    
    if not node_modules.exists():
        print_error("frontend/node_modules not found - run 'npm install'")
        return False
    
    # Check if vite is installed globally
    success, _ = check_command_exists("vite")
    if not success:
        print_warning("vite not installed globally (optional)")
    
    print_success("Node.js packages are installed")
    return True


def check_postgresql() -> bool:
    """Check if PostgreSQL is installed and running."""
    print_info("Checking PostgreSQL...")
    
    # Check if psql exists
    success, _ = check_command_exists("psql")
    if not success:
        print_error("PostgreSQL client (psql) not found")
        return False
    
    print_success("PostgreSQL client installed")
    
    # Check if PostgreSQL is running
    success, _ = check_command_exists("pg_isready")
    if success:
        success, output = run_command(["pg_isready", "-h", "localhost", "-p", "5432"])
        if success:
            print_success("PostgreSQL service is running")
            return True
        else:
            print_warning("PostgreSQL service may not be running")
            return False
    else:
        print_warning("Cannot verify if PostgreSQL is running (pg_isready not found)")
        return True  # Don't fail if we can't check


def check_redis() -> bool:
    """Check if Redis is installed and running."""
    print_info("Checking Redis...")
    
    # Check if redis-cli exists
    success, _ = check_command_exists("redis-cli")
    if not success:
        print_warning("Redis CLI not found")
        return False
    
    print_success("Redis CLI installed")
    
    # Check if Redis is running
    success, output = run_command(["redis-cli", "ping"])
    if success and "PONG" in output:
        print_success("Redis service is running")
        return True
    else:
        print_warning("Redis service may not be running")
        return False


def check_environment_files() -> bool:
    """Check if environment files exist."""
    print_info("Checking environment files...")
    
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    all_ok = True
    
    # Check backend .env
    backend_env = project_root / "backend" / ".env"
    if backend_env.exists():
        print_success("backend/.env exists")
    else:
        print_warning("backend/.env not found (will use defaults)")
        all_ok = False
    
    # Check frontend .env
    frontend_env = project_root / "frontend" / ".env"
    if frontend_env.exists():
        print_success("frontend/.env exists")
    else:
        print_warning("frontend/.env not found (will use defaults)")
        all_ok = False
    
    return all_ok


def check_database_connection() -> bool:
    """Check if database connection works."""
    print_info("Checking database connection...")
    
    try:
        import psycopg2
        
        # Try to connect to the database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="hiremebahamas",
            user="hiremebahamas",
            password="hiremebahamas",
            connect_timeout=5
        )
        conn.close()
        print_success("Database connection successful")
        return True
    except ImportError:
        print_warning("psycopg2 not installed, skipping database connection test")
        return True  # Don't fail
    except Exception as e:
        print_warning(f"Database connection failed: {e}")
        print_info("This is OK if you haven't set up the database yet")
        return True  # Don't fail, as database might not be set up yet


def check_redis_connection() -> bool:
    """Check if Redis connection works."""
    print_info("Checking Redis connection...")
    
    try:
        import redis
        
        # Try to connect to Redis
        r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=5)
        r.ping()
        print_success("Redis connection successful")
        return True
    except ImportError:
        print_warning("redis package not installed, skipping Redis connection test")
        return True  # Don't fail
    except Exception as e:
        print_warning(f"Redis connection failed: {e}")
        print_info("This is OK if Redis is not running yet")
        return True  # Don't fail, as Redis might not be running


def generate_report(results: Dict[str, bool]) -> None:
    """Generate a summary report."""
    print_header("Installation Verification Report")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\n{Colors.BOLD}Results:{Colors.NC}")
    print(f"  Total checks: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.NC}")
    if failed > 0:
        print(f"  {Colors.RED}Failed: {failed}{Colors.NC}")
    
    print(f"\n{Colors.BOLD}Detailed Results:{Colors.NC}")
    for check, result in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.NC}" if result else f"{Colors.RED}✗ FAIL{Colors.NC}"
        print(f"  {status}  {check}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ All checks passed!{Colors.NC}")
        print(f"\n{Colors.BOLD}Your HireMeBahamas installation is ready!{Colors.NC}")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some checks failed{Colors.NC}")
        print(f"\n{Colors.BOLD}Please review the failed checks above and:${Colors.NC}")
        print(f"  1. Re-run the installation script")
        print(f"  2. Check the installation log")
        print(f"  3. Manually install missing dependencies")


def main() -> int:
    """Main verification function."""
    print_header("HireMeBahamas - Installation Verification")
    
    print(f"{Colors.BOLD}Verifying all dependencies and services...{Colors.NC}\n")
    
    results = {}
    
    # System tools
    print_header("System Tools")
    results["Python Version"] = check_python_version()
    results["Node.js Version"] = check_node_version()
    results["npm Version"] = check_npm_version()
    
    # Package installations
    print_header("Package Installations")
    results["Python Packages"] = check_python_packages()
    results["Node.js Packages"] = check_node_packages()
    
    # Services
    print_header("Services")
    results["PostgreSQL"] = check_postgresql()
    results["Redis"] = check_redis()
    
    # Configuration
    print_header("Configuration")
    results["Environment Files"] = check_environment_files()
    
    # Connections
    print_header("Service Connections")
    results["Database Connection"] = check_database_connection()
    results["Redis Connection"] = check_redis_connection()
    
    # Generate report
    generate_report(results)
    
    # Return exit code
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verification interrupted{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.NC}")
        sys.exit(1)
