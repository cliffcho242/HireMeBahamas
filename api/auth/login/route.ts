/**
 * Edge-compatible Login API Route
 * JWT Authentication + Vercel KV Rate Limiting
 * Target: < 45ms globally, zero cold starts
 */

// Edge Runtime configuration
export const config = {
  runtime: 'edge',
  regions: ['iad1', 'sfo1', 'cdg1', 'hnd1', 'syd1'], // Global edge locations
};

// Rate limiting configuration
const RATE_LIMIT_WINDOW = 60 * 1000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 10; // 10 login attempts per minute
const LOCKOUT_DURATION = 15 * 60 * 1000; // 15 minute lockout after too many failures

// In-memory rate limiting (for edge, use Vercel KV in production)
const rateLimitMap = new Map<string, { count: number; resetTime: number; locked?: boolean }>();

// JWT configuration - fail if not set in production
const JWT_SECRET = process.env.JWT_SECRET;
const IS_PRODUCTION = process.env.NODE_ENV === 'production' || process.env.VERCEL_ENV === 'production';

if (!JWT_SECRET && IS_PRODUCTION) {
  throw new Error('JWT_SECRET environment variable is required in production');
}

// Use default only in development
const EFFECTIVE_JWT_SECRET = JWT_SECRET || 'dev-only-jwt-secret-not-for-production';
const JWT_EXPIRY_SECONDS = 24 * 60 * 60; // 24 hours

/**
 * Base64URL encode (RFC 4648)
 */
function base64UrlEncode(data: string): string {
  return btoa(data)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

/**
 * Base64URL decode
 */
function base64UrlDecode(data: string): string {
  // Restore base64 padding
  let base64 = data.replace(/-/g, '+').replace(/_/g, '/');
  const padding = base64.length % 4;
  if (padding) {
    base64 += '='.repeat(4 - padding);
  }
  return atob(base64);
}

/**
 * Create HMAC-SHA256 signature using Web Crypto API
 */
async function createHmacSignature(data: string, secret: string): Promise<string> {
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
  
  const signature = await crypto.subtle.sign('HMAC', key, messageData);
  
  // Convert ArrayBuffer to base64url
  const bytes = new Uint8Array(signature);
  let binary = '';
  bytes.forEach(byte => binary += String.fromCharCode(byte));
  return base64UrlEncode(binary);
}

/**
 * Verify HMAC-SHA256 signature using Web Crypto API
 */
async function verifyHmacSignature(data: string, signature: string, secret: string): Promise<boolean> {
  const expectedSignature = await createHmacSignature(data, secret);
  
  // Constant-time comparison to prevent timing attacks
  if (signature.length !== expectedSignature.length) {
    return false;
  }
  
  let result = 0;
  for (let i = 0; i < signature.length; i++) {
    result |= signature.charCodeAt(i) ^ expectedSignature.charCodeAt(i);
  }
  return result === 0;
}

/**
 * Create JWT with HMAC-SHA256 signature (Edge-compatible)
 */
async function createEdgeJWT(payload: Record<string, unknown>): Promise<string> {
  const header = { alg: 'HS256', typ: 'JWT' };
  const now = Math.floor(Date.now() / 1000);
  
  const tokenPayload = {
    ...payload,
    iat: now,
    exp: now + JWT_EXPIRY_SECONDS,
  };
  
  const base64Header = base64UrlEncode(JSON.stringify(header));
  const base64Payload = base64UrlEncode(JSON.stringify(tokenPayload));
  const signatureInput = `${base64Header}.${base64Payload}`;
  
  const signature = await createHmacSignature(signatureInput, EFFECTIVE_JWT_SECRET);
  
  return `${base64Header}.${base64Payload}.${signature}`;
}

/**
 * Verify and decode JWT with HMAC-SHA256 signature
 */
async function verifyEdgeJWT(token: string): Promise<{ valid: boolean; payload?: Record<string, unknown> }> {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return { valid: false };
    }
    
    const [header, payload, signature] = parts;
    const signatureInput = `${header}.${payload}`;
    
    // Verify signature
    const isValid = await verifyHmacSignature(signatureInput, signature, EFFECTIVE_JWT_SECRET);
    if (!isValid) {
      return { valid: false };
    }
    
    // Decode and verify payload
    const decodedPayload = JSON.parse(base64UrlDecode(payload));
    
    // Check expiration
    if (decodedPayload.exp && decodedPayload.exp < Math.floor(Date.now() / 1000)) {
      return { valid: false };
    }
    
    return { valid: true, payload: decodedPayload };
  } catch {
    return { valid: false };
  }
}

/**
 * Check rate limit for IP
 */
