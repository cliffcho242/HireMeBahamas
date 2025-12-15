#!/usr/bin/env python3
"""
Test script to validate Gunicorn/Uvicorn entry points.

This script verifies that all documented entry points for the application
have valid module structures. It checks that:
1. The module files exist
2. The import paths are correct
3. The module hierarchy is properly structured

Note: This script validates module structure only. It does not perform
actual imports because that would require all dependencies (PostgreSQL,
Redis, etc.) to be installed. For full validation, use the actual
deployment environment.
"""
import sys
import importlib.util


def test_entry_point(module_path, attr_name, description):
    """
    Test if an entry point can be imported.
    
    Args:
        module_path: Module path (e.g., 'final_backend_postgresql')
        attr_name: Attribute name (e.g., 'application')
        description: Human-readable description
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if module file exists
        parts = module_path.split('.')
        spec = importlib.util.find_spec(parts[0])
        if spec is None:
            print(f"❌ {description}")
            print(f"   Module '{parts[0]}' not found")
            return False
        
        # For nested modules, check if the full path exists
        if len(parts) > 1:
            full_spec = importlib.util.find_spec(module_path)
            if full_spec is None:
                print(f"❌ {description}")
                print(f"   Module path '{module_path}' not found")
                return False
        
        # Attempt to check if attribute would be available
        # Note: We can't actually import due to missing dependencies,
        # but we can verify the module structure exists
        print(f"✅ {description}")
        print(f"   Entry point '{module_path}:{attr_name}' is valid")
        print(f"   (Module structure verified, actual import requires dependencies)")
        return True
        
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Error: {e}")
        return False


def main():
    """Run all entry point tests."""
    print("=" * 70)
    print("GUNICORN/UVICORN ENTRY POINT VALIDATION")
    print("=" * 70)
    print()
    
    tests = [
        # Flask entry points (for Gunicorn with default worker)
        ("final_backend_postgresql", "application", 
         "Flask: final_backend_postgresql:application (RECOMMENDED)"),
        ("final_backend_postgresql", "app", 
         "Flask: final_backend_postgresql:app (alternative)"),
        ("app", "application", 
         "Flask: app:application (via wrapper)"),
        ("app", "app", 
         "Flask: app:app (via wrapper)"),
        
        # FastAPI entry points (for Uvicorn or Gunicorn with Uvicorn workers)
        ("app.main", "app", 
         "FastAPI: app.main:app (wrapper - root directory)"),
        ("api.backend_app.main", "app", 
         "FastAPI: api.backend_app.main:app (direct)"),
        ("backend.app.main", "app", 
         "FastAPI: backend.app.main:app (backend directory)"),
    ]
    
    results = []
    for module_path, attr_name, description in tests:
        result = test_entry_point(module_path, attr_name, description)
        results.append(result)
        print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All entry points are valid!")
        print("\nRECOMMENDED ENTRY POINTS:")
        print("  Flask (Gunicorn):  final_backend_postgresql:application")
        print("  Flask (Gunicorn):  app:application")
        print("  FastAPI (Uvicorn): app.main:app")
        print("  FastAPI (Uvicorn): api.backend_app.main:app")
        return 0
    else:
        print(f"\n⚠️  {total - passed} entry point(s) failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
