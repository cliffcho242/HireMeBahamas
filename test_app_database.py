"""
Test app/database.py - Bulletproof DATABASE_URL parsing
This test validates the bulletproof database initialization function
"""

import os
import sys
import logging
from unittest.mock import patch, MagicMock

# Configure logging to see test output
logging.basicConfig(level=logging.INFO)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_missing_database_url():
    """Test that init_db returns None when DATABASE_URL is not set"""
    print("\n✅ Test 1: Missing DATABASE_URL")

    with patch.dict(os.environ, {}, clear=True):
        # Clear any module cache
        if "app.database" in sys.modules:
            del sys.modules["app.database"]

        # Import fresh to get DATABASE_URL = None
        import app.database as db_module

        # Force DATABASE_URL to None for this test
        original_url = db_module.DATABASE_URL
        db_module.DATABASE_URL = None
        db_module.engine = None

        try:
            result = db_module.init_db()
            assert result is None, "Expected None when DATABASE_URL is not set"
            print("✓ Correctly returns None when DATABASE_URL is missing")
        finally:
            # Restore original value
            db_module.DATABASE_URL = original_url


def test_invalid_database_url_missing_credentials():
    """Test that init_db returns None when DATABASE_URL is missing credentials"""
    print("\n✅ Test 2: Invalid DATABASE_URL (missing credentials)")

    invalid_url = "postgresql://@localhost:5432/testdb"

    with patch.dict(os.environ, {"DATABASE_URL": invalid_url}, clear=True):
        # Clear module cache to reload with new env
        if "app.database" in sys.modules:
            del sys.modules["app.database"]

        import app.database as db_module

        db_module.engine = None

        result = db_module.init_db()
        assert result is None, "Expected None when credentials are missing"
        print("✓ Correctly returns None when credentials are missing")


def test_invalid_database_url_missing_host():
    """Test that init_db returns None when DATABASE_URL is missing host"""
    print("\n✅ Test 3: Invalid DATABASE_URL (missing host)")

    # URL with credentials but no host
    invalid_url = "postgresql://user:pass@:5432/testdb"

    with patch.dict(os.environ, {"DATABASE_URL": invalid_url}, clear=True):
        if "app.database" in sys.modules:
            del sys.modules["app.database"]

        import app.database as db_module

        db_module.engine = None

        result = db_module.init_db()
        assert result is None, "Expected None when host is missing"
        print("✓ Correctly returns None when host is missing")


def test_malformed_database_url():
    """Test that init_db returns None when DATABASE_URL is malformed"""
    print("\n✅ Test 4: Malformed DATABASE_URL")

    invalid_url = "not-a-valid-url"

    with patch.dict(os.environ, {"DATABASE_URL": invalid_url}, clear=True):
        if "app.database" in sys.modules:
            del sys.modules["app.database"]

        import app.database as db_module

        db_module.engine = None

        result = db_module.init_db()
        assert result is None, "Expected None when DATABASE_URL is malformed"
        print("✓ Correctly returns None when DATABASE_URL is malformed")


