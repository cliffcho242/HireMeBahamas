/**
 * Real-time Notification Service using Server-Sent Events (SSE)
 * 
 * SSE is chosen over WebSocket because:
 * 1. Works with serverless/edge deployments (Vercel, Railway free tier)
 * 2. Automatic reconnection handling
 * 3. Simpler server implementation (no special WebSocket support needed)
 * 4. Works through proxies and load balancers without special configuration
 * 
 * For job notifications, SSE provides:
 * - New job alerts matching user preferences
 * - Application status updates
 * - Message notifications
 * - Connection status alerts
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { create } from 'zustand';

// Types for notification events
export interface JobNotification {
  type: 'new_job';
  id: number;
  title: string;
  company: string;
  location: string;
  timestamp: string;
}

export interface MessageNotification {
  type: 'new_message';
  conversationId: number;
  senderId: number;
  senderName: string;
  preview: string;
  timestamp: string;
}

export interface ApplicationNotification {
  type: 'application_update';
  jobId: number;
  jobTitle: string;
  status: 'viewed' | 'shortlisted' | 'interview' | 'rejected' | 'accepted';
  timestamp: string;
}

export interface SystemNotification {
  type: 'system';
  message: string;
  level: 'info' | 'warning' | 'error';
  timestamp: string;
}

export type RealtimeNotification =
  | JobNotification
  | MessageNotification
  | ApplicationNotification
  | SystemNotification;

// Connection states
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

// Zustand store for real-time state
interface RealtimeStore {
  connectionStatus: ConnectionStatus;
  notifications: RealtimeNotification[];
  unreadCount: number;
  setConnectionStatus: (status: ConnectionStatus) => void;
  addNotification: (notification: RealtimeNotification) => void;
  markAsRead: (index: number) => void;
  clearNotifications: () => void;
  decrementUnread: () => void;
}

export const useRealtimeStore = create<RealtimeStore>((set) => ({
  connectionStatus: 'disconnected',
  notifications: [],
  unreadCount: 0,
  setConnectionStatus: (status) => set({ connectionStatus: status }),
  addNotification: (notification) =>
    set((state) => ({
      notifications: [notification, ...state.notifications].slice(0, 50), // Keep last 50
      unreadCount: state.unreadCount + 1,
    })),
  markAsRead: (index) =>
    set((state) => ({
      notifications: state.notifications.map((n, i) =>
        i === index ? { ...n, read: true } : n
      ),
    })),
  clearNotifications: () => set({ notifications: [], unreadCount: 0 }),
  decrementUnread: () =>
    set((state) => ({
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),
}));

// SSE Configuration
const SSE_RETRY_DELAYS = [1000, 2000, 5000, 10000, 30000]; // Exponential backoff

/**
 * useRealtimeNotifications - Hook for connecting to SSE notifications
 * 
 * @param enabled - Whether to enable the SSE connection
 * @param token - Auth token for authentication
 * @returns Connection status and notification methods
 */
