/**
 * Vercel Edge Middleware
 * Auth + A/B Testing + Geo-Redirects + Rate Limiting
 * Runs on every request at the edge
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Edge Middleware Configuration
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (favicon)
     * - public files (public folder)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)',
  ],
};

// Rate limiting configuration
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 100; // 100 requests per minute per IP
const rateLimit = new Map<string, { count: number; resetTime: number }>();

// A/B Testing configuration
const AB_TEST_COOKIE = 'hireme_ab_variant';
const AB_TESTS: Record<string, { variants: string[]; weights: number[] }> = {
  'landing_hero': {
    variants: ['control', 'variant_a', 'variant_b'],
    weights: [0.5, 0.25, 0.25], // 50% control, 25% each variant
  },
  'job_card_layout': {
    variants: ['grid', 'list'],
    weights: [0.5, 0.5], // 50/50 split
  },
  'cta_color': {
    variants: ['blue', 'green', 'orange'],
    weights: [0.34, 0.33, 0.33], // Equal split
  },
};

// Feature flags (can be overridden by Edge Config)
const FEATURE_FLAGS: Record<string, boolean> = {
  'new_search_ui': true,
  'instant_notifications': true,
  'video_calls': false,
  'ai_job_matching': false,
  'dark_mode': true,
  'social_sharing': true,
};

// Geo-redirect configuration
const GEO_REDIRECTS: Record<string, string> = {
  // Redirect specific countries to localized pages
  'BS': '/bahamas', // Bahamas
  'US': '/us',
  'CA': '/ca',
  'GB': '/uk',
};

// Protected routes that require authentication
const PROTECTED_ROUTES = [
  '/dashboard',
  '/profile',
  '/messages',
  '/jobs/my',
  '/jobs/create',
  '/notifications',
  '/settings',
];

// Admin routes
const ADMIN_ROUTES = [
  '/admin',
  '/admin/users',
  '/admin/jobs',
  '/admin/reports',
];

/**
 * Check rate limit for IP
 */
function checkRateLimit(ip: string): { allowed: boolean; remaining: number } {
  const now = Date.now();
  const entry = rateLimit.get(ip);
  
  if (!entry || entry.resetTime < now) {
    rateLimit.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW });
    return { allowed: true, remaining: MAX_REQUESTS_PER_WINDOW - 1 };
  }
  
  if (entry.count >= MAX_REQUESTS_PER_WINDOW) {
    return { allowed: false, remaining: 0 };
  }
  
  entry.count++;
  return { allowed: true, remaining: MAX_REQUESTS_PER_WINDOW - entry.count };
}

/**
 * Select A/B test variant based on weights
 */
function selectVariant(test: { variants: string[]; weights: number[] }): string {
  const random = Math.random();
  let cumulative = 0;
  
  for (let i = 0; i < test.variants.length; i++) {
    cumulative += test.weights[i];
    if (random < cumulative) {
      return test.variants[i];
    }
  }
  
  return test.variants[0];
}

/**
 * Get or create A/B test assignments
 */
function getAbTestAssignments(request: NextRequest): Record<string, string> {
  const cookie = request.cookies.get(AB_TEST_COOKIE);
  let assignments: Record<string, string> = {};
  
  if (cookie?.value) {
    try {
      assignments = JSON.parse(cookie.value);
    } catch {
      assignments = {};
    }
  }
  
  // Assign missing tests
  for (const [testName, test] of Object.entries(AB_TESTS)) {
    if (!assignments[testName]) {
      assignments[testName] = selectVariant(test);
    }
  }
  
  return assignments;
}

/**
 * Validate JWT token
 */
function validateToken(token: string): { valid: boolean; payload?: Record<string, unknown> } {
  try {
    if (!token) return { valid: false };
    
    const parts = token.split('.');
    if (parts.length !== 3) return { valid: false };
    
    const payload = JSON.parse(atob(parts[1]));
    
    // Check expiration
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
      return { valid: false };
    }
    
    return { valid: true, payload };
  } catch {
    return { valid: false };
  }
}

