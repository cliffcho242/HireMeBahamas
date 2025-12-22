# Safe URL Builder - Usage Examples

This document demonstrates how to use the safe URL builder utility.

## Import

```typescript
import { apiUrl } from '@/lib/api';
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

The utility uses the `VITE_API_BASE_URL` environment variable and fails fast if it is missing or insecure:

```bash
VITE_API_BASE_URL=https://hiremebahamas-backend.onrender.com
```

Trailling slashes and non-HTTPS values are rejected during build.
