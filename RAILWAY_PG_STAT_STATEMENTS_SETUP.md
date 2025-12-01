# Railway PostgreSQL pg_stat_statements Setup Guide

## Overview

This guide provides a **PERMANENT** solution for enabling `pg_stat_statements` on Railway-hosted PostgreSQL databases. This extension is essential for performance monitoring, query optimization, and integrating tools like PgHero.

## The Problem

When trying to query `pg_stat_statements` for performance monitoring, you get this error:

```json
{"success":false,"error":"ERROR: pg_stat_statements must be loaded via \"shared_preload_libraries\"","rows":[],"rowCount":0}
```

This occurs because `pg_stat_statements` requires server-side configuration (`shared_preload_libraries`) which isn't enabled by default on Railway's managed PostgreSQL.

---

## Solution Options

### Option 1: Railway Custom Postgres Image (Recommended)

Railway allows you to use a custom Docker image for your PostgreSQL service. This is the most reliable and permanent solution.

#### Step 1: Create a Custom PostgreSQL Dockerfile

Create a new file `postgres/Dockerfile` in a separate repo or directory:

```dockerfile
# Custom PostgreSQL with pg_stat_statements enabled
FROM postgres:16-alpine

# Create custom postgresql.conf with pg_stat_statements
RUN echo "shared_preload_libraries = 'pg_stat_statements'" >> /usr/local/share/postgresql/postgresql.conf.sample
RUN echo "pg_stat_statements.max = 10000" >> /usr/local/share/postgresql/postgresql.conf.sample
RUN echo "pg_stat_statements.track = all" >> /usr/local/share/postgresql/postgresql.conf.sample
RUN echo "pg_stat_statements.save = on" >> /usr/local/share/postgresql/postgresql.conf.sample

# Alternatively, use a custom init script
COPY init-pg-stat-statements.sh /docker-entrypoint-initdb.d/
```

#### Step 2: Create the Init Script

Create `postgres/init-pg-stat-statements.sh`:

```bash
#!/bin/bash
set -e

# Enable pg_stat_statements extension
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
EOSQL

echo "pg_stat_statements extension created successfully"
```

#### Step 3: Deploy Custom Image to Railway

1. Push the Dockerfile to a GitHub repo
2. In Railway Dashboard:
   - Go to your project
   - Add a new service → "GitHub Repo"
   - Select your postgres repo
   - Railway will build and deploy your custom Postgres image

### Option 2: Railway Template with Custom Start Command

If you're using Railway's official PostgreSQL plugin, you can try using a custom start command (limited support):

#### Step 1: Railway Dashboard Configuration

1. Go to your Railway project → PostgreSQL service
2. Click on "Settings" tab
3. Under "Deploy" section, find "Start Command"
4. Enter the custom command:

```bash
docker-entrypoint.sh postgres -c shared_preload_libraries=pg_stat_statements -c pg_stat_statements.track=all -c pg_stat_statements.max=10000
```

> **Note**: This method may not work with Railway's managed PostgreSQL plugin. If it doesn't work, use Option 1 (Custom Image) or Option 3 (External Provider).

### Option 3: Use Neon, Supabase, or Other Managed PostgreSQL

Several managed PostgreSQL providers have `pg_stat_statements` enabled by default:

| Provider | pg_stat_statements | Free Tier | Notes |
|----------|-------------------|-----------|-------|
| **Neon** | ✅ Enabled | Yes | Recommended for Railway apps |
| **Supabase** | ✅ Enabled | Yes | Good free tier |
| **DigitalOcean** | ✅ Enabled | No | Requires paid plan |
| **AWS RDS** | ✅ Configurable | No | Parameter groups |

#### Using Neon with Railway:

1. Create a Neon account at https://neon.tech
2. Create a new project/database
3. Copy the connection string (Neon provides pooled and non-pooled versions)
4. In Railway:
   - Go to your backend service
   - Add environment variable:
   ```
   # Pooled connection (with pgbouncer) - for application queries
   DATABASE_URL=postgres://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require&pgbouncer=true&connect_timeout=15
   
   # Non-pooled connection (without pgbouncer) - for migrations/schema changes
   DATABASE_URL_NON_POOLING=postgres://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require&pgbouncer=false
   ```
5. Redeploy your service

**Note**: Neon/Vercel Postgres uses pgbouncer for connection pooling. Use the pooled connection (`pgbouncer=true`) for application queries and the non-pooled connection (`pgbouncer=false`) for database migrations.

---

## Post-Enable Verification

After enabling `pg_stat_statements`, run these SQL commands to verify:

### Step 1: Create the Extension

```sql
-- Create the extension (run once)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

### Step 2: Verify Installation

```sql
-- Check if extension is installed
SELECT * FROM pg_extension WHERE extname = 'pg_stat_statements';

-- Query performance stats (should return data now)
SELECT 
    query,
    calls,
    total_exec_time AS total_time_ms,
    mean_exec_time AS avg_time_ms,
    rows,
    100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

### Expected Output

