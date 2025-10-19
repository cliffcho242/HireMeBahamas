#!/usr/bin/env python3
"""
Automated Requirements Installer for AI Network Authenticator
Ensures all required packages are installed and up to date
"""

import os
import sys
import subprocess
import importlib.util

def run_command(cmd, shell=True, capture_output=True):
    """Run a command and return result"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_package_installed(package_name):
    """Check if a Python package is installed"""
    try:
        spec = importlib.util.find_spec(package_name.replace('-', '_'))
        return spec is not None
    except:
        return False

def install_requirements():
    """Install all required packages"""
    print("🔧 Installing AI Network Authenticator Requirements...")

    required_packages = [
        'psutil',      # Process management
        'requests',    # HTTP requests
        'bcrypt',      # Password hashing
        'flask-cors',  # CORS handling
        'pyjwt',       # JWT tokens
        'flask'        # Web framework
    ]

    missing_packages = []
    for package in required_packages:
        if not check_package_installed(package):
            missing_packages.append(package)

    if not missing_packages:
        print("✅ All required packages are already installed")
        return True

    print(f"📦 Installing {len(missing_packages)} missing packages: {', '.join(missing_packages)}")

    # Try to install from requirements.txt first
    if os.path.exists('requirements.txt'):
        print("Installing from requirements.txt...")
        success, stdout, stderr = run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        if success:
            print("✅ Requirements installed successfully")
            return True

    # Fallback: install individual packages
    print("Installing packages individually...")
    failed_packages = []

    for package in missing_packages:
        print(f"Installing {package}...")
        success, stdout, stderr = run_command([sys.executable, '-m', 'pip', 'install', package])
        if not success:
            failed_packages.append(package)
            print(f"❌ Failed to install {package}: {stderr}")

    if failed_packages:
        print(f"❌ Failed to install: {', '.join(failed_packages)}")
        return False

    print("✅ All packages installed successfully")
    return True

def verify_installations():
    """Verify all critical packages are working"""
    print("🔍 Verifying package installations...")

    test_imports = [
        ('psutil', 'psutil.cpu_percent()'),
        ('requests', 'requests.get("http://httpbin.org/get", timeout=5)'),
        ('bcrypt', 'bcrypt.hashpw(b"test", bcrypt.gensalt())'),
        ('flask_cors', 'from flask_cors import CORS'),
        ('jwt', 'import jwt'),
        ('flask', 'from flask import Flask')
    ]

    failed_tests = []

    for module_name, test_code in test_imports:
        try:
            # Test import first
            module = __import__(module_name.replace('-', '_'))
            print(f"✅ {module_name} (imported)")

            # Test basic functionality (skip network tests in verification)
            if 'httpbin' not in test_code and 'requests.get' not in test_code:
                try:
                    exec(test_code)
                    print(f"✅ {module_name} (functional)")
                except Exception as e:
                    print(f"⚠️ {module_name} (limited functionality: {e})")

        except ImportError as e:
            failed_tests.append(f"{module_name} (import error: {e})")
        except Exception as e:
            failed_tests.append(f"{module_name} (error: {e})")

    if failed_tests:
        print(f"❌ Verification issues: {', '.join(failed_tests)}")
        return False

    print("✅ All packages verified successfully")
    return True

def main():
    """Main installation function"""
    print("🤖 AI REQUIREMENTS INSTALLER")
    print("=" * 30)

    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return 1

    # Verify installations
    if not verify_installations():
        print("❌ Package verification failed")
        return 1

    print("\n🎉 AI Network Authenticator is ready!")
    print("You can now run: python ai_network_authenticator.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())