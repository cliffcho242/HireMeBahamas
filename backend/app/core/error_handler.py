"""
Centralized error handling for HireMeBahamas API.

This module provides:
- Custom exception classes
- Error response formatting
- Error tracking and metrics
- Integration with logging system
"""

from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# =============================================================================
# CUSTOM EXCEPTION CLASSES
# =============================================================================

class AppError(Exception):
    """Base exception for application errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize application error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Application-specific error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "APP_ERROR"
        self.details = details or {}


class ValidationError(AppError):
    """Error for validation failures."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class AuthenticationError(AppError):
    """Error for authentication failures."""
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(AppError):
    """Error for authorization failures."""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class NotFoundError(AppError):
    """Error for resource not found."""
    
    def __init__(self, resource: str, identifier: Optional[Union[str, int]] = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier},
        )


class DatabaseError(AppError):
    """Error for database operations."""
    
    def __init__(self, message: str = "Database error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details,
        )


class ExternalServiceError(AppError):
    """Error for external service failures."""
    
    def __init__(
        self,
        service: str,
        message: str = "External service error",
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["service"] = service
        
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )


class RateLimitError(AppError):
    """Error for rate limit exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
    ):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details,
        )


# =============================================================================
# ERROR RESPONSE MODELS
# =============================================================================

class ErrorDetail(BaseModel):
    """Detailed error information."""
    
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response."""
    
    error: str
    message: str
    error_code: str
    status_code: int
    request_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    errors: Optional[list[ErrorDetail]] = None


# =============================================================================
# ERROR HANDLER FUNCTIONS
# =============================================================================

def format_error_response(
    error: Union[AppError, HTTPException, Exception],
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Format error as standardized response.
    
    Args:
        error: Error object
        request_id: Request ID for tracking
        
    Returns:
        Formatted error response dictionary
    """
    # Handle custom AppError
    if isinstance(error, AppError):
        return {
            "error": error.error_code,
            "message": error.message,
            "error_code": error.error_code,
            "status_code": error.status_code,
            "request_id": request_id,
            "details": error.details if error.details else None,
        }
    
    # Handle FastAPI HTTPException
    if isinstance(error, HTTPException):
        return {
            "error": "HTTP_EXCEPTION",
            "message": str(error.detail),
            "error_code": "HTTP_EXCEPTION",
            "status_code": error.status_code,
            "request_id": request_id,
        }
    
    # Handle generic exceptions
    error_message = str(error) if str(error) else "An unexpected error occurred"
    return {
        "error": "INTERNAL_SERVER_ERROR",
        "message": error_message,
        "error_code": "INTERNAL_SERVER_ERROR",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "request_id": request_id,
    }


async def handle_app_error(request: Request, error: AppError) -> JSONResponse:
    """Handle custom application errors.
    
    Args:
        request: Request object
        error: Application error
        
    Returns:
        JSON error response
    """
    from .logging import logger
    
    request_id = getattr(request.state, "request_id", None)
    
    # Log the error
    if error.status_code >= 500:
        logger.error(
            f"Application error: {error.message}",
            exc_info=error,
            request_id=request_id,
            error_code=error.error_code,
            status_code=error.status_code,
        )
    else:
        logger.warning(
            f"Client error: {error.message}",
            request_id=request_id,
            error_code=error.error_code,
            status_code=error.status_code,
        )
    
    # Format response
    response_data = format_error_response(error, request_id)
    
    return JSONResponse(
        status_code=error.status_code,
        content=response_data,
        headers={"X-Request-ID": request_id} if request_id else {},
    )


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions.
    
    Args:
        request: Request object
        exc: HTTP exception
        
    Returns:
        JSON error response
    """
    from .logging import logger
    
    request_id = getattr(request.state, "request_id", None)
    
    # Log based on status code
    if exc.status_code >= 500:
        logger.error(
            f"HTTP exception: {exc.detail}",
            request_id=request_id,
            status_code=exc.status_code,
            path=request.url.path,
        )
    else:
        logger.warning(
            f"HTTP exception: {exc.detail}",
            request_id=request_id,
            status_code=exc.status_code,
            path=request.url.path,
        )
    
    # Format response
    response_data = format_error_response(exc, request_id)
    
    # Add WWW-Authenticate header for 401 responses
    headers = {"X-Request-ID": request_id} if request_id else {}
    if exc.status_code == 401 and exc.headers:
        headers.update(exc.headers)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data,
        headers=headers,
    )


async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.
    
    Args:
        request: Request object
        exc: Exception
        
    Returns:
        JSON error response
    """
    from .logging import logger
    
    request_id = getattr(request.state, "request_id", None)
    
    # Log the full exception with traceback
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        exc_info=exc,
        request_id=request_id,
        path=request.url.path,
        method=request.method,
    )
    
    # Format response (never expose internal details in production)
    response_data = {
        "error": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected error occurred. Please try again later.",
        "error_code": "INTERNAL_SERVER_ERROR",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "request_id": request_id,
    }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data,
        headers={"X-Request-ID": request_id} if request_id else {},
    )


# =============================================================================
# ERROR TRACKING
# =============================================================================

class ErrorTracker:
    """Track and aggregate error metrics."""
    
    def __init__(self):
        """Initialize error tracker."""
        self._error_counts: Dict[str, int] = {}
        self._last_errors: list[Dict[str, Any]] = []
        self._max_last_errors = 100
    
    def track_error(
        self,
        error_code: str,
        message: str,
        request_id: Optional[str] = None,
        **context: Any,
    ) -> None:
        """Track an error occurrence.
        
        Args:
            error_code: Error code
            message: Error message
            request_id: Optional request ID
            **context: Additional context
        """
        # Increment error count
        self._error_counts[error_code] = self._error_counts.get(error_code, 0) + 1
        
        # Store last error
        error_info = {
            "error_code": error_code,
            "message": message,
            "request_id": request_id,
            "timestamp": None,  # Would use datetime.utcnow() if needed
            **context,
        }
        
        self._last_errors.append(error_info)
        
        # Keep only last N errors
        if len(self._last_errors) > self._max_last_errors:
            self._last_errors.pop(0)
    
    def get_error_counts(self) -> Dict[str, int]:
        """Get error counts by error code.
        
        Returns:
            Dictionary of error codes and their counts
        """
        return self._error_counts.copy()
    
    def get_last_errors(self, count: int = 10) -> list[Dict[str, Any]]:
        """Get last N errors.
        
        Args:
            count: Number of errors to return
            
        Returns:
            List of recent errors
        """
        return self._last_errors[-count:]
    
    def clear(self) -> None:
        """Clear all tracked errors."""
        self._error_counts.clear()
        self._last_errors.clear()


# Global error tracker instance
error_tracker = ErrorTracker()
