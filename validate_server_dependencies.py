#!/usr/bin/env python3
"""
Validation script to verify critical server dependencies are installed.
This prevents random errors from missing gunicorn, uvicorn, or fastapi.

Usage:
    python validate_server_dependencies.py
    
Exit codes:
    0 - All dependencies are installed correctly
    1 - One or more dependencies are missing or incorrect version
"""

import sys
import importlib.metadata
from typing import Dict, Tuple, List


# Required dependencies with minimum versions
REQUIRED_DEPENDENCIES = {
    "gunicorn": "23.0.0",
    "uvicorn": "0.31.0",  # Minimum acceptable version
    "fastapi": "0.115.0",  # Minimum acceptable version
}


def parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse version string into tuple of integers for comparison."""
    return tuple(map(int, version_str.split('.')[:3]))


def check_dependency(package_name: str, min_version: str) -> Tuple[bool, str]:
    """
    Check if a package is installed and meets minimum version requirement.
    
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        installed_version = importlib.metadata.version(package_name)
        
        # Parse versions for comparison
        installed_tuple = parse_version(installed_version)
        required_tuple = parse_version(min_version)
        
        if installed_tuple >= required_tuple:
            return True, f"✅ {package_name}=={installed_version} (>= {min_version})"
        else:
            return False, f"❌ {package_name}=={installed_version} is below minimum {min_version}"
            
    except importlib.metadata.PackageNotFoundError:
        return False, f"❌ {package_name} is NOT installed"
    except Exception as e:
        return False, f"❌ {package_name} - Error checking: {str(e)}"


def verify_server_imports() -> Tuple[bool, List[str]]:
    """
    Verify that server packages can be imported.
    
    Returns:
        Tuple of (all_success, messages)
    """
    messages = []
    all_success = True
    
    # Test gunicorn import
    try:
        import gunicorn
        messages.append(f"✅ gunicorn module imports successfully")
    except ImportError as e:
        messages.append(f"❌ gunicorn cannot be imported: {e}")
        all_success = False
    
    # Test uvicorn import
    try:
        import uvicorn
        messages.append(f"✅ uvicorn module imports successfully")
    except ImportError as e:
        messages.append(f"❌ uvicorn cannot be imported: {e}")
        all_success = False
    
    # Test fastapi import
    try:
        import fastapi
        messages.append(f"✅ fastapi module imports successfully")
    except ImportError as e:
        messages.append(f"❌ fastapi cannot be imported: {e}")
        all_success = False
    
    return all_success, messages


def main():
    """Main validation function."""
    print("🔍 Validating Server Dependencies for HireMeBahamas")
    print("=" * 60)
    print()
    
    all_valid = True
    
    # Check each required dependency
    print("📦 Checking installed versions:")
    for package, min_version in REQUIRED_DEPENDENCIES.items():
        is_valid, message = check_dependency(package, min_version)
        print(f"   {message}")
        if not is_valid:
            all_valid = False
    
    print()
    
    # Verify imports
    print("🔌 Verifying module imports:")
    import_success, import_messages = verify_server_imports()
    for message in import_messages:
        print(f"   {message}")
    
    if not import_success:
        all_valid = False
    
    print()
    print("=" * 60)
    
    if all_valid:
        print("✅ SUCCESS: All server dependencies are properly installed!")
        print()
        print("The following are correctly configured:")
        print("   • gunicorn - WSGI/ASGI HTTP server")
        print("   • uvicorn - ASGI server with WebSocket support")
        print("   • fastapi - Modern Python web framework")
        print()
        print("Your deployment will NOT experience random errors from missing dependencies.")
        return 0
    else:
        print("❌ FAILURE: Some dependencies are missing or incorrect!")
        print()
        print("To fix this issue:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. For specific installs:")
        print(f"      pip install gunicorn>={REQUIRED_DEPENDENCIES['gunicorn']}")
        print(f"      pip install 'uvicorn[standard]'>={REQUIRED_DEPENDENCIES['uvicorn']}")
        print(f"      pip install fastapi>={REQUIRED_DEPENDENCIES['fastapi']}")
        print()
        print("⚠️  Without these dependencies, you may experience random deployment errors!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
