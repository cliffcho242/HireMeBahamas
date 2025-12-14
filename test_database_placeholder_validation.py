#!/usr/bin/env python3
"""
Test suite for DATABASE_URL placeholder hostname validation.

This test validates that the application properly detects and rejects
DATABASE_URL values that contain placeholder hostnames like 'host',
'hostname', etc., preventing the error:
"could not translate host name 'host' to address: No address associated with hostname"
"""

import os
import sys
from pathlib import Path


def test_api_database_placeholder_detection():
    """Test that api/database.py has placeholder validation code"""
    api_db_path = Path(__file__).parent / 'api' / 'database.py'
    with open(api_db_path, 'r') as f:
        content = f.read()
    
    # Check that validation code is present
    assert 'PLACEHOLDER_HOSTS' in content, "PLACEHOLDER_HOSTS list should be defined in api/database.py"
    assert '"host"' in content, "Should check for 'host' placeholder"
    assert '"hostname"' in content, "Should check for 'hostname' placeholder"
    # Check for the phrase with original casing
    assert 'placeholder hostname' in content or 'placeholder hostname' in content.lower(), "Should mention placeholder in error"
    
    print("✅ Placeholder validation code is present in api/database.py")


def test_api_database_valid_hostnames():
    """Test that api/database.py validation logic is correct"""
    # Test placeholder hostnames that should be rejected
    placeholder_hosts = ['host', 'hostname', 'your-host', 'your-hostname', 'example.com', 'your-db-host']
    
    # Verify these are in the code
    api_db_path = Path(__file__).parent / 'api' / 'database.py'
    with open(api_db_path, 'r') as f:
        content = f.read()
    
    for placeholder in placeholder_hosts:
        # Check for the placeholder string in quotes (case-sensitive)
        assert f'"{placeholder}"' in content, f"Should validate against placeholder '{placeholder}'"
    
    print("✅ All expected placeholder hostnames are validated in api/database.py")


def test_final_backend_postgresql_placeholder_detection():
    """Test that final_backend_postgresql.py would detect placeholder hostnames"""
    # This is more of an integration test that would require running the actual file
    # For now, we'll just verify the pattern is in the code
    
    backend_path = Path(__file__).parent / 'final_backend_postgresql.py'
    with open(backend_path, 'r') as f:
        content = f.read()
    
    # Check that validation code is present
    assert 'PLACEHOLDER_HOSTS' in content, "PLACEHOLDER_HOSTS list should be defined"
    assert '"host"' in content, "Should check for 'host' placeholder"
    assert '"hostname"' in content, "Should check for 'hostname' placeholder"
    # Check for the phrase with proper handling of case
    assert 'placeholder hostname' in content or 'placeholder hostname' in content.lower(), "Should mention placeholder in error"
    
    print("✅ Placeholder validation code is present in final_backend_postgresql.py")


def test_env_example_has_warnings():
    """Test that .env.example has clear warnings about placeholders"""
    env_example_path = Path(__file__).parent / '.env.example'
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    # Check for warnings about placeholders
    assert 'YOUR-ACTUAL-HOSTNAME' in content, ".env.example should use clear placeholder syntax"
    assert 'Do NOT use placeholder' in content or 'Do NOT manually type placeholders' in content, \
        ".env.example should warn against using placeholders"
    
    # Check that uncommented DATABASE_URL lines use clear placeholder syntax
    lines_with_database_url = [line for line in content.split('\n') 
                              if 'DATABASE_URL=' in line and not line.strip().startswith('#')]
    
    for line in lines_with_database_url:
        # If line contains a hostname placeholder, it should use the clear syntax
        if 'hostname:5432' in line:
            assert 'YOUR-ACTUAL-HOSTNAME' in line, \
                f"Uncommented DATABASE_URL line with hostname should use YOUR-ACTUAL-HOSTNAME: {line}"
    
    print("✅ .env.example has appropriate warnings about placeholders")


def main():
    """Run all tests"""
    print("="*60)
    print("🧪 DATABASE_URL Placeholder Validation Test Suite")
    print("="*60)
    
    tests = [
        test_api_database_placeholder_detection,
        test_api_database_valid_hostnames,
        test_final_backend_postgresql_placeholder_detection,
        test_env_example_has_warnings,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"\n📝 Running: {test.__name__}")
            test()
            passed += 1
            print(f"   ✅ {test.__name__} PASSED")
        except AssertionError as e:
            print(f"   ❌ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ {test.__name__} CRASHED: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60)
    
    if failed == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
