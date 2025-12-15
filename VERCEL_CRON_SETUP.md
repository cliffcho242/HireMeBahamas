# Vercel Cron Job Setup Guide

## Overview
This project includes a serverless cron job function that runs on a schedule using Vercel's cron job feature.

## Files Created
- `pages/api/cron.js` - Serverless function handler for the cron job
- `vercel.json` - Updated with cron configuration

## Configuration

### Cron Schedule
The cron job is scheduled to run **daily at 10:00 AM UTC**.

Schedule format: `0 10 * * *`
- `0` - Minute (0)
- `10` - Hour (10:00 AM)
- `*` - Day of month (every day)
- `*` - Month (every month)
- `*` - Day of week (every day of the week)

### Required Environment Variable

#### CRON_SECRET
You must add the `CRON_SECRET` environment variable to your Vercel project to enable authorization.

**How to add it:**

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add a new environment variable:
   - **Name**: `CRON_SECRET`
   - **Value**: A secure random string (e.g., generate using `openssl rand -hex 32`)
   - **Environment**: Select all environments (Production, Preview, Development)

**Example:**
```bash
# Generate a secure secret
openssl rand -hex 32
# Output: abc123def456...
```

Then add `CRON_SECRET=abc123def456...` to your Vercel project.

## Security

### Authorization
The cron function includes authorization checking to prevent unauthorized access:

```javascript
if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
  return res.status(401).end('Unauthorized');
}
```

Vercel automatically adds the `CRON_SECRET` value to the `Authorization` header when triggering cron jobs, so only Vercel can call this endpoint successfully.

### Benefits
- Prevents unauthorized external calls to the cron endpoint
- Ensures only Vercel's cron scheduler can trigger the function
- Protects against abuse and unauthorized execution

## Testing

### Local Testing
You can test the function locally:

```bash
# Run the test suite
node test_cron_function.js
```

### Manual Testing
To manually test the endpoint (after deployment):

```bash
# Without authorization (should return 401)
curl -X GET https://your-domain.vercel.app/api/cron

# With authorization (should return 200)
curl -X GET https://your-domain.vercel.app/api/cron \
  -H "Authorization: Bearer YOUR_CRON_SECRET"
```

## Monitoring

### View Cron Logs
1. Go to your Vercel project dashboard
2. Navigate to **Deployments** → Select your deployment
3. Click on **Functions** → Select the cron function
4. View logs to see execution history

### Cron Job Status
Vercel provides a dashboard to monitor cron job execution:
- Success/failure status
- Execution time
- Error logs (if any)

## Customization

### Change Schedule
Edit the `schedule` field in `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron",
      "schedule": "0 10 * * *"  // Change this
    }
  ]
}
```

Common schedules:
- Every hour: `0 * * * *`
- Every 6 hours: `0 */6 * * *`
- Every day at midnight: `0 0 * * *`
- Every Monday at 9 AM: `0 9 * * 1`

### Add Custom Logic
Edit `pages/api/cron.js` to add your custom cron job logic:

```javascript
export default function handler(req, res) {
  // Authorization check
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).end('Unauthorized');
  }
  
  // Add your custom logic here
  // - Database cleanup
  // - Send notifications
  // - Generate reports
  // - Cache warming
  // - etc.
  
  res.status(200).end('Hello Cron!');
}
```

## Limitations

### Vercel Hobby Plan
- Up to 2 cron jobs included for free
- Maximum execution time: 10 seconds (configurable)
- Cron jobs run in serverless environment

### Pro/Enterprise Plans
- More cron jobs available
- Longer execution times
- Advanced monitoring features

## References
- [Vercel Cron Jobs Documentation](https://vercel.com/docs/cron-jobs)
- [Cron Schedule Format](https://crontab.guru/)
