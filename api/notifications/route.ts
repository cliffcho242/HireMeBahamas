/**
 * Edge-compatible Notifications API Route
 * Real-time via Edge + WebSocket fallback
 * Target: Instant notifications everywhere
 */

export const config = {
  runtime: 'edge',
  regions: ['iad1', 'sfo1', 'cdg1', 'hnd1', 'syd1'], // Global edge locations
};

// JWT secret for verification
const JWT_SECRET = process.env.JWT_SECRET || 'hiremebahamas-edge-secret-2025';

// Notification types
interface Notification {
  id: string;
  type: 'message' | 'like' | 'follow' | 'comment' | 'job_application' | 'job_posted';
  title: string;
  body: string;
  data?: Record<string, unknown>;
  timestamp: string;
  read: boolean;
  user_id: string;
}

// In-memory notification store (use Vercel KV in production)
const notificationStore = new Map<string, Notification[]>();

/**
 * Base64URL decode for JWT
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
    
    // Convert ArrayBuffer to base64url
    const bytes = new Uint8Array(expectedSignatureBuffer);
    let binary = '';
    bytes.forEach(byte => binary += String.fromCharCode(byte));
    const expectedSignature = btoa(binary)
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
    
    // Constant-time comparison to prevent timing attacks
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
 * Validate JWT token from Edge with HMAC-SHA256 verification
 */
async function validateEdgeToken(token: string): Promise<{ valid: boolean; userId?: string }> {
  try {
    if (!token || !token.startsWith('Bearer ')) {
      return { valid: false };
    }
    
    const jwt = token.replace('Bearer ', '');
    const parts = jwt.split('.');
    
    if (parts.length !== 3) {
      return { valid: false };
    }
    
    const [header, payload, signature] = parts;
    const signatureInput = `${header}.${payload}`;
    
    // Verify HMAC-SHA256 signature
    const isValidSignature = await verifyHmacSignature(signatureInput, signature, JWT_SECRET);
    if (!isValidSignature) {
      return { valid: false };
    }
    
    // Decode payload after signature verification
    const decodedPayload = JSON.parse(base64UrlDecode(payload));
    
    // Check expiration
    if (decodedPayload.exp && decodedPayload.exp < Math.floor(Date.now() / 1000)) {
      return { valid: false };
    }
    
    return { valid: true, userId: decodedPayload.user_id || decodedPayload.sub };
  } catch {
    return { valid: false };
  }
}

/**
 * Generate unique notification ID
 */
