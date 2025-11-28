"""
Test registration request timeout functionality.

This test verifies that the registration endpoint properly handles request timeouts
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


def test_registration_request_timeout_config():
    """Test that REGISTRATION_REQUEST_TIMEOUT_SECONDS is properly configured."""
    from final_backend_postgresql import REGISTRATION_REQUEST_TIMEOUT_SECONDS
    
    # Default should be 25 seconds
    assert REGISTRATION_REQUEST_TIMEOUT_SECONDS == 25, (
        f"Default REGISTRATION_REQUEST_TIMEOUT_SECONDS should be 25, got {REGISTRATION_REQUEST_TIMEOUT_SECONDS}"
    )


def test_registration_request_timeout_env_override():
    """Test that _get_env_int correctly reads REGISTRATION_REQUEST_TIMEOUT_SECONDS from environment.
    
    Note: This test verifies the _get_env_int function works correctly with environment variables.
    The actual REGISTRATION_REQUEST_TIMEOUT_SECONDS module variable is set at import time,
    but the underlying _get_env_int function is what reads the environment variable.
    """
    # Save original value
    original_value = os.environ.get('REGISTRATION_REQUEST_TIMEOUT_SECONDS')
    
    try:
        # Set a custom value
        os.environ['REGISTRATION_REQUEST_TIMEOUT_SECONDS'] = '15'
        
        # Test that _get_env_int reads the environment variable correctly
        from final_backend_postgresql import _get_env_int
        
        result = _get_env_int("REGISTRATION_REQUEST_TIMEOUT_SECONDS", 25, 5, 60)
        assert result == 15, f"Expected 15, got {result}"
    finally:
        # Restore original value
        if original_value is not None:
            os.environ['REGISTRATION_REQUEST_TIMEOUT_SECONDS'] = original_value
        elif 'REGISTRATION_REQUEST_TIMEOUT_SECONDS' in os.environ:
            del os.environ['REGISTRATION_REQUEST_TIMEOUT_SECONDS']


def test_check_request_timeout_used_in_registration():
    """Test that registration endpoint uses _check_request_timeout function."""
    import inspect
    from final_backend_postgresql import register
    
    # Get source code of register function
    source = inspect.getsource(register)
    
    # Check that the function uses _check_request_timeout
    assert '_check_request_timeout' in source, (
        "Registration endpoint should use _check_request_timeout for timeout handling"
    )
    
    # Check for early timeout check before password hashing
    assert 'early check' in source, (
        "Registration endpoint should have early timeout check before CPU-intensive operations"
    )
    
    # Check for detailed timing logs
    assert 'password_hash_ms' in source, (
        "Registration endpoint should track password hashing time"
    )
    assert 'db_check_ms' in source, (
        "Registration endpoint should track database check time"
    )
    assert 'insert_ms' in source, (
        "Registration endpoint should track database insert time"
    )
    assert 'token_create_ms' in source, (
        "Registration endpoint should track token creation time"
    )
    
    # Check for client type tracking
    assert 'client_type' in source, (
        "Registration endpoint should track client type for mobile timeout analysis"
    )


def test_registration_returns_504_on_timeout():
    """Test that registration returns 504 when request times out."""
    from final_backend_postgresql import app, g, _check_request_timeout, REGISTRATION_REQUEST_TIMEOUT_SECONDS
    
    with app.test_client() as client:
        # Patch _check_request_timeout to always return True (simulating timeout)
        with patch('final_backend_postgresql._check_request_timeout', return_value=True):
            response = client.post(
                '/api/auth/register',
                json={
                    'email': 'timeouttest@example.com',
                    'password': 'TestPass123!',
                    'first_name': 'Timeout',
                    'last_name': 'Test',
                    'user_type': 'user',
                    'location': 'Nassau'
                },
                content_type='application/json'
            )
            
            # Should return 504 Gateway Timeout
            assert response.status_code == 504, (
                f"Expected 504 on timeout, got {response.status_code}"
            )
            
            data = response.get_json()
            assert data['success'] is False
            assert 'timed out' in data['message'].lower()


def test_registration_logs_slow_requests():
    """Test that registration logs warnings for slow requests (>1 second)."""
    import inspect
    from final_backend_postgresql import register
    
    # Get source code of register function
    source = inspect.getsource(register)
    
    # Check for slow registration warning message
    assert 'SLOW REGISTRATION' in source, (
        "Registration endpoint should log warnings for slow requests"
    )
    assert 'total_registration_ms > 1000' in source, (
        "Registration should warn when total time exceeds 1000ms"
    )


def test_registration_handles_pool_exhaustion():
    """Test that registration handles connection pool exhaustion gracefully."""
    from final_backend_postgresql import app
    
    with app.test_client() as client:
        # Patch get_db_connection to return None (simulating pool exhaustion)
        with patch('final_backend_postgresql.get_db_connection', return_value=None):
            response = client.post(
                '/api/auth/register',
                json={
                    'email': 'pooltest@example.com',
                    'password': 'TestPass123!',
                    'first_name': 'Pool',
                    'last_name': 'Test',
                    'user_type': 'user',
                    'location': 'Nassau'
                },
                content_type='application/json'
            )
            
            # Should return 503 Service Unavailable
            assert response.status_code == 503, (
                f"Expected 503 on pool exhaustion, got {response.status_code}"
            )
            
            data = response.get_json()
            assert data['success'] is False
            assert 'temporarily unavailable' in data['message'].lower()


def test_startup_timing_tracked():
    """Test that application startup timing is properly tracked."""
    from final_backend_postgresql import _APP_START_TIME, _APP_IMPORT_COMPLETE_TIME
    
    # Verify startup timing variables are set
    assert _APP_START_TIME is not None, (
        "_APP_START_TIME should be set at module load time"
    )
    
    assert _APP_IMPORT_COMPLETE_TIME is not None, (
        "_APP_IMPORT_COMPLETE_TIME should be set after initialization completes"
    )
    
    # Verify timing is reasonable (import should complete after start)
    assert _APP_IMPORT_COMPLETE_TIME >= _APP_START_TIME, (
        "_APP_IMPORT_COMPLETE_TIME should be >= _APP_START_TIME"
    )
    
    # Verify startup time is reasonable (less than 60 seconds in test environment)
    startup_time = _APP_IMPORT_COMPLETE_TIME - _APP_START_TIME
    assert startup_time < 60, (
        f"Startup time should be less than 60 seconds, got {startup_time:.2f}s"
    )


if __name__ == "__main__":
    # Run tests manually
    print("Running registration timeout tests...")
    
    print("\n1. Testing REGISTRATION_REQUEST_TIMEOUT_SECONDS config...")
    test_registration_request_timeout_config()
    print("   ✓ Passed")
    
    print("\n2. Testing REGISTRATION_REQUEST_TIMEOUT_SECONDS env override...")
    test_registration_request_timeout_env_override()
    print("   ✓ Passed")
    
    print("\n3. Testing _check_request_timeout used in registration...")
    test_check_request_timeout_used_in_registration()
    print("   ✓ Passed")
    
    print("\n4. Testing registration returns 504 on timeout...")
    test_registration_returns_504_on_timeout()
    print("   ✓ Passed")
    
    print("\n5. Testing registration logs slow requests...")
    test_registration_logs_slow_requests()
    print("   ✓ Passed")
    
    print("\n6. Testing registration handles pool exhaustion...")
    test_registration_handles_pool_exhaustion()
    print("   ✓ Passed")
    
    print("\n7. Testing startup timing tracked...")
    test_startup_timing_tracked()
    print("   ✓ Passed")
    
    print("\n" + "=" * 50)
    print("All registration timeout tests passed!")
    print("=" * 50)
