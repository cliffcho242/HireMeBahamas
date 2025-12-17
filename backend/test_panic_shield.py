"""
Test the global exception handler (PANIC SHIELD) implementation.

This test validates that:
1. Unhandled exceptions are caught by the global handler
2. Users receive a friendly error message
3. The error is logged with request ID
4. The response has correct status code (500)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import logging
import sys
import os

# Ensure we import from the backend app, not the root app
backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)


def test_panic_shield_is_registered():
    """Test that the panic shield exception handler is registered"""
    from app.main import app
    
    # Check that Exception handler is registered
    assert Exception in app.exception_handlers
    assert app.exception_handlers[Exception].__name__ == "panic_handler"


def test_panic_shield_catches_unhandled_exception():
    """Test that the panic shield catches unhandled exceptions and returns clean error"""
    # Import the app
    from app.main import app
    
    # Create a test endpoint that raises an exception
    @app.get("/test-panic-endpoint-unique")
    async def test_panic_endpoint():
        raise ValueError("This is a test exception")
    
    client = TestClient(app, raise_server_exceptions=False)
    
    # Make a request that will trigger the exception
    response = client.get("/test-panic-endpoint-unique")
    
    # Verify the response
    assert response.status_code == 500
    assert "error" in response.json()
    assert response.json()["error"] == "Temporary issue. Try again."


def test_panic_shield_logs_with_request_id():
    """Test that the panic shield logs exceptions with request ID"""
    from app.main import app
    import logging
    
    # Get the logger
    logger = logging.getLogger("app.main")
    
    # Create a test endpoint that raises an exception
    @app.get("/test-panic-logging-endpoint")
    async def test_panic_logging_endpoint():
        raise RuntimeError("Test logging exception")
    
    client = TestClient(app, raise_server_exceptions=False)
    
    # Mock the logger to capture log calls
    with patch.object(logger, 'error') as mock_error:
        # Make a request that will trigger the exception
        response = client.get("/test-panic-logging-endpoint")
        
        # Verify logging was called
        assert mock_error.called
        
        # Verify the log message format
        log_call_args = mock_error.call_args[0][0]
        assert "PANIC" in log_call_args
        assert "Test logging exception" in str(log_call_args) or mock_error.call_args[1].get('exc_info')


def test_panic_shield_preserves_request_state_id():
    """Test that the panic shield uses request.state.id if available"""
    from app.main import app
    from fastapi import Request
    import logging
    
    # Get the logger
    logger = logging.getLogger("app.main")
    
    # Create a test endpoint that sets request.state.id and raises an exception
    @app.get("/test-panic-with-id-endpoint")
    async def test_panic_with_id(request: Request):
        request.state.id = "test-request-123"
        raise Exception("Test exception with ID")
    
    client = TestClient(app, raise_server_exceptions=False)
    
    # Mock the logger to capture log calls
    with patch.object(logger, 'error') as mock_error:
        # Make a request
        response = client.get("/test-panic-with-id-endpoint")
        
        # Verify the response
        assert response.status_code == 500
        
        # Verify logging was called with the request ID
        assert mock_error.called
        log_message = mock_error.call_args[0][0]
        assert "PANIC test-request-123" in log_message


def test_panic_shield_handles_various_exception_types():
    """Test that the panic shield handles different types of exceptions"""
    from app.main import app
    
    # Test ValueError
    @app.get("/test-value-error-endpoint")
    async def test_value_error():
        raise ValueError("Value error test")
    
    # Test RuntimeError
    @app.get("/test-runtime-error-endpoint")
    async def test_runtime_error():
        raise RuntimeError("Runtime error test")
    
    # Test generic Exception
    @app.get("/test-generic-error-endpoint")
    async def test_generic_error():
        raise Exception("Generic error test")
    
    client = TestClient(app, raise_server_exceptions=False)
    
    # Test each exception type
    for endpoint in ["/test-value-error-endpoint", "/test-runtime-error-endpoint", "/test-generic-error-endpoint"]:
        response = client.get(endpoint)
        assert response.status_code == 500
        assert response.json()["error"] == "Temporary issue. Try again."


def test_panic_shield_does_not_affect_normal_responses():
    """Test that the panic shield doesn't interfere with successful requests"""
    from app.main import app
    
    client = TestClient(app, raise_server_exceptions=False)
    
    # Test a normal endpoint (ready check)
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ready"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
