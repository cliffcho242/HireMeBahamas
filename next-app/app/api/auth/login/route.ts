import { NextResponse } from "next/server";
import { SignJWT } from "jose";
import bcrypt from "bcryptjs";
import { sql } from "@vercel/postgres";
import { kv } from "@vercel/kv";

// Edge runtime for ultra-fast performance (<45ms worldwide)
export const runtime = "edge";

// JWT secret from environment
const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "hiremebahamas-super-secret-key-2025"
);

// Sign JWT helper function
function signJWT(user: {
  id: number;
  email: string;
  role: string;
  isAdmin: boolean;
}): Promise<string> {
  return new SignJWT({
    userId: user.id,
    email: user.email,
    role: user.role,
    isAdmin: user.isAdmin,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("24h")
    .sign(JWT_SECRET);
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password } = body;

    // Input validation
    if (!email || typeof email !== "string" || !password || typeof password !== "string") {
      return new Response("Invalid email or password", { status: 400 });
    }

    // Rate limit per IP (extract first IP from x-forwarded-for header)
    const forwardedFor = request.headers.get("x-forwarded-for");
    const ip = forwardedFor?.split(",")[0]?.trim() ?? "anonymous";
    
    const rateLimitKey = `rate:${ip}`;
    const attempts = await kv.incr(rateLimitKey);
    
    // Set expiration on first attempt (15 minutes)
    if (attempts === 1) {
      await kv.expire(rateLimitKey, 900);
    }
    
    if (attempts > 10) {
      return new Response("Too many attempts", { status: 429 });
    }

    // Auth logic (bcrypt + JWT)
    const normalizedEmail = email.toLowerCase().trim();
    const { rows } = await sql`
      SELECT id, email, hashed_password, first_name, last_name, is_admin, role
      FROM users
      WHERE email = ${normalizedEmail}
      LIMIT 1
    `;

    const user = rows[0];
    
    // Always run bcrypt.compare to prevent timing attacks
    const passwordHash = user?.hashed_password ?? "$2a$12$invalidhashtopreventtimingattack";
    const isValidPassword = await bcrypt.compare(password, passwordHash);
    
    if (!user || !isValidPassword) {
      return new Response("Invalid credentials", { status: 401 });
    }

    // Clear rate limit on successful login
    await kv.del(rateLimitKey);

    const token = await signJWT({
      id: user.id,
      email: user.email,
      role: user.role,
      isAdmin: user.is_admin,
    });

    return NextResponse.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        name: `${user.first_name} ${user.last_name}`,
        role: user.role,
        isAdmin: user.is_admin,
      },
    });
  } catch (error) {
    console.error("Login error:", error);
    return new Response("An error occurred during login", { status: 500 });
  }
}

