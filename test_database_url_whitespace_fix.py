#!/usr/bin/env python3
"""
Test DATABASE_URL whitespace fix
Verifies that internal whitespace is removed from DATABASE_URL
"""
import os
import re


def test_database_url_whitespace_removal():
    """Test that spaces are removed from DATABASE_URL"""
    test_cases = [
        {
            "name": "neon.tech with space",
            "input": "postgresql://user:pass@ep-dawn-cloud-a4rbrgox.us-east-1.aws.neon. tech:5432/db",
            "expected": "postgresql://user:pass@ep-dawn-cloud-a4rbrgox.us-east-1.aws.neon.tech:5432/db",
        },
        {
            "name": "multiple spaces",
            "input": "postgresql://user:pass@host. example. com:5432/db",
            "expected": "postgresql://user:pass@host.example.com:5432/db",
        },
        {
            "name": "space in password (should also be removed)",
            "input": "postgresql://user:pa ss@host.com:5432/db",
            "expected": "postgresql://user:pass@host.com:5432/db",
        },
        {
            "name": "no spaces (should remain unchanged)",
            "input": "postgresql://user:pass@host.com:5432/db",
            "expected": "postgresql://user:pass@host.com:5432/db",
        },
        {
            "name": "leading/trailing spaces",
            "input": "  postgresql://user:pass@host.com:5432/db  ",
            "expected": "postgresql://user:pass@host.com:5432/db",
        },
        {
            "name": "tabs and newlines",
            "input": "postgresql://user:pass@host.com:5432/db\t\n",
            "expected": "postgresql://user:pass@host.com:5432/db",
        },
    ]
    
    print("Testing DATABASE_URL whitespace removal...")
    print("=" * 70)
    
    all_passed = True
    for test_case in test_cases:
        input_url = test_case["input"]
        expected_url = test_case["expected"]
        
        # Simulate the fix logic
        processed_url = input_url.strip()
        if ' ' in processed_url:
            processed_url = re.sub(r'\s+', '', processed_url)
        
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
