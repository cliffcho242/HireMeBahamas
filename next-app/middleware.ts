// middleware.ts — EDGE AUTH + GEO + A/B + CACHE
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { jwtVerify } from "jose";
import { CACHE_HEADERS } from "@/lib/cache-config";

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "hiremebahamas-super-secret-key-2025"
);

// Routes that require authentication
const protectedRoutes = [
  "/dashboard",
  "/profile",
  "/messages",
  "/post-job",
  "/settings",
];

// Routes that should redirect to home if already authenticated
const authRoutes = ["/login", "/register"];

// API routes that require authentication
const protectedApiRoutes = [
  "/api/jobs", // POST only
  "/api/posts",
  "/api/messages",
  "/api/notifications",
  "/api/profile",
];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Get token from cookie or Authorization header
  const token =
    request.cookies.get("token")?.value ||
    request.headers.get("authorization")?.replace("Bearer ", "");

  let isAuthenticated = false;
  let userId: number | undefined;

  // Verify token if present
  if (token) {
    try {
      const { payload } = await jwtVerify(token, JWT_SECRET);
      isAuthenticated = true;
      userId = payload.userId as number;
    } catch {
      // Token is invalid or expired
      isAuthenticated = false;
    }
  }

  // Handle protected routes
  if (protectedRoutes.some((route) => pathname.startsWith(route))) {
    if (!isAuthenticated) {
      const url = new URL("/login", request.url);
      url.searchParams.set("redirect", pathname);
      return NextResponse.redirect(url);
    }
  }

  // Handle auth routes (redirect if already authenticated)
  if (authRoutes.some((route) => pathname.startsWith(route))) {
    if (isAuthenticated) {
      return NextResponse.redirect(new URL("/", request.url));
    }
  }

  // Handle protected API routes (POST, PUT, DELETE)
  if (protectedApiRoutes.some((route) => pathname.startsWith(route))) {
    const method = request.method;
    if (["POST", "PUT", "DELETE", "PATCH"].includes(method)) {
      if (!isAuthenticated) {
        return NextResponse.json(
          { success: false, message: "Authentication required" },
          { status: 401 }
        );
      }
    }
  }

  // Create response
  const response = NextResponse.next();

  // Set general Cache-Control header for all responses (Edge caching + security)
  // This enables stale-while-revalidate for better performance
  response.headers.set("Cache-Control", CACHE_HEADERS.GENERAL);

  // A/B testing - only for page routes (not static assets or API routes)
  if (!pathname.startsWith("/api") && !pathname.startsWith("/_next")) {
    const variant = Math.random() < 0.5 ? "a" : "b";
    response.headers.set("x-ab-test", variant);
  }

  // Geo-location from Edge runtime - only for page routes
  // Vercel Edge provides geo info in headers
  if (!pathname.startsWith("/api") && !pathname.startsWith("/_next")) {
    const country = request.headers.get("x-vercel-ip-country") || "unknown";
    const city = request.headers.get("x-vercel-ip-city") || "unknown";
    const region = request.headers.get("x-vercel-ip-country-region") || "unknown";
    
    response.headers.set("x-geo-country", country);
    response.headers.set("x-geo-city", city);
    response.headers.set("x-geo-region", region);
  }

  // Add security headers
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-XSS-Protection", "1; mode=block");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");

  // Add user ID to request headers for downstream use
  if (userId) {
    response.headers.set("X-User-Id", userId.toString());
  }

  // Override cache headers for static assets (longer cache time)
  if (
    pathname.startsWith("/_next/static") ||
    pathname.match(/\.(ico|png|jpg|jpeg|svg|gif|webp|woff2?)$/)
  ) {
    response.headers.set("Cache-Control", CACHE_HEADERS.STATIC);
  }
  // Override cache headers for API responses with optimized caching
  else if (pathname.startsWith("/api/jobs") && request.method === "GET") {
    response.headers.set("Cache-Control", CACHE_HEADERS.API_JOBS);
  }
  // Override cache headers for health endpoint
  else if (pathname.startsWith("/api/health") && request.method === "GET") {
    response.headers.set("Cache-Control", CACHE_HEADERS.HEALTH);
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api/auth (auth endpoints)
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (icon)
     */
    "/((?!api/auth|_next/static|_next/image|favicon.ico).*)",
  ],
};
