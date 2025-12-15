import { NextResponse } from "next/server";
import { kv } from "@vercel/kv";

// Edge Runtime for ultra-fast health checks (<30ms)
export const runtime = "edge";
export const dynamic = "force-dynamic";

/**
 * GET /api/health
 * Ultra-fast health check endpoint for monitoring and latency testing
 * 
 * This runs on Edge Runtime for global <30ms response times
 * Used for:
 * - Uptime monitoring
 * - Latency testing from different regions
 * - Edge network verification
 */
export async function GET(request: Request) {
  // Check for CRON_SECRET authorization when called from cron
  const cronSecret = process.env.CRON_SECRET;
  if (cronSecret) {
    const authHeader = request.headers.get("Authorization") || "";
    const expectedAuth = `Bearer ${cronSecret}`;
    
    // Simple comparison for edge runtime (crypto module not available in edge)
    if (authHeader !== expectedAuth) {
      return NextResponse.json(
        {
          error: "Unauthorized",
          message: "Invalid or missing Authorization header",
        },
        { status: 401 }
      );
    }
  }

  const startTime = Date.now();

  try {
    // Quick KV ping to verify cache is accessible
    const kvStart = Date.now();
    await kv.set("health:ping", Date.now(), { ex: 10 });
    const kvDuration = Date.now() - kvStart;

    const totalDuration = Date.now() - startTime;

    return NextResponse.json(
      {
        status: "healthy",
        timestamp: new Date().toISOString(),
        runtime: "edge",
        checks: {
          kv: {
            status: "connected",
            durationMs: kvDuration,
          },
        },
        performance: {
          totalDurationMs: totalDuration,
        },
      },
      {
        status: 200,
        headers: {
          "Cache-Control": "no-store, no-cache, must-revalidate",
          "X-Response-Time": `${totalDuration}ms`,
          "X-Runtime": "edge",
        },
      }
    );
  } catch (error) {
    console.error("Health check error:", error);
    const duration = Date.now() - startTime;

    return NextResponse.json(
      {
        status: "degraded",
        timestamp: new Date().toISOString(),
        runtime: "edge",
        error: error instanceof Error ? error.message : "Unknown error",
        performance: {
          totalDurationMs: duration,
        },
      },
      {
        status: 503,
        headers: {
          "Cache-Control": "no-store",
          "X-Response-Time": `${duration}ms`,
          "X-Runtime": "edge",
        },
      }
    );
  }
}
