# Vercel Configuration Guide

## Overview

This document explains the Vercel configuration in `vercel.json` for the HireMeBahamas platform.

## API Proxy Configuration

### Rewrite Rules

The `vercel.json` file contains a crucial rewrite rule that proxies API requests to the Render backend:

```json
"rewrites": [
  {
    "source": "/api/(.*)",
    "destination": "https://hiremebahamas.onrender.com/api/$1"
  }
]
```

**How it works:**
1. When a user's browser makes a request to `/api/auth/login` on the Vercel deployment
2. Vercel intercepts this request and rewrites the destination
3. The request is forwarded to `https://hiremebahamas.onrender.com/api/auth/login`
4. The response is returned to the user
5. From the browser's perspective, this is a same-origin request (no CORS issues)

**Important Notes:**
- API requests to `/api/*` are proxied to the Render backend
- Frontend should use relative URLs (`/api/*`) 
- **DO NOT** set `VITE_API_URL` in Vercel environment variables
- This allows seamless proxy without CORS issues

### Why This Approach?

**Benefits:**
- ✅ No CORS configuration needed on backend
- ✅ Simplified frontend code (relative URLs)
- ✅ Browser security policies are satisfied
- ✅ Single domain for frontend and API
- ✅ Works with cookies and credentials

**Alternative Approach (NOT recommended):**
- Setting `VITE_API_URL=https://hiremebahamas.onrender.com` in Vercel
- This would require CORS configuration on the backend
- Slower (browser makes cross-origin requests)
- More complex security configuration

## Cache Control Headers

The configuration includes optimized cache control headers for different asset types:

### Static Assets (Long Cache)
```json
"source": "/assets/(.*)",
"Cache-Control": "public, max-age=31536000, immutable"
```
- JavaScript, CSS, fonts, images in `/assets/`
- Cached for 1 year (max-age=31536000)
- Marked as immutable (never changes)
- Allows browsers to aggressively cache assets

### HTML Files (No Cache)
```json
"source": "/index.html",
"Cache-Control": "public, max-age=0, must-revalidate"
```
- HTML files are not cached
- Ensures users always get the latest version
- Critical for SPA applications where the HTML entry point references the latest assets

### API Requests (No Cache)
```json
"source": "/api/(.*)",
"Cache-Control": "no-store"
```
- API responses are never cached
- Ensures fresh data on every request
- Critical for authentication and dynamic content

## Security Headers

The configuration includes comprehensive security headers:

```json
"X-Content-Type-Options": "nosniff"           // Prevent MIME type sniffing
"X-Frame-Options": "DENY"                     // Prevent clickjacking
"X-XSS-Protection": "1; mode=block"           // XSS protection
"Referrer-Policy": "strict-origin-when-cross-origin"
"Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"
"Permissions-Policy": "camera=(), microphone=(), geolocation=(self), payment=()"
"X-DNS-Prefetch-Control": "on"               // Enable DNS prefetching
```

## Build Configuration

### Build Command
```json
"buildCommand": "cd frontend && npm run build"
```
- Builds the Vite/React frontend
- Output goes to `frontend/dist`

### Install Command
```json
"installCommand": "cd frontend && npm ci"
```
- Uses `npm ci` for clean install (faster, more reliable than `npm install`)
- Installs dependencies from `package-lock.json`

### Output Directory
```json
"outputDirectory": "frontend/dist"
```
- Vite's default output directory
- Contains the built static files served by Vercel

## Environment Variables

### Required Variables (Set in Vercel Dashboard)

**Backend:**
- `DATABASE_URL` - PostgreSQL connection string (from Vercel Postgres or Neon)
- `SECRET_KEY` - Secret key for session management
- `JWT_SECRET_KEY` - Secret key for JWT tokens

**Frontend:**
- **DO NOT SET** `VITE_API_URL` - Use same-origin with proxy rewrites

**Optional:**
- `VITE_GOOGLE_CLIENT_ID` - For Google OAuth (if enabled)
- `VITE_APPLE_CLIENT_ID` - For Apple Sign-In (if enabled)
- `VITE_SENTRY_DSN` - For error tracking (if enabled)

### Local Development

In `frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
```

This overrides the same-origin behavior for local development.

## Troubleshooting

### API requests return 404
1. Check that the rewrite rule is present in `vercel.json`
2. Verify the Render backend URL is correct
3. Redeploy to Vercel to apply configuration changes

### CORS errors in browser console
1. Make sure `VITE_API_URL` is NOT set in Vercel environment variables
2. Frontend should use relative URLs (`/api/*`)
3. Redeploy frontend after removing the variable

### Backend connection issues
1. Check Render service status
2. Verify the backend URL in the rewrite rule matches your Render deployment
3. Test the backend health endpoint directly: `https://hiremebahamas.onrender.com/health`

## Related Documentation

- `API_CONNECTION_GUIDE.md` - Comprehensive API connection guide
- `DEPLOYMENT_GUIDE.md` - Full deployment instructions
- `SECURITY.md` - Security best practices

## References

- [Vercel Rewrites Documentation](https://vercel.com/docs/projects/project-configuration#rewrites)
- [Vercel Headers Documentation](https://vercel.com/docs/projects/project-configuration#headers)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
