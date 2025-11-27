"""
Test login request timeout functionality.

This test verifies that the login endpoint properly handles request timeouts
to prevent HTTP 499 (Client Closed Request) errors.
"""
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def test_check_request_timeout_returns_false_when_not_timed_out():
    """Test that _check_request_timeout returns False when request has not timed out."""
    # Import the function after adding to path
    from final_backend_postgresql import _check_request_timeout, app, g
    
    # Use Flask app context
    with app.app_context():
        g.request_id = 'test123'
        start_time = time.time()
        timeout_seconds = 25.0
        
        # Request just started, should not be timed out
        result = _check_request_timeout(start_time, timeout_seconds, "test operation")
        
        assert result is False, "Request that just started should not be timed out"


def test_check_request_timeout_returns_true_when_timed_out():
    """Test that _check_request_timeout returns True when request has timed out."""
    from final_backend_postgresql import _check_request_timeout, app, g
    
    # Use Flask app context
    with app.app_context():
        g.request_id = 'test123'
        # Simulate a request that started 30 seconds ago
        start_time = time.time() - 30
        timeout_seconds = 25.0
        
        # Request should be timed out
        result = _check_request_timeout(start_time, timeout_seconds, "test operation")
        
        assert result is True, "Request that exceeded timeout should return True"
        
        assert result is True, "Request that exceeded timeout should return True"


def test_login_request_timeout_config():
    """Test that LOGIN_REQUEST_TIMEOUT_SECONDS is properly configured."""
    from final_backend_postgresql import LOGIN_REQUEST_TIMEOUT_SECONDS
    
    # Default should be 25 seconds
    assert LOGIN_REQUEST_TIMEOUT_SECONDS == 25, (
        f"Default LOGIN_REQUEST_TIMEOUT_SECONDS should be 25, got {LOGIN_REQUEST_TIMEOUT_SECONDS}"
    )


def test_login_request_timeout_env_override():
    """Test that LOGIN_REQUEST_TIMEOUT_SECONDS can be overridden via environment."""
    # Save original value
    original_value = os.environ.get('LOGIN_REQUEST_TIMEOUT_SECONDS')
    
    try:
        # Set a custom value
        os.environ['LOGIN_REQUEST_TIMEOUT_SECONDS'] = '15'
        
        # Re-import to pick up new value
        from final_backend_postgresql import _get_env_int
        
        result = _get_env_int("LOGIN_REQUEST_TIMEOUT_SECONDS", 25, 5, 60)
        assert result == 15, f"Expected 15, got {result}"
    finally:
        # Restore original value
        if original_value is not None:
            os.environ['LOGIN_REQUEST_TIMEOUT_SECONDS'] = original_value
        elif 'LOGIN_REQUEST_TIMEOUT_SECONDS' in os.environ:
            del os.environ['LOGIN_REQUEST_TIMEOUT_SECONDS']


def test_get_env_int_validates_bounds():
    """Test that _get_env_int validates min/max bounds."""
    from final_backend_postgresql import _get_env_int
    
    # Save original value
    original_value = os.environ.get('TEST_ENV_INT')
    
    try:
        # Test value below minimum
        os.environ['TEST_ENV_INT'] = '1'
        result = _get_env_int("TEST_ENV_INT", 25, 5, 60)
        assert result == 25, f"Value below minimum should return default, got {result}"
        
        # Test value above maximum
        os.environ['TEST_ENV_INT'] = '100'
        result = _get_env_int("TEST_ENV_INT", 25, 5, 60)
        assert result == 25, f"Value above maximum should return default, got {result}"
        
        # Test value within bounds
        os.environ['TEST_ENV_INT'] = '30'
        result = _get_env_int("TEST_ENV_INT", 25, 5, 60)
        assert result == 30, f"Value within bounds should be returned, got {result}"
        
        # Test invalid value
        os.environ['TEST_ENV_INT'] = 'invalid'
        result = _get_env_int("TEST_ENV_INT", 25, 5, 60)
        assert result == 25, f"Invalid value should return default, got {result}"
    finally:
        # Restore original value
        if original_value is not None:
            os.environ['TEST_ENV_INT'] = original_value
        elif 'TEST_ENV_INT' in os.environ:
            del os.environ['TEST_ENV_INT']


if __name__ == "__main__":
    # Run tests manually
    print("Running login timeout tests...")
    
    print("\n1. Testing _check_request_timeout (not timed out)...")
    test_check_request_timeout_returns_false_when_not_timed_out()
    print("   ✓ Passed")
    
    print("\n2. Testing _check_request_timeout (timed out)...")
    test_check_request_timeout_returns_true_when_timed_out()
    print("   ✓ Passed")
    
    print("\n3. Testing LOGIN_REQUEST_TIMEOUT_SECONDS config...")
    test_login_request_timeout_config()
    print("   ✓ Passed")
    
    print("\n4. Testing LOGIN_REQUEST_TIMEOUT_SECONDS env override...")
    test_login_request_timeout_env_override()
    print("   ✓ Passed")
    
    print("\n5. Testing _get_env_int bounds validation...")
    test_get_env_int_validates_bounds()
    print("   ✓ Passed")
    
    print("\n" + "=" * 50)
    print("All login timeout tests passed!")
    print("=" * 50)
