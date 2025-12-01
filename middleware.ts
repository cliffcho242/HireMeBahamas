/**
 * Vercel Edge Middleware
 * Auth + A/B Testing + Geo-Redirects + Rate Limiting
 * Runs on every request at the edge
 * 
 * Uses standard Web Request/Response API for Vite/Vercel compatibility.
 */

// Edge Middleware Configuration
export const config = {
  runtime: 'edge',
  regions: ['iad1', 'sfo1', 'cdg1', 'hnd1', 'syd1'],
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico)$).*)',
  ],
};

// JWT secret for verification - fail if not set in production
const JWT_SECRET = process.env.JWT_SECRET;
const IS_PRODUCTION = process.env.NODE_ENV === 'production' || process.env.VERCEL_ENV === 'production';

if (!JWT_SECRET && IS_PRODUCTION) {
  throw new Error('JWT_SECRET environment variable is required in production');
}

// Use default only in development
const EFFECTIVE_JWT_SECRET = JWT_SECRET || 'dev-only-jwt-secret-not-for-production';

// Rate limiting configuration
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 100; // 100 requests per minute per IP
const rateLimit = new Map<string, { count: number; resetTime: number }>();

// A/B Testing configuration
const AB_TEST_COOKIE = 'hireme_ab_variant';
const AB_TESTS: Record<string, { variants: string[]; weights: number[] }> = {
  'landing_hero': {
    variants: ['control', 'variant_a', 'variant_b'],
    weights: [0.5, 0.25, 0.25],
  },
  'job_card_layout': {
    variants: ['grid', 'list'],
    weights: [0.5, 0.5],
  },
  'cta_color': {
    variants: ['blue', 'green', 'orange'],
    weights: [0.34, 0.33, 0.33],
  },
};

// Feature flags
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
  'BS': '/bahamas',
  'US': '/us',
  'CA': '/ca',
  'GB': '/uk',
};

// Protected routes
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
 * Parse cookies from request header
 */
function parseCookies(cookieHeader: string | null): Record<string, string> {
  const cookies: Record<string, string> = {};
  if (!cookieHeader) return cookies;
  
  cookieHeader.split(';').forEach(cookie => {
    const [name, ...valueParts] = cookie.trim().split('=');
    if (name) {
      cookies[name] = valueParts.join('=');
    }
  });
  
  return cookies;
}

/**
 * Get or create A/B test assignments
 */
function getAbTestAssignments(cookies: Record<string, string>): Record<string, string> {
  let assignments: Record<string, string> = {};
  
  if (cookies[AB_TEST_COOKIE]) {
    try {
      assignments = JSON.parse(decodeURIComponent(cookies[AB_TEST_COOKIE]));
    } catch {
      assignments = {};
    }
  }
  
  for (const [testName, test] of Object.entries(AB_TESTS)) {
    if (!assignments[testName]) {
      assignments[testName] = selectVariant(test);
    }
  }
  
  return assignments;
}

/**
 * Base64URL decode for JWT
 */
function base64UrlDecode(data: string): string {
  let base64 = data.replace(/-/g, '+').replace(/_/g, '/');
  const padding = base64.length % 4;
  if (padding) {
    base64 += '='.repeat(4 - padding);
  }
  return atob(base64);
}

/**
 * Verify HMAC-SHA256 signature using Web Crypto API
 */
async function verifyHmacSignature(data: string, signature: string, secret: string): Promise<boolean> {
  try {
    const encoder = new TextEncoder();
    const keyData = encoder.encode(secret);
    const messageData = encoder.encode(data);
    
    const key = await crypto.subtle.importKey(
      'raw',
      keyData,
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    );
    
    const expectedSignatureBuffer = await crypto.subtle.sign('HMAC', key, messageData);
    
    const bytes = new Uint8Array(expectedSignatureBuffer);
    let binary = '';
    bytes.forEach(byte => binary += String.fromCharCode(byte));
    const expectedSignature = btoa(binary)
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
    
    if (signature.length !== expectedSignature.length) {
      return false;
    }
    
    let result = 0;
    for (let i = 0; i < signature.length; i++) {
      result |= signature.charCodeAt(i) ^ expectedSignature.charCodeAt(i);
    }
    return result === 0;
  } catch {
    return false;
  }
}

/**
 * Validate JWT token with HMAC-SHA256 signature verification
 */
