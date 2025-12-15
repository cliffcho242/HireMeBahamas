#!/usr/bin/env python3
"""
Verification script for gunicorn installation fix

This script verifies that gunicorn is properly configured in all necessary files
to prevent the "bash: line 1: gunicorn: command not found" error.

Run this after installing dependencies to verify the fix:
    pip install -r requirements.txt
    python verify_gunicorn_fix.py
"""

import sys
import os
from pathlib import Path


def print_status(message, status="info"):
    """Print colored status message"""
    colors = {
        "success": "\033[92m✓\033[0m",
        "error": "\033[91m✗\033[0m",
        "warning": "\033[93m⚠\033[0m",
        "info": "\033[94mℹ\033[0m"
    }
    print(f"{colors.get(status, '')} {message}")


def check_file_contains(filepath, search_string, description):
    """Check if a file contains a specific string"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if search_string in content:
                print_status(f"{description}: Found in {filepath}", "success")
                return True
            else:
                print_status(f"{description}: NOT found in {filepath}", "error")
                return False
    except FileNotFoundError:
        print_status(f"{description}: File {filepath} not found", "warning")
        return False


def check_gunicorn_installed():
    """Check if gunicorn is installed and can be imported"""
    try:
        import gunicorn
        print_status(f"gunicorn is installed (version {gunicorn.__version__})", "success")
        return True
    except ImportError:
        print_status("gunicorn is NOT installed", "error")
        print_status("Run: pip install -r requirements.txt", "info")
        return False


def main():
    """Main verification function"""
    print("=" * 70)
    print("Gunicorn Installation Fix Verification")
    print("=" * 70)
    print()
    
    all_checks_passed = True
    
    # Check 1: Gunicorn in requirements.txt
    print("Checking requirements files...")
    if not check_file_contains("requirements.txt", "gunicorn", "gunicorn in requirements.txt"):
        all_checks_passed = False
    
    if not check_file_contains("api/requirements.txt", "gunicorn", "gunicorn in api/requirements.txt"):
        all_checks_passed = False
    
    print()
    
    # Check 2: Gunicorn in pyproject.toml
    print("Checking pyproject.toml...")
    if not check_file_contains("pyproject.toml", "gunicorn", "gunicorn in pyproject.toml"):
        all_checks_passed = False
    
    print()
    
    # Check 3: Build script exists and is executable
    print("Checking build script...")
    build_script = Path("build.sh")
    if build_script.exists():
        print_status("build.sh exists", "success")
        if os.access(build_script, os.X_OK):
            print_status("build.sh is executable", "success")
        else:
            print_status("build.sh is NOT executable", "warning")
            print_status("Run: chmod +x build.sh", "info")
    else:
        print_status("build.sh does not exist", "error")
        all_checks_passed = False
    
    print()
    
    # Check 4: .render-buildpacks.json exists
    print("Checking Render buildpack configuration...")
    if Path(".render-buildpacks.json").exists():
        print_status(".render-buildpacks.json exists", "success")
        check_file_contains(
            ".render-buildpacks.json",
            "heroku-buildpack-python",
            "Python buildpack configured"
        )
    else:
        print_status(".render-buildpacks.json does not exist", "error")
        all_checks_passed = False
    
    print()
    
    # Check 5: Gunicorn installation status
    print("Checking gunicorn installation...")
    if not check_gunicorn_installed():
        all_checks_passed = False
        print_status(
            "Install dependencies first: pip install -r requirements.txt",
            "info"
        )
    
    print()
    
    # Check 6: Verify deployment configurations
    print("Checking deployment configurations...")
    check_file_contains("render.yaml", "bash build.sh", "render.yaml uses build.sh")
    check_file_contains("render.yaml", "gunicorn", "render.yaml uses gunicorn")
    check_file_contains("api/render.yaml", "bash build.sh", "api/render.yaml uses build.sh")
    
    print()
    
    # Final summary
    print("=" * 70)
    if all_checks_passed:
        print_status("All checks passed! Gunicorn is properly configured.", "success")
        print()
        print("The fix for 'bash: line 1: gunicorn: command not found' is complete.")
        print()
        print("Next steps:")
        print("  1. Commit and push changes to your repository")
        print("  2. Deploy to Render/Railway using the configured build commands")
        print("  3. Verify deployment logs show gunicorn starting successfully")
        return 0
    else:
        print_status("Some checks failed. Please review the errors above.", "error")
        print()
        print("Common fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Make build.sh executable: chmod +x build.sh")
        print("  - Ensure all configuration files are present")
        return 1


if __name__ == "__main__":
    sys.exit(main())