/**
 * Check if user is admin
 */
function isAdmin(payload: Record<string, unknown> | undefined): boolean {
  return payload?.user_type === 'admin' || payload?.role === 'admin';
}

/**
 * Edge Middleware Handler
 */
export default async function middleware(request: NextRequest): Promise<NextResponse> {
  const startTime = Date.now();
  const { pathname, searchParams } = request.nextUrl;
  
  // Get client IP
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 
             request.headers.get('x-real-ip') || 
             'unknown';
  
  // Get geo information
  const geo = request.geo || {};
  const country = geo.country || 'US';
  const city = geo.city || 'Unknown';
  const region = geo.region || 'Unknown';
  
  // Rate limiting
  const rateLimitResult = checkRateLimit(ip);
  if (!rateLimitResult.allowed) {
    return new NextResponse(
      JSON.stringify({
        error: 'Too many requests',
        message: 'Please slow down',
        retry_after: 60,
      }),
      {
        status: 429,
        headers: {
          'Content-Type': 'application/json',
          'Retry-After': '60',
          'X-RateLimit-Limit': MAX_REQUESTS_PER_WINDOW.toString(),
          'X-RateLimit-Remaining': '0',
        },
      }
    );
  }
  
  // Create response
  let response = NextResponse.next();
  
  // Get auth token
  const authHeader = request.headers.get('authorization');
  const cookieToken = request.cookies.get('token')?.value;
  const token = authHeader?.replace('Bearer ', '') || cookieToken || '';
  const authResult = validateToken(token);
  
  // Check protected routes
  const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route));
  const isAdminRoute = ADMIN_ROUTES.some(route => pathname.startsWith(route));
  
  if (isProtectedRoute && !authResult.valid) {
    // Redirect to login
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }
  
  if (isAdminRoute) {
    if (!authResult.valid || !isAdmin(authResult.payload)) {
      return new NextResponse(
        JSON.stringify({ error: 'Forbidden', message: 'Admin access required' }),
        { status: 403, headers: { 'Content-Type': 'application/json' } }
      );
    }
  }
  
  // A/B Test assignments
  const abAssignments = getAbTestAssignments(request);
  response.cookies.set(AB_TEST_COOKIE, JSON.stringify(abAssignments), {
    httpOnly: false,
    secure: true,
    sameSite: 'lax',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  });
  
  // Geo-based redirects (only for landing page, first visit)
  if (pathname === '/' && !request.cookies.get('geo_redirect_done')) {
    const geoRedirect = GEO_REDIRECTS[country];
    if (geoRedirect && !searchParams.get('no_geo')) {
      const redirectUrl = new URL(geoRedirect, request.url);
      redirectUrl.searchParams.set('geo_country', country);
      
      const redirectResponse = NextResponse.redirect(redirectUrl);
      redirectResponse.cookies.set('geo_redirect_done', '1', {
        maxAge: 24 * 60 * 60, // 1 day
      });
      return redirectResponse;
    }
  }
  
  // Add headers for edge info
  const responseTime = Date.now() - startTime;
  response.headers.set('X-Edge-Country', country);
  response.headers.set('X-Edge-City', city);
  response.headers.set('X-Edge-Region', region);
  response.headers.set('X-Edge-Response-Time', `${responseTime}ms`);
  response.headers.set('X-RateLimit-Limit', MAX_REQUESTS_PER_WINDOW.toString());
  response.headers.set('X-RateLimit-Remaining', rateLimitResult.remaining.toString());
  response.headers.set('X-AB-Assignments', JSON.stringify(abAssignments));
  response.headers.set('X-Feature-Flags', JSON.stringify(FEATURE_FLAGS));
  
  // Add authentication status header
  if (authResult.valid && authResult.payload) {
    response.headers.set('X-User-ID', String(authResult.payload.user_id || ''));
    response.headers.set('X-User-Type', String(authResult.payload.user_type || ''));
  }
  
  // Security headers (already in vercel.json, but ensure they're set)
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  return response;
}
