# PostgreSQL Connection String Guide for HireMeBahamas

## Overview

This guide explains how to properly configure PostgreSQL connection strings for different deployment platforms, with specific focus on Vercel Postgres and Neon databases that use pgbouncer for connection pooling.

## Connection String Formats

### Vercel Postgres / Neon (with pgbouncer)

Vercel Postgres and Neon provide multiple connection string formats for different use cases:

#### 1. Pooled Connection (for application queries)

**Environment Variable:** `POSTGRES_URL`  
**Format:** `postgres://user:password@host:5432/database?sslmode=require&pgbouncer=true&connect_timeout=15`

**Use for:**
- API endpoints
- Web application queries
- Regular CRUD operations
- Application logic

**Benefits:**
- Better performance through connection reuse
- Lower connection overhead
- Handles high concurrent request loads

**Example:**
```bash
POSTGRES_URL=postgres://default:ENCRYPTED_PASSWORD@ep-xxxxx.us-east-2.aws.neon.tech/verceldb?sslmode=require&pgbouncer=true&connect_timeout=15
```

#### 2. Non-Pooled Connection (for migrations and schema changes)

**Environment Variable:** `POSTGRES_URL_NON_POOLING`  
**Format:** `postgres://user:password@host:5432/database?sslmode=require&pgbouncer=false`

**Use for:**
- Database migrations
- Schema changes (DDL operations)
- Creating/dropping tables, indexes, extensions
- Operations that don't work with connection poolers

**Benefits:**
- Direct database connection
- Full access to all PostgreSQL features
- No pooler limitations

**Example:**
```bash
POSTGRES_URL_NON_POOLING=postgres://default:ENCRYPTED_PASSWORD@ep-xxxxx.us-east-2.aws.neon.tech/verceldb?sslmode=require&pgbouncer=false
```

#### 3. Prisma Compatible Connection (for Prisma ORM)

**Environment Variable:** `POSTGRES_PRISMA_URL`  
**Format:** Same as `POSTGRES_URL`

**Use for:**
- Prisma ORM queries
- Prisma Client operations

**Example:**
```bash
POSTGRES_PRISMA_URL=$POSTGRES_URL
```

### Railway (Private Network)

Railway provides optimized connection strings for private network access:

**Environment Variable:** `DATABASE_PRIVATE_URL`  
**Format:** `postgresql://user:password@hostname:5432/database`

**Benefits:**
- Zero egress fees (internal network)
- Faster connection (no public internet)
- More secure (private network only)

**Example:**
```bash
DATABASE_PRIVATE_URL=postgresql://railway_user:pass@railway.internal:5432/railway
```

### Standard PostgreSQL

For other platforms or self-hosted PostgreSQL:

**Environment Variable:** `DATABASE_URL`  
**Format:** `postgresql://user:password@hostname:5432/database`

**Example:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
```

## Application Configuration

### Next.js Application (next-app)

The Next.js application uses different connection strings for different purposes:

1. **Application queries** (`lib/db.ts`): Uses `POSTGRES_URL` (pooled)
   - Automatically configured by `@vercel/postgres` package
   - No code changes needed

2. **Database migrations** (`drizzle.config.ts`): Uses `POSTGRES_URL_NON_POOLING`
   - Prefers `POSTGRES_URL_NON_POOLING` for migrations
   - Falls back to `POSTGRES_URL` if non-pooling URL not available
   - Throws error if neither is set

**Example `.env.local`:**
```bash
# Pooled connection for queries
POSTGRES_URL=postgres://user:pass@host/db?sslmode=require&pgbouncer=true&connect_timeout=15

# Non-pooled connection for migrations
POSTGRES_URL_NON_POOLING=postgres://user:pass@host/db?sslmode=require&pgbouncer=false

