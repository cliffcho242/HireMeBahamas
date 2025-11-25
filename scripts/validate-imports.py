#!/usr/bin/env python3
"""
Validate all Python imports for the HireMeBahamas application.
This script checks that all critical modules can be imported without errors.
"""

import sys
import importlib
from pathlib import Path

def validate_module(module_name, description):
    """Try to import a module and report success/failure"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {description}: {module_name}")
        return True
    except Exception as e:
        print(f"✗ {description}: {module_name}")
        print(f"  Error: {e}")
        return False

def main():
    print("=" * 60)
    print("HireMeBahamas - Import Validation")
    print("=" * 60)
    print()
    
    # Add the project root to Python path
    # This ensures the script works when run from any directory
    project_root = Path(__file__).parent.parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    print(f"Project root: {project_root}")
    print()
    
    all_passed = True
    
    # Critical dependencies
    print("Checking critical dependencies...")
    critical_modules = [
        ("flask", "Flask framework"),
        ("flask_cors", "Flask CORS"),
        ("flask_caching", "Flask Caching"),
        ("flask_limiter", "Flask Rate Limiter"),
        ("jwt", "PyJWT"),
        ("bcrypt", "bcrypt password hashing"),
        ("psycopg2", "PostgreSQL adapter"),
        ("sqlalchemy", "SQLAlchemy ORM"),
        ("dotenv", "python-dotenv"),
    ]
    
    for module, desc in critical_modules:
        if not validate_module(module, desc):
            all_passed = False
    
    print()
    
    # Main application module
    print("Checking main application...")
    if not validate_module("final_backend_postgresql", "Production Flask app"):
        all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✓ All imports validated successfully!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ Some imports failed!")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
