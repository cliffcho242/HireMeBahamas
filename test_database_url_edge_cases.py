#!/usr/bin/env python3
"""
Test database URL parsing edge cases to identify password authentication issues.

This test checks for common issues that can cause password authentication to fail:
1. Trailing/leading whitespace in DATABASE_URL
2. Double URL encoding
3. Empty or None password fields
4. Special characters that may not be properly decoded
5. Mixed encoding (partially encoded passwords)
"""

from urllib.parse import urlparse, unquote, quote
import sys


def test_url_parsing(test_name, database_url, expected_password):
    """Test URL parsing with expected password"""
    print(f"\n{'='*70}")
    print(f"Test: {test_name}")
    print(f"{'='*70}")
    print(f"DATABASE_URL: {database_url}")
    print(f"Expected password: {expected_password}")
    
    try:
        # Strip whitespace from URL (this may be missing in the actual code)
        cleaned_url = database_url.strip()
        print(f"After strip: {cleaned_url}")
        
        parsed = urlparse(cleaned_url)
        
        # URL decode credentials
        username = unquote(parsed.username) if parsed.username else None
        password = unquote(parsed.password) if parsed.password else None
        
        print(f"Parsed username: {username}")
        print(f"Parsed password: {password}")
        print(f"Password match: {password == expected_password}")
        
        if password != expected_password:
            print(f"❌ FAIL: Password mismatch!")
            print(f"   Expected: {repr(expected_password)}")
            print(f"   Got:      {repr(password)}")
            return False
        else:
            print(f"✅ PASS: Password correctly decoded")
            return True
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False


def test_edge_cases():
    """Run comprehensive edge case tests"""
    
    tests = [
        # Test 1: Simple password without special characters
        (
            "Simple password",
            "postgresql://user:password123@host:5432/db",
            "password123"
        ),
        
        # Test 2: Password with @ symbol (URL-encoded as %40)
        (
            "Password with @ symbol",
            "postgresql://user:p%40ssword@host:5432/db",
            "p@ssword"
        ),
        
        # Test 3: Password with multiple special characters
        (
            "Password with multiple special chars",
            "postgresql://user:p%40ssw%3Bord%21@host:5432/db",
            "p@ssw;ord!"
        ),
        
        # Test 4: URL with trailing whitespace
        (
            "URL with trailing whitespace",
            "postgresql://user:password123@host:5432/db   \n",
            "password123"
        ),
        
        # Test 5: URL with leading whitespace
        (
            "URL with leading whitespace",
            "   postgresql://user:password123@host:5432/db",
            "password123"
        ),
        
        # Test 6: Password with percent symbol (double encoded: % -> %25)
        (
            "Password with % symbol",
            "postgresql://user:pass%25word@host:5432/db",
            "pass%word"
        ),
        
        # Test 7: Password with space (encoded as %20)
        (
            "Password with space",
            "postgresql://user:pass%20word@host:5432/db",
            "pass word"
        ),
        
        # Test 8: Complex Railway-style password
        (
            "Complex Railway password",
            "postgresql://postgres:G%23kL9%40mX%24pR8%26nT5%21qW2@containers-us-west-1.railway.app:5432/railway",
            "G#kL9@mX$pR8&nT5!qW2"
        ),
        
        # Test 9: Password already decoded (not URL-encoded)
        # This tests backward compatibility
        (
            "Plain password without encoding",
            "postgresql://user:simplepass@host:5432/db",
            "simplepass"
        ),
        
        # Test 10: Empty password
        (
            "Empty password",
            "postgresql://user:@host:5432/db",
            ""
        ),
        
        # Test 11: No password field (should return None)
        (
            "No password field",
            "postgresql://user@host:5432/db",
            None
        ),
    ]
    
    print("=" * 70)
    print("DATABASE URL PASSWORD PARSING EDGE CASE TESTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, database_url, expected_password in tests:
        if test_url_parsing(test_name, database_url, expected_password):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Total tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n✅ All tests passed! URL decoding is working correctly.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed! URL decoding has issues.")
        return 1


def test_double_encoding():
    """Test for double encoding issues"""
    print(f"\n{'='*70}")
    print("DOUBLE ENCODING TEST")
    print(f"{'='*70}")
    
    # Original password with @ symbol
    original_password = "p@ssword"
    print(f"Original password: {original_password}")
    
    # First encoding: @ -> %40
    encoded_once = quote(original_password, safe='')
    print(f"Encoded once: {encoded_once}")
    
    # Double encoding: %40 -> %2540
    encoded_twice = quote(encoded_once, safe='')
    print(f"Encoded twice (WRONG): {encoded_twice}")
    
    # Test with single encoding (CORRECT)
    url_correct = f"postgresql://user:{encoded_once}@host:5432/db"
    parsed_correct = urlparse(url_correct)
    decoded_correct = unquote(parsed_correct.password) if parsed_correct.password else None
    print(f"\nCorrect URL: {url_correct}")
    print(f"Decoded password (correct): {decoded_correct}")
    print(f"Match: {decoded_correct == original_password}")
    
    # Test with double encoding (WRONG)
    url_wrong = f"postgresql://user:{encoded_twice}@host:5432/db"
    parsed_wrong = urlparse(url_wrong)
    decoded_wrong = unquote(parsed_wrong.password) if parsed_wrong.password else None
    print(f"\nWrong URL (double encoded): {url_wrong}")
    print(f"Decoded password (wrong): {decoded_wrong}")
    print(f"Match: {decoded_wrong == original_password}")
    
    if decoded_correct == original_password and decoded_wrong != original_password:
        print("\n✅ Double encoding detected correctly")
        return 0
    else:
        print("\n❌ Issue with encoding detection")
        return 1


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DATABASE PASSWORD URL DECODING TEST SUITE")
    print("="*70)
    
    result1 = test_edge_cases()
    result2 = test_double_encoding()
    
    sys.exit(max(result1, result2))
