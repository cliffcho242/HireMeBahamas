#!/usr/bin/env python3
"""
Test database URL normalization utility.

This test verifies that the normalize_database_url function correctly
handles various URL formats for both async and sync connections.
"""
import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from backend_app.core.db_url_normalizer import (
    normalize_database_url,
    get_url_scheme,
    is_async_url,
)


def test_normalize_for_sync():
    """Test normalization for sync connections (psycopg2)"""
    print("\n=== Testing Sync URL Normalization (for_async=False) ===\n")
    
    test_cases = [
        # (input_url, expected_output, description)
        (
            "postgresql+asyncpg://user:pass@host:5432/db",
            "postgresql://user:pass@host:5432/db",
            "Remove +asyncpg suffix"
        ),
        (
            "postgresql+psycopg2://user:pass@host:5432/db",
            "postgresql://user:pass@host:5432/db",
            "Remove +psycopg2 suffix"
        ),
        (
            "postgres://user:pass@host:5432/db",
            "postgresql://user:pass@host:5432/db",
            "Normalize postgres:// to postgresql://"
        ),
        (
            "postgresql://user:pass@host:5432/db",
            "postgresql://user:pass@host:5432/db",
            "Already in sync format - no change"
        ),
        (
            "postgresql://user:p@ss@host:5432/db?sslmode=require",
            "postgresql://user:p@ss@host:5432/db?sslmode=require",
            "Preserve query parameters and special chars in password"
        ),
    ]
    
    all_passed = True
    for input_url, expected, description in test_cases:
        result = normalize_database_url(input_url, for_async=False)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {description}")
        print(f"  Input:    {input_url}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print()
    
    return all_passed


def test_normalize_for_async():
    """Test normalization for async connections (asyncpg)"""
    print("\n=== Testing Async URL Normalization (for_async=True) ===\n")
    
    test_cases = [
        # (input_url, expected_output, description)
        (
            "postgresql://user:pass@host:5432/db",
            "postgresql+asyncpg://user:pass@host:5432/db",
            "Add +asyncpg suffix"
        ),
        (
            "postgres://user:pass@host:5432/db",
            "postgresql+asyncpg://user:pass@host:5432/db",
            "Normalize postgres:// and add +asyncpg"
        ),
        (
            "postgresql+asyncpg://user:pass@host:5432/db",
            "postgresql+asyncpg://user:pass@host:5432/db",
            "Already in async format - no change"
        ),
        (
            "postgresql+psycopg2://user:pass@host:5432/db",
            "postgresql+asyncpg://user:pass@host:5432/db",
            "Replace +psycopg2 with +asyncpg"
        ),
    ]
    
    all_passed = True
    for input_url, expected, description in test_cases:
        result = normalize_database_url(input_url, for_async=True)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {description}")
        print(f"  Input:    {input_url}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print()
    
    return all_passed


def test_utility_functions():
    """Test utility functions"""
    print("\n=== Testing Utility Functions ===\n")
    
    all_passed = True
    
    # Test get_url_scheme
    test_cases = [
        ("postgresql+asyncpg://host/db", "postgresql+asyncpg", "Get asyncpg scheme"),
        ("postgresql://host/db", "postgresql", "Get postgresql scheme"),
        ("postgres://host/db", "postgres", "Get postgres scheme"),
    ]
    
    for url, expected, description in test_cases:
        result = get_url_scheme(url)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {description}")
        print(f"  URL:      {url}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print()
    
    # Test is_async_url
    async_test_cases = [
        ("postgresql+asyncpg://host/db", True, "Detect asyncpg URL"),
        ("postgresql://host/db", False, "Detect sync URL"),
        ("postgres://host/db", False, "Detect non-asyncpg URL"),
    ]
    
    for url, expected, description in async_test_cases:
        result = is_async_url(url)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {description}")
        print(f"  URL:      {url}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print()
    
    return all_passed


def test_edge_cases():
    """Test edge cases"""
    print("\n=== Testing Edge Cases ===\n")
    
    all_passed = True
    
    # Test None and empty strings
    test_cases = [
        (None, None, "Handle None input"),
        ("", "", "Handle empty string"),
    ]
    
    for input_url, expected, description in test_cases:
        result_sync = normalize_database_url(input_url, for_async=False)
        result_async = normalize_database_url(input_url, for_async=True)
        passed = result_sync == expected and result_async == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {description}")
        print(f"  Input:    {repr(input_url)}")
        print(f"  Expected: {repr(expected)}")
        print(f"  Got (sync):  {repr(result_sync)}")
        print(f"  Got (async): {repr(result_async)}")
        print()
    
    return all_passed


def main():
    """Run all tests"""
    print("="*70)
    print("Database URL Normalizer Test Suite")
    print("="*70)
    
    results = []
    results.append(("Sync Normalization", test_normalize_for_sync()))
    results.append(("Async Normalization", test_normalize_for_async()))
    results.append(("Utility Functions", test_utility_functions()))
    results.append(("Edge Cases", test_edge_cases()))
    
    print("\n" + "="*70)
    print("Test Results Summary")
    print("="*70 + "\n")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        all_passed = all_passed and passed
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ All tests passed!")
        print("="*70)
        return 0
    else:
        print("❌ Some tests failed")
        print("="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
