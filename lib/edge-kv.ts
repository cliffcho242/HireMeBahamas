/**
 * Edge KV Wrapper - Typed Vercel KV client for Edge Runtime
 * Provides typed access to Vercel KV with fallback to in-memory store
 */

// KV Types
export interface KVOptions {
  ex?: number; // Expiration in seconds
  px?: number; // Expiration in milliseconds
  nx?: boolean; // Only set if key doesn't exist
  xx?: boolean; // Only set if key exists
}

export interface RateLimitEntry {
  count: number;
  resetTime: number;
  locked?: boolean;
}

export interface SessionData {
  userId: string;
  email: string;
  userType: string;
  createdAt: number;
  expiresAt: number;
  ip?: string;
  userAgent?: string;
}

export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  notifications: boolean;
  emailDigest: 'daily' | 'weekly' | 'never';
  language: string;
}

export interface JobSearchCache {
  query: string;
  filters: Record<string, unknown>;
  results: unknown[];
  total: number;
  timestamp: number;
}

// In-memory fallback store
const memoryStore = new Map<string, { value: string; expiresAt?: number }>();

/**
 * Edge KV Client
 * Uses Vercel KV in production, falls back to in-memory for development
 */
export class EdgeKV {
  private readonly kvUrl: string | undefined;
  private readonly kvToken: string | undefined;
  private readonly useMemory: boolean;

  constructor() {
    this.kvUrl = process.env.KV_REST_API_URL;
    this.kvToken = process.env.KV_REST_API_TOKEN;
    this.useMemory = !this.kvUrl || !this.kvToken;
    
    if (this.useMemory) {
      console.warn('EdgeKV: Using in-memory fallback. Set KV_REST_API_URL and KV_REST_API_TOKEN for production.');
    }
  }

  /**
   * Clean expired entries from memory store
   */
  private cleanExpired(): void {
    const now = Date.now();
    const keysToDelete: string[] = [];
    memoryStore.forEach((entry, key) => {
      if (entry.expiresAt && entry.expiresAt < now) {
        keysToDelete.push(key);
      }
    });
    keysToDelete.forEach(key => memoryStore.delete(key));
  }

