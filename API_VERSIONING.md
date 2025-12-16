# API Versioning Guide

## Overview

The HireMeBahamas API now supports versioned endpoints using the `/api/v1` prefix. This allows for future API evolution while maintaining backward compatibility.

## Structure

### V1 API Router

All API endpoints are now accessible under the `/api/v1` prefix:

```
/api/v1/health          - Health check endpoints
/api/v1/auth            - Authentication endpoints
/api/v1/users           - User management
/api/v1/feed            - Feed endpoints
/api/v1/posts           - Post management
/api/v1/messages        - Messaging system
/api/v1/notifications   - Notifications
/api/v1/jobs            - Job postings
/api/v1/hireme          - HireMe features
/api/v1/reviews         - Reviews and ratings
/api/v1/upload          - File uploads
/api/v1/profile_pictures - Profile picture management
/api/v1/analytics       - Analytics endpoints
/api/v1/debug           - Debug endpoints (development only)
```

### Directory Structure

```
backend/app/api/
├── __init__.py           # Base API package
├── v1/                   # Version 1 API
│   ├── __init__.py       # V1 router aggregator
│   ├── analytics.py      # Re-exports analytics router
│   ├── auth.py           # Re-exports auth router
│   ├── debug.py          # Re-exports debug router
│   ├── feed.py           # Re-exports feed router
│   ├── health.py         # Re-exports health router
│   ├── hireme.py         # Re-exports hireme router
│   ├── jobs.py           # Re-exports jobs router
│   ├── messages.py       # Re-exports messages router
│   ├── notifications.py  # Re-exports notifications router
│   ├── posts.py          # Re-exports posts router
│   ├── profile_pictures.py # Re-exports profile_pictures router
│   ├── reviews.py        # Re-exports reviews router
│   ├── upload.py         # Re-exports upload router
│   └── users.py          # Re-exports users router
├── analytics.py          # Analytics API implementation
├── auth.py               # Auth API implementation
├── debug.py              # Debug API implementation
├── feed.py               # Feed API implementation
├── health.py             # Health API implementation
├── hireme.py             # HireMe API implementation
├── jobs.py               # Jobs API implementation
├── messages.py           # Messages API implementation
├── notifications.py      # Notifications API implementation
├── posts.py              # Posts API implementation
├── profile_pictures.py   # Profile pictures API implementation
├── reviews.py            # Reviews API implementation
├── upload.py             # Upload API implementation
└── users.py              # Users API implementation
```

## Implementation Details

### V1 Router Aggregator

The `backend/app/api/v1/__init__.py` file aggregates all API routers and applies the `/api/v1` prefix:

```python
from fastapi import APIRouter

# Import all v1 routers
from app.api.v1.analytics import router as analytics
from app.api.v1.auth import router as auth
# ... (other imports)

# Create v1 router with prefix
router = APIRouter(prefix="/api/v1")

# Include all routers
router.include_router(health)
router.include_router(auth)
router.include_router(users)
# ... (other routers)
```

### Router Re-exports

Each v1 module (e.g., `backend/app/api/v1/auth.py`) re-exports the router from the parent API module:

```python
"""Authentication API v1 - Re-exports router from parent API module."""
from app.api.auth import router

__all__ = ["router"]
```

This approach allows:
- ✅ Single source of truth for API logic (in parent `api/` directory)
- ✅ Versioned URL structure (`/api/v1/...`)
- ✅ Easy future versioning (add `v2/`, `v3/`, etc.)
- ✅ Backward compatibility (maintain old endpoints while adding new versions)

### Main Application Integration

The v1 router is registered in `backend/app/main.py`:

```python
# Import versioned API v1 router
from .api.v1 import router as v1_router

# Include versioned API v1 router
if v1_router is not None:
    app.include_router(v1_router, tags=["v1"])
    logger.info("✅ V1 API router registered at /api/v1")
```

## Backward Compatibility

The existing non-versioned endpoints (`/api/auth`, `/api/users`, etc.) continue to work alongside the new versioned endpoints. This ensures existing clients are not broken while new clients can use the versioned API.

## Future Versioning

To add a new API version (e.g., v2):

1. Create `backend/app/api/v2/` directory
2. Create `backend/app/api/v2/__init__.py` with v2 router aggregator
3. Create v2 modules that either:
   - Re-export from parent API (for unchanged endpoints)
   - Import from parent and override specific endpoints (for modified endpoints)
   - Implement new logic (for new endpoints)
4. Register v2 router in `backend/app/main.py`

## Benefits

- **Gradual Migration**: Clients can migrate to v1 endpoints at their own pace
- **Clear Versioning**: API version is explicit in the URL
- **Flexibility**: Future versions can coexist with current versions
- **Maintainability**: Single source of truth for API logic
- **Documentation**: Version-specific API documentation via FastAPI's automatic docs

## Testing

To test the v1 API structure:

```bash
python3 test_api_v1_structure.py
```

This verifies:
- All v1 modules can be imported
- The v1 router has the correct `/api/v1` prefix
- All routers are properly included

## API Documentation

Once the application is running, visit:
- `/docs` - Interactive API documentation (Swagger UI)
- `/redoc` - Alternative API documentation (ReDoc)

Both will show the versioned endpoints under the `/api/v1` prefix.
