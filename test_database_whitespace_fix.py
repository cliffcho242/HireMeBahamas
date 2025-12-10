#!/usr/bin/env python3
"""
Test that the database URL whitespace fix works correctly.

This test verifies that database names with trailing spaces are properly
stripped from the URL path component.
"""

import os
import sys
from urllib.parse import urlparse


def test_api_database_whitespace_fix():
    """Test that api/database.py strips whitespace from database names"""
    print("Testing API database whitespace fix...")
    
    # Save original environment
    original_url = os.environ.get("DATABASE_URL")
    
    try:
        # Test URL with database name containing trailing space
        test_url = "postgresql://user:pass@localhost:5432/Vercel "
        os.environ["DATABASE_URL"] = test_url
        
        # Import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location("api_database", "api/database.py")
        if spec is None or spec.loader is None:
            print("  ⚠️  Could not load api/database.py")
            return False
            
        api_db = importlib.util.module_from_spec(spec)
        
        # Add current directory to path for relative imports
        sys.path.insert(0, '/home/runner/work/HireMeBahamas/HireMeBahamas/api')
        
        try:
            spec.loader.exec_module(api_db)
        except Exception as e:
            print(f"  ⚠️  Could not execute api/database.py: {e}")
            return False
        finally:
            sys.path.pop(0)
        
        # Get the cleaned URL
        try:
            cleaned_url = api_db.get_database_url()
        except Exception as e:
            print(f"  ⚠️  Could not get database URL: {e}")
            return False
        
        # Parse and check the database name
        parsed = urlparse(cleaned_url)
        db_name = parsed.path.lstrip('/')
        
        print(f"  Input URL: '{test_url}'")
        print(f"  Output URL: '{cleaned_url}'")
        print(f"  Database name: '{db_name}'")
        
        # Verify no trailing space
        if db_name.endswith(' '):
            print(f"  ❌ FAILED: Database name still has trailing space: '{db_name}'")
            return False
        
        if db_name != 'Vercel':
            print(f"  ❌ FAILED: Expected 'Vercel', got '{db_name}'")
            return False
        
        print("  ✅ PASSED: Database name whitespace correctly stripped")
        return True
        
    finally:
        # Restore original environment
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        if original_url:
            os.environ["DATABASE_URL"] = original_url


def test_backend_database_whitespace_fix():
    """Test that backend database.py strips whitespace from database names"""
    print("\nTesting backend database whitespace fix...")
    
    # Save original environment
    original_url = os.environ.get("DATABASE_URL")
    original_pgdatabase = os.environ.get("PGDATABASE")
    
    try:
        # Test 1: URL with database name containing trailing space
        test_url = "postgresql://user:pass@localhost:5432/Vercel "
        os.environ["DATABASE_URL"] = test_url
        
        # Clear other env vars
        for key in ["DATABASE_PRIVATE_URL", "POSTGRES_URL", "PGDATABASE"]:
            if key in os.environ:
                del os.environ[key]
        
        print("  Test 1: DATABASE_URL with trailing space in database name")
        print(f"    Input: '{test_url}'")
        
        # Import the module
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "backend_database", 
            "api/backend_app/database.py"
        )
        if spec is None or spec.loader is None:
            print("    ⚠️  Could not load api/backend_app/database.py")
            return False
        
        # Add paths for imports
        sys.path.insert(0, '/home/runner/work/HireMeBahamas/HireMeBahamas')
        sys.path.insert(0, '/home/runner/work/HireMeBahamas/HireMeBahamas/api/backend_app')
        
        try:
            backend_db = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(backend_db)
        except Exception as e:
            print(f"    ⚠️  Could not execute backend database.py: {e}")
            return False
        finally:
            sys.path.pop(0)
            sys.path.pop(0)
        
        # Get the cleaned URL
        cleaned_url = backend_db.DATABASE_URL
        
        # Parse and check the database name
        parsed = urlparse(cleaned_url)
        db_name = parsed.path.lstrip('/')
        
        print(f"    Output: '{cleaned_url}'")
        print(f"    Database name: '{db_name}'")
        
        # Verify no trailing space
        if db_name.endswith(' '):
            print(f"    ❌ FAILED: Database name still has trailing space: '{db_name}'")
            return False
        
        if db_name != 'Vercel':
            print(f"    ❌ FAILED: Expected 'Vercel', got '{db_name}'")
            return False
        
        print("    ✅ PASSED: Database name whitespace correctly stripped")
        
        # Test 2: PGDATABASE with trailing space
        print("\n  Test 2: PGDATABASE environment variable with trailing space")
        
        # Clear DATABASE_URL and set individual PG* variables
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        
        os.environ["PGHOST"] = "localhost"
        os.environ["PGPORT"] = "5432"
        os.environ["PGUSER"] = "testuser"
        os.environ["PGPASSWORD"] = "testpass"
        os.environ["PGDATABASE"] = "TestDB "
        
        print(f"    Input PGDATABASE: '{os.environ['PGDATABASE']}'")
        
        # Reload module
        try:
            spec = importlib.util.spec_from_file_location(
                "backend_database2", 
                "api/backend_app/database.py"
            )
            backend_db2 = importlib.util.module_from_spec(spec)
            
            sys.path.insert(0, '/home/runner/work/HireMeBahamas/HireMeBahamas')
            sys.path.insert(0, '/home/runner/work/HireMeBahamas/HireMeBahamas/api/backend_app')
            spec.loader.exec_module(backend_db2)
        except Exception as e:
            print(f"    ⚠️  Could not reload backend database.py: {e}")
            return False
        finally:
            sys.path.pop(0)
            sys.path.pop(0)
        
        # Get the constructed URL
        constructed_url = backend_db2.DATABASE_URL
        
        # Parse and check the database name
        parsed2 = urlparse(constructed_url)
        db_name2 = parsed2.path.lstrip('/')
        
        print(f"    Output URL: '{constructed_url}'")
        print(f"    Database name: '{db_name2}'")
        
        # Verify no trailing space
        if db_name2.endswith(' '):
            print(f"    ❌ FAILED: Database name still has trailing space: '{db_name2}'")
            return False
        
        if db_name2 != 'TestDB':
            print(f"    ❌ FAILED: Expected 'TestDB', got '{db_name2}'")
            return False
        
        print("    ✅ PASSED: PGDATABASE whitespace correctly stripped")
        return True
        
    finally:
        # Restore original environment
        for key in ["DATABASE_URL", "DATABASE_PRIVATE_URL", "POSTGRES_URL", 
                    "PGHOST", "PGPORT", "PGUSER", "PGPASSWORD", "PGDATABASE"]:
            if key in os.environ:
                del os.environ[key]
        
        if original_url:
            os.environ["DATABASE_URL"] = original_url
        if original_pgdatabase:
            os.environ["PGDATABASE"] = original_pgdatabase


def main():
    """Run all tests"""
    print("=" * 70)
    print("Database URL Whitespace Fix Tests")
    print("=" * 70)
    print()
    
    all_passed = True
    
    try:
        if not test_api_database_whitespace_fix():
            all_passed = False
    except Exception as e:
        print(f"\n❌ API test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    try:
        if not test_backend_database_whitespace_fix():
            all_passed = False
    except Exception as e:
        print(f"\n❌ Backend test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print()
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
