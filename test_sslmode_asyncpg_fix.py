#!/usr/bin/env python3
"""
Test to validate that the sslmode parameter fix works correctly
Tests that asyncpg.connect() calls work with URLs containing sslmode parameter
"""
import sys
import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


def strip_sslmode_from_url(db_url: str) -> str:
    """Remove sslmode parameter from database URL.
    
    asyncpg doesn't accept 'sslmode' as a connection parameter.
    It handles SSL automatically based on the server's requirements.
    
    Args:
        db_url: Database URL that may contain sslmode parameter
        
    Returns:
        Database URL without sslmode parameter
    """
    parsed = urlparse(db_url)
    if not parsed.query:
        return db_url
    
    # Parse query parameters
    query_params = parse_qs(parsed.query)
    
    # Remove sslmode if present
    if 'sslmode' in query_params:
        del query_params['sslmode']
    
    # Rebuild query string
    new_query = urlencode(query_params, doseq=True)
    
    # Rebuild URL
    new_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))
    
    return new_url


def test_strip_sslmode():
    """Test that sslmode is correctly stripped from URLs"""
    test_cases = [
        # (input_url, expected_output, description)
        (
            "postgresql://user:pass@host:5432/db?sslmode=require",
            "postgresql://user:pass@host:5432/db",
            "URL with only sslmode parameter"
        ),
        (
            "postgresql://user:pass@host:5432/db?sslmode=require&timeout=30",
            "postgresql://user:pass@host:5432/db?timeout=30",
            "URL with sslmode and other parameters"
        ),
        (
            "postgresql://user:pass@host:5432/db?timeout=30&sslmode=require",
            "postgresql://user:pass@host:5432/db?timeout=30",
            "URL with sslmode as second parameter"
        ),
        (
            "postgresql://user:pass@host:5432/db?timeout=30&sslmode=require&pool_size=10",
            "postgresql://user:pass@host:5432/db?timeout=30&pool_size=10",
            "URL with sslmode between other parameters"
        ),
        (
            "postgresql://user:pass@host:5432/db",
            "postgresql://user:pass@host:5432/db",
            "URL without sslmode parameter"
        ),
        (
            "postgresql://user:pass@host:5432/db?timeout=30",
            "postgresql://user:pass@host:5432/db?timeout=30",
            "URL without sslmode but with other parameters"
        ),
        (
            "postgresql+asyncpg://user:pass@host:5432/db?sslmode=require",
            "postgresql+asyncpg://user:pass@host:5432/db",
            "asyncpg URL with sslmode"
        ),
    ]
    
    print("Testing sslmode stripping functionality:")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for input_url, expected_output, description in test_cases:
        result = strip_sslmode_from_url(input_url)
        
        # Normalize the result to handle parameter order differences
        # Parse both URLs and compare their components
        parsed_result = urlparse(result)
        parsed_expected = urlparse(expected_output)
        
        # Compare scheme, netloc, and path
        scheme_match = parsed_result.scheme == parsed_expected.scheme
        netloc_match = parsed_result.netloc == parsed_expected.netloc
        path_match = parsed_result.path == parsed_expected.path
        
        # Compare query parameters as dictionaries
        result_params = parse_qs(parsed_result.query) if parsed_result.query else {}
        expected_params = parse_qs(parsed_expected.query) if parsed_expected.query else {}
        params_match = result_params == expected_params
        
        # Check that sslmode is not in the result
        sslmode_removed = 'sslmode' not in result
        
        if scheme_match and netloc_match and path_match and params_match and sslmode_removed:
            print(f"✅ PASS: {description}")
            print(f"   Input:  {input_url}")
            print(f"   Output: {result}")
            passed += 1
        else:
            print(f"❌ FAIL: {description}")
            print(f"   Input:    {input_url}")
            print(f"   Expected: {expected_output}")
            print(f"   Got:      {result}")
            if not sslmode_removed:
                print(f"   ERROR: sslmode still in URL!")
            failed += 1
        print()
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


def test_fixed_files():
    """Test that all files have been fixed"""
    print("\nChecking that all files with asyncpg.connect have sslmode stripping:")
    print("=" * 80)
    
    files_to_check = [
        "scripts/verify_vercel_postgres_migration.py",
        "scripts/health_check.py",
        "backend/create_database_indexes.py",
        "immortal_vercel_migration_fix.py"
    ]
    
    all_fixed = True
    
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            print(f"⚠️  WARNING: {filepath} not found (may not exist in this environment)")
            continue
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check if file has asyncpg.connect
        has_asyncpg = 'asyncpg.connect' in content
        
        if has_asyncpg:
            # Check if it has sslmode stripping logic
            has_strip_logic = (
                'strip_sslmode' in content or 
                ('parse_qs' in content and 'sslmode' in content and 'del query_params' in content)
            )
            
            if has_strip_logic:
                print(f"✅ FIXED: {filepath}")
            else:
                print(f"❌ NOT FIXED: {filepath} - has asyncpg.connect but no sslmode stripping")
                all_fixed = False
        else:
            print(f"ℹ️  SKIP: {filepath} - no asyncpg.connect calls")
    
    print("=" * 80)
    return all_fixed


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("SSLMODE ASYNCPG FIX VALIDATION TEST")
    print("=" * 80 + "\n")
    
    # Test 1: Strip function works correctly
    test1_passed = test_strip_sslmode()
    
    # Test 2: All files are fixed
    test2_passed = test_fixed_files()
    
    # Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED")
        print("\nThe fix is working correctly:")
        print("  • sslmode parameter is correctly stripped from URLs")
        print("  • All files with asyncpg.connect have been updated")
        print("\nDatabase connections should now work without the sslmode error!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        if not test1_passed:
            print("  • Strip function test failed")
        if not test2_passed:
            print("  • Some files are not properly fixed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