  /**
   * Execute a KV command
   */
  private async execute<T>(command: string[]): Promise<T | null> {
    if (this.useMemory) {
      return this.executeMemory<T>(command);
    }

    try {
      const response = await fetch(`${this.kvUrl}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.kvToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(command),
      });

      if (!response.ok) {
        throw new Error(`KV Error: ${response.status}`);
      }

      const data = await response.json();
      return data.result as T;
    } catch (error) {
      console.error('EdgeKV execute error:', error);
      // Fallback to memory
      return this.executeMemory<T>(command);
    }
  }

  /**
   * Execute command in memory store
   */
  private executeMemory<T>(command: string[]): T | null {
    this.cleanExpired();
    const [cmd, ...args] = command;

    switch (cmd.toUpperCase()) {
      case 'GET': {
        const entry = memoryStore.get(args[0]);
        if (!entry) return null;
        if (entry.expiresAt && entry.expiresAt < Date.now()) {
          memoryStore.delete(args[0]);
          return null;
        }
        return entry.value as unknown as T;
      }

      case 'SET': {
        const [key, value, ...opts] = args;
        let expiresAt: number | undefined;

        for (let i = 0; i < opts.length; i++) {
          if (opts[i].toUpperCase() === 'EX' && opts[i + 1]) {
            expiresAt = Date.now() + parseInt(opts[i + 1]) * 1000;
          } else if (opts[i].toUpperCase() === 'PX' && opts[i + 1]) {
            expiresAt = Date.now() + parseInt(opts[i + 1]);
          }
        }

        memoryStore.set(key, { value, expiresAt });
        return 'OK' as unknown as T;
      }

      case 'DEL': {
        let count = 0;
        for (const key of args) {
          if (memoryStore.delete(key)) count++;
        }
        return count as unknown as T;
      }

      case 'INCR': {
        const entry = memoryStore.get(args[0]);
        const current = entry ? parseInt(entry.value) || 0 : 0;
        const next = current + 1;
        memoryStore.set(args[0], { value: next.toString(), expiresAt: entry?.expiresAt });
        return next as unknown as T;
      }

      case 'EXPIRE': {
        const entry = memoryStore.get(args[0]);
        if (!entry) return 0 as unknown as T;
        entry.expiresAt = Date.now() + parseInt(args[1]) * 1000;
        return 1 as unknown as T;
      }

      case 'TTL': {
        const entry = memoryStore.get(args[0]);
        if (!entry) return -2 as unknown as T;
        if (!entry.expiresAt) return -1 as unknown as T;
        return Math.ceil((entry.expiresAt - Date.now()) / 1000) as unknown as T;
      }

      case 'EXISTS': {
        let count = 0;
        for (const key of args) {
          if (memoryStore.has(key)) count++;
        }
        return count as unknown as T;
      }

      default:
        console.warn(`EdgeKV: Unsupported command ${cmd}`);
        return null;
    }
  }

  /**
   * Get a value
   */
  async get<T = string>(key: string): Promise<T | null> {
    const value = await this.execute<string>(['GET', key]);
    if (value === null) return null;
    
    try {
      return JSON.parse(value) as T;
    } catch {
      return value as unknown as T;
    }
  }

  /**
   * Set a value
   */
  async set(key: string, value: unknown, options?: KVOptions): Promise<'OK' | null> {
    const serialized = typeof value === 'string' ? value : JSON.stringify(value);
    const args = ['SET', key, serialized];

    if (options?.ex) args.push('EX', options.ex.toString());
    if (options?.px) args.push('PX', options.px.toString());
    if (options?.nx) args.push('NX');
    if (options?.xx) args.push('XX');

    return this.execute<'OK'>(args);
  }

  /**
   * Delete keys
   */
  async del(...keys: string[]): Promise<number> {
    return (await this.execute<number>(['DEL', ...keys])) ?? 0;
  }

  /**
   * Increment a value
   */
  async incr(key: string): Promise<number> {
    return (await this.execute<number>(['INCR', key])) ?? 0;
  }

  /**
   * Set expiration
   */
  async expire(key: string, seconds: number): Promise<boolean> {
    return (await this.execute<number>(['EXPIRE', key, seconds.toString()])) === 1;
  }

  /**
   * Get TTL
   */
  async ttl(key: string): Promise<number> {
    return (await this.execute<number>(['TTL', key])) ?? -2;
  }

  /**
   * Check if keys exist
   */
  async exists(...keys: string[]): Promise<number> {
    return (await this.execute<number>(['EXISTS', ...keys])) ?? 0;
  }

  // ============ High-Level Methods ============

  /**
   * Rate limiting check
   */
  async checkRateLimit(
    key: string,
    maxRequests: number,
    windowSeconds: number
  ): Promise<{ allowed: boolean; remaining: number; resetIn: number }> {
    const now = Date.now();
    const data = await this.get<RateLimitEntry>(`ratelimit:${key}`);

    if (!data || data.resetTime < now) {
      await this.set(`ratelimit:${key}`, {
        count: 1,
        resetTime: now + windowSeconds * 1000,
      }, { ex: windowSeconds });
      
      return { allowed: true, remaining: maxRequests - 1, resetIn: windowSeconds };
    }

    if (data.count >= maxRequests) {
      return {
        allowed: false,
        remaining: 0,
        resetIn: Math.ceil((data.resetTime - now) / 1000),
      };
    }

    data.count++;
    await this.set(`ratelimit:${key}`, data, {
      ex: Math.ceil((data.resetTime - now) / 1000),
    });

    return {
      allowed: true,
      remaining: maxRequests - data.count,
      resetIn: Math.ceil((data.resetTime - now) / 1000),
    };
  }

  /**
   * Session management
   */
  async setSession(sessionId: string, data: SessionData, ttlSeconds = 86400): Promise<boolean> {
    const result = await this.set(`session:${sessionId}`, data, { ex: ttlSeconds });
    return result === 'OK';
  }

  async getSession(sessionId: string): Promise<SessionData | null> {
    return this.get<SessionData>(`session:${sessionId}`);
  }

  async deleteSession(sessionId: string): Promise<boolean> {
    return (await this.del(`session:${sessionId}`)) > 0;
  }

  /**
   * Cache with TTL
   */
  async cache<T>(key: string, ttlSeconds: number, fetchFn: () => Promise<T>): Promise<T> {
    const cached = await this.get<CacheEntry<T>>(`cache:${key}`);
    
    if (cached && cached.timestamp + cached.ttl * 1000 > Date.now()) {
      return cached.data;
    }

    const data = await fetchFn();
    await this.set(`cache:${key}`, {
      data,
      timestamp: Date.now(),
      ttl: ttlSeconds,
    }, { ex: ttlSeconds });

    return data;
  }

  /**
   * User preferences
   */
  async getUserPreferences(userId: string): Promise<UserPreferences | null> {
    return this.get<UserPreferences>(`prefs:${userId}`);
  }

  async setUserPreferences(userId: string, prefs: UserPreferences): Promise<boolean> {
    const result = await this.set(`prefs:${userId}`, prefs);
    return result === 'OK';
  }

  /**
   * Search cache
   */
  async cacheSearchResults(cacheKey: string, results: JobSearchCache, ttlSeconds = 300): Promise<boolean> {
    const result = await this.set(`search:${cacheKey}`, results, { ex: ttlSeconds });
    return result === 'OK';
  }

  async getSearchResults(cacheKey: string): Promise<JobSearchCache | null> {
    return this.get<JobSearchCache>(`search:${cacheKey}`);
  }
}

// Singleton instance
let kvInstance: EdgeKV | null = null;

/**
 * Get EdgeKV singleton instance
 */
export function getEdgeKV(): EdgeKV {
  if (!kvInstance) {
    kvInstance = new EdgeKV();
  }
  return kvInstance;
}

// Export singleton
export const kv = getEdgeKV();

export default EdgeKV;
