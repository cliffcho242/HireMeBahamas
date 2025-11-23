#!/usr/bin/env python3
"""
Test script to verify all critical Python dependencies are installed.
This ensures the app can run without ModuleNotFoundError.
"""

import sys

def test_import(module_name, package_name=None):
    """Test if a module can be imported."""
    try:
        __import__(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("Testing Python Dependencies")
    print("=" * 60)
    print()
    
    required_packages = [
        ("flask", "Flask"),
        ("flask_cors", "Flask-CORS"),
        ("flask_limiter", "Flask-Limiter"),
        ("flask_caching", "Flask-Caching"),
        ("jwt", "PyJWT"),
        ("bcrypt", "bcrypt"),
        ("psycopg2", "psycopg2-binary"),
        ("aiosqlite", "aiosqlite"),
        ("dotenv", "python-dotenv"),
        ("decouple", "python-decouple"),
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("requests", "requests"),
    ]
    
    results = []
    for module, package in required_packages:
        results.append(test_import(module, package))
    
    print()
    print("=" * 60)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"Results: {passed}/{total} packages available")
    
    if failed > 0:
        print(f"⚠️  {failed} packages are missing!")
        print()
        print("To install missing packages:")
        print("  pip3 install -r requirements.txt")
        print("  pip3 install -r backend/requirements.txt")
        sys.exit(1)
    else:
        print("✅ All critical packages are installed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
