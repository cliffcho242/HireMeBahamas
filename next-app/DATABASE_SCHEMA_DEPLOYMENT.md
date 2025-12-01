# Database Schema Deployment Guide

This guide explains how to deploy the database schema for HireMeBahamas using Drizzle Kit.

## Overview

HireMeBahamas uses [Drizzle ORM](https://orm.drizzle.team/) with PostgreSQL for database management. The schema is defined in TypeScript (`lib/schema.ts`) and deployed using Drizzle Kit.

## Database Schema

The application uses the following tables:

1. **users** - User accounts and profiles
2. **jobs** - Job postings
3. **posts** - Social feed posts
4. **messages** - Direct messages between users
5. **notifications** - User notifications
6. **push_subscriptions** - Web push notification subscriptions
7. **applications** - Job applications
8. **reviews** - User reviews and ratings

## Prerequisites

- Node.js 18+ installed
- PostgreSQL database (Vercel Postgres recommended)
- Database connection URL (`POSTGRES_URL`)

## Quick Start

### Option 1: Using the Deployment Script (Recommended)

```bash
# Set your database URL
export POSTGRES_URL='postgresql://user:password@host:port/database'

# Run the deployment script
./deploy-schema.sh
```

### Option 2: Manual Deployment

```bash
# 1. Install dependencies
npm install

# 2. Set database URL
export POSTGRES_URL='postgresql://user:password@host:port/database'

# 3. Generate migration files (optional, for review)
npm run db:generate

# 4. Push schema to database
npm run db:push
```

### Option 3: Vercel Deployment

When deploying to Vercel with Vercel Postgres:

```bash
# 1. Pull environment variables from Vercel
npx vercel env pull .env.local

# 2. Load environment variables
source .env.local  # Linux/macOS
# or
set -a; source .env.local; set +a  # More compatible

# 3. Deploy schema
npm run db:push
```

## NPM Scripts

The following scripts are available in `package.json`:

- `npm run db:generate` - Generate SQL migration files from schema
- `npm run db:push` - Push schema directly to database (recommended)
- `npm run db:migrate` - Run migration files (alternative approach)
- `npm run db:studio` - Open Drizzle Studio (database GUI)

## Migration Strategy

This project uses **push-based migrations** (`drizzle-kit push`), which:

- ✅ Applies schema changes directly from TypeScript definitions
- ✅ Automatically detects schema changes
- ✅ Prompts for confirmation on destructive changes
- ✅ Suitable for development and production
- ✅ No manual migration file management needed

### Generate Command vs Push Command

**`drizzle-kit generate`** (formerly `drizzle-kit generate:pg`):
- Generates SQL migration files in `./drizzle/` directory
- Useful for reviewing changes before applying
- Migration files are gitignored (push-based workflow)
- No database connection required

**`drizzle-kit push`** (formerly `drizzle-kit push:pg`):
- Pushes schema changes directly to database
- Compares schema with current database state
- Applies necessary changes automatically
- Requires database connection
- Recommended for most use cases

## Environment Variables

Required environment variables:

```env
# Database (Vercel Postgres)
POSTGRES_URL=postgresql://user:password@host:port/database

# Alternative formats supported:
POSTGRES_URL=postgres://user:password@host:port/database
POSTGRES_URL=postgres://user:password@host.region.postgres.vercel-storage.com:5432/database
```

For Vercel Postgres, these are automatically injected when you connect the database in the Vercel Dashboard.

## Configuration

Database configuration is in `drizzle.config.ts`:

```typescript
import { defineConfig } from "drizzle-kit";

export default defineConfig({
  schema: "./lib/schema.ts",      // Schema definition
  out: "./drizzle",                // Migration files output
  dialect: "postgresql",           // Database type
  dbCredentials: {
    url: process.env.POSTGRES_URL!, // Connection string
  },
  verbose: true,                   // Show detailed output
  strict: true,                    // Confirm destructive changes
});
```

## Troubleshooting

### Error: `POSTGRES_URL` is not set

**Solution**: Set the environment variable before running deployment:

```bash
export POSTGRES_URL='your-database-url'
```

### Error: Version mismatch between drizzle-orm and drizzle-kit

**Solution**: Update both packages to latest versions:

```bash
npm install drizzle-orm@latest --legacy-peer-deps
npm install drizzle-kit@latest --save-dev --legacy-peer-deps
```

### Error: Connection timeout or refused

**Solution**: 
1. Check if database is running
2. Verify connection string is correct
3. Check firewall/network settings
4. For Vercel Postgres, ensure you're connecting from an allowed IP

### Warning: Destructive changes detected

Drizzle Kit will prompt you when changes may result in data loss (e.g., dropping columns). Review the changes carefully before confirming.

## Production Deployment

For production deployments:

1. **Always backup your database** before schema changes
2. **Test schema changes** in a staging environment first
3. **Review generated SQL** using `npm run db:generate` before pushing
4. **Use transactions** where possible (automatic with Drizzle Kit)
5. **Monitor the deployment** and have a rollback plan

### Automated Deployment

For CI/CD pipelines (GitHub Actions, etc.):

```yaml
- name: Deploy Database Schema
  env:
    POSTGRES_URL: ${{ secrets.POSTGRES_URL }}
  run: |
    cd next-app
    npm install
    npm run db:push
```

## Database Studio

Drizzle Kit includes a database management GUI:

```bash
npm run db:studio
```

This opens Drizzle Studio at `https://local.drizzle.studio` where you can:
- Browse and edit data
- View table structures
- Run queries
- Manage relationships

## Schema Updates

When you modify `lib/schema.ts`:

1. **Development**: Simply run `npm run db:push`
2. **Production**: Follow the production deployment checklist
3. **Review changes**: Use `npm run db:generate` to see SQL diffs

## Additional Resources

- [Drizzle ORM Documentation](https://orm.drizzle.team/)
- [Drizzle Kit Documentation](https://orm.drizzle.team/kit-docs/overview)
- [Vercel Postgres Documentation](https://vercel.com/docs/storage/vercel-postgres)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Support

For issues specific to:
- **Schema design**: See `lib/schema.ts`
- **Deployment**: See `DEPLOY_CHECKLIST.md`
- **Vercel setup**: See `VERCEL_EDGE_SETUP.md`
- **Database queries**: See `lib/db.ts`
