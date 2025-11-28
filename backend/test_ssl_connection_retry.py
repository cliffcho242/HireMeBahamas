"""
Test SSL connection retry behavior.

This test suite verifies that the execute_query function correctly handles
SSL errors by retrying with a fresh connection.
"""

import sys
import os
from unittest import mock
from pathlib import Path

# Add parent directory to path for imports
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))


class MockSSLError(Exception):
    """Mock SSL error for testing."""
    def __init__(self, message="SSL error: decryption failed or bad record mac"):
        super().__init__(message)


class MockOtherError(Exception):
    """Mock non-SSL error for testing."""
    pass


def test_is_stale_ssl_connection_error_detection():
    """Test that SSL errors are correctly detected."""
    from final_backend_postgresql import _is_stale_ssl_connection_error
    
    # Test SSL errors that should be detected
    ssl_error_messages = [
        "decryption failed or bad record mac",
        "SSL error: decryption failed or bad record mac",
        "bad record mac",
        "ssl error: unexpected eof",
        "unexpected eof while reading",
        "ssl connection has been closed unexpectedly",
        "connection reset by peer",
        "connection timed out",
    ]
    
    # Mock psycopg2.Error for testing
    import psycopg2
    
    for msg in ssl_error_messages:
        # Create a mock psycopg2.Error with the error message
        error = psycopg2.OperationalError(msg)
        assert _is_stale_ssl_connection_error(error), \
            f"Expected '{msg}' to be detected as SSL error"
        print(f"✓ SSL error detected: '{msg}'")
    
    # Test non-SSL errors that should NOT be detected
    non_ssl_errors = [
        "syntax error at position 5",
        "relation does not exist",
        "permission denied",
        "unique constraint violation",
        "foreign key violation",
    ]
    
    for msg in non_ssl_errors:
        error = psycopg2.OperationalError(msg)
        assert not _is_stale_ssl_connection_error(error), \
            f"Expected '{msg}' to NOT be detected as SSL error"
        print(f"✓ Non-SSL error correctly not matched: '{msg}'")
    
    # Test non-psycopg2 errors
    assert not _is_stale_ssl_connection_error(ValueError("ssl error")), \
        "ValueError should not be detected as SSL error"
    assert not _is_stale_ssl_connection_error(Exception("bad record mac")), \
        "Generic Exception should not be detected as SSL error"
    print("✓ Non-psycopg2 errors correctly not matched")
    
    print("\n✅ All SSL error detection tests passed!")


def test_is_transient_connection_error_detection():
    """Test that transient connection errors are correctly detected."""
    from final_backend_postgresql import _is_transient_connection_error
    
    import psycopg2
    
    # Test transient errors that should be detected
    transient_messages = [
        "connection refused",
        "could not connect to server",
        "server closed the connection unexpectedly",
        "connection reset by peer",
        "timeout expired",
        "the database system is starting up",
        "the database system is in recovery mode",
        "too many connections for role",
        "connection is closed",
        "terminating connection due to administrator command",
        "unexpected eof while reading",
        "ssl connection has been closed unexpectedly",
        "decryption failed or bad record mac",
    ]
    
    for msg in transient_messages:
        error = psycopg2.OperationalError(msg)
        assert _is_transient_connection_error(error), \
            f"Expected '{msg}' to be detected as transient error"
        print(f"✓ Transient error detected: '{msg}'")
    
    # Test non-transient errors
    non_transient_errors = [
        "syntax error",
        "relation does not exist",
        "column does not exist",
    ]
    
    for msg in non_transient_errors:
        error = psycopg2.OperationalError(msg)
        assert not _is_transient_connection_error(error), \
            f"Expected '{msg}' to NOT be detected as transient error"
        print(f"✓ Non-transient error correctly not matched: '{msg}'")
    
    print("\n✅ All transient error detection tests passed!")


def test_execute_query_internal_function_exists():
    """Test that the internal query execution helper exists."""
    from final_backend_postgresql import _execute_query_internal
    
    # Just verify the function is importable
    assert callable(_execute_query_internal), \
        "_execute_query_internal should be callable"
    print("✓ _execute_query_internal function exists")
    print("\n✅ Internal function test passed!")


def test_execute_query_retry_logic_structure():
    """Test that execute_query has retry logic for SSL errors."""
    import inspect
    from final_backend_postgresql import execute_query
    
    # Get the source code of execute_query
    source = inspect.getsource(execute_query)
    
    # Verify the function contains retry-related code
    assert "max_attempts" in source, \
        "execute_query should have max_attempts variable"
    assert "for attempt in range" in source, \
        "execute_query should have retry loop"
    assert "_is_stale_ssl_connection_error" in source, \
        "execute_query should check for SSL errors"
    assert "retrying with fresh connection" in source, \
        "execute_query should log retry attempts"
    
    print("✓ execute_query contains retry logic")
    print("✓ execute_query checks for SSL errors")
    print("✓ execute_query logs retry attempts")
    print("\n✅ Execute query retry structure test passed!")


