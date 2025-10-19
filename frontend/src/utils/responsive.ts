/**
 * Responsive Utilities for Mobile, Tablet, and Desktop
 * Optimized for excellent performance across all devices
 */

// Device detection utilities
export const isMobile = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
};

export const isTablet = () => {
  const userAgent = navigator.userAgent.toLowerCase();
  return (
    /(ipad|tablet|(android(?!.*mobile))|(windows(?!.*phone)(.*touch))|kindle|playbook|silk|(puffin(?!.*(IP|AP|WP))))/.test(
      userAgent
    )
  );
};

export const isDesktop = () => {
  return !isMobile() && !isTablet();
};

// Touch detection
export const isTouchDevice = () => {
  return (
    'ontouchstart' in window ||
    navigator.maxTouchPoints > 0 ||
    // @ts-ignore
    navigator.msMaxTouchPoints > 0
  );
};

// Screen size utilities
export const getScreenSize = () => {
  const width = window.innerWidth;
  
  if (width < 640) return 'mobile';
  if (width < 768) return 'sm';
  if (width < 1024) return 'tablet';
  if (width < 1280) return 'lg';
  if (width < 1536) return 'desktop';
  return 'xl';
};

// Orientation detection
export const isPortrait = () => {
  return window.innerHeight > window.innerWidth;
};

export const isLandscape = () => {
  return window.innerWidth > window.innerHeight;
};

// Safe area support for notched devices
export const getSafeAreaInsets = () => {
  const style = getComputedStyle(document.documentElement);
  
  return {
    top: parseInt(style.getPropertyValue('env(safe-area-inset-top)') || '0'),
    right: parseInt(style.getPropertyValue('env(safe-area-inset-right)') || '0'),
    bottom: parseInt(style.getPropertyValue('env(safe-area-inset-bottom)') || '0'),
    left: parseInt(style.getPropertyValue('env(safe-area-inset-left)') || '0'),
  };
};

// Performance optimization
export const prefersReducedMotion = () => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

export const prefersDarkMode = () => {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
};

// Network detection
export const getConnectionType = () => {
  // @ts-ignore
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  return connection?.effectiveType || 'unknown';
};

export const isSlowConnection = () => {
  const type = getConnectionType();
  return type === 'slow-2g' || type === '2g';
};

// Device capabilities
export const supportsWebP = () => {
  const elem = document.createElement('canvas');
  if (elem.getContext && elem.getContext('2d')) {
    return elem.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }
  return false;
};

export const supportsServiceWorker = () => {
  return 'serviceWorker' in navigator;
};

// Viewport utilities
export const getViewportSize = () => {
  return {
    width: window.innerWidth,
    height: window.innerHeight,
  };
};

export const getScrollbarWidth = () => {
  return window.innerWidth - document.documentElement.clientWidth;
};

// Touch event utilities
export const preventPullToRefresh = () => {
  let lastTouchY = 0;
  let maybePreventPullToRefresh = false;

  document.addEventListener('touchstart', (e) => {
    if (e.touches.length !== 1) return;
    lastTouchY = e.touches[0].clientY;
    maybePreventPullToRefresh = window.pageYOffset === 0;
  }, { passive: false });

  document.addEventListener('touchmove', (e) => {
    const touchY = e.touches[0].clientY;
    const touchYDelta = touchY - lastTouchY;
    lastTouchY = touchY;

    if (maybePreventPullToRefresh && touchYDelta > 0) {
      e.preventDefault();
      return;
    }
  }, { passive: false });
};

// Responsive image loading
export const getOptimalImageSize = () => {
  const width = window.innerWidth;
  const dpr = window.devicePixelRatio || 1;
  
  if (width < 640) return Math.round(640 * dpr);
  if (width < 768) return Math.round(768 * dpr);
  if (width < 1024) return Math.round(1024 * dpr);
  return Math.round(1280 * dpr);
};

// Debounce for resize events
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// Throttle for scroll events
export const throttle = <T extends (...args: any[]) => any>(
  func: T,
  limit: number
): ((...args: Parameters<T>) => void) => {
  let inThrottle: boolean;
  
  return (...args: Parameters<T>) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

// Custom hook for responsive behavior
export const useResponsive = () => {
  const [screenSize, setScreenSize] = React.useState(getScreenSize());
  
  React.useEffect(() => {
    const handleResize = debounce(() => {
      setScreenSize(getScreenSize());
    }, 150);
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return {
    isMobile: screenSize === 'mobile',
    isTablet: screenSize === 'tablet',
    isDesktop: ['lg', 'desktop', 'xl'].includes(screenSize),
    screenSize,
  };
};

// PWA install prompt
export const promptPWAInstall = () => {
  let deferredPrompt: any;
  
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
  });
  
  return {
    show: async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        deferredPrompt = null;
        return outcome === 'accepted';
      }
      return false;
    },
  };
};

// Haptic feedback for mobile
export const hapticFeedback = (type: 'light' | 'medium' | 'heavy' = 'light') => {
  if ('vibrate' in navigator) {
    const duration = type === 'light' ? 10 : type === 'medium' ? 20 : 50;
    navigator.vibrate(duration);
  }
};

// React import for hooks
import React from 'react';

export default {
  isMobile,
  isTablet,
  isDesktop,
  isTouchDevice,
  getScreenSize,
  isPortrait,
  isLandscape,
  getSafeAreaInsets,
  prefersReducedMotion,
  prefersDarkMode,
  getConnectionType,
  isSlowConnection,
  supportsWebP,
  supportsServiceWorker,
  getViewportSize,
  getScrollbarWidth,
  preventPullToRefresh,
  getOptimalImageSize,
  debounce,
  throttle,
  useResponsive,
  promptPWAInstall,
  hapticFeedback,
};
