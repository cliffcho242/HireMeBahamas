# Central Error Handling + Logging

This directory contains centralized error handling and logging modules for the HireMeBahamas FastAPI application.

## Overview

The error handling and logging system provides:
- **Consistent error responses** across all endpoints
- **Centralized logging configuration** with a standard format
- **Automatic exception logging** with full tracebacks
- **Production-safe error messages** that don't expose sensitive information

## Modules

### `app/errors.py`
Provides centralized error handling for FastAPI applications.

**Key Features:**
- Global exception handler that catches all unhandled exceptions
- Logs exceptions with full context and traceback
- Returns consistent JSON error responses
- Protects sensitive information from being exposed to clients

**Usage:**
```python
from fastapi import FastAPI
from app.errors import register_error_handlers

app = FastAPI()
register_error_handlers(app)
```

### `app/logging.py`
Provides centralized logging configuration.

**Key Features:**
- Consistent log format across the application
- INFO level logging by default (suitable for production)
- Structured log messages with timestamp, level, logger name, and message

**Usage:**
```python
from app.logging import setup_logging

# Call this early in your application startup
setup_logging()
```

## Integration Guide

### Step-by-Step Integration

1. **Set up logging first** (before creating your FastAPI app):
```python
from app.logging import setup_logging

setup_logging()
```

2. **Create your FastAPI application**:
```python
from fastapi import FastAPI

app = FastAPI(title="Your App")
```

3. **Register error handlers**:
```python
from app.errors import register_error_handlers

register_error_handlers(app)
```

4. **Add your routes and middleware**:
```python
@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Complete Example

See `app/example_integration.py` for a complete working example.

To run the example:
```bash
python -m app.example_integration
```

Then test the endpoints:
- `GET http://localhost:8000/` - Normal endpoint
- `GET http://localhost:8000/health` - Health check
- `GET http://localhost:8000/error` - Trigger error to see error handling in action
- `GET http://localhost:8000/docs` - API documentation

## Log Format

The logging system uses the following format:
```
%(asctime)s | %(levelname)s | %(name)s | %(message)s
```

Example log output:
```
2025-12-16 17:05:22,188 | INFO | app.api.auth | User login successful: user_id=123
2025-12-16 17:05:23,456 | ERROR | app | Unhandled exception
```

## Error Response Format

When an unhandled exception occurs, the error handler returns:

**Response:**
```json
{
  "detail": "Internal server error"
}
```

**Status Code:** `500`

**Logging:**
The full exception with traceback is logged to help with debugging, but sensitive details are not exposed to the client.

## Testing

Run the test suite to verify the modules work correctly:

```bash
python test_error_logging_modules.py
```

Expected output:
```
============================================================
Central Error Handling + Logging Module Tests
============================================================
Testing logging setup...
✅ Logging setup works correctly

Testing error handlers...
✅ Normal endpoint works correctly
✅ Error handler works correctly

Testing integration...
✅ Root endpoint works
✅ Error endpoint handled correctly

============================================================
✅ ALL TESTS PASSED
============================================================
```

## Best Practices

1. **Call `setup_logging()` early**: Set up logging before importing other modules to ensure all logs use the consistent format.

2. **Register error handlers after creating the app**: This ensures the error handler is properly integrated with FastAPI's exception handling system.

3. **Use structured logging**: Include relevant context in log messages (user_id, request_id, etc.) to aid in debugging.

4. **Don't expose sensitive information**: The error handler returns generic messages to clients while logging full details for developers.

## Integration with Existing Application

The main application (`api/backend_app/main.py`) already has error handling and logging configured. These modules provide a reusable, centralized implementation that can be used across different parts of the application or in new services.

To integrate into the main application:

1. Import the modules at the top of `api/backend_app/main.py`:
```python
from app.errors import register_error_handlers
from app.logging import setup_logging
```

2. Replace the existing logging configuration with:
```python
# Early in the file, before other imports
setup_logging()
```

3. Replace the existing exception handler with:
```python
# After creating the FastAPI app
register_error_handlers(app)
```

## Files

- `app/errors.py` - Error handling module
- `app/logging.py` - Logging configuration module
- `app/example_integration.py` - Complete integration example
- `app/ERROR_LOGGING_README.md` - This documentation
- `test_error_logging_modules.py` - Test suite

## Support

For questions or issues, please refer to the main project documentation or create an issue in the repository.
