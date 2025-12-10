#!/usr/bin/env python3
"""
Unit test for database URL whitespace stripping logic.

This test verifies the URL sanitization logic without importing
the actual database modules (which require SQLAlchemy).
"""

from urllib.parse import urlparse, urlunparse


def strip_database_name_whitespace(db_url):
    """
    Strip whitespace from database name in the URL path.
    
    This is the logic implemented in both api/database.py and
    api/backend_app/database.py.
    """
    try:
        parsed = urlparse(db_url)
        if parsed.path:
            # Strip leading slash and whitespace from database name
            db_name = parsed.path.lstrip('/').strip()
            if db_name:
                # Reconstruct path with cleaned database name
                new_path = '/' + db_name
                db_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    new_path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
        return db_url
    except Exception:
        # If URL parsing fails, return original URL
        return db_url


def test_database_name_with_trailing_space():
    """Test URL with database name containing trailing space"""
    test_url = "postgresql://user:pass@localhost:5432/Vercel "
    cleaned_url = strip_database_name_whitespace(test_url)
    
    parsed = urlparse(cleaned_url)
    db_name = parsed.path.lstrip('/')
    
    print(f"Test 1: Database name with trailing space")
    print(f"  Input:  '{test_url}'")
    print(f"  Output: '{cleaned_url}'")
    print(f"  DB name: '{db_name}'")
    
    assert not db_name.endswith(' '), f"Database name should not have trailing space: '{db_name}'"
    assert db_name == 'Vercel', f"Expected 'Vercel', got '{db_name}'"
    print("  ✅ PASSED")
    return True


def test_database_name_with_leading_space():
    """Test URL with database name containing leading space"""
    test_url = "postgresql://user:pass@localhost:5432/ MyDB"
    cleaned_url = strip_database_name_whitespace(test_url)
    
    parsed = urlparse(cleaned_url)
    db_name = parsed.path.lstrip('/')
    
    print(f"\nTest 2: Database name with leading space")
    print(f"  Input:  '{test_url}'")
    print(f"  Output: '{cleaned_url}'")
    print(f"  DB name: '{db_name}'")
    
    assert not db_name.startswith(' '), f"Database name should not have leading space: '{db_name}'"
    assert db_name == 'MyDB', f"Expected 'MyDB', got '{db_name}'"
    print("  ✅ PASSED")
    return True


def test_database_name_with_both_spaces():
    """Test URL with database name containing both leading and trailing spaces"""
    test_url = "postgresql://user:pass@localhost:5432/ TestDB  "
    cleaned_url = strip_database_name_whitespace(test_url)
    
    parsed = urlparse(cleaned_url)
    db_name = parsed.path.lstrip('/')
    
    print(f"\nTest 3: Database name with both leading and trailing spaces")
    print(f"  Input:  '{test_url}'")
    print(f"  Output: '{cleaned_url}'")
    print(f"  DB name: '{db_name}'")
    
    assert not db_name.startswith(' '), f"Database name should not have leading space: '{db_name}'"
    assert not db_name.endswith(' '), f"Database name should not have trailing space: '{db_name}'"
    assert db_name == 'TestDB', f"Expected 'TestDB', got '{db_name}'"
    print("  ✅ PASSED")
    return True


def test_database_name_without_spaces():
    """Test URL with normal database name (no spaces)"""
    test_url = "postgresql://user:pass@localhost:5432/mydb"
    cleaned_url = strip_database_name_whitespace(test_url)
    
    parsed = urlparse(cleaned_url)
    db_name = parsed.path.lstrip('/')
    
    print(f"\nTest 4: Normal database name (no spaces)")
    print(f"  Input:  '{test_url}'")
    print(f"  Output: '{cleaned_url}'")
    print(f"  DB name: '{db_name}'")
    
    assert db_name == 'mydb', f"Expected 'mydb', got '{db_name}'"
    assert cleaned_url == test_url, "URL should not be modified"
    print("  ✅ PASSED")
    return True


def test_url_with_query_params():
    """Test URL with query parameters and database name with trailing space"""
    test_url = "postgresql://user:pass@localhost:5432/Vercel ?sslmode=require"
    cleaned_url = strip_database_name_whitespace(test_url)
    
    parsed = urlparse(cleaned_url)
    db_name = parsed.path.lstrip('/')
    
    print(f"\nTest 5: Database name with trailing space and query parameters")
    print(f"  Input:  '{test_url}'")
    print(f"  Output: '{cleaned_url}'")
    print(f"  DB name: '{db_name}'")
    print(f"  Query:  '{parsed.query}'")
    
    assert not db_name.endswith(' '), f"Database name should not have trailing space: '{db_name}'"
    assert db_name == 'Vercel', f"Expected 'Vercel', got '{db_name}'"
    assert 'sslmode=require' in parsed.query, "Query parameters should be preserved"
    print("  ✅ PASSED")
    return True


def test_asyncpg_url_with_trailing_space():
    """Test asyncpg URL with database name containing trailing space"""
    test_url = "postgresql+asyncpg://user:pass@localhost:5432/production "
    cleaned_url = strip_database_name_whitespace(test_url)
    
    parsed = urlparse(cleaned_url)
    db_name = parsed.path.lstrip('/')
    
    print(f"\nTest 6: AsyncPG URL with trailing space in database name")
    print(f"  Input:  '{test_url}'")
    print(f"  Output: '{cleaned_url}'")
    print(f"  DB name: '{db_name}'")
    
    assert not db_name.endswith(' '), f"Database name should not have trailing space: '{db_name}'"
    assert db_name == 'production', f"Expected 'production', got '{db_name}'"
    assert 'postgresql+asyncpg' in cleaned_url, "Scheme should be preserved"
    print("  ✅ PASSED")
    return True


def main():
    """Run all tests"""
    print("=" * 70)
    print("Database URL Whitespace Stripping - Unit Tests")
    print("=" * 70)
    print()
    
    all_passed = True
    tests = [
        test_database_name_with_trailing_space,
        test_database_name_with_leading_space,
        test_database_name_with_both_spaces,
        test_database_name_without_spaces,
        test_url_with_query_params,
        test_asyncpg_url_with_trailing_space,
    ]
    
    for test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            all_passed = False
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print()
    print("=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        print()
        print("The database URL whitespace stripping logic is working correctly.")
        print("This fix resolves the error:")
        print('  psql: error: database "Vercel " does not exist')
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
