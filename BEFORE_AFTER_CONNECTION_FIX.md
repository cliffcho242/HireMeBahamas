# Before/After: Vercel → Backend Connection Fix

This document shows the changes made to fix hardcoded localhost URLs in the frontend.

## 🔴 BEFORE (Broken)

### Problem

The frontend had hardcoded localhost URLs that would fail in production:

```typescript
// ❌ Stories.tsx - BEFORE
const fetchStories = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8008/api/stories');
    // ...
  }
}

// ❌ AdvancedAIContext.tsx - BEFORE  
export const AdvancedAIProvider: React.FC<AdvancedAIProviderProps> = ({
  children,
  apiBaseUrl = 'http://127.0.0.1:8009/api/ai'
}) => {
  // ...
}

// ❌ AIMonitoringContext.tsx - BEFORE
export const AIMonitoringProvider: React.FC<AIMonitoringProviderProps> = ({
  children,
  backendUrl = 'http://127.0.0.1:8008',
  // ...
}) => {
  // ...
}

// ❌ graphql/client.ts - BEFORE
let API_BASE_URL = 'http://127.0.0.1:9999';

if (!ENV_API && typeof window !== 'undefined') {
  const hostname = window.location.hostname;
  const isProduction = hostname === 'hiremebahamas.com' || 
                       hostname === 'www.hiremebahamas.com';
  const isVercel = hostname.includes('.vercel.app');
  
  if (isProduction || isVercel) {
    API_BASE_URL = window.location.origin;
  }
}

// ❌ lib/realtime.ts - BEFORE
let SOCKET_URL = 'http://127.0.0.1:9999';

if (!ENV_API && typeof window !== 'undefined') {
  const hostname = window.location.hostname;
  const isProduction = hostname === 'hiremebahamas.com' || 
                       hostname === 'www.hiremebahamas.com';
  const isVercel = hostname.includes('.vercel.app');
  
  if (isProduction || isVercel) {
    SOCKET_URL = window.location.origin;
  }
}

// ❌ api.ts - BEFORE
let API_BASE_URL = 'http://127.0.0.1:8000';

if (!ENV_API && typeof window !== 'undefined') {
  const hostname = window.location.hostname;
  const isProduction = hostname === 'hiremebahamas.com' || 
                       hostname === 'www.hiremebahamas.com';
  const isVercel = hostname.includes('.vercel.app');
  
  if (isProduction || isVercel) {
    API_BASE_URL = window.location.origin;
  }
}
```

### Why This Was Broken

1. **Hardcoded localhost in components** - Would always try to connect to localhost in all environments
2. **Complex hostname detection** - Required checking specific domains
3. **Default to localhost** - If domain check failed, would fallback to localhost
4. **Inconsistent ports** - Different files used different localhost ports (8000, 8008, 8009, 9999)

### What Happened in Production

```
❌ Frontend deployed to: https://hiremebahamas.vercel.app
❌ Tries to fetch: http://127.0.0.1:8008/api/stories
❌ Result: Connection refused / Network error
```

## 🟢 AFTER (Fixed)

### Solution

Use environment variable or same-origin, never hardcode localhost in components:

```typescript
// ✅ Stories.tsx - AFTER
const fetchStories = async () => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;
    const response = await axios.get(`${apiUrl}/api/stories`);
    // ...
  }
}

// ✅ AdvancedAIContext.tsx - AFTER
export const AdvancedAIProvider: React.FC<AdvancedAIProviderProps> = ({
  children,
  apiBaseUrl = import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}/api/ai`
    : (typeof window !== 'undefined' ? `${window.location.origin}/api/ai` : '/api/ai')
}) => {
  // ...
}

// ✅ AIMonitoringContext.tsx - AFTER
export const AIMonitoringProvider: React.FC<AIMonitoringProviderProps> = ({
  children,
  backendUrl = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : ''),
  // ...
}) => {
  // ...
}

// ✅ graphql/client.ts - AFTER
let API_BASE_URL: string;

if (ENV_API) {
  API_BASE_URL = ENV_API;
} else if (typeof window !== 'undefined') {
  API_BASE_URL = window.location.origin;
} else {
  API_BASE_URL = 'http://localhost:8000'; // Only for build-time, not used in practice
}

// ✅ lib/realtime.ts - AFTER
let SOCKET_URL: string;

if (ENV_API) {
  SOCKET_URL = ENV_API;
} else if (typeof window !== 'undefined') {
  SOCKET_URL = window.location.origin;
} else {
  SOCKET_URL = 'http://localhost:8000'; // Only for build-time, not used in practice
}

// ✅ api.ts - AFTER
let API_BASE_URL: string;

