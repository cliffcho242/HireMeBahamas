/* eslint-disable react-refresh/only-export-components */
/**
 * MessageNotificationContext
 * 
 * Global context for message notifications that provides:
 * - Real-time unread message count
 * - Browser notification permission management
 * - Notification sound playback
 * - Automatic permission request on login
 */

import { ReactNode, createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { useSocket } from './SocketContext';
import { useAuth } from './AuthContext';
import { messagesAPI } from '../services/api';
import { BackendMessage } from '../types';
import toast from 'react-hot-toast';

// Configuration constants
const NOTIFICATION_SOUND_PATH = '/sounds/notification.mp3';

// Type for window with webkitAudioContext
interface WebkitWindow extends Window {
  webkitAudioContext?: typeof AudioContext;
}

// Generate a notification beep using Web Audio API
const playWebAudioBeep = () => {
  try {
    const AudioContextClass = window.AudioContext || ((window as WebkitWindow).webkitAudioContext as typeof AudioContext);
    if (!AudioContextClass) {
      console.warn('Web Audio API not supported');
      return;
    }
    
    const audioContext = new AudioContextClass();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800; // Frequency in Hz
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.2);
    
    // Cleanup
    setTimeout(() => {
      audioContext.close().catch(() => {});
    }, 500);
  } catch (error) {
    console.warn('Web Audio API beep failed:', error);
  }
};

interface MessageNotificationContextType {
  unreadCount: number;
  setUnreadCount: (count: number) => void;
  decrementUnreadCount: () => void;
  incrementUnreadCount: () => void;
  requestNotificationPermission: () => Promise<boolean>;
  notificationPermission: NotificationPermission | null;
  isSupported: boolean;
  playNotificationSound: () => void;
  soundEnabled: boolean;
  setSoundEnabled: (enabled: boolean) => void;
  browserNotificationsEnabled: boolean;
  setBrowserNotificationsEnabled: (enabled: boolean) => void;
  refreshUnreadCount: () => Promise<void>;
}

const MessageNotificationContext = createContext<MessageNotificationContextType | undefined>(undefined);

// Storage keys
const SOUND_ENABLED_KEY = 'hireme_sound_enabled';
const BROWSER_NOTIFICATIONS_KEY = 'hireme_browser_notifications';

interface MessageNotificationProviderProps {
  children: ReactNode;
}

