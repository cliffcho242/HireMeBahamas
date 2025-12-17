/**
 * Real-time WebSocket hook for addictive user experience
 * 
 * Features:
 * - Instant message delivery with sound + red dot
 * - Typing indicators ("User is typing...")
 * - Live like/follow/notification updates
 * - Automatic reconnection with exponential backoff
 * - Optimistic updates for instant feedback
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { getApiBase } from './api';

// ✅ SAFE: Use the safe API URL builder - never breaks
const SOCKET_URL = getApiBase();
const RECONNECT_DELAY_BASE = 1000;
const MAX_RECONNECT_DELAY = 30000;
const TYPING_TIMEOUT = 3000; // Show "typing" for 3 seconds after last keystroke

// Sound paths
const NOTIFICATION_SOUND = '/sounds/notification.mp3';
const MESSAGE_SOUND = '/sounds/notification.mp3';

// Notification types
export type NotificationType = 
  | 'message'
  | 'like'
  | 'follow'
  | 'comment'
  | 'mention'
  | 'job_application'
  | 'job_posted';

export interface RealtimeNotification {
  id: string;
  type: NotificationType;
  title: string;
  body: string;
  data?: Record<string, unknown>;
  timestamp: Date;
  read: boolean;
}

export interface TypingIndicator {
  userId: string;
  userName: string;
  conversationId: string;
  isTyping: boolean;
  lastUpdate: number;
}

export interface UserStatus {
  userId: string;
  status: 'online' | 'offline' | 'away';
  lastSeen?: Date;
}

export interface RealtimeMessage {
  id: string;
  conversationId: string;
  senderId: string;
  receiverId: string;
  content: string;
  createdAt: string;
  sender: {
    id: string;
    fullName: string;
    profileImage?: string;
  };
}

interface RealtimeState {
  isConnected: boolean;
  unreadCount: number;
  notifications: RealtimeNotification[];
  typingUsers: Map<string, TypingIndicator>;
  onlineUsers: Set<string>;
}

/**
 * Audio service for managing notification sounds
 * Uses a singleton pattern to prevent memory leaks and ensure consistent playback
 */
class AudioService {
  private static instance: AudioService;
  private notificationAudio: HTMLAudioElement | null = null;
  private messageAudio: HTMLAudioElement | null = null;
  private initialized = false;

  private constructor() {
    // Private constructor for singleton
  }

  static getInstance(): AudioService {
    if (!AudioService.instance) {
      AudioService.instance = new AudioService();
    }
    return AudioService.instance;
  }

  private initializeAudio(): void {
    if (this.initialized || typeof window === 'undefined') return;
    
    try {
      this.notificationAudio = new Audio(NOTIFICATION_SOUND);
      this.notificationAudio.volume = 0.5;
      this.messageAudio = new Audio(MESSAGE_SOUND);
      this.messageAudio.volume = 0.6;
      this.initialized = true;
    } catch {
      // Audio not supported
    }
  }

  playNotificationSound(): void {
    this.initializeAudio();
    try {
      if (this.notificationAudio) {
        this.notificationAudio.currentTime = 0;
        this.notificationAudio.play().catch(() => {
          // User hasn't interacted yet, ignore
        });
      }
    } catch {
      // Audio playback failed
    }
  }

  playMessageSound(): void {
    this.initializeAudio();
    try {
      if (this.messageAudio) {
        this.messageAudio.currentTime = 0;
        this.messageAudio.play().catch(() => {
          // User hasn't interacted yet, ignore
        });
      }
    } catch {
      // Audio playback failed
    }
  }

  cleanup(): void {
    if (this.notificationAudio) {
      this.notificationAudio.pause();
      this.notificationAudio = null;
    }
    if (this.messageAudio) {
      this.messageAudio.pause();
      this.messageAudio = null;
    }
    this.initialized = false;
  }
}

// Singleton audio service instance
const audioService = AudioService.getInstance();

const playNotificationSound = () => {
  audioService.playNotificationSound();
};

const playMessageSound = () => {
  audioService.playMessageSound();
};

// Show browser notification with badge
const showBrowserNotification = (title: string, body: string, data?: Record<string, unknown>) => {
  if ('Notification' in window && Notification.permission === 'granted') {
    // NotificationOptions extended for PWA features
    const options: NotificationOptions & { vibrate?: number[]; data?: Record<string, unknown> } = {
      body,
      icon: '/pwa-192x192.png',
      badge: '/pwa-192x192.png',
      tag: 'hireme-' + Date.now(),
      data,
    };

    // Add vibration pattern if supported
    if ('vibrate' in navigator) {
      options.vibrate = [200, 100, 200];
    }

    const notification = new Notification(title, options as NotificationOptions);

    notification.onclick = () => {
      window.focus();
      notification.close();
      // Navigate to relevant page based on notification type
      if (data?.url) {
        window.location.href = data.url as string;
      }
    };

    // Auto-close after 5 seconds
    setTimeout(() => notification.close(), 5000);
  }
};

