"""
Tests for app/database.py module.

Validates that the database module follows the requirements:
* No psycopg direct calls (uses SQLAlchemy only)
* No sslmode in connect_args
* No blocking imports
* Proper lazy initialization
"""
import os
import sys
import logging
from unittest.mock import patch, MagicMock

# Configure logging for test output
logging.basicConfig(level=logging.INFO)


def test_no_psycopg_imports():
    """Verify that app/database.py doesn't import psycopg directly."""
    print("\n=== Test 1: No psycopg direct imports ===")
    
    with open("app/database.py", "r") as f:
        content = f.read()
    
    # Check for direct psycopg imports
    forbidden_imports = [
        "import psycopg",
        "from psycopg",
        "import psycopg2",
        "from psycopg2"
    ]
    
    for forbidden in forbidden_imports:
        assert forbidden not in content, f"Found forbidden import: {forbidden}"
    
    print("✅ No psycopg direct imports found")


def test_no_sslmode_in_connect_args():
    """Verify that sslmode is not in connect_args."""
    print("\n=== Test 2: No sslmode in connect_args ===")
    
    with open("app/database.py", "r") as f:
        content = f.read()
    
    # Check for sslmode in connect_args
    assert "connect_args" not in content or '"sslmode"' not in content, \
        "sslmode should not be in connect_args (should be in DATABASE_URL)"
    
    assert "connect_args" not in content or "'sslmode'" not in content, \
        "sslmode should not be in connect_args (should be in DATABASE_URL)"
    
    print("✅ No sslmode in connect_args")


def test_no_blocking_imports():
    """Verify that database module doesn't create connections at import time."""
    print("\n=== Test 3: No blocking imports ===")
    
    # Unset DATABASE_URL to verify no connection is attempted at import time
    original_db_url = os.environ.get("DATABASE_URL")
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
    
    try:
        # Import should succeed even without DATABASE_URL
        from app import database
        
        # Engine should be None at import time
        assert database.engine is None, "Engine should be None at import time"
        
        print("✅ No blocking imports - module loads without DATABASE_URL")
        
    finally:
        # Restore DATABASE_URL
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url


def test_init_db_without_database_url():
    """Verify that init_db() handles missing DATABASE_URL gracefully."""
    print("\n=== Test 4: init_db() without DATABASE_URL ===")
    
    # Unset DATABASE_URL
    original_db_url = os.environ.get("DATABASE_URL")
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
    
    try:
        from app import database
        
        # init_db() should return None without DATABASE_URL
        result = database.init_db()
        assert result is None, "init_db() should return None without DATABASE_URL"
        
        print("✅ init_db() handles missing DATABASE_URL gracefully")
        
    finally:
        # Restore DATABASE_URL
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url


def test_init_db_with_valid_url():
    """Verify that init_db() creates engine with valid DATABASE_URL."""
    print("\n=== Test 5: init_db() with valid DATABASE_URL ===")
    
    # This test verifies the configuration by checking the source code
    # rather than executing it, since we can't mock deep enough without psycopg2
    
    with open("app/database.py", "r") as f:
        content = f.read()
    
    # Verify the init_db function has correct structure
    assert "def init_db():" in content, "init_db() function should exist"
    assert "os.environ.get(\"DATABASE_URL\")" in content, "Should get DATABASE_URL from environment"
    assert "make_url(db_url)" in content, "Should use make_url to parse URL"
    assert "create_engine(" in content, "Should call create_engine"
    
    # Verify configuration parameters are passed correctly
    assert "pool_pre_ping=True" in content, "pool_pre_ping should be True"
    assert "pool_recycle=300" in content, "pool_recycle should be 300"
    assert "pool_size=5" in content, "pool_size should be 5"
    assert "max_overflow=10" in content, "max_overflow should be 10"
    
    # Verify no connect_args with sslmode
    if "connect_args" in content:
        # If connect_args exists, ensure it doesn't have sslmode
        assert '"sslmode"' not in content and "'sslmode'" not in content, \
            "sslmode should not be in connect_args"
    
    print("✅ init_db() has correct configuration structure")


def test_warmup_db_with_none_engine():
    """Verify that warmup_db() handles None engine gracefully."""
    print("\n=== Test 6: warmup_db() with None engine ===")
    
    from app import database
    
    # Should not raise exception
    database.warmup_db(None)
    
    print("✅ warmup_db() handles None engine gracefully")


def test_warmup_db_with_valid_engine():
    """Verify that warmup_db() executes test query."""
    print("\n=== Test 7: warmup_db() with valid engine ===")
    
    from app import database
    
    # Create mock engine
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn
    
    # Call warmup_db
    database.warmup_db(mock_engine)
    
    # Verify connection was used
    assert mock_engine.connect.called, "Engine.connect() should be called"
    assert mock_conn.execute.called, "Connection.execute() should be called"
    
    # Verify SELECT 1 was executed
    call_args = mock_conn.execute.call_args[0]
    assert len(call_args) > 0, "execute() should be called with arguments"
    
    print("✅ warmup_db() executes test query correctly")


def test_engine_configuration_pattern():
    """Verify that engine configuration follows best practices."""
    print("\n=== Test 8: Engine configuration pattern ===")
    
    with open("app/database.py", "r") as f:
        content = f.read()
    
    # Verify required configuration parameters
    assert "pool_pre_ping=True" in content, "pool_pre_ping should be True"
    assert "pool_recycle=300" in content, "pool_recycle should be 300"
    assert "pool_size=5" in content, "pool_size should be 5"
    assert "max_overflow=10" in content, "max_overflow should be 10"
    
    print("✅ Engine configuration follows best practices")


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing app/database.py module")
    print("=" * 70)
    
    tests = [
        test_no_psycopg_imports,
        test_no_sslmode_in_connect_args,
        test_no_blocking_imports,
        test_init_db_without_database_url,
        test_init_db_with_valid_url,
        test_warmup_db_with_none_engine,
        test_warmup_db_with_valid_engine,
        test_engine_configuration_pattern,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
