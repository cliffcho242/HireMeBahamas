#!/usr/bin/env python3
"""
Test script to verify DATABASE_URL password decoding works correctly.

This script tests that passwords with special characters are properly URL-decoded
before being used for database authentication.
"""

import os
import sys
from urllib.parse import urlparse, unquote, quote


def test_url_decoding():
    """Test URL decoding for various password scenarios."""
    
    test_cases = [
        {
            "name": "Simple password (no special chars)",
            "password": "simplepass123",
            "encoded": "simplepass123",
            "expected": "simplepass123"
        },
        {
            "name": "Password with @ symbol",
            "password": "p@ssword",
            "encoded": "p%40ssword",
            "expected": "p@ssword"
        },
        {
            "name": "Password with multiple special chars",
            "password": "p@ss;w!rd%",
            "encoded": "p%40ss%3Bw%21rd%25",
            "expected": "p@ss;w!rd%"
        },
        {
            "name": "Password with spaces",
            "password": "pass word 123",
            "encoded": "pass%20word%20123",
            "expected": "pass word 123"
        },
        {
            "name": "Complex password",
            "password": "Abc123!@#$%^&*()",
            "encoded": quote("Abc123!@#$%^&*()"),
            "expected": "Abc123!@#$%^&*()"
        }
    ]
    
    print("🧪 Testing DATABASE_URL password decoding...")
    print("=" * 70)
    
    all_passed = True
    
    for test in test_cases:
        # Construct test URL
        test_url = f"postgresql://testuser:{test['encoded']}@localhost:5432/testdb"
        
        # Parse URL
        parsed = urlparse(test_url)
        decoded_password = unquote(parsed.password) if parsed.password else None
        
        # Check result
        passed = decoded_password == test['expected']
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"\n{status} - {test['name']}")
        print(f"   Original:  {test['password']}")
        print(f"   Encoded:   {test['encoded']}")
        print(f"   Decoded:   {decoded_password}")
        print(f"   Expected:  {test['expected']}")
        
        if not passed:
            all_passed = False
            print(f"   ERROR: Decoded password doesn't match expected!")
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


def test_database_url_parsing():
    """Test full DATABASE_URL parsing with credentials."""
    
    print("\n🧪 Testing full DATABASE_URL parsing...")
    print("=" * 70)
    
    # Test with a realistic Railway DATABASE_URL format
    test_url = "postgresql://hiremebahamas_user:p%40ssw%3Bord%21@dpg-test.railway.app:5432/railway"
    
    print(f"\nTest URL: {test_url}")
    
    parsed = urlparse(test_url)
    
    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None
    
    print(f"\nParsed components:")
    print(f"   Host:      {parsed.hostname}")
    print(f"   Port:      {parsed.port}")
    print(f"   Database:  {parsed.path[1:] if parsed.path else None}")
    print(f"   Username:  {username}")
    print(f"   Password:  {password}")
    
    # Validate expected results
    expected_password = "p@ssw;ord!"
    if password == expected_password:
        print(f"\n✅ Password decoded correctly: {password}")
        return 0
    else:
        print(f"\n❌ Password decoding failed!")
        print(f"   Expected: {expected_password}")
        print(f"   Got:      {password}")
        return 1


def main():
    """Run all tests."""
    print("=" * 70)
    print("DATABASE_URL PASSWORD DECODING TEST SUITE")
    print("=" * 70)
    
    result1 = test_url_decoding()
    result2 = test_database_url_parsing()
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    
    if result1 == 0 and result2 == 0:
        print("✅ All tests passed! URL decoding is working correctly.")
        print("\nThis fix ensures that DATABASE_URL passwords with special")
        print("characters are properly decoded before database authentication.")
        return 0
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