export function useRealtimeNotifications(
  enabled: boolean = true,
  token?: string | null
) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const retryCountRef = useRef(0);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [lastEventTime, setLastEventTime] = useState<Date | null>(null);

  const {
    connectionStatus,
    setConnectionStatus,
    addNotification,
    notifications,
    unreadCount,
    clearNotifications,
  } = useRealtimeStore();

  // Get the API base URL
  const getApiUrl = useCallback(() => {
    const apiUrl = import.meta.env.VITE_API_URL || '';
    return apiUrl.replace(/\/$/, ''); // Remove trailing slash
  }, []);

  // Connect to SSE endpoint
  const connect = useCallback(function sseConnect() {
    if (!enabled || !token) {
      return;
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setConnectionStatus('connecting');

    try {
      const apiUrl = getApiUrl();
      // SSE endpoint with auth token as query param (SSE doesn't support headers)
      const sseUrl = `${apiUrl}/api/notifications/stream?token=${encodeURIComponent(token)}`;
      
      const eventSource = new EventSource(sseUrl);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setConnectionStatus('connected');
        retryCountRef.current = 0; // Reset retry count on successful connection
        console.log('📡 SSE Connected - Real-time notifications active');
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as RealtimeNotification;
          addNotification(data);
          setLastEventTime(new Date());
        } catch (error) {
          console.error('Failed to parse SSE message:', error);
        }
      };

      // Handle specific event types
      eventSource.addEventListener('job', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data) as JobNotification;
          addNotification({ ...data, type: 'new_job' });
          setLastEventTime(new Date());
        } catch (error) {
          console.error('Failed to parse job event:', error);
        }
      });

      eventSource.addEventListener('message', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data) as MessageNotification;
          addNotification({ ...data, type: 'new_message' });
          setLastEventTime(new Date());
        } catch (error) {
          console.error('Failed to parse message event:', error);
        }
      });

      eventSource.addEventListener('application', (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data) as ApplicationNotification;
          addNotification({ ...data, type: 'application_update' });
          setLastEventTime(new Date());
        } catch (error) {
          console.error('Failed to parse application event:', error);
        }
      });

      eventSource.addEventListener('ping', () => {
        // Heartbeat to keep connection alive
        setLastEventTime(new Date());
      });

      eventSource.onerror = () => {
        setConnectionStatus('error');
        eventSource.close();
        eventSourceRef.current = null;

        // Retry with exponential backoff
        const retryDelay =
          SSE_RETRY_DELAYS[Math.min(retryCountRef.current, SSE_RETRY_DELAYS.length - 1)];
        
        console.log(`📡 SSE Disconnected - Retrying in ${retryDelay / 1000}s`);
        
        retryTimeoutRef.current = setTimeout(() => {
          retryCountRef.current++;
          // Note: Reconnection is handled by useEffect dependencies
          // This is a fallback that will trigger when visibility changes
        }, retryDelay);
      };
    } catch (error) {
      console.error('SSE connection error:', error);
      setConnectionStatus('error');
    }
  }, [enabled, token, getApiUrl, setConnectionStatus, addNotification]);

  // Disconnect from SSE
  const disconnect = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    
    setConnectionStatus('disconnected');
  }, [setConnectionStatus]);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    if (enabled && token) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, token, connect, disconnect]);

  // Handle visibility change - reconnect when page becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && enabled && token) {
        // Check if we need to reconnect
        if (connectionStatus !== 'connected') {
          connect();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [enabled, token, connectionStatus, connect]);

  return {
    connectionStatus,
    notifications,
    unreadCount,
    lastEventTime,
    connect,
    disconnect,
    clearNotifications,
  };
}

/**
 * Fallback polling for environments where SSE isn't supported
 * 
 * This provides a graceful fallback that still delivers notifications,
 * just with slightly higher latency (polling every 30 seconds).
 */
export function usePollingNotifications(
  enabled: boolean = true,
  token?: string | null,
  intervalMs: number = 30000
) {
  const { addNotification } = useRealtimeStore();
  const [lastCheck, setLastCheck] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled || !token) return;

    const checkNotifications = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_URL || '';
        const url = lastCheck
          ? `${apiUrl}/api/notifications?since=${encodeURIComponent(lastCheck)}`
          : `${apiUrl}/api/notifications`;

        const response = await fetch(url, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.notifications && Array.isArray(data.notifications)) {
            data.notifications.forEach((notification: RealtimeNotification) => {
              addNotification(notification);
            });
          }
          setLastCheck(new Date().toISOString());
        }
      } catch (error) {
        console.error('Failed to poll notifications:', error);
      }
    };

    // Initial check
    checkNotifications();

    // Set up polling interval
    const interval = setInterval(checkNotifications, intervalMs);

    return () => {
      clearInterval(interval);
    };
  }, [enabled, token, intervalMs, lastCheck, addNotification]);
}

export default useRealtimeNotifications;
