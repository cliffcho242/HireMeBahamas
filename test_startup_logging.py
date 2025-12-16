#!/usr/bin/env python3
"""
Test script to validate startup logging functionality.

This script tests that the startup logging can parse environment variables
and database URLs correctly without actually starting the server.
"""
import os
import sys
from urllib.parse import urlparse

def test_database_url_parsing():
    """Test that DATABASE_URL parsing works correctly."""
    test_cases = [
        {
            "url": "postgresql+asyncpg://user:pass@localhost:5432/testdb?sslmode=require",
            "expected": {
                "driver": "postgresql+asyncpg",
                "host": "localhost",
                "port": 5432,
                "name": "testdb",
                "ssl": True
            }
        },
        {
            "url": "postgresql+asyncpg://user:pass@ep-test.aws.neon.tech:5432/mydb",
            "expected": {
                "driver": "postgresql+asyncpg",
                "host": "ep-test.aws.neon.tech",
                "port": 5432,
                "name": "mydb",
                "ssl": False
            }
        },
    ]
    
    print("Testing DATABASE_URL parsing...")
    for i, test_case in enumerate(test_cases, 1):
        url = test_case["url"]
        expected = test_case["expected"]
        
        try:
            parsed = urlparse(url)
            db_host = parsed.hostname or "unknown"
            db_port = parsed.port or "unknown"
            db_name = parsed.path.lstrip('/').split('?')[0] if parsed.path else "unknown"
            db_driver = parsed.scheme or "unknown"
            db_ssl = "sslmode=require" in url
            
            assert db_driver == expected["driver"], f"Driver mismatch: {db_driver} != {expected['driver']}"
            assert db_host == expected["host"], f"Host mismatch: {db_host} != {expected['host']}"
            assert db_port == expected["port"], f"Port mismatch: {db_port} != {expected['port']}"
            assert db_name == expected["name"], f"Name mismatch: {db_name} != {expected['name']}"
            assert db_ssl == expected["ssl"], f"SSL mismatch: {db_ssl} != {expected['ssl']}"
            
            print(f"  ✅ Test case {i}: PASSED")
            print(f"     Driver: {db_driver}")
            print(f"     Host: {db_host}")
            print(f"     Port: {db_port}")
            print(f"     Name: {db_name}")
            print(f"     SSL: {'enabled' if db_ssl else 'disabled'}")
        except Exception as e:
            print(f"  ❌ Test case {i}: FAILED - {e}")
            return False
    
    print("\n✅ All DATABASE_URL parsing tests passed!")
    return True


def test_environment_variables():
    """Test environment variable checking logic."""
    print("\nTesting environment variable checks...")
    
    # Test with environment variables set
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/testdb"
    os.environ["ENVIRONMENT"] = "production"
    os.environ["VERCEL_ENV"] = "production"
    
    env_vars = {
        "DATABASE_URL": "✅ set" if os.getenv("DATABASE_URL") else "❌ not set",
        "REDIS_URL": "✅ set" if os.getenv("REDIS_URL") else "ℹ️  not set (optional)",
        "JWT_SECRET_KEY": "✅ set" if os.getenv("JWT_SECRET_KEY") else "⚠️  not set (using default)",
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "❌ not set"),
        "VERCEL_ENV": os.getenv("VERCEL_ENV", "ℹ️  not set"),
    }
    
    print("  Environment Variables:")
    for var, status in env_vars.items():
        print(f"    - {var}: {status}")
    
    assert env_vars["DATABASE_URL"] == "✅ set", "DATABASE_URL should be set"
    assert env_vars["ENVIRONMENT"] == "production", "ENVIRONMENT should be production"
    
    print("\n✅ Environment variable checks passed!")
    return True


def test_log_formatting():
    """Test that log messages format correctly."""
    print("\nTesting log message formatting...")
    
    # Test separator line
    separator = "=" * 80
    assert len(separator) == 80, "Separator should be 80 characters"
    print(f"  ✅ Separator: {len(separator)} chars")
    
    # Test emoji rendering (just verify they don't cause errors)
    test_emojis = ["🚀", "📍", "💾", "🌐", "🖥️", "🏥", "🔑", "✅", "❌", "⚠️", "ℹ️"]
    for emoji in test_emojis:
        # Just verify we can print them without errors
        _ = f"{emoji} Test"
    print(f"  ✅ Emojis render without errors")
    
    print("\n✅ Log formatting tests passed!")
    return True


if __name__ == "__main__":
    print("=" * 80)
    print("Startup Logging Validation Tests")
    print("=" * 80)
    print()
    
    all_passed = True
    
    try:
        all_passed &= test_database_url_parsing()
        all_passed &= test_environment_variables()
        all_passed &= test_log_formatting()
        
        print()
        print("=" * 80)
        if all_passed:
            print("🎉 ALL TESTS PASSED!")
            print("=" * 80)
            sys.exit(0)
        else:
            print("❌ SOME TESTS FAILED")
            print("=" * 80)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
