# Central Error Handling and Logging Guide

This guide explains the centralized error handling and logging functionality in HireMeBahamas.

## Overview

The application now includes a comprehensive error handling and logging system that provides:

- **Structured Logging**: JSON-formatted logs in production, human-readable in development
- **Request Tracking**: Automatic request ID tracking across all logs
- **Error Handling**: Standardized error responses with proper status codes
- **Error Tracking**: Metrics collection for error patterns
- **Performance Monitoring**: Automatic logging of slow operations

## Backend (Python/FastAPI)

### Logging

#### Using the Logger

```python
from app.core.logging import logger

# Basic logging
logger.info("User logged in successfully")
logger.warning("Rate limit approaching")
logger.error("Database connection failed", exc_info=exception)

# Logging with context
logger.info(
    "User created post",
    request_id="req-123",
    user_id=456,
    post_id=789
)
```

#### Helper Functions

```python
from app.core.logging import log_request, log_error, log_performance

# Log HTTP requests
log_request(
    method="GET",
    path="/api/users/123",
    status_code=200,
    duration_ms=45.5,
    request_id="req-abc",
    user_id=123
)

# Log errors with full context
try:
    # ... some operation
    pass
except Exception as e:
    log_error(
        message="Failed to process payment",
        error=e,
        request_id="req-xyz",
        user_id=456,
        amount=99.99
    )

# Log performance metrics
log_performance(
    operation="database_query",
    duration_ms=1500.0,
    request_id="req-123"
)
```

#### Log Levels

- **DEBUG**: Detailed debugging information (development only)
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors requiring immediate attention

### Error Handling

#### Custom Exceptions

```python
from app.core.error_handler import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    DatabaseError,
    ExternalServiceError,
    RateLimitError,
)

# Use custom exceptions in your code
def create_user(email: str):
    if not is_valid_email(email):
        raise ValidationError(
            "Invalid email format",
            details={"field": "email", "value": email}
        )
    
    user = User.query.filter_by(email=email).first()
    if user:
        raise ValidationError(
            "Email already exists",
            details={"field": "email"}
        )
    
    # ... create user
```

#### Exception Types

| Exception | Status Code | Use Case |
|-----------|-------------|----------|
| `ValidationError` | 422 | Invalid input data |
| `AuthenticationError` | 401 | Missing or invalid credentials |
| `AuthorizationError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `DatabaseError` | 500 | Database operation failures |
| `ExternalServiceError` | 503 | External service unavailable |
| `RateLimitError` | 429 | Rate limit exceeded |

#### Error Responses

All errors return a standardized JSON response:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid email format",
  "error_code": "VALIDATION_ERROR",
  "status_code": 422,
  "request_id": "req-abc123",
  "details": {
    "field": "email",
    "value": "invalid@"
  }
}
```

#### Error Tracking

```python
from app.core.error_handler import error_tracker

# Errors are automatically tracked
# Get error statistics
error_counts = error_tracker.get_error_counts()
# {"VALIDATION_ERROR": 45, "NOT_FOUND": 12, ...}

# Get recent errors
last_errors = error_tracker.get_last_errors(count=10)

# Clear tracked errors
error_tracker.clear()
```

### Middleware Integration

The error handling and logging are automatically integrated via middleware:

```python
# In main.py - already configured
from app.core.middleware import setup_middleware

app = FastAPI()
setup_middleware(app)  # Adds CORS, Request ID, Timeout, Error Handlers
```

The middleware provides:
- **Request ID**: Automatically adds `X-Request-ID` to all requests/responses
- **Timeout Protection**: 30-second timeout on all requests
- **Global Exception Handler**: Catches all unhandled exceptions
- **Structured Error Responses**: Consistent error format across all endpoints

## Frontend (TypeScript/React)

### Logging

#### Using the Logger

```typescript
import logger from '@/utils/logger';

// Basic logging
logger.info('User logged in successfully');
logger.warn('Connection slow');
logger.error('Failed to load data', error);

// Logging with context
logger.info('Post created', {
  userId: 123,
  postId: 456,
  timestamp: Date.now()
});
```

#### API Logging

```typescript
import { logRequest, logResponse, logApiError } from '@/utils/logger';

// Log API request
logRequest('GET', '/api/posts');

// Log API response
logResponse('GET', '/api/posts', 200, 145); // 145ms duration

// Log API error
try {
  const response = await api.get('/api/posts');
} catch (error) {
  logApiError('GET', '/api/posts', error);
}
```

