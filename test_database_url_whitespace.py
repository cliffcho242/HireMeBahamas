"""
Test database URL whitespace handling

This test verifies that database connection strings with trailing
or leading whitespace are properly stripped to prevent connection errors.
"""

import os
import sys
from urllib.parse import urlparse


def test_backend_database_url_stripping():
    """Test that backend database.py strips whitespace from DATABASE_URL"""
    print("Testing backend database URL whitespace stripping...")
    
    # Save original environment
    original_url = os.environ.get("DATABASE_URL")
    original_postgres_url = os.environ.get("POSTGRES_URL")
    original_private_url = os.environ.get("DATABASE_PRIVATE_URL")
    
    try:
        # Clear all database URLs
        for key in ["DATABASE_URL", "POSTGRES_URL", "DATABASE_PRIVATE_URL"]:
            if key in os.environ:
                del os.environ[key]
        
        # Test case 1: DATABASE_URL with trailing space
        test_url_with_space = "postgresql://user:pass@localhost:5432/Vercel "
        os.environ["DATABASE_URL"] = test_url_with_space
        
        # Import after setting environment
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        from backend.app import database
        
        # Get the parsed DATABASE_URL
        db_url = database.DATABASE_URL
        parsed = urlparse(db_url)
        db_name = parsed.path.lstrip('/')
        
        print(f"  Input URL: '{test_url_with_space}'")
        print(f"  Parsed database name: '{db_name}'")
        
        # Verify no trailing space
        assert not db_name.endswith(' '), f"Database name should not have trailing space: '{db_name}'"
        assert db_name == 'Vercel', f"Expected 'Vercel', got '{db_name}'"
        print("  ✅ Backend correctly strips trailing space from database name")
        
        # Test case 2: DATABASE_URL with leading space
        test_url_leading = " postgresql://user:pass@localhost:5432/mydb"
        os.environ["DATABASE_URL"] = test_url_leading
        
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        from backend.app import database as db2
        
        db_url2 = db2.DATABASE_URL
        assert db_url2.startswith('postgresql'), f"URL should not have leading space: '{db_url2}'"
        print("  ✅ Backend correctly strips leading space from URL")
        
        # Test case 3: DATABASE_URL with both leading and trailing spaces
        test_url_both = "  postgresql://user:pass@localhost:5432/testdb  "
        os.environ["DATABASE_URL"] = test_url_both
        
        if 'backend.app.database' in sys.modules:
            del sys.modules['backend.app.database']
        from backend.app import database as db3
        
        db_url3 = db3.DATABASE_URL
        assert not db_url3.startswith(' '), f"URL should not have leading space: '{db_url3}'"
        assert not db_url3.endswith(' '), f"URL should not have trailing space: '{db_url3}'"
        print("  ✅ Backend correctly strips both leading and trailing spaces")
        
        print("\n✅ All backend database URL whitespace tests passed!\n")
        return True
        
    finally:
        # Restore original environment
        for key in ["DATABASE_URL", "POSTGRES_URL", "DATABASE_PRIVATE_URL"]:
            if key in os.environ:
                del os.environ[key]
        
        if original_url:
            os.environ["DATABASE_URL"] = original_url
        if original_postgres_url:
            os.environ["POSTGRES_URL"] = original_postgres_url
        if original_private_url:
            os.environ["DATABASE_PRIVATE_URL"] = original_private_url


def test_api_database_url_stripping():
    """Test that api database.py strips whitespace from DATABASE_URL"""
    print("Testing api database URL whitespace stripping...")
    
    # Save original environment
    original_url = os.environ.get("DATABASE_URL")
    
    try:
        # Test case 1: DATABASE_URL with trailing space
        test_url_with_space = "postgresql://user:pass@localhost:5432/Vercel "
        os.environ["DATABASE_URL"] = test_url_with_space
        
        # Import and test
        if 'api.database' in sys.modules:
            del sys.modules['api.database']
        
        # Import the module to get the function
        import importlib.util
        spec = importlib.util.spec_from_file_location("api.database", "api/database.py")
        api_db = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_db)
        
        db_url = api_db.get_database_url()
        parsed = urlparse(db_url)
        db_name = parsed.path.lstrip('/')
        
        print(f"  Input URL: '{test_url_with_space}'")
        print(f"  Parsed database name: '{db_name}'")
        
        # Verify no trailing space
        assert not db_name.endswith(' '), f"Database name should not have trailing space: '{db_name}'"
        assert db_name == 'Vercel', f"Expected 'Vercel', got '{db_name}'"
        print("  ✅ API correctly strips trailing space from database name")
        
        # Test case 2: DATABASE_URL with leading space
        test_url_leading = " postgresql://user:pass@localhost:5432/mydb"
        os.environ["DATABASE_URL"] = test_url_leading
        
        # Reload module
        spec = importlib.util.spec_from_file_location("api.database", "api/database.py")
        api_db2 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_db2)
        
        db_url2 = api_db2.get_database_url()
        assert db_url2.startswith('postgresql'), f"URL should not have leading space: '{db_url2}'"
        print("  ✅ API correctly strips leading space from URL")
        
        print("\n✅ All API database URL whitespace tests passed!\n")
        return True
        
    finally:
        # Restore original environment
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
        if original_url:
            os.environ["DATABASE_URL"] = original_url


def main():
    """Run all tests"""
    print("=" * 70)
    print("Database URL Whitespace Handling Tests")
    print("=" * 70)
    print()
    
    try:
        test_backend_database_url_stripping()
        test_api_database_url_stripping()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
