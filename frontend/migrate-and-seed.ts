/**
 * =============================================================================
 * MIGRATE AND SEED SCRIPT - VERCEL POSTGRES
 * =============================================================================
 *
 * One-file migration script for Vercel deploy
 *
 * Usage:
 *   npx tsx migrate-and-seed.ts
 *
 * Or in vercel.json build command:
 *   "buildCommand": "npm run build && npx tsx migrate-and-seed.ts"
 *
 * =============================================================================
 */

import { sql } from '@vercel/postgres';
import { drizzle } from 'drizzle-orm/vercel-postgres';
import { migrate } from 'drizzle-orm/vercel-postgres/migrator';
import * as schema from './src/lib/schema';

// =============================================================================
// CONFIGURATION
// =============================================================================

const ENABLE_SEEDING = process.env.ENABLE_SEEDING === 'true';
const SKIP_MIGRATIONS = process.env.SKIP_MIGRATIONS === 'true';

// =============================================================================
// MAIN MIGRATION FUNCTION
// =============================================================================

async function main() {
  console.log('🚀 Starting database migration...');
  console.log(`📦 Environment: ${process.env.NODE_ENV || 'development'}`);

  const startTime = Date.now();

  try {
    // Initialize Drizzle client
    const db = drizzle(sql, { schema });

    // Health check
    console.log('🔍 Checking database connection...');
    const healthCheck = await sql`SELECT NOW() as current_time, version() as version`;
    console.log(`✅ Connected to database at ${healthCheck.rows[0].current_time}`);

    // Run migrations
    if (!SKIP_MIGRATIONS) {
      console.log('📝 Running migrations...');
      await migrate(db, { migrationsFolder: './drizzle' });
      console.log('✅ Migrations completed successfully');
    } else {
      console.log('⏭️  Skipping migrations (SKIP_MIGRATIONS=true)');
    }

    // Create indexes that Drizzle doesn't handle
    console.log('📊 Creating performance indexes...');
    await createPerformanceIndexes();
    console.log('✅ Performance indexes created');

    // Enable pg_stat_statements if not already enabled
    console.log('📈 Enabling query statistics...');
    await enableQueryStats();
    console.log('✅ Query statistics enabled');

    // Seed data if enabled
    if (ENABLE_SEEDING) {
      console.log('🌱 Seeding initial data...');
      await seedData(db);
      console.log('✅ Seeding completed');
    }

    // Final stats
    const duration = Date.now() - startTime;
    console.log(`\n✨ Migration completed in ${duration}ms`);

    // Print table stats
    const tableStats = await sql`
      SELECT 
        schemaname,
        relname as table_name,
        n_live_tup as row_count
      FROM pg_stat_user_tables
      ORDER BY n_live_tup DESC
      LIMIT 10
    `;

    console.log('\n📊 Table Statistics:');
    console.log('-------------------');
    for (const row of tableStats.rows) {
      console.log(`  ${row.table_name}: ${row.row_count} rows`);
    }

    // Print index stats
    const indexStats = await sql`
      SELECT 
        indexrelname as index_name,
        idx_scan as scans,
        idx_tup_read as tuples_read,
        idx_tup_fetch as tuples_fetched
      FROM pg_stat_user_indexes
      ORDER BY idx_scan DESC
      LIMIT 10
    `;

    console.log('\n📊 Index Usage Statistics:');
    console.log('-------------------------');
    for (const row of indexStats.rows) {
      console.log(`  ${row.index_name}: ${row.scans} scans`);
    }

    process.exit(0);
  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  }
}

// =============================================================================
// CREATE PERFORMANCE INDEXES
// =============================================================================