#### Performance Monitoring

```typescript
import { logPerformance } from '@/utils/logger';

const start = performance.now();
// ... some operation
const duration = performance.now() - start;

logPerformance('data_processing', duration, 1000); // 1000ms threshold
```

### Error Handling

The existing error handler utilities have been enhanced to work with the new logging system:

```typescript
import { getApiErrorMessage } from '@/utils/errorHandler';
import logger from '@/utils/logger';

try {
  await api.post('/api/posts', postData);
} catch (error) {
  // Log the error
  logger.error('Failed to create post', error, { postId: 123 });
  
  // Get user-friendly message
  const message = getApiErrorMessage(error, 'posts', 'Failed to create post');
  
  // Show to user
  toast.error(message);
}
```

## Configuration

### Backend Configuration

Environment variables:

```bash
# Logging
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENVIRONMENT=production            # production or development
RUNTIME_LOG_DIR=/tmp/runtime-logs # Log file directory

# Error Tracking
ERROR_TRACKING_ENABLED=true       # Enable error tracking
```

### Frontend Configuration

The logger automatically detects the environment and adjusts behavior:

- **Development**: All logs to console, debug level enabled
- **Production**: Only INFO and above, no console.log in production

## Best Practices

### Backend

1. **Use structured logging** - Always include context:
   ```python
   logger.info("Action performed", user_id=123, resource_id=456)
   ```

2. **Use custom exceptions** - Don't raise generic exceptions:
   ```python
   # Good
   raise NotFoundError("User", user_id)
   
   # Bad
   raise HTTPException(404, "Not found")
   ```

3. **Log at appropriate levels**:
   - Use `debug()` for verbose debugging info
   - Use `info()` for normal operations
   - Use `warning()` for potential issues
   - Use `error()` for failures
   - Use `critical()` for system-critical errors

4. **Include request context** - Always pass `request_id`:
   ```python
   request_id = request.state.request_id
   logger.error("Operation failed", request_id=request_id)
   ```

### Frontend

1. **Log all API interactions**:
   ```typescript
   logRequest('POST', '/api/posts');
   // ... make request
   logResponse('POST', '/api/posts', 201, duration);
   ```

2. **Don't log sensitive data** - Never log passwords, tokens, etc.

3. **Use appropriate log levels** - Info for normal operations, warn for issues, error for failures

4. **Include context** - Add relevant data to logs:
   ```typescript
   logger.error('Failed to load', error, { userId: 123, retryCount: 3 });
   ```

## Monitoring and Debugging

### View Logs

**Backend (Development)**:
```bash
# Logs output to console with colors
tail -f /tmp/runtime-logs/hiremebahamas.log
```

**Backend (Production)**:
```bash
# JSON-formatted logs
cat /tmp/runtime-logs/hiremebahamas.log | jq
```

**Frontend (Development)**:
```javascript
// In browser console
logger.getLogs()           // Get all stored logs
logger.exportLogs()        // Export as JSON string
logger.clearLogs()         // Clear stored logs
```

### Error Tracking

Check error metrics:

```python
from app.core.error_handler import error_tracker

# Get error counts
counts = error_tracker.get_error_counts()
print(f"Validation errors: {counts.get('VALIDATION_ERROR', 0)}")

# Get recent errors
recent = error_tracker.get_last_errors(count=10)
for error in recent:
    print(f"{error['timestamp']}: {error['message']}")
```

## Testing

Run the tests:

```bash
# Backend tests
pytest backend/test_error_handling_logging.py -v

# All tests
pytest backend/ -v
```

## Migration Guide

### Migrating Existing Code

**Old way**:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("User logged in")
```

**New way**:
```python
from app.core.logging import logger
logger.info("User logged in", user_id=123, request_id=request.state.request_id)
```

**Old way**:
```python
raise HTTPException(status_code=404, detail="User not found")
```

**New way**:
```python
from app.core.error_handler import NotFoundError
raise NotFoundError("User", user_id)
```

## Support

For issues or questions about error handling and logging:

1. Check the test file: `backend/test_error_handling_logging.py`
2. Review the implementation: 
   - `backend/app/core/logging.py`
   - `backend/app/core/error_handler.py`
   - `frontend/src/utils/logger.ts`
3. See existing usage in the codebase