export const MessageNotificationProvider = ({ children }): MessageNotificationProviderProps => {
  const { socket } = useSocket();
  const { user, isAuthenticated } = useAuth();
  
  const [unreadCount, setUnreadCount] = useState<number>(0);
  // Initialize notification permission from Notification API during state initialization
  const [notificationPermission, setNotificationPermission] = useState<NotificationPermission | null>(() => {
    if (typeof Notification !== 'undefined') {
      return Notification.permission;
    }
    return null;
  });
  const [soundEnabled, setSoundEnabledState] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem(SOUND_ENABLED_KEY);
      return saved !== null ? saved === 'true' : true;
    } catch {
      return true;
    }
  });
  const [browserNotificationsEnabled, setBrowserNotificationsEnabledState] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem(BROWSER_NOTIFICATIONS_KEY);
      return saved !== null ? saved === 'true' : true;
    } catch {
      return true;
    }
  });
  
  const originalTitleRef = useRef<string>(document.title.replace(/^\[\d+\]\s*/, ''));
  const blinkIntervalRef = useRef<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const permissionRequestedRef = useRef<boolean>(false);
  const previousUserRef = useRef<typeof user>(user);
  
  // Check if notifications are supported
  const isSupported = typeof Notification !== 'undefined';
  
  // Listen for service worker messages (e.g., notification clicks)
  useEffect(() => {
    const handleServiceWorkerMessage = (event: MessageEvent) => {
      if (event.data?.type === 'NOTIFICATION_CLICK' && event.data?.url) {
        // Use window.location for navigation since we're outside React Router context
        // This is safe because the service worker has already focused the window
        window.location.href = event.data.url;
      }
    };
    
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', handleServiceWorkerMessage);
      return () => {
        navigator.serviceWorker.removeEventListener('message', handleServiceWorkerMessage);
      };
    }
  }, []);
  
  // Initialize audio element
  useEffect(() => {
    // Create audio element for notification sound
    const audio = new Audio(NOTIFICATION_SOUND_PATH);
    audio.preload = 'auto';
    audio.volume = 0.5;
    audioRef.current = audio;
    
    // Handle audio load error (file not found)
    audio.onerror = () => {
      console.warn('Notification sound file not found, will use Web Audio API fallback');
      audioRef.current = null;
    };
    
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);
  
  // Track document visibility for title blinking
  useEffect(() => {
    const handleVisibilityChange = () => {
      // Stop title blinking when tab becomes visible
      if (!document.hidden && blinkIntervalRef.current) {
        clearInterval(blinkIntervalRef.current);
        blinkIntervalRef.current = null;
        // Restore title with unread count
        if (unreadCount > 0) {
          document.title = `[${unreadCount}] ${originalTitleRef.current}`;
        } else {
          document.title = originalTitleRef.current;
        }
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [unreadCount]);
  
  // Request notification permission when user logs in
  useEffect(() => {
    if (isAuthenticated && isSupported && !permissionRequestedRef.current) {
      permissionRequestedRef.current = true;
      
      // Only request if not already granted/denied
      if (Notification.permission === 'default') {
        // Delay the request slightly to avoid blocking initial load
        const timer = setTimeout(async () => {
          try {
            const permission = await Notification.requestPermission();
            setNotificationPermission(permission);
            
            if (permission === 'granted') {
              toast.success('Notifications enabled! You\'ll be notified of new messages.');
            }
          } catch (error) {
            console.warn('Failed to request notification permission:', error);
          }
        }, 2000);
        
        return () => clearTimeout(timer);
      }
    }
  }, [isAuthenticated, isSupported]);
  
  // Fetch unread count - returns the count without setting state
  const fetchUnreadCountAsync = useCallback(async (): Promise<number> => {
    if (!user) return 0;
    
    try {
      const response = await messagesAPI.getUnreadCount();
      return response.unread_count || 0;
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
      return 0;
    }
  }, [user]);
  
  // Public refresh function that calls the fetch and updates state
  const refreshUnreadCount = useCallback(async () => {
    const count = await fetchUnreadCountAsync();
    setUnreadCount(count);
  }, [fetchUnreadCountAsync]);
  
  // Fetch initial unread count and refresh periodically
  // Track user changes to reset unread count when user logs out
  useEffect(() => {
    // Check if user just logged out (was present before, now null)
    if (previousUserRef.current && !user) {
      // User logged out - reset via ref to avoid calling setState synchronously
      previousUserRef.current = user;
      return;
    }
    previousUserRef.current = user;
    
    if (!user) {
      return;
    }
    
    // Use an async IIFE to avoid calling setState synchronously in the effect body
    // The setState call happens in the async callback, not synchronously
    let mounted = true;
    const doFetch = async () => {
      const count = await fetchUnreadCountAsync();
      if (mounted) {
        setUnreadCount(count);
      }
    };
    doFetch();
    
    // Refresh unread count every 30 seconds using the same pattern
    const interval = setInterval(async () => {
      if (mounted) {
        const count = await fetchUnreadCountAsync();
        if (mounted) {
          setUnreadCount(count);
        }
      }
    }, 30000);
    
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [user, fetchUnreadCountAsync]);
  
  // Keep unreadCountRef in sync with unreadCount (for use in callbacks)
  const unreadCountRef = useRef(unreadCount);
  useEffect(() => {
    unreadCountRef.current = unreadCount;
  }, [unreadCount]);
  
  // Reset unread count when user logs out
  // Only depends on user - uses a ref to avoid dependency on unreadCount in the effect
  useEffect(() => {
    if (!user && unreadCountRef.current > 0) {
      // Schedule the reset in a microtask to avoid synchronous setState in effect
      queueMicrotask(() => setUnreadCount(0));
    }
  }, [user]);
  
  // Update document title with unread count
  useEffect(() => {
    if (unreadCount > 0) {
      document.title = `[${unreadCount}] ${originalTitleRef.current}`;
    } else {
      document.title = originalTitleRef.current;
    }
  }, [unreadCount]);
  
  // Play notification sound
  const playNotificationSound = useCallback(() => {
    if (!soundEnabled) return;
    
    try {
      if (audioRef.current) {
        // Reset and play the audio
        audioRef.current.currentTime = 0;
        audioRef.current.play().catch((error) => {
          console.warn('Audio playback failed, using fallback:', error);
          playWebAudioBeep();
        });
      } else {
        // Use Web Audio API fallback
        playWebAudioBeep();
      }
    } catch (error) {
      console.warn('Failed to play notification sound:', error);
    }
  }, [soundEnabled]);
  
  // Show browser notification
  const showBrowserNotification = useCallback((message: BackendMessage) => {
    if (!browserNotificationsEnabled) return;
    if (!isSupported || Notification.permission !== 'granted') return;
    
    const senderName = `${message.sender.first_name} ${message.sender.last_name}`.trim() || 'Someone';
    const truncatedContent = message.content.length > 50 
      ? message.content.substring(0, 50) + '...' 
      : message.content;
    
    try {
      // Use type assertion for non-standard but widely supported notification options
      const notificationOptions: NotificationOptions & { renotify?: boolean } = {
        body: truncatedContent,
        icon: '/pwa-192x192.png',
        badge: '/pwa-192x192.png',
        tag: `message-${message.id}`,
        renotify: true,
        requireInteraction: false,
        silent: true, // We play our own sound
      };
      
      const notification = new Notification(`New message from ${senderName}`, notificationOptions);
      
      notification.onclick = () => {
        window.focus();
        notification.close();
        // Navigate to messages
        window.location.href = `/messages`;
      };
      
      // Auto-close after 5 seconds
      setTimeout(() => notification.close(), 5000);
    } catch (error) {
      console.warn('Failed to show browser notification:', error);
    }
  }, [browserNotificationsEnabled, isSupported]);
  
  // Start title blinking
  const startTitleBlink = useCallback((message: BackendMessage) => {
    if (document.visibilityState !== 'hidden') return; // Don't blink if tab is visible
    
    // Stop any existing blink
    if (blinkIntervalRef.current) {
      clearInterval(blinkIntervalRef.current);
    }
    
    const senderName = `${message.sender.first_name} ${message.sender.last_name}`.trim() || 'Someone';
    const newMessageTitle = `💬 New message from ${senderName}`;
    let showOriginal = false;
    
    blinkIntervalRef.current = window.setInterval(() => {
      // Use unreadCountRef to get current value without dependency
      const currentCount = unreadCountRef.current;
      document.title = showOriginal 
        ? (currentCount > 0 ? `[${currentCount}] ${originalTitleRef.current}` : originalTitleRef.current)
        : newMessageTitle;
      showOriginal = !showOriginal;
    }, 1000);
  }, []);
  
  // Handle incoming messages from WebSocket
  useEffect(() => {
    if (!socket || !user) return;
    
    const handleNewMessage = (message: BackendMessage) => {
      // Don't notify for own messages
      if (message.sender_id === user.id) return;
      
      // Update unread count
      setUnreadCount((prev) => prev + 1);
      
      // Play sound
      playNotificationSound();
      
      // Show browser notification (if tab is not visible)
      if (document.hidden) {
        showBrowserNotification(message);
        startTitleBlink(message);
      } else {
        // Show in-app toast notification when tab is visible
        const senderName = `${message.sender.first_name} ${message.sender.last_name}`.trim() || 'Someone';
        toast(`New message from ${senderName}`, {
          icon: '💬',
          duration: 4000,
        });
      }
    };
    
    socket.on('new_message', handleNewMessage);
    
    return () => {
      socket.off('new_message', handleNewMessage);
    };
  }, [socket, user, playNotificationSound, showBrowserNotification, startTitleBlink]);
  
  // Request notification permission
  const requestNotificationPermission = useCallback(async (): Promise<boolean> => {
    if (!isSupported) {
      console.warn('Browser notifications not supported');
      return false;
    }
    
    if (Notification.permission === 'granted') {
      setNotificationPermission('granted');
      return true;
    }
    
    if (Notification.permission === 'denied') {
      setNotificationPermission('denied');
      return false;
    }
    
    try {
      const permission = await Notification.requestPermission();
      setNotificationPermission(permission);
      return permission === 'granted';
    } catch (error) {
      console.error('Failed to request notification permission:', error);
      return false;
    }
  }, [isSupported]);
  
  // Setters with persistence
  const setSoundEnabled = useCallback((enabled: boolean) => {
    setSoundEnabledState(enabled);
    try {
      localStorage.setItem(SOUND_ENABLED_KEY, String(enabled));
    } catch (error) {
      console.warn('Failed to save sound preference:', error);
    }
  }, []);
  
  const setBrowserNotificationsEnabled = useCallback((enabled: boolean) => {
    setBrowserNotificationsEnabledState(enabled);
    try {
      localStorage.setItem(BROWSER_NOTIFICATIONS_KEY, String(enabled));
    } catch (error) {
      console.warn('Failed to save notification preference:', error);
    }
  }, []);
  
  const decrementUnreadCount = useCallback(() => {
    setUnreadCount((prev) => Math.max(0, prev - 1));
  }, []);
  
  const incrementUnreadCount = useCallback(() => {
    setUnreadCount((prev) => prev + 1);
  }, []);
  
  const value: MessageNotificationContextType = {
    unreadCount,
    setUnreadCount,
    decrementUnreadCount,
    incrementUnreadCount,
    requestNotificationPermission,
    notificationPermission,
    isSupported,
    playNotificationSound,
    soundEnabled,
    setSoundEnabled,
    browserNotificationsEnabled,
    setBrowserNotificationsEnabled,
    refreshUnreadCount,
  };
  
  return (
    <MessageNotificationContext.Provider value={value}>
      {children}
    </MessageNotificationContext.Provider>
  );
};

export const useMessageNotifications = (): MessageNotificationContextType => {
  const context = useContext(MessageNotificationContext);
  if (context === undefined) {
    throw new Error('useMessageNotifications must be used within a MessageNotificationProvider');
  }
  return context;
};
