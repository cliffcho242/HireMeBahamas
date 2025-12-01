import { NextRequest } from "next/server";
import { jwtVerify } from "jose";
import { kv } from "@vercel/kv";

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "hiremebahamas-super-secret-key-2025"
);

export type AuthResult = {
  success: boolean;
  userId?: number;
  email?: string;
  role?: string;
  isAdmin?: boolean;
  message?: string;
};

/**
 * Verify JWT token from request
 * Checks both Authorization header and KV session store
 */
export async function verifyAuth(request: NextRequest): Promise<AuthResult> {
  try {
    // Get token from Authorization header
    const authHeader = request.headers.get("authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return { success: false, message: "No authorization token provided" };
    }

    const token = authHeader.slice(7);

    // Verify JWT
    const { payload } = await jwtVerify(token, JWT_SECRET);

    const userId = payload.userId as number;
    const email = payload.email as string;
    const role = payload.role as string;
    const isAdmin = payload.isAdmin as boolean;

    // Check if session is still valid in KV
    const sessionKey = `session:${userId}`;
    const session = await kv.get<{
      token: string;
      userId: number;
      email: string;
    }>(sessionKey);

    if (!session || session.token !== token) {
      return { success: false, message: "Session expired or invalid" };
    }

    return {
      success: true,
      userId,
      email,
      role,
      isAdmin,
    };
  } catch (error) {
    console.error("Auth verification error:", error);
    return { success: false, message: "Invalid or expired token" };
  }
}

/**
 * Require admin role
 */
export async function requireAdmin(request: NextRequest): Promise<AuthResult> {
  const auth = await verifyAuth(request);
  
  if (!auth.success) {
    return auth;
  }

  if (!auth.isAdmin) {
    return { success: false, message: "Admin access required" };
  }

  return auth;
}

/**
 * Invalidate user session
 */
export async function invalidateSession(userId: number): Promise<void> {
  const sessionKey = `session:${userId}`;
  await kv.del(sessionKey);
}

/**
 * Hash password using bcrypt
 */
export async function hashPassword(password: string): Promise<string> {
  const bcrypt = await import("bcryptjs");
  return bcrypt.hash(password, 12);
}

/**
 * Verify password against hash
 */
export async function verifyPassword(
  password: string,
  hash: string
): Promise<boolean> {
  const bcrypt = await import("bcryptjs");
  return bcrypt.compare(password, hash);
}