function checkRateLimit(ip: string): { allowed: boolean; remaining: number; resetIn: number } {
  const now = Date.now();
  const entry = rateLimitMap.get(ip);
  
  // Check if locked out
  if (entry?.locked && entry.resetTime > now) {
    return {
      allowed: false,
      remaining: 0,
      resetIn: Math.ceil((entry.resetTime - now) / 1000),
    };
  }
  
  // Reset if window expired
  if (!entry || entry.resetTime < now) {
    rateLimitMap.set(ip, { count: 1, resetTime: now + RATE_LIMIT_WINDOW });
    return { allowed: true, remaining: MAX_REQUESTS_PER_WINDOW - 1, resetIn: 60 };
  }
  
  // Check if over limit
  if (entry.count >= MAX_REQUESTS_PER_WINDOW) {
    // Lock out for extended period
    rateLimitMap.set(ip, { count: 0, resetTime: now + LOCKOUT_DURATION, locked: true });
    return {
      allowed: false,
      remaining: 0,
      resetIn: Math.ceil(LOCKOUT_DURATION / 1000),
    };
  }
  
  // Increment count
  entry.count++;
  rateLimitMap.set(ip, entry);
  
  return {
    allowed: true,
    remaining: MAX_REQUESTS_PER_WINDOW - entry.count,
    resetIn: Math.ceil((entry.resetTime - now) / 1000),
  };
}

/**
 * Validate email format
 */
function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Allowed CORS origins
 */
const ALLOWED_ORIGINS = [
  'https://hiremebahamas.com',
  'https://www.hiremebahamas.com',
  'https://hiremebahamas.vercel.app',
  'http://localhost:3000',
  'http://localhost:5173',
  'http://127.0.0.1:5173',
];

/**
 * Get CORS headers with dynamic origin checking
 */
function getCorsHeaders(request: Request): Record<string, string> {
  const origin = request.headers.get('origin') || '';
  const allowedOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  
  return {
    'Access-Control-Allow-Origin': allowedOrigin,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  };
}

/**
 * Edge Login Handler
 */
export default async function handler(request: Request): Promise<Response> {
  const startTime = Date.now();
  
  // Dynamic CORS headers
  const corsHeaders = getCorsHeaders(request);
  
  // Handle preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }
  
  // Only allow POST
  if (request.method !== 'POST') {
    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
  
  // Get client IP for rate limiting
  const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 
             request.headers.get('x-real-ip') || 
             'unknown';
  
  // Check rate limit
  const rateLimit = checkRateLimit(ip);
  
  const rateLimitHeaders = {
    'X-RateLimit-Limit': MAX_REQUESTS_PER_WINDOW.toString(),
    'X-RateLimit-Remaining': rateLimit.remaining.toString(),
    'X-RateLimit-Reset': rateLimit.resetIn.toString(),
  };
  
  if (!rateLimit.allowed) {
    return new Response(
      JSON.stringify({
        error: 'Too many login attempts',
        message: `Please try again in ${rateLimit.resetIn} seconds`,
        retry_after: rateLimit.resetIn,
      }),
      {
        status: 429,
        headers: {
          ...corsHeaders,
          ...rateLimitHeaders,
          'Content-Type': 'application/json',
          'Retry-After': rateLimit.resetIn.toString(),
        },
      }
    );
  }
  
  try {
    // Parse request body
    const body = await request.json();
    const { email, password } = body;
    
    // Validate input
    if (!email || !password) {
      return new Response(
        JSON.stringify({ error: 'Email and password are required' }),
        { status: 400, headers: { ...corsHeaders, ...rateLimitHeaders, 'Content-Type': 'application/json' } }
      );
    }
    
    if (!isValidEmail(email)) {
      return new Response(
        JSON.stringify({ error: 'Invalid email format' }),
        { status: 400, headers: { ...corsHeaders, ...rateLimitHeaders, 'Content-Type': 'application/json' } }
      );
    }
    
    // Forward to backend for actual authentication
    // Edge handles rate limiting, JWT generation, and caching
    const backendUrl = process.env.BACKEND_URL || 'https://hiremebahamas.onrender.com';
    
    const backendResponse = await fetch(`${backendUrl}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Forwarded-For': ip,
        'X-Edge-Request': 'true',
      },
      body: JSON.stringify({ email, password }),
    });
    
    const responseData = await backendResponse.json();
    
    if (!backendResponse.ok) {
      return new Response(
        JSON.stringify(responseData),
        {
          status: backendResponse.status,
          headers: { ...corsHeaders, ...rateLimitHeaders, 'Content-Type': 'application/json' },
        }
      );
    }
    
    // Generate Edge JWT with user data
    const edgeToken = await createEdgeJWT({
      user_id: responseData.user?.id,
      email: responseData.user?.email,
      user_type: responseData.user?.user_type,
      edge: true,
    });
    
    const responseTime = Date.now() - startTime;
    
    // Return success with Edge optimizations
    return new Response(
      JSON.stringify({
        ...responseData,
        edge_token: edgeToken,
        edge_optimized: true,
        response_time_ms: responseTime,
      }),
      {
        status: 200,
        headers: {
          ...corsHeaders,
          ...rateLimitHeaders,
          'Content-Type': 'application/json',
          'X-Edge-Response-Time': `${responseTime}ms`,
          'Cache-Control': 'no-store, no-cache, must-revalidate',
        },
      }
    );
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Edge login error:', errorMessage);
    
    return new Response(
      JSON.stringify({
        error: 'Authentication failed',
        message: 'Please try again later',
      }),
      {
        status: 500,
        headers: { ...corsHeaders, ...rateLimitHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
}
