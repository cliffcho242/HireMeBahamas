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
function signJWT(userId: number): Promise<string> {
  return new SignJWT({ userId })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("24h")
    .sign(JWT_SECRET);
}

export async function POST(request: Request) {
  const { email, password } = await request.json();

  // Rate limit per IP
  const ip = request.headers.get("x-forwarded-for") ?? "anonymous";
  const attempts = await kv.incr(`rate:${ip}`);
  if (attempts > 10) return new Response("Too many attempts", { status: 429 });

  // Auth logic (bcrypt + JWT)
  const { rows } = await sql`
    SELECT id, email, hashed_password, first_name, last_name, is_admin, role
    FROM users
    WHERE email = ${email.toLowerCase().trim()}
    LIMIT 1
  `;

  const user = rows[0];
  if (!user || !(await bcrypt.compare(password, user.hashed_password))) {
    return new Response("Invalid credentials", { status: 401 });
  }

  const token = await signJWT(user.id);
  return NextResponse.json({ 
    token, 
    user: {
      id: user.id,
      email: user.email,
      name: `${user.first_name} ${user.last_name}`,
      role: user.role,
      isAdmin: user.is_admin
    }
  });
}

