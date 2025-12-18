# Frontend Backend URL Configuration

## Vercel Frontend Configuration

### Environment Variable

Set the following environment variable in your Vercel project:

```bash
VITE_API_URL=https://hire-me-bahamas.onrender.com
```

### Usage in Frontend Code

```typescript
fetch(`${import.meta.env.VITE_API_URL}/api/auth/me`);
```

### vercel.json Configuration

The `vercel.json` file includes rewrites to proxy API requests to the backend:

```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://hire-me-bahamas.onrender.com/api/$1"
    }
  ]
}
```

## ABSOLUTE REQUIREMENTS

1. ✅ Frontend uses `VITE_API_URL` environment variable
2. ✅ vercel.json has rewrites to backend URL
3. ✅ NO comments in vercel.json
4. ✅ Backend is ONLY on Render (not Render or any other platform)
5. ✅ Single Gunicorn worker configuration
6. ✅ Health endpoint does NOT touch database
7. ✅ NO database calls at import time
8. ✅ SSL configured in DATABASE_URL (not connect_args)
