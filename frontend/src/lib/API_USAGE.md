# Safe URL Builder - Usage Examples

This document demonstrates how to use the safe URL builder utility.

## Import

```typescript
import { apiUrl } from '../lib/api';
```

## Basic Usage

### Making API Requests

```typescript
// Before (unsafe - can fail silently):
fetch("/api/auth/me", {
  credentials: "include",
});

// After (safe - validates URL):
fetch(apiUrl("/api/auth/me"), {
  credentials: "include",
});
```

### With Different HTTP Methods

```typescript
// POST request
fetch(apiUrl("/api/posts"), {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ content: "Hello world" }),
  credentials: "include",
});

// DELETE request
fetch(apiUrl("/api/posts/123"), {
  method: "DELETE",
  credentials: "include",
});
```

## Configuration

The utility uses the `VITE_API_URL` environment variable:

```bash
# For development
VITE_API_URL=http://localhost:8000

# For production (Render)
VITE_API_URL=https://your-app.up.render.app

# For Vercel serverless (no variable needed)
# It will use window.location.origin automatically
```

## Error Handling

The utility validates the configuration and throws clear errors:

```typescript
// Missing or invalid URL
// Error: VITE_API_URL is missing or invalid. Set VITE_API_URL environment 
// variable to your backend URL, or deploy to a serverless environment where 
// same-origin is used.

// Invalid protocol
// Error: VITE_API_URL is invalid: "invalid-url". URL must start with 
// 'http://' or 'https://'. Example: VITE_API_URL=https://your-backend.com
```

## Benefits

1. **Never fails silently**: Throws clear errors if misconfigured
2. **Automatic normalization**: Removes trailing slashes, adds leading slashes
3. **Environment-aware**: Works with VITE_API_URL or falls back to same-origin
4. **Type-safe**: Full TypeScript support
5. **Consistent**: One function for all API requests

## Migration Guide

### From Direct Fetch

```typescript
// Old
fetch("/api/auth/login", { /* ... */ });

// New
import { apiUrl } from '../lib/api';
fetch(apiUrl("/api/auth/login"), { /* ... */ });
```

### From Manual URL Construction

```typescript
// Old
const base = import.meta.env.VITE_API_URL || window.location.origin;
fetch(`${base}/api/auth/login`, { /* ... */ });

// New
import { apiUrl } from '../lib/api';
fetch(apiUrl("/api/auth/login"), { /* ... */ });
```

## Additional Functions

### Check if API is Configured

```typescript
import { isApiConfigured } from '../lib/api';

if (isApiConfigured()) {
  console.log('API is ready');
}
```

### Get Base API URL

```typescript
import { getApiBase } from '../lib/api';

const baseUrl = getApiBase();
console.log('API Base:', baseUrl);
```
