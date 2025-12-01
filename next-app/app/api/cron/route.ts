import { NextResponse } from "next/server";
import { sql } from "@vercel/postgres";
import { kv } from "@vercel/kv";

// Edge Runtime for fastest cron execution
export const runtime = "edge";

// Vercel Cron - runs every 5 minutes
export const dynamic = "force-dynamic";

/**
 * Keep-alive cron job that:
 * 1. Warms the database connection pool
 * 2. Refreshes cache for frequently accessed data
 * 3. Logs health metrics
 * 
 * Schedule: every 5 minutes (configured in vercel.json)
 */
export async function GET() {
  const startTime = Date.now();
  const results: Record<string, unknown> = {};

  try {
    // 1. Warm database connection
    const { rows } = await sql`SELECT 1 as ping`;
    results.database = { status: "connected", ping: rows[0]?.ping };

    // 2. Refresh job count cache
    const { rows: jobCount } = await sql`
      SELECT COUNT(*) as total FROM jobs WHERE is_active = true
    `;
    await kv.set("stats:activeJobs", jobCount[0]?.total || 0);
    results.jobsCache = { refreshed: true, count: jobCount[0]?.total };

    // 3. Refresh user count cache
    const { rows: userCount } = await sql`
      SELECT COUNT(*) as total FROM users WHERE is_active = true
    `;
    await kv.set("stats:activeUsers", userCount[0]?.total || 0);
    results.usersCache = { refreshed: true, count: userCount[0]?.total };

    // 4. Cache latest jobs for instant page load
    const { rows: latestJobs } = await sql`
      SELECT 
        id, title, company, location, job_type, salary_min, salary_max, created_at
      FROM jobs 
      WHERE is_active = true 
      ORDER BY created_at DESC 
      LIMIT 20
    `;
    await kv.setex("cache:latestJobs", 300, latestJobs);
    results.latestJobsCache = { refreshed: true, count: latestJobs.length };

    const duration = Date.now() - startTime;

    // Log cron execution
    console.log(`Cron executed successfully in ${duration}ms`, results);

    return NextResponse.json(
      {
        success: true,
        message: "Keep-alive cron executed successfully",
        timestamp: new Date().toISOString(),
        duration: `${duration}ms`,
        results,
      },
      {
        status: 200,
        headers: {
          "Cache-Control": "no-store",
          "X-Response-Time": `${duration}ms`,
        },
      }
    );
  } catch (error) {
    console.error("Cron error:", error);
    return NextResponse.json(
      {
        success: false,
        message: "Cron execution failed",
        error: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