async function createPerformanceIndexes() {
  // GIN indexes for full-text search
  const ginIndexes = [
    // Jobs full-text search
    `CREATE INDEX IF NOT EXISTS jobs_title_search_idx 
     ON jobs USING gin(to_tsvector('english', title))`,

    `CREATE INDEX IF NOT EXISTS jobs_description_search_idx 
     ON jobs USING gin(to_tsvector('english', description))`,

    `CREATE INDEX IF NOT EXISTS jobs_skills_search_idx 
     ON jobs USING gin(to_tsvector('english', COALESCE(skills, '')))`,

    // Users full-text search
    `CREATE INDEX IF NOT EXISTS users_name_search_idx 
     ON users USING gin(to_tsvector('english', first_name || ' ' || last_name))`,

    `CREATE INDEX IF NOT EXISTS users_bio_search_idx 
     ON users USING gin(to_tsvector('english', COALESCE(bio, '')))`,

    `CREATE INDEX IF NOT EXISTS users_skills_search_idx 
     ON users USING gin(to_tsvector('english', COALESCE(skills, '')))`,

    // Messages full-text search
    `CREATE INDEX IF NOT EXISTS messages_content_search_idx 
     ON messages USING gin(to_tsvector('english', content))`,

    // Posts full-text search
    `CREATE INDEX IF NOT EXISTS posts_content_search_idx 
     ON posts USING gin(to_tsvector('english', content))`,
  ];

  // BTREE indexes for range queries and sorting
  const btreeIndexes = [
    // Jobs - salary range queries
    `CREATE INDEX IF NOT EXISTS jobs_salary_range_btree_idx 
     ON jobs (salary_min, salary_max) WHERE status = 'active'`,

    // Jobs - budget queries
    `CREATE INDEX IF NOT EXISTS jobs_budget_btree_idx 
     ON jobs (budget) WHERE status = 'active'`,

    // Jobs - recent active jobs (most common query)
    `CREATE INDEX IF NOT EXISTS jobs_active_recent_idx 
     ON jobs (created_at DESC) WHERE status = 'active'`,

    // Users - recent active users
    `CREATE INDEX IF NOT EXISTS users_active_recent_idx 
     ON users (created_at DESC) WHERE is_active = true`,

    // Messages - unread per user (critical for notification counts)
    `CREATE INDEX IF NOT EXISTS messages_unread_count_idx 
     ON messages (receiver_id, is_read) WHERE is_read = false`,

    // Notifications - unread per user
    `CREATE INDEX IF NOT EXISTS notifications_unread_count_idx 
     ON notifications (user_id, is_read) WHERE is_read = false`,

    // Posts - user feed (recent posts)
    `CREATE INDEX IF NOT EXISTS posts_feed_idx 
     ON posts (created_at DESC)`,

    // Job applications - pending by employer
    `CREATE INDEX IF NOT EXISTS applications_pending_idx 
     ON job_applications (status, created_at DESC) WHERE status = 'pending'`,
  ];

  // Execute all index creation statements
  for (const indexSql of [...ginIndexes, ...btreeIndexes]) {
    try {
      await sql.query(indexSql);
    } catch (error) {
      // Index might already exist, log and continue
      console.log(`  Index creation skipped (may already exist): ${error}`);
    }
  }
}

// =============================================================================
// ENABLE QUERY STATISTICS
// =============================================================================

async function enableQueryStats() {
  try {
    // Check if pg_stat_statements is available
    const extCheck = await sql`
      SELECT * FROM pg_available_extensions 
      WHERE name = 'pg_stat_statements'
    `;

    if (extCheck.rows.length > 0) {
      // Try to create extension (requires superuser)
      await sql`CREATE EXTENSION IF NOT EXISTS pg_stat_statements`;
      console.log('  ✓ pg_stat_statements extension enabled');
    } else {
      console.log('  ⚠️ pg_stat_statements not available on this database');
    }
  } catch {
    // Extension might require superuser privileges
    console.log('  ⚠️ pg_stat_statements requires admin privileges (skipped)');
  }
}

// =============================================================================
// SEED INITIAL DATA
// =============================================================================

async function seedData(db: ReturnType<typeof drizzle>) {
  // Check if data already exists
  const userCount = await sql`SELECT COUNT(*) as count FROM users`;

  if (parseInt(userCount.rows[0].count as string) > 0) {
    console.log('  ⏭️  Database already has data, skipping seeding');
    return;
  }

  // Create admin user
  console.log('  Creating admin user...');
  await db.insert(schema.users).values({
    email: 'admin@hiremebahamas.com',
    hashedPassword: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.bqGPKe7W7.6S5.',
    firstName: 'Admin',
    lastName: 'User',
    username: 'admin',
    role: 'admin',
    isAdmin: true,
    isActive: true,
    location: 'Nassau, Bahamas',
  });

  // Create sample categories
  const categories = [
    'Technology',
    'Healthcare',
    'Finance',
    'Education',
    'Hospitality',
    'Construction',
    'Marketing',
    'Sales',
  ];

  // Create sample jobs
  console.log('  Creating sample jobs...');
  const adminUser = await sql`SELECT id FROM users WHERE email = 'admin@hiremebahamas.com'`;
  const adminId = adminUser.rows[0]?.id as number;

  if (adminId) {
    for (const category of categories.slice(0, 3)) {
      await db.insert(schema.jobs).values({
        title: `Senior ${category} Specialist`,
        company: 'HireMeBahamas Demo',
        description: `We are looking for a talented ${category} specialist to join our team.`,
        category,
        jobType: 'full-time',
        location: 'Nassau, Bahamas',
        salaryMin: 50000,
        salaryMax: 80000,
        status: 'active',
        employerId: adminId,
      });
    }
  }

  console.log('  ✓ Sample data created');
}

// =============================================================================
// RUN MIGRATION
// =============================================================================

main();