async function validateToken(token: string): Promise<{ valid: boolean; payload?: Record<string, unknown> }> {
  try {
    if (!token) return { valid: false };
    
    const parts = token.split('.');
    if (parts.length !== 3) return { valid: false };
    
    const [header, payload, signature] = parts;
    const signatureInput = `${header}.${payload}`;
    
    const isValidSignature = await verifyHmacSignature(signatureInput, signature, EFFECTIVE_JWT_SECRET);
    if (!isValidSignature) {
      return { valid: false };
    }
    
    const decodedPayload = JSON.parse(base64UrlDecode(payload));
    
    if (decodedPayload.exp && decodedPayload.exp < Math.floor(Date.now() / 1000)) {
      return { valid: false };
    }
    
    return { valid: true, payload: decodedPayload };
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
export default async function middleware(request: Request): Promise<Response> {
  const startTime = Date.now();
  const url = new URL(request.url);
  const pathname = url.pathname;
  
  // Get client IP
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 
             request.headers.get('x-real-ip') || 
             'unknown';
  
  // Get geo information from Vercel headers
  const country = request.headers.get('x-vercel-ip-country') || 'US';
  const city = request.headers.get('x-vercel-ip-city') || 'Unknown';
  const region = request.headers.get('x-vercel-ip-country-region') || 'Unknown';
  
  // Parse cookies
  const cookieHeader = request.headers.get('cookie');
  const cookies = parseCookies(cookieHeader);
  
  // Rate limiting
  const rateLimitResult = checkRateLimit(ip);
  if (!rateLimitResult.allowed) {
    return new Response(
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
  
  // Get auth token
  const authHeader = request.headers.get('authorization');
  const cookieToken = cookies['token'] || '';
  const token = authHeader?.replace('Bearer ', '') || cookieToken;
  const authResult = await validateToken(token);
  
  // Check protected routes
  const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route));
  const isAdminRoute = ADMIN_ROUTES.some(route => pathname.startsWith(route));
  
  if (isProtectedRoute && !authResult.valid) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return Response.redirect(loginUrl.toString(), 302);
  }
  
  if (isAdminRoute) {
    if (!authResult.valid || !isAdmin(authResult.payload)) {
      return new Response(
        JSON.stringify({ error: 'Forbidden', message: 'Admin access required' }),
        { status: 403, headers: { 'Content-Type': 'application/json' } }
      );
    }
  }
  
  // Get A/B test assignments
  const abAssignments = getAbTestAssignments(cookies);
  
  // Check for geo-redirect (only for landing page, first visit)
  if (pathname === '/' && !cookies['geo_redirect_done']) {
    const geoRedirect = GEO_REDIRECTS[country];
    if (geoRedirect && !url.searchParams.get('no_geo')) {
      const redirectUrl = new URL(geoRedirect, request.url);
      redirectUrl.searchParams.set('geo_country', country);
      
      const response = Response.redirect(redirectUrl.toString(), 302);
      // Note: Cookies would be set via Set-Cookie header in production
      return response;
    }
  }
  
  // For passthrough, we need to forward the request
  // In Vercel Edge, returning undefined or calling next() continues to origin
  // We'll add headers to the response by using a passthrough fetch
  
  const responseTime = Date.now() - startTime;
  
  // Create response headers
  const responseHeaders = new Headers();
  responseHeaders.set('X-Edge-Country', country);
  responseHeaders.set('X-Edge-City', city);
  responseHeaders.set('X-Edge-Region', region);
  responseHeaders.set('X-Edge-Response-Time', `${responseTime}ms`);
  responseHeaders.set('X-RateLimit-Limit', MAX_REQUESTS_PER_WINDOW.toString());
  responseHeaders.set('X-RateLimit-Remaining', rateLimitResult.remaining.toString());
  responseHeaders.set('X-AB-Assignments', JSON.stringify(abAssignments));
  responseHeaders.set('X-Feature-Flags', JSON.stringify(FEATURE_FLAGS));
  responseHeaders.set('Set-Cookie', `${AB_TEST_COOKIE}=${encodeURIComponent(JSON.stringify(abAssignments))}; Path=/; Max-Age=${30 * 24 * 60 * 60}; SameSite=Lax; Secure`);
  
  if (authResult.valid && authResult.payload) {
    responseHeaders.set('X-User-ID', String(authResult.payload.user_id || ''));
    responseHeaders.set('X-User-Type', String(authResult.payload.user_type || ''));
  }
  
  // Security headers
  responseHeaders.set('X-Frame-Options', 'DENY');
  responseHeaders.set('X-Content-Type-Options', 'nosniff');
  responseHeaders.set('X-XSS-Protection', '1; mode=block');
  responseHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  
  // For Vercel Edge Middleware, we return a response with headers only
  // The actual content will be served by the origin (Vite/static files)
  // These headers will be merged with the origin response by Vercel
  // 
  // Note: In production Vercel deployment, this middleware runs before the origin
  // and Vercel handles merging headers. We just need to pass through with our headers.
  
  // Create a passthrough response with our Edge headers
  // Vercel will merge these with the origin response
  const response = new Response(null, {
    status: 200,
    headers: responseHeaders,
  });
  
  return response;
}

