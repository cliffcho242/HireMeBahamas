"""
Tests for centralized error handling and logging functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch
from fastapi import Request, HTTPException, status
from backend.app.core.error_handler import (
    AppError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    DatabaseError,
    ExternalServiceError,
    RateLimitError,
    format_error_response,
    ErrorTracker,
)
from backend.app.core.logging import AppLogger, log_request, log_error, log_performance


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_app_error(self):
        """Test base AppError class."""
        error = AppError(
            message="Test error",
            status_code=500,
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        
        assert error.message == "Test error"
        assert error.status_code == 500
        assert error.error_code == "TEST_ERROR"
        assert error.details == {"key": "value"}
    
    def test_validation_error(self):
        """Test ValidationError class."""
        error = ValidationError("Invalid input", details={"field": "email"})
        
        assert error.message == "Invalid input"
        assert error.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details == {"field": "email"}
    
    def test_authentication_error(self):
        """Test AuthenticationError class."""
        error = AuthenticationError()
        
        assert error.message == "Authentication required"
        assert error.status_code == 401
        assert error.error_code == "AUTHENTICATION_ERROR"
    
    def test_authorization_error(self):
        """Test AuthorizationError class."""
        error = AuthorizationError()
        
        assert error.message == "Access denied"
        assert error.status_code == 403
        assert error.error_code == "AUTHORIZATION_ERROR"
    
    def test_not_found_error(self):
        """Test NotFoundError class."""
        error = NotFoundError("User", identifier=123)
        
        assert error.message == "User not found: 123"
        assert error.status_code == 404
        assert error.error_code == "NOT_FOUND"
        assert error.details == {"resource": "User", "identifier": 123}
    
    def test_database_error(self):
        """Test DatabaseError class."""
        error = DatabaseError("Connection failed")
        
        assert error.message == "Connection failed"
        assert error.status_code == 500
        assert error.error_code == "DATABASE_ERROR"
    
    def test_external_service_error(self):
        """Test ExternalServiceError class."""
        error = ExternalServiceError("S3", "Upload failed")
        
        assert error.message == "Upload failed"
        assert error.status_code == 503
        assert error.error_code == "EXTERNAL_SERVICE_ERROR"
        assert error.details["service"] == "S3"
    
    def test_rate_limit_error(self):
        """Test RateLimitError class."""
        error = RateLimitError(retry_after=60)
        
        assert error.message == "Rate limit exceeded"
        assert error.status_code == 429
        assert error.error_code == "RATE_LIMIT_EXCEEDED"
        assert error.details["retry_after"] == 60


class TestErrorFormatting:
    """Test error response formatting."""
    
    def test_format_app_error(self):
        """Test formatting AppError."""
        error = ValidationError("Invalid email", details={"field": "email"})
        response = format_error_response(error, request_id="test-123")
        
        assert response["error"] == "VALIDATION_ERROR"
        assert response["message"] == "Invalid email"
        assert response["status_code"] == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response["request_id"] == "test-123"
        assert response["details"]["field"] == "email"
    
    def test_format_http_exception(self):
        """Test formatting HTTPException."""
        error = HTTPException(status_code=404, detail="Not found")
        response = format_error_response(error, request_id="test-456")
        
        assert response["error"] == "HTTP_EXCEPTION"
        assert response["message"] == "Not found"
        assert response["status_code"] == 404
        assert response["request_id"] == "test-456"
    
    def test_format_generic_exception(self):
        """Test formatting generic exception."""
        error = ValueError("Something went wrong")
        response = format_error_response(error, request_id="test-789")
        
        assert response["error"] == "INTERNAL_SERVER_ERROR"
        assert "Something went wrong" in response["message"]
        assert response["status_code"] == 500
        assert response["request_id"] == "test-789"


class TestErrorTracker:
    """Test error tracking functionality."""
    
    def test_track_error(self):
        """Test tracking errors."""
        tracker = ErrorTracker()
        
        tracker.track_error(
            error_code="TEST_ERROR",
            message="Test message",
            request_id="req-123",
            user_id=1
        )
        
        counts = tracker.get_error_counts()
        assert counts["TEST_ERROR"] == 1
        
        last_errors = tracker.get_last_errors(1)
        assert len(last_errors) == 1
        assert last_errors[0]["error_code"] == "TEST_ERROR"
        assert last_errors[0]["message"] == "Test message"
    
    def test_error_count_increment(self):
        """Test error count incrementing."""
        tracker = ErrorTracker()
        
        tracker.track_error("ERROR_1", "Message 1")
        tracker.track_error("ERROR_1", "Message 2")
        tracker.track_error("ERROR_2", "Message 3")
        
        counts = tracker.get_error_counts()
        assert counts["ERROR_1"] == 2
        assert counts["ERROR_2"] == 1
    
    def test_last_errors_limit(self):
        """Test last errors buffer limit."""
        tracker = ErrorTracker()
        
        # Track more than max errors
        for i in range(150):
            tracker.track_error(f"ERROR_{i}", f"Message {i}")
        
        last_errors = tracker.get_last_errors(100)
        assert len(last_errors) == 100
    
    def test_clear_errors(self):
        """Test clearing tracked errors."""
        tracker = ErrorTracker()
        
        tracker.track_error("ERROR_1", "Message 1")
        tracker.track_error("ERROR_2", "Message 2")
        
        tracker.clear()
        
        counts = tracker.get_error_counts()
        assert len(counts) == 0
        
        last_errors = tracker.get_last_errors()
        assert len(last_errors) == 0


class TestLogging:
    """Test logging functionality."""
    
    def test_logger_initialization(self):
        """Test logger initializes correctly."""
        logger = AppLogger("test_logger")
        assert logger.name == "test_logger"
    
    def test_log_levels(self):
        """Test different log levels."""
        logger = AppLogger("test_logger")
        
        # These should not raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    
    def test_log_with_context(self):
        """Test logging with context."""
        logger = AppLogger("test_logger")
        
        # Should not raise exception
        logger.info(
            "User logged in",
            request_id="req-123",
            user_id=456,
            ip_address="192.168.1.1"
        )
    
    def test_log_with_exception(self):
        """Test logging with exception."""
        logger = AppLogger("test_logger")
        
        try:
            raise ValueError("Test exception")
        except Exception as e:
            # Should not raise exception
            logger.error("An error occurred", exc_info=e)
    
    def test_log_request_helper(self):
        """Test log_request helper function."""
        # Should not raise exception
        log_request(
            method="GET",
            path="/api/users/1",
            status_code=200,
            duration_ms=45.5,
            request_id="req-123",
            user_id=1
        )
    
    def test_log_error_helper(self):
        """Test log_error helper function."""
        try:
            raise RuntimeError("Test error")
        except Exception as e:
            # Should not raise exception
            log_error(
                message="Failed to process request",
                error=e,
                request_id="req-456",
                user_id=2
            )
    
    def test_log_performance_helper(self):
        """Test log_performance helper function."""
        # Should not raise exception
        log_performance(
            operation="database_query",
            duration_ms=1500.0,
            request_id="req-789"
        )


class TestIntegration:
    """Test integration of error handling and logging."""
    
    @pytest.mark.asyncio
    async def test_error_handler_logs_error(self):
        """Test that error handler logs errors."""
        from backend.app.core.error_handler import handle_app_error
        
        # Create mock request
        request = Mock(spec=Request)
        request.state.request_id = "test-req-123"
        request.url.path = "/api/test"
        
        # Create error
        error = ValidationError("Invalid input")
        
        # Handle error (should not raise exception)
        response = await handle_app_error(request, error)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        
        # Check response body
        body = json.loads(response.body.decode())
        assert body["error_code"] == "VALIDATION_ERROR"
        assert body["message"] == "Invalid input"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
