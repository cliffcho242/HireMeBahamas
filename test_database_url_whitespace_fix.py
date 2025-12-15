#!/usr/bin/env python3
"""
Test DATABASE_URL whitespace fix
Verifies that internal whitespace is removed from hostname only
"""
import re
from urllib.parse import urlparse, urlunparse


def fix_database_url_whitespace(database_url):
    """
    Fix whitespace in DATABASE_URL hostname only.
    This is the actual implementation from final_backend_postgresql.py
    """
    if not database_url:
        return database_url
    
    # Strip leading/trailing whitespace
    database_url = database_url.strip()
    
    # Remove whitespace from hostname only
    if ' ' in database_url:
        try:
            parsed = urlparse(database_url)
            if parsed.hostname and ' ' in parsed.hostname:
                # Remove all whitespace from hostname only
                fixed_hostname = re.sub(r'\s+', '', parsed.hostname)
                # Reconstruct the URL with the fixed hostname
                fixed_netloc = parsed.netloc.replace(parsed.hostname, fixed_hostname)
                fixed_url = urlunparse((
                    parsed.scheme,
                    fixed_netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                return fixed_url
        except Exception:
            pass
    
    return database_url


def test_database_url_whitespace_removal():
    """Test that spaces are removed from DATABASE_URL hostname only"""
    test_cases = [
        {
            "name": "neon.tech with space (main issue from problem statement)",
            "input": "postgresql://user:pass@ep-dawn-cloud-a4rbrgox.us-east-1.aws.neon. tech:5432/db",
            "expected": "postgresql://user:pass@ep-dawn-cloud-a4rbrgox.us-east-1.aws.neon.tech:5432/db",
        },
        {
            "name": "multiple spaces in hostname",
            "input": "postgresql://user:pass@host. example. com:5432/db",
            "expected": "postgresql://user:pass@host.example.com:5432/db",
        },
        {
            "name": "space in password (should NOT be removed)",
            "input": "postgresql://user:pa ss@host.com:5432/db",
            "expected": "postgresql://user:pa ss@host.com:5432/db",
        },
        {
            "name": "no spaces (should remain unchanged)",
            "input": "postgresql://user:pass@host.com:5432/db",
            "expected": "postgresql://user:pass@host.com:5432/db",
        },
        {
            "name": "leading/trailing spaces (should be stripped)",
            "input": "  postgresql://user:pass@host.com:5432/db  ",
            "expected": "postgresql://user:pass@host.com:5432/db",
        },
        {
            "name": "tabs and newlines at end (should be stripped)",
            "input": "postgresql://user:pass@host.com:5432/db\t\n",
            "expected": "postgresql://user:pass@host.com:5432/db",
        },
        {
            "name": "space in hostname with query params",
            "input": "postgresql://user:pass@host. com:5432/db?sslmode=require",
            "expected": "postgresql://user:pass@host.com:5432/db?sslmode=require",
        },
    ]
    
    print("Testing DATABASE_URL whitespace removal...")
    print("=" * 70)
    
    all_passed = True
    for test_case in test_cases:
        input_url = test_case["input"]
        expected_url = test_case["expected"]
        
        # Use the actual implementation
        processed_url = fix_database_url_whitespace(input_url)
        
        passed = processed_url == expected_url
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n{status}: {test_case['name']}")
        print(f"  Input:    '{input_url}'")
        print(f"  Expected: '{expected_url}'")
        print(f"  Got:      '{processed_url}'")
        
        if not passed:
            print(f"  ERROR: Output does not match expected!")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit(test_database_url_whitespace_removal())
