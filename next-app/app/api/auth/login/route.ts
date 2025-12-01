import { NextRequest, NextResponse } from "next/server";
import { SignJWT } from "jose";
import bcrypt from "bcryptjs";
import { sql } from "@vercel/postgres";
import { kv } from "@vercel/kv";
import { z } from "zod";

// Edge Runtime for <120ms login globally
export const runtime = "edge";
export const preferredRegion = ["iad1", "sfo1", "sin1", "fra1"];

// Login request schema
const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

// JWT secret from environment
const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "hiremebahamas-super-secret-key-2025"
);

export async function POST(request: NextRequest) {
  const startTime = Date.now();

  try {
    // Parse request body
    const body = await request.json();
    const result = loginSchema.safeParse(body);

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          message: result.error.errors[0]?.message || "Invalid input",
        },
        { status: 400 }
      );
    }

    const { email, password } = result.data;
    const normalizedEmail = email.toLowerCase().trim();

    // Check rate limit in KV (5 attempts per email per 15 minutes)
    const rateLimitKey = `login:attempts:${normalizedEmail}`;
    const attempts = (await kv.get<number>(rateLimitKey)) || 0;

    if (attempts >= 5) {
      return NextResponse.json(
        {
          success: false,
          message: "Too many login attempts. Please try again later.",
        },
        { status: 429 }
      );
    }

    // Check session cache in KV first (ultra-fast repeat logins)
    const sessionCacheKey = `session:cache:${normalizedEmail}`;
    const cachedSession = await kv.get<{
      userId: number;
      passwordHash: string;
      firstName: string;
      lastName: string;
      role: string;
      isAdmin: boolean;
    }>(sessionCacheKey);

    let user;

    if (cachedSession) {
      // Verify password against cached hash
      const passwordValid = await bcrypt.compare(password, cachedSession.passwordHash);
      if (!passwordValid) {
        // Increment rate limit
        await kv.setex(rateLimitKey, 900, attempts + 1);
        return NextResponse.json(
          { success: false, message: "Invalid email or password" },
          { status: 401 }
        );
      }
      user = {
        id: cachedSession.userId,
        email: normalizedEmail,
        firstName: cachedSession.firstName,
        lastName: cachedSession.lastName,
        role: cachedSession.role,
        isAdmin: cachedSession.isAdmin,
      };
    } else {
      // Query database
      const { rows } = await sql`
        SELECT id, email, hashed_password, first_name, last_name, is_admin, role
        FROM users
        WHERE email = ${normalizedEmail}
        LIMIT 1
      `;

      if (rows.length === 0) {
        await kv.setex(rateLimitKey, 900, attempts + 1);
        return NextResponse.json(
          { success: false, message: "Invalid email or password" },
          { status: 401 }
        );
      }

      const dbUser = rows[0];

      // Verify password
      const passwordValid = await bcrypt.compare(
        password,
        dbUser.hashed_password
      );
      if (!passwordValid) {
        await kv.setex(rateLimitKey, 900, attempts + 1);
        return NextResponse.json(
          { success: false, message: "Invalid email or password" },
          { status: 401 }
        );
      }

      user = {
        id: dbUser.id,
        email: dbUser.email,
        firstName: dbUser.first_name,
        lastName: dbUser.last_name,
        role: dbUser.role,
        isAdmin: dbUser.is_admin,
      };

      // Cache session for 1 hour (ultra-fast repeat logins)
      await kv.setex(sessionCacheKey, 3600, {
        userId: user.id,
        passwordHash: dbUser.hashed_password,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        isAdmin: user.isAdmin,
      });
    }

    // Clear rate limit on successful login
    await kv.del(rateLimitKey);

    // Create JWT token (24 hour expiry)
    const token = await new SignJWT({
      userId: user.id,
      email: user.email,
      role: user.role,
      isAdmin: user.isAdmin,
    })
      .setProtectedHeader({ alg: "HS256" })
      .setIssuedAt()
      .setExpirationTime("24h")
      .sign(JWT_SECRET);

    // Store active session in KV
    const sessionKey = `session:${user.id}`;
    await kv.setex(sessionKey, 86400, {
      token,
      userId: user.id,
      email: user.email,
      createdAt: new Date().toISOString(),
    });

    const duration = Date.now() - startTime;

    return NextResponse.json(
      {
        success: true,
        message: "Login successful",
        user: {
          id: user.id,
          email: user.email,
          name: `${user.firstName} ${user.lastName}`,
          role: user.role,
          isAdmin: user.isAdmin,
        },
        token,
        performance: {
          durationMs: duration,
          cached: !!cachedSession,
        },
      },
      {
        status: 200,
        headers: {
          "X-Response-Time": `${duration}ms`,
        },
      }
    );
  } catch (error) {
    console.error("Login error:", error);
    return NextResponse.json(
      {
        success: false,
        message: "An error occurred during login",
      },
      { status: 500 }
    );
  }
}

// Preflight for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