if (ENV_API) {
  API_BASE_URL = ENV_API;
} else if (typeof window !== 'undefined') {
  API_BASE_URL = window.location.origin;
} else {
  API_BASE_URL = 'http://localhost:8000'; // Only for build-time, not used in practice
}
```

### Why This Works

1. **Priority-based URL selection:**
   - First: Use `VITE_API_URL` if set (explicit configuration)
   - Second: Use `window.location.origin` (same-origin for Vercel)
   - Last: Fallback to localhost (only for build-time, not runtime)

2. **No hardcoded localhost in components** - All API calls use dynamic URLs

3. **Works in all environments:**
   - **Production (Vercel serverless):** Uses same-origin
   - **Production (separate backend):** Uses `VITE_API_URL` env var
   - **Local development:** Uses `VITE_API_URL` from `.env.local`

4. **Consistent pattern** - All files use the same logic

### What Happens in Production Now

```
✅ Frontend deployed to: https://hiremebahamas.vercel.app
✅ VITE_API_URL not set (using Vercel serverless)
✅ Detects: window.location.origin = https://hiremebahamas.vercel.app
✅ Fetches: https://hiremebahamas.vercel.app/api/stories
✅ Result: Success! Same-origin request, no CORS issues
```

OR

```
✅ Frontend deployed to: https://hiremebahamas.vercel.app
✅ VITE_API_URL = https://backend.render.app (set in Vercel)
✅ Fetches: https://backend.render.app/api/stories
✅ Result: Success! Backend CORS allows Vercel domain
```

## 📊 Comparison Table

| Aspect | Before (Broken) | After (Fixed) |
|--------|----------------|---------------|
| **Component URLs** | Hardcoded localhost | Dynamic via env var or same-origin |
| **Production Detection** | Complex hostname checks | Simple: env var or same-origin |
| **Default Behavior** | Falls back to localhost | Falls back to same-origin |
| **Local Development** | Hardcoded in code | Configured via `.env.local` |
| **Deployment Config** | Requires code changes | Environment variable only |
| **CORS Issues** | Can occur | Avoided with same-origin |
| **Port Consistency** | Multiple ports (8000, 8008, 9999) | Standardized (8000 fallback) |
| **Build-time Safety** | Could fail | Has safe fallback |

## 🎯 Key Improvements

### 1. Eliminated Hardcoded URLs
**Before:** `'http://127.0.0.1:8008/api/stories'`
**After:** `${apiUrl}/api/stories` where `apiUrl` is dynamic

### 2. Simplified Configuration
**Before:** Required checking `hostname === 'hiremebahamas.com'` etc.
**After:** Simple priority: env var → same-origin → fallback

### 3. Better Defaults
**Before:** Default to localhost (fails in production)
**After:** Default to same-origin (works in production)

### 4. Explicit Configuration
**Before:** Needed code changes to switch backends
**After:** Just set `VITE_API_URL` environment variable

## 🚀 Usage Examples

### Example 1: Vercel Serverless Backend

```bash
# No configuration needed!
# Deploy frontend to Vercel
# Backend runs as serverless functions in /api
# Frontend automatically uses same-origin
```

Result:
- Frontend: `https://app.vercel.app`
- API calls: `https://app.vercel.app/api/*`
- ✅ No CORS, no configuration needed

### Example 2: Render Backend

```bash
# In Vercel Dashboard → Environment Variables:
VITE_API_URL=https://backend.render.app

# Deploy frontend to Vercel
```

Result:
- Frontend: `https://app.vercel.app`
- API calls: `https://backend.render.app/api/*`
- ✅ Works if backend CORS allows Vercel domain

### Example 3: Local Development

```bash
# In frontend/.env.local:
VITE_API_URL=http://localhost:8000

# Start backend on port 8000
# Start frontend with npm run dev
```

Result:
- Frontend: `http://localhost:5173`
- API calls: `http://localhost:8000/api/*`
- ✅ Works for local development

## 🔒 Security Benefits

1. **No hardcoded URLs** - Reduces attack surface
2. **Environment-based config** - Secrets stay in environment variables
3. **Same-origin by default** - Avoids CORS vulnerabilities
4. **CodeQL verified** - No security issues found

## ✅ Conclusion

The fix transforms the frontend from having hardcoded localhost URLs that break in production to a flexible, environment-aware system that:

- ✅ Works with Vercel serverless backend (same-origin)
- ✅ Works with separate backends (Render, Render) via env var
- ✅ Works in local development with proper configuration
- ✅ Never tries to connect to localhost in production
- ✅ Has clear, maintainable code
- ✅ Passes security validation

**Result:** The Vercel → Backend connection now works correctly in all deployment scenarios! 🎉
