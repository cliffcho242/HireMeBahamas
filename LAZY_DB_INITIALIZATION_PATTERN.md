# Lazy Database Initialization Pattern

## Overview

This document describes the **lazy database initialization pattern** implemented across all database modules in HireMeBahamas to prevent import-time database connections.

## The Problem

### ❌ BAD: Import-Time Database Access

```python
# DON'T DO THIS - Engine created when module is imported
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(DATABASE_URL)  # ❌ BAD - connects at import time
```

**Why this is bad:**
- In serverless environments (Vercel, AWS Lambda), import-time connections can fail
- Database may not be ready when module is imported during cold starts
- Creates connections that may timeout before first request
- Wastes resources by creating connections that aren't immediately needed
- Can cause deployment failures if database is temporarily unavailable

## The Solution

### ✅ GOOD: Lazy Initialization Pattern

```python
# GOOD - Engine created on first use
from sqlalchemy.ext.asyncio import create_async_engine
import threading

# Global variables for lazy initialization
_engine = None
_engine_lock = threading.Lock()

def get_engine():
    """Get or create database engine (lazy initialization for serverless).
    
    ✅ GOOD PATTERN: Defers connection until first request.
    Thread-safe: Uses double-checked locking.
    
    Returns:
        AsyncEngine: Database engine instance
    """
    global _engine
    
    # Double-checked locking pattern for thread safety
    if _engine is None:
        with _engine_lock:
            # Check again inside the lock
            if _engine is None:
                _engine = create_async_engine(
                    DATABASE_URL,
                    pool_pre_ping=True,
                    pool_recycle=300,
                    # ... other configuration
                )
    
    return _engine

# Backward compatibility wrapper
class LazyEngine:
    """Wrapper that defers all attribute access to the lazily-initialized engine."""
    
    def __getattr__(self, name: str):
        actual_engine = get_engine()
        return getattr(actual_engine, name)

engine = LazyEngine()  # ✅ GOOD - Defers to get_engine() on first access
```

## Implementation Across Modules

### 1. api/database.py
```python
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(...)
    return _engine
```

### 2. api/backend_app/database.py
```python
_engine = None
_engine_lock = threading.Lock()

def get_engine():
    global _engine
    if _engine is None:
        with _engine_lock:
            if _engine is None:
                _engine = create_async_engine(...)
    return _engine

engine = LazyEngine()  # Backward compatibility
```

### 3. backend/app/database.py
Same pattern as api/backend_app/database.py

### 4. backend/app/core/database.py
Same pattern as api/backend_app/database.py

### 5. api/index.py
```python
_db_engine = None
_async_session_maker = None
_engine_lock = None

def get_db_engine():
    global _db_engine, _async_session_maker, _engine_lock
    
    if _engine_lock is None:
        _engine_lock = threading.Lock()
    
    if _db_engine is None:
        with _engine_lock:
            if _db_engine is None:
                # Try to reuse backend engine first
                try:
                    from backend_app.database import engine as backend_engine
                    _db_engine = backend_engine
                    return _db_engine, _async_session_maker
                except ImportError:
                    pass
                
                # Fallback: create new engine
                _db_engine = create_async_engine(...)
    
    return _db_engine, _async_session_maker

# Usage in endpoints:
@app.get("/api/health")
async def health():
    db_engine, _ = get_db_engine()  # ✅ Lazy initialization on first request
    # ... use db_engine
```

## Usage Guidelines

### In New Code

**Always call `get_engine()` before using the engine:**

```python
# ✅ GOOD
async def my_function():
    engine = get_engine()  # Engine created on first call
    async with engine.begin() as conn:
        # Use connection
```

**Never create engine at module level:**

```python
# ❌ BAD
engine = create_async_engine(...)  # Don't do this!

async def my_function():
    async with engine.begin() as conn:
        # Use connection
```

### In Endpoint Handlers

```python
# api/index.py example
@app.get("/some-endpoint")
async def some_endpoint():
    # Initialize engine lazily on first use
    db_engine, async_session_maker = get_db_engine()
    
    if not db_engine:
        return {"error": "Database not available"}
    
    async with db_engine.begin() as conn:
        # Use connection
```

## Benefits

1. **Serverless-Friendly**: Works reliably in Vercel, AWS Lambda, Google Cloud Functions
2. **Resilient**: Handles database unavailability during deployment
3. **Efficient**: Only creates connections when actually needed
4. **Thread-Safe**: Double-checked locking prevents race conditions
5. **Backward Compatible**: `LazyEngine` wrapper maintains existing API

## Testing

Run the test script to verify lazy initialization:

```bash
python3 test_lazy_db_init.py
```

Expected output:
```
✅ ALL TESTS PASSED - Lazy initialization pattern is correct!

Pattern summary:
  ✅ GOOD: def get_engine() -> creates engine on first call
  ✅ GOOD: engine = LazyEngine() -> defers to get_engine()
  ❌ BAD:  engine = create_async_engine() -> creates at import
```

## Common Pitfalls

### ❌ Forgetting to call get_engine()

```python
# BAD - assumes engine is already initialized
async with engine.begin() as conn:  # May fail if engine not created yet
    # Use connection
```

### ✅ Always initialize first

```python
# GOOD - explicitly initialize
engine = get_engine()
async with engine.begin() as conn:
    # Use connection
```

### ❌ Creating engine in multiple places

```python
# BAD - creates duplicate connections
engine1 = create_async_engine(DATABASE_URL)
engine2 = create_async_engine(DATABASE_URL)
```

### ✅ Reuse singleton engine

```python
# GOOD - reuses same engine
engine = get_engine()  # Returns existing engine if already created
```

## Deployment Checklist

When deploying to serverless platforms:

- [x] All database modules use `get_engine()` pattern
- [x] No `create_async_engine()` calls at module level
- [x] Endpoint handlers call `get_engine()` before using engine
- [x] Thread safety with locks where needed
- [x] Backward compatibility with `LazyEngine` wrapper
- [x] Tests verify lazy initialization

## References

- Problem statement: Issue #5 - NO IMPORT-TIME DB ACCESS
- Implementation PR: Branch `copilot/fix-no-import-time-db-access`
- Related patterns:
  - [Singleton Pattern](https://en.wikipedia.org/wiki/Singleton_pattern)
  - [Lazy Initialization](https://en.wikipedia.org/wiki/Lazy_initialization)
  - [Double-checked Locking](https://en.wikipedia.org/wiki/Double-checked_locking)

## See Also

- `api/database.py` - Simple lazy initialization
- `api/backend_app/database.py` - Full pattern with LazyEngine
- `backend/app/database.py` - Same pattern
- `backend/app/core/database.py` - Same pattern
- `api/index.py` - Lazy initialization with fallback
- `test_lazy_db_init.py` - Test script