# For Prisma ORM (if used)
POSTGRES_PRISMA_URL=$POSTGRES_URL
```

### Flask/FastAPI Backend (backend)

The Python backend uses a single connection string with automatic format conversion:

**Priority order:**
1. `DATABASE_PRIVATE_URL` (Railway private network)
2. `DATABASE_URL` (Standard PostgreSQL URL)
3. Local development default

**Automatic conversion:**
- `postgresql://` → `postgresql+asyncpg://` (for asyncpg driver)
- `postgres://` → `postgresql+asyncpg://` (Neon/Vercel format)

**Example `.env`:**
```bash
# For Railway (private network)
DATABASE_PRIVATE_URL=postgresql://railway_user:pass@railway.internal:5432/railway

# For Vercel Postgres/Neon (pooled connection)
DATABASE_URL=postgres://user:pass@host/db?sslmode=require&pgbouncer=true&connect_timeout=15

# The backend will automatically convert to:
# postgresql+asyncpg://user:pass@host/db?sslmode=require&pgbouncer=true&connect_timeout=15
```

## Migration Guide

### Migrating from Railway to Vercel Postgres

1. **Create Vercel Postgres database** in Vercel Dashboard
2. **Get connection strings** from Vercel:
   - `POSTGRES_URL` (pooled)
   - `POSTGRES_URL_NON_POOLING` (non-pooled)
3. **Export data from Railway:**
   ```bash
   pg_dump "$RAILWAY_DATABASE_URL" > backup.sql
   ```
4. **Import to Vercel Postgres** (using non-pooled URL):
   ```bash
   psql "$POSTGRES_URL_NON_POOLING" < backup.sql
   ```
5. **Update environment variables** in both frontend and backend:
   - Frontend: Set `POSTGRES_URL` and `POSTGRES_URL_NON_POOLING`
   - Backend: Set `DATABASE_URL` to `$POSTGRES_URL`
6. **Run migrations** (uses non-pooled URL automatically):
   ```bash
   cd next-app
   npm run db:push
   ```

### Migrating from Render to Vercel Postgres

Follow the same steps as above, replacing `RAILWAY_DATABASE_URL` with your Render database URL.

## Troubleshooting

### Error: "pgbouncer cannot be used with prepared statements"

**Solution:** Use `POSTGRES_URL_NON_POOLING` for operations that require prepared statements or transactions.

### Error: "Database URL not found"

**Solution:** Ensure at least one of these environment variables is set:
- `POSTGRES_URL` (for Next.js app)
- `DATABASE_URL` or `DATABASE_PRIVATE_URL` (for backend)

### Migrations fail with pooled connection

**Solution:** The `drizzle.config.ts` automatically uses `POSTGRES_URL_NON_POOLING` for migrations. Ensure this variable is set in your environment.

### Backend fails to connect to Vercel Postgres

**Solution:** 
1. Ensure `DATABASE_URL` is set to the pooled URL (`POSTGRES_URL`)
2. The backend will automatically convert `postgres://` to `postgresql+asyncpg://`
3. Check that the connection includes `sslmode=require`

## Best Practices

1. **Always use pooled connections** (`pgbouncer=true`) for application queries
2. **Always use non-pooled connections** (`pgbouncer=false`) for migrations and schema changes
3. **Use Railway private URLs** when both services are on Railway (zero egress fees)
4. **Set connect_timeout** parameter (15 seconds recommended) for better reliability
5. **Use sslmode=require** for production databases (security)
6. **Keep connection strings in environment variables** (never commit to code)

## Security Notes

⚠️ **NEVER commit database connection strings to version control**

✅ Use environment variables for all connection strings  
✅ Use `.env.local` for local development (not committed)  
✅ Use Vercel Dashboard for production environment variables  
✅ Use Railway Dashboard for Railway environment variables  
✅ Rotate credentials regularly  
✅ Use SSL/TLS connections (`sslmode=require`)  

## References

- [Vercel Postgres Documentation](https://vercel.com/docs/storage/vercel-postgres)
- [Neon Documentation](https://neon.tech/docs)
- [Railway Documentation](https://docs.railway.app)
- [Drizzle ORM Documentation](https://orm.drizzle.team)
- [Project-specific docs](./VERCEL_POSTGRES_MIGRATION.md)
