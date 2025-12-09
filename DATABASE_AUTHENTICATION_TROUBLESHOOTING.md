# Database Authentication Troubleshooting Guide

This guide helps you resolve PostgreSQL authentication errors like:
```
⚠️ Failed to create connection pool: password authentication failed for user "hiremebahamas_user"
```

## Understanding the Error

This error means the application is trying to connect to PostgreSQL, but the credentials (username or password) are incorrect or the database user doesn't exist.

## Quick Diagnosis

Check your deployment logs for these messages:
- `✅ Using DATABASE_PRIVATE_URL` - Good! Using Railway's private network
- `✅ Using DATABASE_URL` - Using public connection
- `⚠️ No DATABASE_URL found` - **Problem**: Environment variable not set
- `❌ DATABASE AUTHENTICATION ERROR` - **Problem**: Credentials are incorrect

## Solutions by Platform

### Railway Deployment (Backend)

1. **Check Database Service Status**
   - Go to your Railway project dashboard
   - Verify your PostgreSQL service is running (green status)
   - Click on the PostgreSQL service

2. **Get the Correct Connection String**
   - In PostgreSQL service, go to the "Connect" tab
   - Copy the `DATABASE_PRIVATE_URL` (recommended for internal connections)
   - **DO NOT** use `DATABASE_PUBLIC_URL` unless connecting from outside Railway

3. **Update Backend Environment Variables**
   - Go to your backend service in Railway
   - Navigate to "Variables" tab
   - Set or update `DATABASE_PRIVATE_URL` with the value from step 2
   - **Important**: Remove any old `DATABASE_URL` that points to a different database

4. **Verify the Connection String Format**
   ```
   postgresql://username:password@hostname:5432/database
   ```
   - Make sure it starts with `postgresql://` (not `postgres://`)
   - All parts must be present: username, password, hostname, port, database name

5. **Trigger Redeploy**
   - After updating variables, Railway will automatically redeploy
   - Wait for the new deployment to complete
   - Check logs for `✅ PostgreSQL pool` message

### Vercel Deployment (Frontend/API Routes)

1. **Check Environment Variables**
   - Go to your Vercel project settings
   - Navigate to "Environment Variables"
   - Verify `DATABASE_URL` is set correctly

2. **Get Railway Database Connection String**
   - In Railway PostgreSQL service, go to "Connect"
   - Copy the `DATABASE_URL` (public connection)
   - **Note**: Vercel cannot use `DATABASE_PRIVATE_URL` as it's external to Railway

3. **Update Vercel Environment Variable**
   - Set `DATABASE_URL` in Vercel to the Railway public connection string
   - Make sure to set it for the correct environment (Production/Preview/Development)
   - Click "Save"

4. **Redeploy**
   - Go to "Deployments" tab
   - Click "..." on the latest deployment
   - Select "Redeploy"

### Local Development

1. **Check .env File**
   - Look for `.env` file in project root
   - Verify `DATABASE_URL` is set

2. **Use Local PostgreSQL or Railway Database**
   
   **Option A: Local PostgreSQL**
   ```bash
   DATABASE_URL=postgresql://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas
   ```
   - Ensure PostgreSQL is running locally
   - Create the database and user if they don't exist

   **Option B: Connect to Railway Database**
   ```bash
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@containers-us-west-xxx.railway.app:5432/railway
   ```
   - Get this from Railway PostgreSQL "Connect" tab
   - Use `DATABASE_URL` (public), not `DATABASE_PRIVATE_URL`

3. **Test Connection**
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DATABASE_URL'))"
   ```
   - This shows what DATABASE_URL the app will use

## Common Issues and Fixes

### Issue 1: Old DATABASE_URL Pointing to Deleted Database

**Symptoms:**
- Error: `password authentication failed`
- You've created a new database but app still tries the old one

**Fix:**
1. Update `DATABASE_URL` or `DATABASE_PRIVATE_URL` to point to new database
2. Remove any cached or old environment variables
3. Redeploy the application

### Issue 2: Using Wrong Connection String Type

**Symptoms:**
- Railway backend can't connect
- Error mentions timeout or authentication failure

**Fix:**
- Railway backend → Use `DATABASE_PRIVATE_URL`
- Vercel/External → Use `DATABASE_URL` (public)
- Never use `DATABASE_PRIVATE_URL` from outside Railway

### Issue 3: Password Contains Special Characters

**Symptoms:**
- Connection string looks correct but fails
- Password has symbols like `@`, `:`, `/`, `?`, `#`

**Fix:**
- Special characters in passwords must be URL-encoded
- Common encodings:
  - `@` → `%40`
  - `:` → `%3A`
  - `/` → `%2F`
  - `?` → `%3F`
  - `#` → `%23`
  - `%` → `%25`
- Railway provides already-encoded connection strings

### Issue 4: Whitespace in Environment Variable

**Symptoms:**
- Connection string looks correct when viewed
- Still fails with authentication error

**Fix:**
- Environment variables might have invisible whitespace
- Re-copy the connection string from Railway
- Or manually edit to remove any spaces/newlines

### Issue 5: Wrong Database User

**Symptoms:**
- Error shows `password authentication failed for user "hiremebahamas_user"`
- But Railway uses `postgres` as default user

**Fix:**
- Check the username in your DATABASE_URL
- Railway default format: `postgresql://postgres:password@host:5432/railway`
- Your connection string should use `postgres` as the username, not `hiremebahamas_user`

## Verification Steps

After applying any fix:

1. **Check Deployment Logs**
   ```
   ✅ Using DATABASE_PRIVATE_URL (Railway private network)
   ✅ Database config parsed: postgres@xxx.railway.internal:5432/railway
   ✅ PostgreSQL pool: min=2, max=5, timeout=45s
   ```

2. **Test API Health Check**
   - Visit: `https://your-backend.railway.app/health`
   - Should return: `{"status": "healthy"}`

3. **Check Connection Pool**
   - Look for: `✅ Initial database keepalive ping 1/5 successful`
   - If you see multiple failures, credentials are still wrong

## Getting Help

If you're still stuck:

1. **Check Railway Logs**
   - Railway project → Select service → View logs
   - Look for red error messages

2. **Verify Database Exists**
   - Railway project → PostgreSQL service
   - Should show "Active" status
   - Click "Data" tab to verify it's accessible

3. **Test Direct Connection**
   - Use a PostgreSQL client (psql, DBeaver, pgAdmin)
   - Connect using the credentials from Railway
   - If this fails, the issue is with Railway database setup, not your app

4. **Contact Support**
   - Railway: https://railway.app/help
   - Include: service name, error message, and connection string (with password masked)

## Prevention Tips

1. **Use Environment Variable References in Railway**
   - Railway can auto-inject variables from linked services
   - In backend service, reference PostgreSQL: `${{Postgres.DATABASE_PRIVATE_URL}}`
   - This automatically updates if database credentials change

2. **Separate Environments**
   - Use different databases for production and development
   - Never connect production app to development database

3. **Document Your Setup**
   - Keep a record of which DATABASE_URL each service uses
   - Note whether it's PRIVATE_URL or public URL

4. **Regular Backups**
   - Enable Railway automated backups
   - Test restore process occasionally
