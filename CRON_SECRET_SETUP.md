# CRON_SECRET Setup Guide

This guide explains how to configure the `CRON_SECRET` environment variable to secure your Vercel cron job endpoints.

## Overview

The `CRON_SECRET` provides authorization protection for cron job endpoints to prevent unauthorized access. When configured, Vercel automatically includes this secret in the `Authorization` header when invoking cron jobs.

## Affected Endpoints

The following endpoints now require authorization when `CRON_SECRET` is set:

1. `/api/cron` - Main cron job for database warmup and cache refresh (TypeScript)
2. `/api/health` - Health check endpoint used by cron (TypeScript)
3. `/api/cron/health` - Health check endpoint for Python backend

## Setup Instructions

### 1. Generate a Secure Secret

Generate a random secret token (minimum 32 characters):

```bash
# Using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### 2. Add to Vercel Project

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add a new environment variable:
   - **Name**: `CRON_SECRET`
   - **Value**: The generated secret from step 1
   - **Environments**: Select Production (and Staging/Development if needed)
4. Click **Save**

### 3. Redeploy

After adding the environment variable, trigger a new deployment for the changes to take effect:

```bash
git push origin main
```

Or manually redeploy from the Vercel dashboard.

## How It Works

### Authorization Flow

1. Vercel cron job triggers at the scheduled time
2. Vercel automatically adds the `Authorization` header: `Bearer {CRON_SECRET}`
3. The endpoint handler checks if the header matches the expected value
4. If valid: Process the request normally
5. If invalid or missing: Return 401 Unauthorized

### Security Features

- **Constant-time comparison**: Uses `secrets.compare_digest()` (Python) and `crypto.timingSafeEqual()` (Node.js) to prevent timing attacks
- **Bearer token format**: Follows standard OAuth 2.0 Bearer token pattern
- **Optional security**: Authorization is only enforced when `CRON_SECRET` is set
- **Consistent error response**: All unauthorized requests receive the same 401 response

## Testing

### Test Authorization (with CRON_SECRET set)

```bash
# Should return 401 Unauthorized (no auth header)
curl https://your-domain.vercel.app/api/cron

# Should return 401 Unauthorized (wrong secret)
curl -H "Authorization: Bearer wrong-secret" https://your-domain.vercel.app/api/cron

# Should return 200 OK (correct secret)
curl -H "Authorization: Bearer your-actual-secret" https://your-domain.vercel.app/api/cron
```

### Test Without CRON_SECRET

If `CRON_SECRET` is not set, the endpoints will work without authorization:

```bash
# Should return 200 OK (no auth required)
curl https://your-domain.vercel.app/api/cron
```

## Troubleshooting

### Cron jobs failing with 401 errors

**Cause**: The `CRON_SECRET` environment variable is set in your Vercel project, but Vercel isn't sending it correctly.

**Solution**:
1. Verify the environment variable is set in Vercel dashboard
2. Ensure you've redeployed after adding the variable
3. Check Vercel's cron job logs for any errors

### Endpoints not requiring authorization

**Cause**: The `CRON_SECRET` environment variable is not set.

**Solution**:
- This is expected behavior - authorization is optional
- Add `CRON_SECRET` to Vercel environment variables to enable authorization

### 401 errors when accessing endpoints manually

**Cause**: You're trying to access a cron endpoint directly, but `CRON_SECRET` is enabled.

**Solution**:
- These endpoints are designed for cron jobs, not manual access
- If you need to test them, include the Authorization header with the correct secret
- For health checks outside of cron, use dedicated health endpoints

## Security Best Practices

1. **Use strong secrets**: Generate random tokens with at least 32 characters
2. **Keep secrets confidential**: Never commit secrets to source control
3. **Rotate regularly**: Change the secret periodically (e.g., every 90 days)
4. **Use different secrets per environment**: Don't reuse the same secret across dev/staging/production
5. **Monitor access**: Review Vercel logs for unauthorized access attempts

## Implementation Details

### Python (api/cron/health.py)

```python
cron_secret = os.getenv("CRON_SECRET")
if cron_secret:
    auth_header = self.headers.get("Authorization", "")
    expected_auth = f"Bearer {cron_secret}"
    if not secrets.compare_digest(auth_header, expected_auth):
        # Return 401 Unauthorized
```

### TypeScript (next-app/app/api/cron/route.ts, next-app/app/api/health/route.ts)

```typescript
const cronSecret = process.env.CRON_SECRET;
if (cronSecret) {
  const authHeader = request.headers.get("Authorization") || "";
  const expectedAuth = `Bearer ${cronSecret}`;
  
  const authBuffer = Buffer.from(authHeader);
  const expectedBuffer = Buffer.from(expectedAuth);
  
  const lengthsMatch = authBuffer.length === expectedBuffer.length;
  const valuesMatch = lengthsMatch && timingSafeEqual(authBuffer, expectedBuffer);
  
  if (!valuesMatch) {
    // Return 401 Unauthorized
  }
}
```

## References

- [Vercel Cron Jobs Documentation](https://vercel.com/docs/cron-jobs)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [OAuth 2.0 Bearer Token Usage](https://datatracker.ietf.org/doc/html/rfc6750)
