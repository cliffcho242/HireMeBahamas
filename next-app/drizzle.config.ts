import { defineConfig } from "drizzle-kit";

// Use non-pooling connection for migrations (pgbouncer=false)
// This ensures direct database connection for DDL operations
// Falls back to POSTGRES_URL if POSTGRES_URL_NON_POOLING is not set
const dbUrl = process.env.POSTGRES_URL_NON_POOLING || process.env.POSTGRES_URL;

if (!dbUrl) {
  throw new Error(
    "Database URL not found. Please set POSTGRES_URL or POSTGRES_URL_NON_POOLING environment variable."
  );
}

export default defineConfig({
  schema: "./lib/schema.ts",
  out: "./drizzle",
  dialect: "postgresql",
  dbCredentials: {
    url: dbUrl,
  },
  verbose: true,
  strict: true,
});
