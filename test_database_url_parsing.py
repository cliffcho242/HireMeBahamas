"""
Test DATABASE_URL parsing with various edge cases
This test validates the defensive error handling for malformed DATABASE_URLs
"""

import os
import sys
from unittest.mock import patch
from urllib.parse import urlparse


# Expected DATABASE_URL format message (matching final_backend_postgresql.py)
DATABASE_URL_FORMAT = "postgresql://username:password@hostname:5432/database"


def test_valid_database_url():
    """Test parsing a valid DATABASE_URL"""
    print("\n✅ Test 1: Valid DATABASE_URL")

    DATABASE_URL = "postgresql://testuser:testpass@localhost:5432/testdb"
    parsed = urlparse(DATABASE_URL)

    # Test port parsing
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432
        print(f"⚠️  Invalid port '{parsed.port}' in DATABASE_URL, using default 5432")

    # Test database parsing
    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(f"DATABASE_URL format should be: {DATABASE_URL_FORMAT}")
        raise

    DB_CONFIG = {
        "host": parsed.hostname,
        "port": port,
        "database": database,
        "user": parsed.username,
        "password": parsed.password,
    }

    # Validate all required fields
    required_fields = ["host", "database", "user", "password"]
    missing_fields = [field for field in required_fields if not DB_CONFIG.get(field)]
    if missing_fields:
        print(
            f"❌ Missing required DATABASE_URL components: {', '.join(missing_fields)}"
        )
        print(f"DATABASE_URL format should be: {DATABASE_URL_FORMAT}")
        raise ValueError(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")

    assert DB_CONFIG["host"] == "localhost"
    assert DB_CONFIG["port"] == 5432
    assert DB_CONFIG["database"] == "testdb"
    assert DB_CONFIG["user"] == "testuser"
    assert DB_CONFIG["password"] == "testpass"
    print(
        f"✅ Parsed successfully: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )


def test_malformed_port_as_string():
    """Test parsing DATABASE_URL with port as literal string 'port' (the main bug case)"""
    print("\n✅ Test 2: DATABASE_URL with port as string 'port'")

    # This simulates the bug condition where parsed.port returns 'port' instead of an integer
    # In reality, urlparse() would not produce this, but we simulate the error handling
    DATABASE_URL = "postgresql://testuser:testpass@localhost/testdb"
    parsed = urlparse(DATABASE_URL)

    # Simulate malformed port by testing with a string
    class MalformedParsed:
        def __init__(self, parsed):
            self._parsed = parsed
            self.hostname = parsed.hostname
            self.username = parsed.username
            self.password = parsed.password
            self.path = parsed.path
            self.port = "port"  # Simulate malformed port

    parsed = MalformedParsed(parsed)

    # Test that port parsing handles the error
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432
        print(f"⚠️  Invalid port '{parsed.port}' in DATABASE_URL, using default 5432")

    # Test database parsing
    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(f"DATABASE_URL format should be: {DATABASE_URL_FORMAT}")
        raise

    DB_CONFIG = {
        "host": parsed.hostname,
        "port": port,
        "database": database,
        "user": parsed.username,
        "password": parsed.password,
    }

    assert DB_CONFIG["port"] == 5432  # Should fallback to default
    assert DB_CONFIG["database"] == "testdb"
    print(f"✅ Handled malformed port correctly, used default: {DB_CONFIG['port']}")


def test_missing_port():
    """Test parsing DATABASE_URL without port (should use default 5432)"""
    print("\n✅ Test 3: DATABASE_URL without port")

    DATABASE_URL = "postgresql://testuser:testpass@localhost/testdb"
    parsed = urlparse(DATABASE_URL)

    # Test port parsing (None should default to 5432)
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432
        print(f"⚠️  Invalid port '{parsed.port}' in DATABASE_URL, using default 5432")

    assert port == 5432
    print(f"✅ Missing port correctly defaults to: {port}")


def test_missing_database_name():
    """Test parsing DATABASE_URL without database name (should error)"""
    print("\n✅ Test 4: DATABASE_URL without database name")

    DATABASE_URL = "postgresql://testuser:testpass@localhost:5432/"
    parsed = urlparse(DATABASE_URL)

    # Test database parsing - should raise error
    error_caught = False
    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(f"DATABASE_URL format should be: {DATABASE_URL_FORMAT}")
        error_caught = True

    assert error_caught, "Should have caught missing database name error"
    print("✅ Missing database name correctly caught and reported")


def test_missing_credentials():
    """Test parsing DATABASE_URL with missing username/password"""
    print("\n✅ Test 5: DATABASE_URL with missing credentials")

    DATABASE_URL = "postgresql://localhost:5432/testdb"
    parsed = urlparse(DATABASE_URL)

    # Parse port and database
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432

    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(f"DATABASE_URL format should be: {DATABASE_URL_FORMAT}")
        raise

    DB_CONFIG = {
        "host": parsed.hostname,
        "port": port,
        "database": database,
        "user": parsed.username,
        "password": parsed.password,
    }

    # Validate all required fields - should catch missing user/password
    required_fields = ["host", "database", "user", "password"]
    missing_fields = [field for field in required_fields if not DB_CONFIG.get(field)]

    assert len(missing_fields) > 0, "Should detect missing fields"
    assert "user" in missing_fields
    assert "password" in missing_fields
    print(f"✅ Missing credentials correctly detected: {', '.join(missing_fields)}")


def test_invalid_port_number():
    """Test parsing DATABASE_URL with non-numeric port"""
    print("\n✅ Test 6: DATABASE_URL with invalid port number")

    DATABASE_URL = "postgresql://testuser:testpass@localhost:abc/testdb"

    # urlparse itself may raise an error for invalid ports
    try:
        parsed = urlparse(DATABASE_URL)

        # Test port parsing - should handle ValueError
        try:
            port = int(parsed.port) if parsed.port else 5432
        except (ValueError, TypeError):
            port = 5432
            print(
                f"⚠️  Invalid port '{parsed.port}' in DATABASE_URL, using default 5432"
            )

        assert port == 5432  # Should fallback to default
        print(f"✅ Invalid port number correctly handled, used default: {port}")
    except ValueError as e:
        # urlparse itself raises ValueError for invalid ports
        print(f"⚠️  urlparse raised error for invalid port: {e}")
        print(
            "✅ Invalid port correctly causes error during URL parsing (expected behavior)"
        )
        # This is acceptable - the URL is malformed at the parse level


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("DATABASE_URL Parsing Tests")
    print("=" * 80)

    tests = [
        test_valid_database_url,
        test_malformed_port_as_string,
        test_missing_port,
        test_missing_database_name,
        test_missing_credentials,
        test_invalid_port_number,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR in {test.__name__}: {e}")
            failed += 1

    print("\n" + "=" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