def test_valid_database_url_structure():
    """Test that init_db properly validates URL structure"""
    print("\n✅ Test 5: Valid DATABASE_URL structure validation")

    valid_url = "postgresql://testuser:testpass@localhost:5432/testdb"

    with patch.dict(os.environ, {"DATABASE_URL": valid_url}, clear=True):
        if "app.database" in sys.modules:
            del sys.modules["app.database"]

        import app.database as db_module

        # Mock create_engine to avoid actual connection
        with patch("app.database.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine

            db_module.engine = None
            result = db_module.init_db()

            # Verify create_engine was called with correct parameters
            assert mock_create_engine.called, "create_engine should be called"
            call_args = mock_create_engine.call_args

            # Verify pool configuration
            assert (
                call_args.kwargs["pool_pre_ping"] is True
            ), "pool_pre_ping should be True"
            assert call_args.kwargs["pool_recycle"] == 300, "pool_recycle should be 300"
            assert (
                call_args.kwargs["connect_args"]["sslmode"] == "require"
            ), "sslmode should be require"

            # Verify result is the engine
            assert result == mock_engine, "Should return the engine"
            print("✓ Correctly validates URL structure and creates engine")
            print(f"  - pool_pre_ping: {call_args.kwargs['pool_pre_ping']}")
            print(f"  - pool_recycle: {call_args.kwargs['pool_recycle']}")
            print(f"  - sslmode: {call_args.kwargs['connect_args']['sslmode']}")


def test_url_validation_with_make_url():
    """Test that make_url properly parses and validates URLs"""
    print("\n✅ Test 6: URL parsing with make_url")

    from sqlalchemy.engine.url import make_url

    # Test valid URL
    valid_url = "postgresql://user:pass@host:5432/db"
    url = make_url(valid_url)

    assert url.username == "user", "Username should be parsed correctly"
    assert url.password == "pass", "Password should be parsed correctly"
    assert url.host == "host", "Host should be parsed correctly"
    assert url.database == "db", "Database should be parsed correctly"
    print("✓ make_url correctly parses valid URLs")

    # Test URL with missing username
    invalid_url = "postgresql://:pass@host:5432/db"
    url = make_url(invalid_url)
    assert not url.username, "Username should be None or empty"
    print("✓ make_url handles missing username")


def test_engine_configuration():
    """Test that engine is configured with bulletproof settings"""
    print("\n✅ Test 7: Engine configuration")

    valid_url = "postgresql://testuser:testpass@localhost:5432/testdb"

    with patch.dict(os.environ, {"DATABASE_URL": valid_url}, clear=True):
        if "app.database" in sys.modules:
            del sys.modules["app.database"]

        import app.database as db_module

        with patch("app.database.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine

            db_module.engine = None
            db_module.init_db()

            # Get the call arguments
            call_args = mock_create_engine.call_args

            # Verify bulletproof configuration
            print("  Engine configuration:")
            print(f"    - pool_pre_ping: {call_args.kwargs.get('pool_pre_ping')}")
            print(f"    - pool_recycle: {call_args.kwargs.get('pool_recycle')}")
            print(
                f"    - sslmode: {call_args.kwargs.get('connect_args', {}).get('sslmode')}"
            )

            assert (
                call_args.kwargs.get("pool_pre_ping") is True
            ), "pool_pre_ping must be True"
            assert (
                call_args.kwargs.get("pool_recycle") == 300
            ), "pool_recycle must be 300"
            assert (
                call_args.kwargs.get("connect_args", {}).get("sslmode") == "require"
            ), "sslmode must be require"
            print("✓ Engine configured with bulletproof settings")


def test_no_crashes_on_error():
    """Test that init_db never crashes, always returns None on error"""
    print("\n✅ Test 8: No crashes on any error")

    test_cases = [
        ("", "Empty string"),
        ("postgresql://", "Incomplete URL"),
        ("postgresql://user@host/db", "Missing password"),
        ("postgresql://user:@host/db", "Empty password"),
        ("postgresql://:pass@host/db", "Missing username"),
        ("http://invalid:url@host/db", "Wrong protocol"),
    ]

    for url, description in test_cases:
        with patch.dict(os.environ, {"DATABASE_URL": url} if url else {}, clear=True):
            if "app.database" in sys.modules:
                del sys.modules["app.database"]

            try:
                import app.database as db_module

                db_module.engine = None
                result = db_module.init_db()
                assert result is None, f"Expected None for {description}"
                print(f"  ✓ {description}: No crash, returns None")
            except Exception as e:
                raise AssertionError(f"init_db crashed with {description}: {e}")


def test_logging_output():
    """Test that appropriate log messages are generated"""
    print("\n✅ Test 9: Logging output")

    # Test missing URL logging
    with patch.dict(os.environ, {}, clear=True):
        if "app.database" in sys.modules:
            del sys.modules["app.database"]

        import app.database as db_module

        db_module.DATABASE_URL = None
        db_module.engine = None

        with patch("logging.warning") as mock_warning:
            db_module.init_db()
            mock_warning.assert_called_once_with("DATABASE_URL is not set")
            print("✓ Logs warning when DATABASE_URL is not set")

    # Test success logging
    valid_url = "postgresql://testuser:testpass@localhost:5432/testdb"
    with patch.dict(os.environ, {"DATABASE_URL": valid_url}, clear=True):
        if "app.database" in sys.modules:
            del sys.modules["app.database"]

        import app.database as db_module

        with patch("app.database.create_engine") as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine

            with patch("logging.info") as mock_info:
                db_module.engine = None
                db_module.init_db()
                mock_info.assert_called_once_with(
                    "Database engine initialized successfully"
                )
                print("✓ Logs success message when engine is initialized")


if __name__ == "__main__":
    print("=" * 70)
    print("Testing Bulletproof Database Parsing (app/database.py)")
    print("=" * 70)

    test_missing_database_url()
    test_invalid_database_url_missing_credentials()
    test_invalid_database_url_missing_host()
    test_malformed_database_url()
    test_valid_database_url_structure()
    test_url_validation_with_make_url()
    test_engine_configuration()
    test_no_crashes_on_error()
    test_logging_output()

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED - Bulletproof database parsing works correctly!")
    print("=" * 70)
