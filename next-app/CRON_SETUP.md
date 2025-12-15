# Vercel Cron Job Setup

This project includes a serverless cron job that runs on Vercel's platform.

## Overview

The cron job is located at `/app/api/cron/route.ts` and performs the following tasks:
- Warms the database connection pool
- Refreshes cache for frequently accessed data
- Logs health metrics

## Configuration

### 1. Schedule
The cron job runs **daily at 10:00 AM UTC** as configured in `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron",
      "schedule": "0 10 * * *"
    }
  ]
}
```

Schedule format follows standard cron syntax:
- `0 10 * * *` = At 10:00 AM every day

### 2. Authorization

The endpoint is protected with a secret to prevent unauthorized access.

#### Setting up CRON_SECRET

1. In your Vercel project dashboard, go to **Settings** → **Environment Variables**
2. Add a new environment variable:
   - **Name:** `CRON_SECRET`
   - **Value:** A secure random string. Generate one using:
     - OpenSSL: `openssl rand -hex 32`
     - Node.js: `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`
     - Python: `python -c "import secrets; print(secrets.token_hex(32))"`
     - Or use a secure online generator like [1Password](https://1password.com/password-generator/)
   - **Environment:** All (Production, Preview, Development)

3. Redeploy your application for the changes to take effect

#### How it works

When Vercel triggers the cron job, it automatically includes the `CRON_SECRET` in the `Authorization` header as:
```
Authorization: Bearer YOUR_CRON_SECRET
```

The route handler validates this header before executing:

```typescript
const authHeader = request.headers.get("Authorization");
const expectedAuth = `Bearer ${process.env.CRON_SECRET}`;

if (authHeader !== expectedAuth) {
  return NextResponse.json(
    { error: "Unauthorized" },
    { status: 401 }
  );
}
```

## Testing

### Manual Testing (Local Development)

You can test the endpoint locally by running:

```bash
curl -H "Authorization: Bearer YOUR_CRON_SECRET" http://localhost:3000/api/cron
```

Replace `YOUR_CRON_SECRET` with your actual secret.

### Expected Response

**Success (200):**
```json
{
  "success": true,
  "message": "Keep-alive cron executed successfully",
  "timestamp": "2024-12-15T18:00:00.000Z",
  "duration": "125ms",
  "results": {
    "database": { "status": "connected", "ping": 1 },
    "jobsCache": { "refreshed": true, "count": 42 },
    "usersCache": { "refreshed": true, "count": 150 },
    "latestJobsCache": { "refreshed": true, "count": 20 }
  }
}
```

**Unauthorized (401):**
```json
{
  "error": "Unauthorized"
}
```

## Monitoring

You can monitor cron job executions in:
1. **Vercel Dashboard** → **Deployments** → **Functions** → **Cron**
2. **Logs** - Check the function logs for execution details
3. **Error Tracking** - Set up alerts for failed executions

## Security Best Practices

1. **Never commit the CRON_SECRET** - Always use environment variables
2. **Use a strong secret** - Generate with `openssl rand -hex 32` or similar
3. **Rotate secrets regularly** - Update the CRON_SECRET periodically
4. **Monitor logs** - Watch for unauthorized access attempts

## Troubleshooting

### Cron job not running
- Check that the cron is configured in `vercel.json`
- Verify your Vercel plan supports cron jobs
- Check function logs for errors

### 401 Unauthorized errors
- Verify `CRON_SECRET` is set in Vercel environment variables
- Ensure the secret matches on both sides
- Redeploy after adding the environment variable

### Function timeout
- The default timeout for serverless functions on Vercel is 10 seconds (Hobby plan) or up to 60 seconds (Pro plan)
- If operations take longer, optimize queries or add a `maxDuration` configuration in `vercel.json`:
  ```json
  "functions": {
    "app/api/cron/route.ts": {
      "maxDuration": 30
    }
  }
  ```

## Additional Resources

- [Vercel Cron Jobs Documentation](https://vercel.com/docs/cron-jobs)
- [Vercel Environment Variables](https://vercel.com/docs/environment-variables)
- [Next.js Route Handlers](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