```
          query           | calls | total_time_ms | avg_time_ms | rows | hit_percent
--------------------------+-------+---------------+-------------+------+-------------
 SELECT * FROM users ...  |  1234 |     45678.12  |      37.02  | 5678 |       99.8
 UPDATE posts SET ...     |   567 |     12345.67  |      21.78  |  567 |       98.5
 ...
```

---

## PgHero Integration (Recommended)

PgHero provides an excellent dashboard for PostgreSQL performance monitoring.

### Option A: One-Click Railway Template Deploy

1. Go to: https://railway.app/template/pghero
2. Click "Deploy Now"
3. Configure environment variables:
   ```
   DATABASE_URL=<your-postgres-private-url>
   PGHERO_USERNAME=admin
   PGHERO_PASSWORD=<secure-password>
   ```
4. Deploy and access the dashboard

### Option B: Deploy PgHero via Docker

Add PgHero as a new service in your Railway project:

```dockerfile
FROM ankane/pghero

ENV DATABASE_URL=${DATABASE_URL}
ENV PGHERO_USERNAME=admin
ENV PGHERO_PASSWORD=${PGHERO_PASSWORD}

EXPOSE 8080
```

### Option C: Self-Hosted PgHero with Railway

1. Create a new service in Railway
2. Use the "Docker Image" option
3. Image: `ankane/pghero`
4. Add environment variables:
   - `DATABASE_URL`: Your PostgreSQL private URL (use private URL to avoid egress costs)
   - `PGHERO_USERNAME`: Admin username
   - `PGHERO_PASSWORD`: Secure password

### PgHero Features

- ✅ Query performance dashboard
- ✅ Slow query identification (>500ms)
- ✅ Index recommendations
- ✅ Connection monitoring
- ✅ Table statistics
- ✅ Query explain plans

---

## FastAPI/Flask Integration for Real-Time Alerts

The HireMeBahamas backend now includes a `/api/query-stats` endpoint for querying performance metrics programmatically.

### API Endpoint Usage

```bash
# Get top 10 slowest queries
curl -H "Authorization: Bearer <token>" \
     "https://your-backend.railway.app/api/query-stats?limit=10"

# Get queries slower than 500ms
curl -H "Authorization: Bearer <token>" \
     "https://your-backend.railway.app/api/query-stats?min_avg_time_ms=500"
```

### Response Format

```json
{
    "success": true,
    "query_stats": [
        {
            "query": "SELECT * FROM users WHERE email = $1",
            "calls": 1234,
            "total_time_ms": 45678.12,
            "avg_time_ms": 37.02,
            "rows": 1234,
            "hit_percent": 99.8
        }
    ],
    "extension_available": true,
    "message": "Query stats retrieved successfully"
}
```

### Slow Query Alerting Example

```python
import requests

def check_slow_queries(threshold_ms=500):
    """Check for queries slower than threshold and alert."""
    response = requests.get(
        f"https://your-api.railway.app/api/query-stats?min_avg_time_ms={threshold_ms}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    data = response.json()
    if data["success"] and data["query_stats"]:
        for query in data["query_stats"]:
            # Send alert (Slack, email, etc.)
            print(f"⚠️ Slow query detected: {query['avg_time_ms']:.2f}ms - {query['query'][:100]}")
```

---

## Troubleshooting

### Error: "pg_stat_statements must be loaded via shared_preload_libraries"

This means `pg_stat_statements` isn't preloaded at server startup. Solutions:
1. Use a custom PostgreSQL image (Option 1)
2. Switch to a provider that supports it (Option 3)
3. The `/api/query-stats` endpoint will return graceful error with `extension_available: false`

### Error: "permission denied for function pg_stat_statements_reset"

Your database user needs superuser privileges or the `pg_read_all_stats` role:

```sql
-- Grant read access to stats (safer than superuser)
GRANT pg_read_all_stats TO your_db_user;
```

### High Memory Usage with pg_stat_statements

Reduce `pg_stat_statements.max` to limit memory usage:

```sql
-- In postgresql.conf or start command
pg_stat_statements.max = 5000  -- Default is 5000, reduce if needed
```

---

## Security Considerations

1. **Protect the /api/query-stats endpoint**: Requires authentication
2. **Use private URLs**: When connecting PgHero to Railway Postgres, use the private URL to avoid egress costs
3. **Limit stats access**: Only grant `pg_read_all_stats` role, not superuser
4. **Secure PgHero**: Always set strong username/password for PgHero dashboard

---

## Summary

| Method | Permanence | Complexity | Cost |
|--------|------------|------------|------|
| Custom Postgres Image | ✅ Permanent | Medium | Free |
| Custom Start Command | ⚠️ May not work | Low | Free |
| External Provider (Neon) | ✅ Permanent | Low | Free tier available |
| PgHero Dashboard | N/A | Low | Free |

**Recommended approach**: Use Neon for production if Railway's managed PostgreSQL doesn't support custom configurations, or deploy a custom PostgreSQL image on Railway.