def test_validate_connection_function():
    """Test the connection validation function."""
    from final_backend_postgresql import _validate_connection
    
    # Test with None connection
    result = _validate_connection(None)
    assert result is False, "None connection should fail validation"
    print("✓ None connection fails validation")
    
    # Test with mock connection that fails
    class MockBadConnection:
        def cursor(self):
            raise Exception("Connection is bad")
    
    result = _validate_connection(MockBadConnection())
    assert result is False, "Bad connection should fail validation"
    print("✓ Bad connection fails validation")
    
    print("\n✅ Connection validation tests passed!")


def test_discard_connection_function():
    """Test the connection discard function."""
    from final_backend_postgresql import _discard_connection
    
    # Test with None connection (should not raise)
    _discard_connection(None)
    print("✓ Discarding None connection doesn't raise")
    
    # Test with mock connection
    class MockConnection:
        def __init__(self):
            self.closed = False
        
        def close(self):
            self.closed = True
    
    conn = MockConnection()
    _discard_connection(conn)
    assert conn.closed, "Connection should be closed after discard"
    print("✓ Connection is closed after discard")
    
    # Test with connection that raises on close
    class MockBadConnection:
        def close(self):
            raise Exception("Close failed")
    
    # Should not raise
    _discard_connection(MockBadConnection())
    print("✓ Exception during close is handled gracefully")
    
    print("\n✅ Connection discard tests passed!")


def test_tcp_keepalive_configuration():
    """Test that TCP keepalive settings are properly configured."""
    from final_backend_postgresql import (
        TCP_KEEPALIVE_ENABLED, TCP_KEEPALIVE_IDLE, TCP_KEEPALIVE_INTERVAL,
        TCP_KEEPALIVE_COUNT, TCP_USER_TIMEOUT_MS
    )
    
    # Verify keepalive is enabled by default
    assert TCP_KEEPALIVE_ENABLED == 1, \
        f"TCP keepalive should be enabled by default, got {TCP_KEEPALIVE_ENABLED}"
    print("✓ TCP keepalive is enabled by default")
    
    # Verify keepalive idle time is aggressive (20 seconds)
    assert TCP_KEEPALIVE_IDLE == 20, \
        f"TCP keepalive idle should be 20s, got {TCP_KEEPALIVE_IDLE}s"
    print("✓ TCP keepalive idle is 20 seconds")
    
    # Verify keepalive interval is aggressive (5 seconds)
    assert TCP_KEEPALIVE_INTERVAL == 5, \
        f"TCP keepalive interval should be 5s, got {TCP_KEEPALIVE_INTERVAL}s"
    print("✓ TCP keepalive interval is 5 seconds")
    
    # Verify keepalive count is 3
    assert TCP_KEEPALIVE_COUNT == 3, \
        f"TCP keepalive count should be 3, got {TCP_KEEPALIVE_COUNT}"
    print("✓ TCP keepalive count is 3")
    
    # Verify tcp_user_timeout is configured (20000ms = 20 seconds)
    assert TCP_USER_TIMEOUT_MS == 20000, \
        f"TCP user timeout should be 20000ms, got {TCP_USER_TIMEOUT_MS}ms"
    print("✓ TCP user timeout is 20000ms (20 seconds)")
    
    # Verify total detection time is reasonable (35 seconds)
    total_detection = TCP_KEEPALIVE_IDLE + (TCP_KEEPALIVE_INTERVAL * TCP_KEEPALIVE_COUNT)
    assert total_detection == 35, \
        f"Total detection time should be 35s, got {total_detection}s"
    print(f"✓ Total keepalive detection time is {total_detection} seconds")
    
    print("\n✅ TCP keepalive configuration tests passed!")


def run_all_tests():
    """Run all SSL connection retry tests."""
    print("=" * 70)
    print("SSL Connection Retry Tests")
    print("=" * 70)
    
    test_functions = [
        test_is_stale_ssl_connection_error_detection,
        test_is_transient_connection_error_detection,
        test_execute_query_internal_function_exists,
        test_execute_query_retry_logic_structure,
        test_validate_connection_function,
        test_discard_connection_function,
        test_tcp_keepalive_configuration,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            print(f"\n--- {test_func.__name__} ---")
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
