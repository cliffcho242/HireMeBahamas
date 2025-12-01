import { NextRequest, NextResponse } from "next/server";
import { sql } from "@vercel/postgres";
import { kv } from "@vercel/kv";
import { verifyAuth } from "@/lib/auth";
import { z } from "zod";

// Serverless runtime for jobs
export const runtime = "nodejs";
export const revalidate = 60; // Revalidate every 60 seconds

// Job query schema
const jobQuerySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(50).default(20),
  search: z.string().optional(),
  location: z.string().optional(),
  type: z.enum(["full-time", "part-time", "contract", "remote"]).optional(),
  minSalary: z.coerce.number().optional(),
  maxSalary: z.coerce.number().optional(),
});

// GET /api/jobs - List jobs with filtering and pagination
export async function GET(request: NextRequest) {
  const startTime = Date.now();

  try {
    const { searchParams } = new URL(request.url);
    const params = Object.fromEntries(searchParams);
    const query = jobQuerySchema.safeParse(params);

    if (!query.success) {
      return NextResponse.json(
        { success: false, message: "Invalid query parameters" },
        { status: 400 }
      );
    }

    const { page, limit, search, location, type, minSalary, maxSalary } =
      query.data;
    const offset = (page - 1) * limit;

    // Get cache version for proper invalidation
    const cacheVersion = await kv.get<number>("jobs:cache:version") || 0;

    // Build cache key with version
    const cacheKey = `jobs:list:v${cacheVersion}:${JSON.stringify(query.data)}`;

    // Check cache first
    const cached = await kv.get<{
      jobs: unknown[];
      total: number;
      cachedAt: string;
    }>(cacheKey);

    if (cached) {
      const duration = Date.now() - startTime;
      return NextResponse.json(
        {
          success: true,
          ...cached,
          pagination: {
            page,
            limit,
            total: cached.total,
            totalPages: Math.ceil(cached.total / limit),
          },
          performance: {
            durationMs: duration,
            cached: true,
          },
        },
        {
          headers: {
            "Cache-Control": "public, s-maxage=60, stale-while-revalidate=120",
            "X-Response-Time": `${duration}ms`,
            "X-Cache": "HIT",
          },
        }
      );
    }

    // Build query conditions
    let whereClause = "WHERE j.is_active = true";
    const queryParams: (string | number)[] = [];
    let paramIndex = 1;

    if (search) {
      whereClause += ` AND (j.title ILIKE $${paramIndex} OR j.description ILIKE $${paramIndex} OR j.company ILIKE $${paramIndex})`;
      queryParams.push(`%${search}%`);
      paramIndex++;
    }

    if (location) {
      whereClause += ` AND j.location ILIKE $${paramIndex}`;
      queryParams.push(`%${location}%`);
      paramIndex++;
    }

    if (type) {
      whereClause += ` AND j.job_type = $${paramIndex}`;
      queryParams.push(type);
      paramIndex++;
    }

    if (minSalary) {
      whereClause += ` AND j.salary_min >= $${paramIndex}`;
      queryParams.push(minSalary);
      paramIndex++;
    }

    if (maxSalary) {
      whereClause += ` AND j.salary_max <= $${paramIndex}`;
      queryParams.push(maxSalary);
      paramIndex++;
    }

    // Get total count
    const countQuery = `
      SELECT COUNT(*) as total FROM jobs j ${whereClause}
    `;

    // Get jobs
    const jobsQuery = `
      SELECT 
        j.id,
        j.title,
        j.company,
        j.location,
        j.job_type,
        j.salary_min,
        j.salary_max,
        j.description,
        j.requirements,
        j.created_at,
        j.updated_at,
        u.first_name || ' ' || u.last_name as posted_by
      FROM jobs j
      LEFT JOIN users u ON j.user_id = u.id
      ${whereClause}
      ORDER BY j.created_at DESC
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `;

    const { rows: countRows } = await sql.query(countQuery, queryParams);
    const { rows: jobs } = await sql.query(jobsQuery, [
      ...queryParams,
      limit,
      offset,
    ]);

    const total = parseInt(countRows[0]?.total || "0", 10);

    // Cache for 60 seconds
    await kv.setex(cacheKey, 60, {
      jobs,
      total,
      cachedAt: new Date().toISOString(),
    });

    const duration = Date.now() - startTime;

    return NextResponse.json(
      {
        success: true,
        jobs,
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit),
        },
        performance: {
          durationMs: duration,
          cached: false,
        },
      },
      {
        headers: {
          "Cache-Control": "public, s-maxage=60, stale-while-revalidate=120",
          "X-Response-Time": `${duration}ms`,
          "X-Cache": "MISS",
        },
      }
    );
  } catch (error) {
    console.error("Jobs list error:", error);
    return NextResponse.json(
      { success: false, message: "Failed to fetch jobs" },
      { status: 500 }
    );
  }
}

// Create job schema
const createJobSchema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  company: z.string().min(1, "Company is required"),
  location: z.string().min(1, "Location is required"),
  jobType: z.enum(["full-time", "part-time", "contract", "remote"]),
  salaryMin: z.number().optional(),
  salaryMax: z.number().optional(),
  description: z.string().min(50, "Description must be at least 50 characters"),
  requirements: z.array(z.string()).optional(),
});

// POST /api/jobs - Create a new job
export async function POST(request: NextRequest) {
  const startTime = Date.now();

  try {
    // Verify authentication
    const auth = await verifyAuth(request);
    if (!auth.success) {
      return NextResponse.json(
        { success: false, message: auth.message },
        { status: 401 }
      );
    }

    // Parse and validate body
    const body = await request.json();
    const result = createJobSchema.safeParse(body);

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          message: result.error.errors[0]?.message || "Invalid input",
          errors: result.error.errors,
        },
        { status: 400 }
      );
    }

    const {
      title,
      company,
      location,
      jobType,
      salaryMin,
      salaryMax,
      description,
      requirements,
    } = result.data;

    // Insert job
    const { rows } = await sql`
      INSERT INTO jobs (
        user_id,
        title,
        company,
        location,
        job_type,
        salary_min,
        salary_max,
        description,
        requirements,
        is_active,
        created_at,
        updated_at
      )
      VALUES (
        ${auth.userId},
        ${title},
        ${company},
        ${location},
        ${jobType},
        ${salaryMin || null},
        ${salaryMax || null},
        ${description},
        ${JSON.stringify(requirements || [])},
        true,
        NOW(),
        NOW()
      )
      RETURNING id, title, company, location, job_type, created_at
    `;

    // Invalidate job list cache using versioned cache key
    // More efficient than pattern scanning - just increment the version
    const cacheVersion = Date.now();
    await kv.set("jobs:cache:version", cacheVersion);

    const duration = Date.now() - startTime;

    return NextResponse.json(
      {
        success: true,
        message: "Job created successfully",
        job: rows[0],
        performance: {
          durationMs: duration,
        },
      },
      {
        status: 201,
        headers: {
          "X-Response-Time": `${duration}ms`,
        },
      }
    );
  } catch (error) {
    console.error("Create job error:", error);
    return NextResponse.json(
      { success: false, message: "Failed to create job" },
      { status: 500 }
    );
  }
}