function generateId(): string {
  return `notif_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Get notifications for user
 */
function getUserNotifications(userId: string): Notification[] {
  return notificationStore.get(userId) || [];
}

/**
 * Add notification for user
 */
function addNotification(userId: string, notification: Omit<Notification, 'id' | 'timestamp' | 'read' | 'user_id'>): Notification {
  const newNotification: Notification = {
    ...notification,
    id: generateId(),
    timestamp: new Date().toISOString(),
    read: false,
    user_id: userId,
  };
  
  const userNotifications = notificationStore.get(userId) || [];
  userNotifications.unshift(newNotification);
  
  // Keep only last 100 notifications
  if (userNotifications.length > 100) {
    userNotifications.splice(100);
  }
  
  notificationStore.set(userId, userNotifications);
  return newNotification;
}

/**
 * Mark notification as read
 */
function markAsRead(userId: string, notificationId: string): boolean {
  const userNotifications = notificationStore.get(userId);
  if (!userNotifications) return false;
  
  const notification = userNotifications.find(n => n.id === notificationId);
  if (notification) {
    notification.read = true;
    return true;
  }
  return false;
}

/**
 * Mark all notifications as read
 */
function markAllAsRead(userId: string): number {
  const userNotifications = notificationStore.get(userId);
  if (!userNotifications) return 0;
  
  let count = 0;
  userNotifications.forEach(n => {
    if (!n.read) {
      n.read = true;
      count++;
    }
  });
  return count;
}

/**
 * Get unread count
 */
function getUnreadCount(userId: string): number {
  const userNotifications = notificationStore.get(userId) || [];
  return userNotifications.filter(n => !n.read).length;
}

/**
 * Edge Notifications Handler
 */
export default async function handler(request: Request): Promise<Response> {
  const startTime = Date.now();
  const url = new URL(request.url);
  const path = url.pathname;
  
  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  };
  
  // Handle preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders });
  }
  
  // Validate authentication
  const authHeader = request.headers.get('Authorization') || '';
  const auth = await validateEdgeToken(authHeader);
  
  if (!auth.valid || !auth.userId) {
    return new Response(
      JSON.stringify({ error: 'Unauthorized' }),
      { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
  
  const userId = auth.userId;
  
  try {
    // GET /api/notifications - List notifications
    if (request.method === 'GET' && (path === '/api/notifications' || path.endsWith('/list'))) {
      const skip = parseInt(url.searchParams.get('skip') || '0');
      const limit = parseInt(url.searchParams.get('limit') || '20');
      const unreadOnly = url.searchParams.get('unread_only') === 'true';
      
      let notifications = getUserNotifications(userId);
      
      if (unreadOnly) {
        notifications = notifications.filter(n => !n.read);
      }
      
      const paginatedNotifications = notifications.slice(skip, skip + limit);
      const responseTime = Date.now() - startTime;
      
      return new Response(
        JSON.stringify({
          success: true,
          notifications: paginatedNotifications,
          total: notifications.length,
          unread_count: getUnreadCount(userId),
          edge_optimized: true,
          response_time_ms: responseTime,
        }),
        {
          status: 200,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
            'X-Edge-Response-Time': `${responseTime}ms`,
            'Cache-Control': 'no-cache, no-store, must-revalidate',
          },
        }
      );
    }
    
    // GET /api/notifications/unread-count
    if (request.method === 'GET' && path.endsWith('/unread-count')) {
      const count = getUnreadCount(userId);
      const responseTime = Date.now() - startTime;
      
      return new Response(
        JSON.stringify({
          success: true,
          unread_count: count,
          edge_optimized: true,
          response_time_ms: responseTime,
        }),
        {
          status: 200,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
            'X-Edge-Response-Time': `${responseTime}ms`,
            'Cache-Control': 'no-cache, max-age=0',
          },
        }
      );
    }
    
    // POST /api/notifications - Create notification (internal/admin)
    if (request.method === 'POST' && path === '/api/notifications') {
      const body = await request.json();
      const { type, title, body: notificationBody, data, target_user_id } = body;
      
      if (!type || !title || !notificationBody) {
        return new Response(
          JSON.stringify({ error: 'Missing required fields: type, title, body' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
      
      const targetUserId = target_user_id || userId;
      const notification = addNotification(targetUserId, {
        type,
        title,
        body: notificationBody,
        data,
      });
      
      const responseTime = Date.now() - startTime;
      
      return new Response(
        JSON.stringify({
          success: true,
          notification,
          edge_optimized: true,
          response_time_ms: responseTime,
        }),
        {
          status: 201,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
            'X-Edge-Response-Time': `${responseTime}ms`,
          },
        }
      );
    }
    
    // PUT /api/notifications/:id/read - Mark as read
    if (request.method === 'PUT' && path.includes('/read')) {
      const notificationId = path.split('/').slice(-2)[0];
      const success = markAsRead(userId, notificationId);
      const responseTime = Date.now() - startTime;
      
      return new Response(
        JSON.stringify({
          success,
          message: success ? 'Notification marked as read' : 'Notification not found',
          edge_optimized: true,
          response_time_ms: responseTime,
        }),
        {
          status: success ? 200 : 404,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
            'X-Edge-Response-Time': `${responseTime}ms`,
          },
        }
      );
    }
    
    // PUT /api/notifications/mark-all-read
    if (request.method === 'PUT' && path.endsWith('/mark-all-read')) {
      const count = markAllAsRead(userId);
      const responseTime = Date.now() - startTime;
      
      return new Response(
        JSON.stringify({
          success: true,
          marked_count: count,
          edge_optimized: true,
          response_time_ms: responseTime,
        }),
        {
          status: 200,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
            'X-Edge-Response-Time': `${responseTime}ms`,
          },
        }
      );
    }
    
    // Stream notifications (Server-Sent Events for real-time)
    if (request.method === 'GET' && path.endsWith('/stream')) {
      const encoder = new TextEncoder();
      
      const stream = new ReadableStream({
        start(controller) {
          // Send initial connection message
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'connected', user_id: userId })}\n\n`));
          
          // Send current unread count
          const unreadCount = getUnreadCount(userId);
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'unread_count', count: unreadCount })}\n\n`));
          
          // Keep connection alive with heartbeat
          const heartbeat = setInterval(() => {
            try {
              controller.enqueue(encoder.encode(`: heartbeat\n\n`));
            } catch {
              clearInterval(heartbeat);
            }
          }, 30000);
          
          // Close after 5 minutes (edge function timeout)
          setTimeout(() => {
            clearInterval(heartbeat);
            controller.close();
          }, 5 * 60 * 1000);
        },
      });
      
      return new Response(stream, {
        status: 200,
        headers: {
          ...corsHeaders,
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
          'X-Accel-Buffering': 'no',
        },
      });
    }
    
    // Not found
    return new Response(
      JSON.stringify({ error: 'Not found' }),
      { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
    
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    console.error('Edge notifications error:', errorMessage);
    
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
}
