"""
Example usage of centralized error handling and logging.

This demonstrates how to use the new error handling and logging functionality
in your API endpoints.
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from app.core.logging import logger, log_request, log_error, log_performance
from app.core.error_handler import (
    ValidationError,
    NotFoundError,
    handle_app_error,
    handle_http_exception,
    handle_generic_exception,
)
import time

app = FastAPI()

# Register error handlers
app.add_exception_handler(Exception, handle_generic_exception)
app.add_exception_handler(HTTPException, handle_http_exception)


# Example 1: Basic logging
@app.get("/example/basic-logging")
async def example_basic_logging(request: Request):
    """Example of basic logging."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.info("Processing basic logging example", request_id=request_id)
    
    return {"message": "Check logs for output"}


# Example 2: Logging with context
@app.get("/example/context-logging")
async def example_context_logging(request: Request):
    """Example of logging with context."""
    request_id = getattr(request.state, "request_id", "unknown")
    user_id = 123  # Would come from auth
    
    logger.info(
        "User accessed endpoint",
        request_id=request_id,
        user_id=user_id,
        endpoint="/example/context-logging",
        method="GET"
    )
    
    return {"message": "Logged with context"}


# Example 3: Error handling with custom exceptions
@app.get("/example/validation-error")
async def example_validation_error(email: str):
    """Example of validation error."""
    if "@" not in email:
        raise ValidationError(
            "Invalid email format",
            details={"field": "email", "value": email}
        )
    
    return {"message": f"Valid email: {email}"}


@app.get("/example/not-found")
async def example_not_found(user_id: int):
    """Example of not found error."""
    # Simulate checking if user exists
    if user_id != 1:
        raise NotFoundError("User", user_id)
    
    return {"user_id": user_id, "name": "John Doe"}


# Example 4: Performance logging
@app.get("/example/performance")
async def example_performance(request: Request):
    """Example of performance logging."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Simulate slow operation
    start_time = time.time()
    time.sleep(0.1)  # 100ms
    duration_ms = (time.time() - start_time) * 1000
    
    log_performance(
        operation="data_processing",
        duration_ms=duration_ms,
        request_id=request_id
    )
    
    return {"duration_ms": duration_ms}


# Example 5: Error logging
@app.get("/example/error-handling")
async def example_error_handling(request: Request):
    """Example of error handling and logging."""
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        # Simulate an operation that might fail
        result = 10 / 0  # This will raise ZeroDivisionError
        return {"result": result}
    except Exception as e:
        log_error(
            message="Failed to perform calculation",
            error=e,
            request_id=request_id,
            operation="division"
        )
        raise


# Example 6: Request logging
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Middleware to log all requests."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Log the request
    log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
        request_id=getattr(request.state, "request_id", "unknown"),
    )
    
    return response


if __name__ == "__main__":
    import uvicorn
    
    # This would normally be in main.py with all middleware setup
    print("🚀 Starting example server...")
    print("📝 Try these endpoints:")
    print("  - http://localhost:8000/example/basic-logging")
    print("  - http://localhost:8000/example/context-logging")
    print("  - http://localhost:8000/example/validation-error?email=invalid")
    print("  - http://localhost:8000/example/validation-error?email=valid@email.com")
    print("  - http://localhost:8000/example/not-found?user_id=999")
    print("  - http://localhost:8000/example/performance")
    print("  - http://localhost:8000/example/error-handling")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
