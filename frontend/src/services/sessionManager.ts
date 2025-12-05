import { User } from '../types/user';

const SESSION_KEY = 'hireme_session';
const ACTIVITY_KEY = 'hireme_last_activity';
const TOKEN_KEY = 'token';
const USER_KEY = 'hireme_user';

// Session timeout in milliseconds (30 minutes of inactivity)
const SESSION_TIMEOUT = 30 * 60 * 1000;

// Warning threshold (5 minutes before timeout)
const WARNING_THRESHOLD = 5 * 60 * 1000;

// Token refresh threshold (refresh 1 day before expiration)
const TOKEN_REFRESH_THRESHOLD = 24 * 60 * 60 * 1000;

export interface SessionData {
  token: string;
  user: User;
  lastActivity: number;
  expiresAt: number;
  rememberMe: boolean;
}

class SessionManager {
  private activityTimer: NodeJS.Timeout | null = null;
  private warningTimer: NodeJS.Timeout | null = null;
  private onSessionExpiring: (() => void) | null = null;
  private onSessionExpired: (() => void) | null = null;
  private activityListeners: Array<{ event: string; handler: EventListener }> = [];
  private lastActivityUpdate: number = 0; // Track last update for throttling

  constructor() {
    this.setupActivityTracking();
  }

  /**
   * Simple base64 encoding for session data
   * For production, consider using Web Crypto API for stronger encryption
   */
  private encode(data: string): string {
    return btoa(unescape(encodeURIComponent(data)));
  }

  /**
   * Simple base64 decoding for session data
   */
  private decode(encodedData: string): string {
    return decodeURIComponent(escape(atob(encodedData)));
  }

  /**
   * Save session data with encoding
   */
  saveSession(sessionData: SessionData): void {
    try {
      const encoded = this.encode(JSON.stringify(sessionData));
      localStorage.setItem(SESSION_KEY, encoded);
      localStorage.setItem(TOKEN_KEY, sessionData.token);
      
      if (sessionData.user) {
        localStorage.setItem(USER_KEY, JSON.stringify(sessionData.user));
      }
      
      this.updateActivity();
    } catch (error) {
      console.error('Failed to save session:', error);
    }
  }

  /**
   * Load session data from storage
   */
  loadSession(): SessionData | null {
    try {
      const encoded = localStorage.getItem(SESSION_KEY);
      if (!encoded) {
        return null;
      }

      const decoded = this.decode(encoded);
      const session: SessionData = JSON.parse(decoded);

      // Check if session has expired
      if (Date.now() > session.expiresAt) {
        this.clearSession();
        return null;
      }

      // Check if session has been inactive too long
      if (!session.rememberMe) {
        const lastActivity = parseInt(localStorage.getItem(ACTIVITY_KEY) || '0');
        if (Date.now() - lastActivity > SESSION_TIMEOUT) {
          this.clearSession();
          return null;
        }
      }

      return session;
    } catch (error) {
      console.error('Failed to load session:', error);
      return null;
    }
  }

  /**
   * Clear session data
   */
  clearSession(): void {
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    localStorage.removeItem(ACTIVITY_KEY);
    this.stopActivityTracking();
  }

  /**
   * Cleanup all resources (call when app unmounts or user logs out permanently)
   */
  cleanup(): void {
    this.stopActivityTracking();
    this.cleanupActivityTracking();
    this.onSessionExpiring = null;
    this.onSessionExpired = null;
  }

  /**
   * Update last activity timestamp
   */
  updateActivity(): void {
    localStorage.setItem(ACTIVITY_KEY, Date.now().toString());
    this.resetTimers();
  }

  /**
   * Setup activity tracking with throttling to reduce overhead
   */
  private setupActivityTracking(): void {
    const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'click'];
    
    // Throttle activity updates to once per 10 seconds to reduce overhead
    const THROTTLE_MS = 10000; // 10 seconds
    
    const handleActivity = () => {
      const now = Date.now();
      if (now - this.lastActivityUpdate > THROTTLE_MS) {
        this.lastActivityUpdate = now;
        this.updateActivity();
      }
    };

    // Store listeners so we can remove them later
    events.forEach(event => {
      window.addEventListener(event, handleActivity, { passive: true });
      this.activityListeners.push({ event, handler: handleActivity });
    });
  }

  /**
   * Remove activity tracking listeners (for cleanup)
   */
  private cleanupActivityTracking(): void {
    this.activityListeners.forEach(({ event, handler }) => {
      window.removeEventListener(event, handler);
    });
    this.activityListeners = [];
  }

  /**
   * Reset activity timers
   */
  private resetTimers(): void {
    // Clear existing timers
    if (this.activityTimer) {
      clearTimeout(this.activityTimer);
    }
    if (this.warningTimer) {
      clearTimeout(this.warningTimer);
    }

    const session = this.loadSession();
    if (!session || session.rememberMe) {
      return;
    }

    // Set warning timer
    this.warningTimer = setTimeout(() => {
      if (this.onSessionExpiring) {
        this.onSessionExpiring();
      }
    }, SESSION_TIMEOUT - WARNING_THRESHOLD);

    // Set expiration timer
    this.activityTimer = setTimeout(() => {
      if (this.onSessionExpired) {
        this.onSessionExpired();
      }
      this.clearSession();
    }, SESSION_TIMEOUT);
  }

  /**
   * Stop activity tracking
   */
  private stopActivityTracking(): void {
    if (this.activityTimer) {
      clearTimeout(this.activityTimer);
      this.activityTimer = null;
    }
    if (this.warningTimer) {
      clearTimeout(this.warningTimer);
      this.warningTimer = null;
    }
  }

  /**
   * Register callback for session expiring warning
   */
  onExpiring(callback: () => void): void {
    this.onSessionExpiring = callback;
  }

  /**
   * Register callback for session expired
   */
  onExpired(callback: () => void): void {
    this.onSessionExpired = callback;
  }

  /**
   * Check if token needs refresh
   */
  shouldRefreshToken(expiresAt: number): boolean {
    const timeUntilExpiration = expiresAt - Date.now();
    return timeUntilExpiration < TOKEN_REFRESH_THRESHOLD && timeUntilExpiration > 0;
  }

  /**
   * Get remaining session time in milliseconds
   */
  getRemainingTime(): number {
    const lastActivity = parseInt(localStorage.getItem(ACTIVITY_KEY) || '0');
    const elapsed = Date.now() - lastActivity;
    return Math.max(0, SESSION_TIMEOUT - elapsed);
  }

  /**
   * Check if session is active
   */
  isSessionActive(): boolean {
    const session = this.loadSession();
    return session !== null;
  }

  /**
   * Extract token expiration from JWT
   */
  getTokenExpiration(token: string): number | null {
    try {
      const payload = token.split('.')[1];
      const decoded = JSON.parse(atob(payload));
      return decoded.exp ? decoded.exp * 1000 : null;
    } catch (error) {
      console.error('Failed to decode token:', error);
      return null;
    }
  }

  /**
   * Extend session
   */
  extendSession(): void {
    const session = this.loadSession();
    if (session) {
      this.updateActivity();
      this.resetTimers();
    }
  }
}

// Export singleton instance
export const sessionManager = new SessionManager();
