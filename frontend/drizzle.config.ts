/**
 * =============================================================================
 * DRIZZLE CONFIG - VERCEL POSTGRES OPTIMIZED
 * =============================================================================
 *
 * MASTERMIND VERCEL POSTGRES OPTIMIZATION (2025)
 *
 * Configuration for Drizzle ORM with Vercel Postgres:
 * - Uses pg driver for migrations (drizzle-kit)
 * - Connection pooling DISABLED (handled by Vercel's pgbouncer)
 * - SSL mode required for Vercel Postgres
 *
 * Environment Variables Required:
 * POSTGRES_URL="postgres://user:pass@host:5432/db?sslmode=require"
 *
 * =============================================================================
 */

import type { Config } from 'drizzle-kit';

export default {
  // Schema location
  schema: './src/lib/schema.ts',

  // Output directory for migrations
  out: './drizzle',

  // Dialect for Vercel Postgres
  dialect: 'postgresql',

  // Database credentials from environment
  dbCredentials: {
    // Vercel Postgres connection string
    // Format: postgres://user:pass@host:5432/db?sslmode=require
    url: process.env.POSTGRES_URL || process.env.DATABASE_URL || '',
  },

  // Verbose logging for debugging
  verbose: true,

  // Strict mode for type checking
  strict: true,

  // Table filters (optional - include all tables)
  tablesFilter: ['*'],
} satisfies Config;
