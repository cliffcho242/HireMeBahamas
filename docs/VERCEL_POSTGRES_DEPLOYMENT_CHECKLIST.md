# VERCEL POSTGRES OPTIMIZATION - DEPLOYMENT CHECKLIST

## MASTERMIND VERCEL POSTGRES + DRIZZLE SETUP (2025)

### ⚡ Performance Targets
- **< 1ms** average query time
- **0** connection pool errors
- **10k+** concurrent users
- **Cheaper** than Railway Hobby
- **Zero** downtime deploys

---

## 📋 7-STEP DEPLOYMENT CHECKLIST

### ✅ Step 1: Create Vercel Postgres Database

```bash
# In Vercel Dashboard:
# 1. Go to Storage → Create Database → Postgres
# 2. Select your region (closest to users)
# 3. Copy the connection strings
```

**Connection String Format:**
```
POSTGRES_URL="postgres://user:pass@host:5432/db?pgbouncer=true&pool_timeout=20"
```

---

### ✅ Step 2: Configure Environment Variables

Add these to Vercel Project Settings → Environment Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `POSTGRES_URL` | Auto-injected | Main connection (pgbouncer) |
| `POSTGRES_URL_NON_POOLING` | Auto-injected | Direct connection (migrations) |
| `POSTGRES_PRISMA_URL` | Auto-injected | Same as POSTGRES_URL |
| `POSTGRES_HOST` | Auto-injected | Database host |
| `POSTGRES_DATABASE` | Auto-injected | Database name |
| `POSTGRES_USER` | Auto-injected | Database user |
| `POSTGRES_PASSWORD` | Auto-injected | Database password |

---

### ✅ Step 3: Install Dependencies

```bash
# Frontend (Drizzle ORM)
cd frontend
npm install @vercel/postgres drizzle-orm
npm install -D drizzle-kit tsx

# Backend (SQLAlchemy - if needed)
pip install sqlalchemy[asyncio] asyncpg psycopg2-binary
```

---

### ✅ Step 4: Run Migrations

```bash
# Generate Drizzle migrations
npx drizzle-kit generate

# Push to Vercel Postgres
npx drizzle-kit push

# Or run the migration script
npx tsx migrate-and-seed.ts
```

---

### ✅ Step 5: Create Database Indexes

Run the index creation script in Vercel Postgres console:

```sql
-- See: docs/DATABASE_INDEXES.sql

-- Quick version - most critical indexes:
CREATE INDEX IF NOT EXISTS jobs_active_recent_idx ON jobs (created_at DESC) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS users_email_idx ON users (email);
CREATE INDEX IF NOT EXISTS messages_receiver_unread_idx ON messages (receiver_id, is_read) WHERE is_read = false;
```

---

### ✅ Step 6: Verify Connection Settings

In Vercel Dashboard → Storage → Postgres → Settings:

| Setting | Recommended Value |
|---------|-------------------|
| Connection Limit | 20 (Hobby) / 100 (Pro) |
| Pool Size | Automatic (pgbouncer) |
| SSL Mode | Required |
| Region | Same as compute |

---

### ✅ Step 7: Deploy and Monitor

```bash
# Deploy to Vercel
vercel --prod

# Check deployment logs for:
# ✓ "Vercel Postgres detected: Using NullPool (pgbouncer mode)"
# ✓ "Database tables initialized successfully"
# ✓ No connection pool errors
```

**Monitoring Dashboard:**
- Vercel Dashboard → Storage → Postgres → Metrics
- Check: Query latency, Connection count, Storage usage

---

## 🔧 Configuration Files Reference

### `frontend/src/lib/db.ts` (Drizzle Client)
```typescript
import { sql } from '@vercel/postgres';
import { drizzle } from 'drizzle-orm/vercel-postgres';
import * as schema from './schema';

export const db = drizzle(sql, { schema });
```

### `frontend/drizzle.config.ts`
```typescript
import type { Config } from 'drizzle-kit';

export default {
  schema: './src/lib/schema.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: process.env.POSTGRES_URL || '',
  },
} satisfies Config;
```

### `backend/app/database.py` (SQLAlchemy)
```python
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

# Vercel Postgres uses NullPool (pgbouncer handles pooling)
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={
        "prepared_statement_cache_size": 0,  # pgbouncer-safe
    }
)
```

### `vercel.json`
```json
{
  "env": {
    "POSTGRES_URL": "@postgres_url",
    "POSTGRES_URL_NON_POOLING": "@postgres_url_non_pooling"
  }
}
```

---

## 📊 Monitoring Queries

Run these in Vercel Postgres console to check performance:

```sql
-- Health check (target: < 1ms)
SELECT NOW();

-- Connection usage (target: < 70%)
SELECT COUNT(*) as connections,
       (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max
FROM pg_stat_activity WHERE datname = current_database();

-- Slow queries (target: avg < 50ms)
SELECT query, calls, ROUND(mean_exec_time::numeric, 2) as avg_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 5;
```

---

## ⚠️ Troubleshooting

### "connection limit exceeded"
- Increase connection limit in Vercel Postgres settings
- Ensure NullPool is being used (no client-side pooling)

### "prepared statement does not exist"
- Set `prepared_statement_cache_size: 0` in connect_args
- This is required for pgbouncer transaction mode

### Slow initial connection
- First connection after cold start may take 100-500ms
- Subsequent connections use warm pool (< 1ms)

### "SSL error: unexpected eof"
- Use the provided SSL context configuration
- Force TLS 1.3 for compatibility

---

## 🎯 Success Metrics

After deployment, verify these metrics:

| Metric | Target | Check |
|--------|--------|-------|
| Health check latency | < 1ms | ✓ |
| Query avg latency | < 10ms | ✓ |
| Connection errors | 0 | ✓ |
| Pool exhaustion | Never | ✓ |
| Cold start time | < 500ms | ✓ |

---

## 📚 Additional Resources

- [Vercel Postgres Docs](https://vercel.com/docs/storage/vercel-postgres)
- [Drizzle ORM Docs](https://orm.drizzle.team/docs/overview)
- [SQLAlchemy Async Docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [pgbouncer Configuration](https://www.pgbouncer.org/config.html)

---

**TOTAL DOMINATION ACHIEVED. 🚀**