// Update document title with unread count (badge effect)
const updateTitleBadge = (count: number) => {
  const baseTitle = 'HireMeBahamas';
  if (count > 0) {
    document.title = `(${count}) ${baseTitle}`;
    // Update favicon with badge (if supported)
    updateFaviconBadge(count);
  } else {
    document.title = baseTitle;
    resetFavicon();
  }
};

// Cache for favicon badge to avoid repeated image loading
let cachedFaviconImage: HTMLImageElement | null = null;
let cachedCanvas: HTMLCanvasElement | null = null;

// Favicon badge helper with caching
const updateFaviconBadge = (count: number) => {
  // Reuse cached canvas or create new one
  if (!cachedCanvas) {
    cachedCanvas = document.createElement('canvas');
    cachedCanvas.width = 32;
    cachedCanvas.height = 32;
  }
  
  const ctx = cachedCanvas.getContext('2d');
  if (!ctx) return;

  const drawBadge = () => {
    if (!cachedFaviconImage || !ctx) return;
    
    // Clear and redraw
    ctx.clearRect(0, 0, 32, 32);
    ctx.drawImage(cachedFaviconImage, 0, 0, 32, 32);
    
    // Draw badge circle
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(24, 8, 8, 0, 2 * Math.PI);
    ctx.fill();
    
    // Draw count text
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 10px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(count > 99 ? '99+' : String(count), 24, 8);
    
    // Update favicon link
    const link = document.querySelector<HTMLLinkElement>("link[rel*='icon']") 
      || document.createElement('link');
    link.type = 'image/x-icon';
    link.rel = 'shortcut icon';
    link.href = cachedCanvas!.toDataURL();
    if (!link.parentNode) {
      document.head.appendChild(link);
    }
  };

  // Load and cache favicon image if not already cached
  if (!cachedFaviconImage) {
    cachedFaviconImage = new Image();
    cachedFaviconImage.onload = drawBadge;
    cachedFaviconImage.src = '/favicon-32x32.png';
  } else {
    drawBadge();
  }
};

const resetFavicon = () => {
  const link = document.querySelector<HTMLLinkElement>("link[rel*='icon']");
  if (link) {
    link.href = '/favicon.ico';
  }
};

/**
 * Sanitize message content for safe display in notifications
 * Uses a whitelist approach - only allows safe alphanumeric and basic punctuation
 * This is the safest approach for untrusted content
 */
