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

# Configuration files to check
REQUIREMENTS_FILES = [
    "requirements.txt",
    "api/requirements.txt"
]

BUILD_SCRIPT = "build.sh"
PYPROJECT_FILE = "pyproject.toml"
RENDER_BUILDPACK_FILE = ".render-buildpacks.json"

DEPLOYMENT_CONFIGS = [
    ("render.yaml", "bash build.sh", "render.yaml uses build.sh"),
    ("render.yaml", "gunicorn", "render.yaml uses gunicorn"),
    ("api/render.yaml", "bash build.sh", "api/render.yaml uses build.sh"),
]


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
    for req_file in REQUIREMENTS_FILES:
        if not check_file_contains(req_file, "gunicorn", f"gunicorn in {req_file}"):
            all_checks_passed = False
    
    print()
    
    # Check 2: Gunicorn in pyproject.toml
    print("Checking pyproject.toml...")
    if not check_file_contains(PYPROJECT_FILE, "gunicorn", "gunicorn in pyproject.toml"):
        all_checks_passed = False
    
    print()
    
    # Check 3: Build script exists and is executable
    print("Checking build script...")
    build_script = Path(BUILD_SCRIPT)
    if build_script.exists():
        print_status(f"{BUILD_SCRIPT} exists", "success")
        if os.access(build_script, os.X_OK):
            print_status(f"{BUILD_SCRIPT} is executable", "success")
        else:
            print_status(f"{BUILD_SCRIPT} is NOT executable", "warning")
            print_status(f"Run: chmod +x {BUILD_SCRIPT}", "info")
    else:
        print_status(f"{BUILD_SCRIPT} does not exist", "error")
        all_checks_passed = False
    
    print()
    
    # Check 4: .render-buildpacks.json exists
    print("Checking Render buildpack configuration...")
    if Path(RENDER_BUILDPACK_FILE).exists():
        print_status(f"{RENDER_BUILDPACK_FILE} exists", "success")
        if not check_file_contains(
            RENDER_BUILDPACK_FILE,
            "heroku-buildpack-python",
            "Python buildpack configured"
        ):
            all_checks_passed = False
    else:
        print_status(f"{RENDER_BUILDPACK_FILE} does not exist", "error")
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
    for filepath, search_string, description in DEPLOYMENT_CONFIGS:
        if not check_file_contains(filepath, search_string, description):
            # Don't fail the entire check if deployment configs are optional
            print_status(f"{description} check failed (non-critical)", "warning")
    
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
        print("  2. Deploy to Render/Render using the configured build commands")
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
