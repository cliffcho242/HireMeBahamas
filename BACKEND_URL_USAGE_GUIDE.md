# Backend URL Usage Guide for Vite Projects

## ✅ Correct Usage

This project uses **Vite** (not Next.js), so the correct environment variable is `VITE_API_URL`.

### Step 1: Define the Backend URL Variable

```typescript
// ✅ CORRECT: Use VITE_API_URL environment variable (exposed to browser by Vite)
const BACKEND_URL = import.meta.env.VITE_API_URL;
```

### Step 2: Use it in fetch calls

```typescript
// ✅ CORRECT: Use the environment variable in fetch calls
fetch(`${BACKEND_URL}/api/auth/me`);

// ✅ CORRECT: With proper URL construction
const url = BACKEND_URL ? `${BACKEND_URL}/api/auth/me` : `${window.location.origin}/api/auth/me`;
fetch(url);
```

## ❌ Wrong Usage Patterns

### 1. Hardcoded localhost
```typescript
// ❌ WRONG: Hardcoded localhost causes errors in production
fetch("localhost:8000/api/auth/me");
fetch("http://localhost:8000/api/auth/me");
```

### 2. Using non-exposed environment variables
```typescript
// ❌ WRONG: process.env.BACKEND_URL is not exposed to browser in Vite
fetch(process.env.BACKEND_URL);

// ❌ WRONG: NEXT_PUBLIC_BACKEND_URL is for Next.js, not Vite
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;
```

### 3. Double slashes in URL
```typescript
// ❌ WRONG: Double slash in URL path
fetch(`${BACKEND_URL}//api/auth/me`);
```

## Environment Variable Configuration

### For Vite Projects (This Project)
- Use `VITE_API_URL` in your `.env` file
- All variables prefixed with `VITE_` are exposed to the browser
- Example: `VITE_API_URL=https://api.example.com`

### For Next.js Projects (Not This Project)
- Use `NEXT_PUBLIC_BACKEND_URL` in your `.env` file
- All variables prefixed with `NEXT_PUBLIC_` are exposed to the browser
- Example: `NEXT_PUBLIC_BACKEND_URL=https://api.example.com`

## Configuration Options

### Option A: Vercel Serverless (Recommended)
```bash
# Don't set VITE_API_URL
# Frontend will automatically use same-origin (/api/* routing)
```

### Option B: Separate Backend (Railway/Render)
```bash
# Set VITE_API_URL to your backend URL
VITE_API_URL=https://your-app.up.railway.app
```

### Option C: Local Development
```bash
# Set VITE_API_URL to local backend
VITE_API_URL=http://localhost:8000
```

## Best Practices

1. **Never hardcode URLs**: Always use environment variables
2. **Provide fallback logic**: Use `window.location.origin` as fallback for same-origin deployments
3. **Validate URLs**: Ensure no double slashes or missing protocols
4. **Clear error messages**: Throw descriptive errors when configuration is missing
5. **Document configuration**: Keep `.env.example` up to date with clear instructions

## Implementation Examples

### API Service
```typescript
// Get backend URL from environment or use same-origin
const BACKEND_URL = import.meta.env.VITE_API_URL;

let API_BASE_URL: string;

if (BACKEND_URL) {
  // Use explicit environment variable if provided
  API_BASE_URL = BACKEND_URL;
} else if (typeof window !== 'undefined') {
  // Use same-origin for serverless deployments
  API_BASE_URL = window.location.origin;
} else {
  // Fail gracefully with clear error message
  throw new Error('API_BASE_URL could not be determined. Set VITE_API_URL environment variable.');
}
```

### Fetch Calls
```typescript
// ✅ CORRECT: Construct full URL
const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// ✅ CORRECT: Use helper function
import { getApiUrl } from '../utils/backendRouter';
const response = await fetch(getApiUrl('/auth/me'));
```

## Troubleshooting

### Error: Cannot connect to backend
1. Check that `VITE_API_URL` is set correctly in your environment
2. Verify the backend is running and accessible
3. Check for CORS issues if using separate backend

### Error: 404 Not Found
1. Verify the API endpoint path is correct
2. Check that backend routes are properly configured
3. Ensure no double slashes in URL construction

### Error: Environment variable not defined
1. Ensure `.env` file exists in frontend directory
2. Verify variable is prefixed with `VITE_`
3. Restart dev server after changing `.env` file

## Summary

✅ **DO**
- Use `VITE_API_URL` for backend URL in Vite projects
- Access via `import.meta.env.VITE_API_URL`
- Provide same-origin fallback for Vercel serverless
- Document configuration in `.env.example`

❌ **DON'T**
- Hardcode `localhost:8000` in production code
- Use `process.env.BACKEND_URL` (not exposed to browser)
- Use `NEXT_PUBLIC_*` variables in Vite projects
- Create URLs with double slashes