const sanitizeMessageContent = (content: string, maxLength = 100): string => {
  if (!content || typeof content !== 'string') return '';
  
  // Use a whitelist approach: only allow safe characters
  // This includes letters, numbers, spaces, and basic punctuation
  // This is safer than trying to blacklist dangerous patterns
  const allowedChars = /[^a-zA-Z0-9\s.,!?@#$%^&*()\-_+=[\]{}|\\:;~]/g;
  
  let sanitized = content
    // First, normalize whitespace
    .replace(/\s+/g, ' ')
    // Remove any characters not in the whitelist
    .replace(allowedChars, '')
    // Remove any remaining angle brackets (double check)
    .replace(/[<>]/g, '')
    // Trim whitespace
    .trim();
  
  // Double-check: encode any remaining special HTML entities
  // This is a fallback in case something slipped through
  sanitized = sanitized
    .replace(/&/g, '')
    .replace(/"/g, '')
    .replace(/'/g, '')
    .replace(/`/g, '');
  
  // Truncate to max length
  if (sanitized.length > maxLength) {
    return sanitized.substring(0, maxLength) + '...';
  }
  
  return sanitized || '';
};

/**
 * Main realtime hook for WebSocket connection
 */
export function useRealtime(userId?: string | number) {
  const socketRef = useRef<Socket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const typingTimeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map());
  
  const [state, setState] = useState<RealtimeState>({
    isConnected: false,
    unreadCount: 0,
    notifications: [],
    typingUsers: new Map(),
    onlineUsers: new Set(),
  });

  // Connect to WebSocket server
  const connect = useCallback(() => {
    if (!userId || socketRef.current?.connected) return;

    const token = localStorage.getItem('token');
    if (!token) return;

    const socket = io(SOCKET_URL, {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnectionAttempts: 10,
      reconnectionDelay: RECONNECT_DELAY_BASE,
      reconnectionDelayMax: MAX_RECONNECT_DELAY,
      timeout: 20000,
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('🔌 Realtime connected');
      reconnectAttemptRef.current = 0;
      setState(prev => ({ ...prev, isConnected: true }));
      
      // Request initial data
      socket.emit('get_unread_count');
      socket.emit('get_online_users');
    });

    socket.on('disconnect', (reason) => {
      console.log('🔌 Realtime disconnected:', reason);
      setState(prev => ({ ...prev, isConnected: false }));
    });

    socket.on('connect_error', (error) => {
      console.error('🔌 Connection error:', error);
      reconnectAttemptRef.current++;
    });

    // Handle new messages - instant push + sound + red dot
    socket.on('new_message', (message: RealtimeMessage) => {
      console.log('📩 New message:', message);
      
      // Play sound
      playMessageSound();
      
      // Update unread count
      setState(prev => {
        const newCount = prev.unreadCount + 1;
        updateTitleBadge(newCount);
        return { ...prev, unreadCount: newCount };
      });
      
      // Show browser notification if tab not focused
      if (document.hidden) {
        // Sanitize message content for safe display
        const sanitizedContent = sanitizeMessageContent(message.content);
        const sanitizedSenderName = sanitizeMessageContent(message.sender.fullName, 50);
        
        showBrowserNotification(
          `New message from ${sanitizedSenderName}`,
          sanitizedContent,
          { url: `/messages?conversation=${message.conversationId}` }
        );
      }
    });

    // Handle notifications (likes, follows, etc)
    socket.on('notification', (notification: RealtimeNotification) => {
      console.log('🔔 New notification:', notification);
      
      // Play notification sound
      playNotificationSound();
      
      // Add to notifications list
      setState(prev => {
        const newNotifications = [notification, ...prev.notifications].slice(0, 50);
        const newCount = prev.unreadCount + 1;
        updateTitleBadge(newCount);
        return { 
          ...prev, 
          notifications: newNotifications,
          unreadCount: newCount 
        };
      });
      
      // Show browser notification with sanitized content
      if (document.hidden) {
        const sanitizedTitle = sanitizeMessageContent(notification.title, 50);
        const sanitizedBody = sanitizeMessageContent(notification.body, 150);
        showBrowserNotification(sanitizedTitle, sanitizedBody, notification.data);
      }
    });

    // Handle typing indicators
    socket.on('typing', (data: TypingIndicator) => {
      console.log('⌨️ Typing:', data);
      
      setState(prev => {
        const newTypingUsers = new Map(prev.typingUsers);
        
        if (data.isTyping) {
          newTypingUsers.set(data.conversationId, {
            ...data,
            lastUpdate: Date.now(),
          });
          
          // Clear existing timeout for this conversation
          const existingTimeout = typingTimeoutsRef.current.get(data.conversationId);
          if (existingTimeout) {
            clearTimeout(existingTimeout);
          }
          
          // Set new timeout to remove typing indicator
          const timeout = setTimeout(() => {
            setState(p => {
              const updated = new Map(p.typingUsers);
              updated.delete(data.conversationId);
              return { ...p, typingUsers: updated };
            });
          }, TYPING_TIMEOUT);
          
          typingTimeoutsRef.current.set(data.conversationId, timeout);
        } else {
          newTypingUsers.delete(data.conversationId);
        }
        
        return { ...prev, typingUsers: newTypingUsers };
      });
    });

    // Handle user status changes
    socket.on('user_status', (status: UserStatus) => {
      console.log('👤 User status:', status);
      
      setState(prev => {
        const newOnlineUsers = new Set(prev.onlineUsers);
        if (status.status === 'online') {
          newOnlineUsers.add(status.userId);
        } else {
          newOnlineUsers.delete(status.userId);
        }
        return { ...prev, onlineUsers: newOnlineUsers };
      });
    });

    // Handle online users list
    socket.on('online_users', (userIds: string[]) => {
      setState(prev => ({
        ...prev,
        onlineUsers: new Set(userIds),
      }));
    });

    // Handle unread count update
    socket.on('unread_count', (count: number) => {
      setState(prev => {
        updateTitleBadge(count);
        return { ...prev, unreadCount: count };
      });
    });

    // Handle like events (for real-time like count updates)
    socket.on('post_liked', (data: { postId: number; likesCount: number; likedBy: string }) => {
      console.log('❤️ Post liked:', data);
      // This will be handled by the PostFeed component via a custom event
      window.dispatchEvent(new CustomEvent('post_liked', { detail: data }));
    });

    // Handle new follower
    socket.on('new_follower', (data: { followerId: string; followerName: string }) => {
      console.log('👥 New follower:', data);
      playNotificationSound();
      
      if (document.hidden) {
        showBrowserNotification(
          'New Follower',
          `${data.followerName} started following you`,
          { url: `/user/${data.followerId}` }
        );
      }
    });

    return () => {
      socket.disconnect();
    };
  }, [userId]);

  // Disconnect and cleanup
  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect();
      socketRef.current = null;
    }
    
    // Clear all typing timeouts
    typingTimeoutsRef.current.forEach(timeout => clearTimeout(timeout));
    typingTimeoutsRef.current.clear();
    
    setState({
      isConnected: false,
      unreadCount: 0,
      notifications: [],
      typingUsers: new Map(),
      onlineUsers: new Set(),
    });
    
    resetFavicon();
    document.title = 'HireMeBahamas';
  }, []);

  // Join a conversation room
  const joinConversation = useCallback((conversationId: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('join_conversation', { conversation_id: conversationId });
    }
  }, []);

  // Leave a conversation room
  const leaveConversation = useCallback((conversationId: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('leave_conversation', { conversation_id: conversationId });
    }
  }, []);

  // Send typing indicator
  const sendTyping = useCallback((conversationId: string, isTyping: boolean) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('typing', {
        conversation_id: conversationId,
        is_typing: isTyping,
      });
    }
  }, []);

  // Mark notifications as read
  const markNotificationsRead = useCallback(() => {
    setState(prev => ({
      ...prev,
      unreadCount: 0,
      notifications: prev.notifications.map(n => ({ ...n, read: true })),
    }));
    updateTitleBadge(0);
    
    if (socketRef.current?.connected) {
      socketRef.current.emit('mark_notifications_read');
    }
  }, []);

  // Check if user is online
  const isUserOnline = useCallback((checkUserId: string) => {
    return state.onlineUsers.has(checkUserId);
  }, [state.onlineUsers]);

  // Get typing indicator for conversation
  const getTypingIndicator = useCallback((conversationId: string) => {
    return state.typingUsers.get(conversationId);
  }, [state.typingUsers]);

  // Connect when userId is available
  useEffect(() => {
    if (userId) {
      connect();
    }
    
    return () => {
      disconnect();
    };
  }, [userId, connect, disconnect]);

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      // Request permission after user interaction
      const requestPermission = () => {
        Notification.requestPermission();
        document.removeEventListener('click', requestPermission);
      };
      document.addEventListener('click', requestPermission);
      return () => document.removeEventListener('click', requestPermission);
    }
  }, []);

  return {
    ...state,
    connect,
    disconnect,
    joinConversation,
    leaveConversation,
    sendTyping,
    markNotificationsRead,
    isUserOnline,
    getTypingIndicator,
    // Use a getter function instead of accessing ref during render
    getSocket: () => socketRef.current,
  };
}

/**
 * Hook for typing indicator with debounce
 */
export function useTypingIndicator(
  conversationId: string,
  sendTyping: (conversationId: string, isTyping: boolean) => void
) {
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isTypingRef = useRef(false);

  const handleTyping = useCallback(() => {
    // Start typing if not already
    if (!isTypingRef.current) {
      isTypingRef.current = true;
      sendTyping(conversationId, true);
    }

    // Reset timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Stop typing after 2 seconds of inactivity
    typingTimeoutRef.current = setTimeout(() => {
      isTypingRef.current = false;
      sendTyping(conversationId, false);
    }, 2000);
  }, [conversationId, sendTyping]);

  const stopTyping = useCallback(() => {
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    if (isTypingRef.current) {
      isTypingRef.current = false;
      sendTyping(conversationId, false);
    }
  }, [conversationId, sendTyping]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  return { handleTyping, stopTyping };
}

/**
 * Hook for online status indicator with green dot
 */
export function useOnlineStatus(userId: string, isUserOnline: (id: string) => boolean) {
  // Initialize state with the current online status to avoid cascading renders
  const [isOnline, setIsOnline] = useState(() => isUserOnline(userId));

  useEffect(() => {
    // Update on status change events
    const handleStatusChange = () => {
      setIsOnline(isUserOnline(userId));
    };
    
    window.addEventListener('user_status_change', handleStatusChange);
    return () => window.removeEventListener('user_status_change', handleStatusChange);
  }, [userId, isUserOnline]);

  return isOnline;
}

export default useRealtime;
