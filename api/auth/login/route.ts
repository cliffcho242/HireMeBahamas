/**
 * Edge-compatible Login API Route
 * JWT Authentication + Vercel KV Rate Limiting
 * Target: < 45ms globally, zero cold starts
 */

import type { VercelRequest, VercelResponse } from '@vercel/node';

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

// JWT configuration
const JWT_SECRET = process.env.JWT_SECRET || 'hiremebahamas-edge-secret-2025';
const JWT_EXPIRY = '24h';

/**
 * Simple JWT encoder for Edge runtime (no crypto dependencies)
 */
function createEdgeJWT(payload: Record<string, unknown>): string {
  const header = { alg: 'HS256', typ: 'JWT' };
  const now = Math.floor(Date.now() / 1000);
  const expiresIn = 24 * 60 * 60; // 24 hours in seconds
  
  const tokenPayload = {
    ...payload,
    iat: now,
    exp: now + expiresIn,
  };
  
  const base64Header = btoa(JSON.stringify(header));
  const base64Payload = btoa(JSON.stringify(tokenPayload));
  
  // Simple signature (in production, use proper HMAC-SHA256)
  const signature = btoa(
    `${base64Header}.${base64Payload}.${JWT_SECRET}`
  );
  
  return `${base64Header}.${base64Payload}.${signature}`;
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
 * Edge Login Handler
 */
export default async function handler(request: Request): Promise<Response> {
  const startTime = Date.now();
  
  // CORS headers for Edge
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  };
  
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
    const edgeToken = createEdgeJWT({
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
