/**
 * Resource Hints Component for Faster Loading
 * 
 * Implements resource hints for better performance:
 * - DNS prefetch for external domains
 * - Preconnect for critical origins
 * - Prefetch for likely next pages
 * - Preload for critical resources
 */
import { useEffect } from 'react';

interface ResourceHintsProps {
  apiOrigin?: string;
  prefetchRoutes?: string[];
}

export function ResourceHints({ apiOrigin, prefetchRoutes = [] }: ResourceHintsProps) {
  useEffect(() => {
    // Add resource hints dynamically
    const head = document.head;

    // DNS Prefetch for external domains
    const externalDomains = [
      'https://fonts.googleapis.com',
      'https://fonts.gstatic.com',
      'https://www.google-analytics.com',
    ];

    externalDomains.forEach(domain => {
      if (!document.querySelector(`link[href="${domain}"][rel="dns-prefetch"]`)) {
        const link = document.createElement('link');
        link.rel = 'dns-prefetch';
        link.href = domain;
        head.appendChild(link);
      }
    });

    // Preconnect to API origin for faster API calls
    if (apiOrigin && !document.querySelector(`link[href="${apiOrigin}"][rel="preconnect"]`)) {
      const link = document.createElement('link');
      link.rel = 'preconnect';
      link.href = apiOrigin;
      link.crossOrigin = 'anonymous';
      head.appendChild(link);
    }

    // Prefetch likely next routes
    prefetchRoutes.forEach(route => {
      if (!document.querySelector(`link[href="${route}"][rel="prefetch"]`)) {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = route;
        link.as = 'document';
        head.appendChild(link);
      }
    });
  }, [apiOrigin, prefetchRoutes]);

  return null; // This component doesn't render anything
}

/**
 * Hook for dynamically adding resource hints based on user navigation
 */
export function useResourceHints() {
  const prefetchRoute = (route: string) => {
    const head = document.head;
    if (!document.querySelector(`link[href="${route}"][rel="prefetch"]`)) {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = route;
      link.as = 'document';
      head.appendChild(link);
    }
  };

  const preloadImage = (src: string) => {
    const head = document.head;
    if (!document.querySelector(`link[href="${src}"][rel="preload"]`)) {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = src;
      link.as = 'image';
      head.appendChild(link);
    }
  };

  const preloadScript = (src: string) => {
    const head = document.head;
    if (!document.querySelector(`link[href="${src}"][rel="preload"]`)) {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = src;
      link.as = 'script';
      head.appendChild(link);
    }
  };

  const preloadFont = (src: string) => {
    const head = document.head;
    if (!document.querySelector(`link[href="${src}"][rel="preload"]`)) {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = src;
      link.as = 'font';
      link.type = 'font/woff2';
      link.crossOrigin = 'anonymous';
      head.appendChild(link);
    }
  };

  return {
    prefetchRoute,
    preloadImage,
    preloadScript,
    preloadFont,
  };
}

/**
 * Preload critical fonts on app startup
 */
export function preloadCriticalFonts() {
  const fonts = [
    '/fonts/inter-var.woff2',
    '/fonts/inter-regular.woff2',
    '/fonts/inter-medium.woff2',
    '/fonts/inter-semibold.woff2',
  ];

  fonts.forEach(font => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = font;
    link.as = 'font';
    link.type = 'font/woff2';
    link.crossOrigin = 'anonymous';
    
    // Only add if font exists (check won't cause error if missing)
    document.head.appendChild(link);
  });
}

/**
 * Intelligent prefetching based on user behavior
 */
export function usePredictivePrefetch() {
  useEffect(() => {
    // Prefetch based on time on page
    const timer = setTimeout(() => {
      // After 3 seconds on homepage, prefetch feed
      if (window.location.pathname === '/') {
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = '/feed';
        link.as = 'document';
        document.head.appendChild(link);
      }
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    // Prefetch on link hover
    const handleLinkHover = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const link = target.closest('a');
      
      if (link && link.href && link.origin === window.location.origin) {
        const prefetchLink = document.createElement('link');
        prefetchLink.rel = 'prefetch';
        prefetchLink.href = link.href;
        prefetchLink.as = 'document';
        
        if (!document.querySelector(`link[href="${link.href}"][rel="prefetch"]`)) {
          document.head.appendChild(prefetchLink);
        }
      }
    };

    // Add hover listener with passive option for better performance
    document.addEventListener('mouseover', handleLinkHover, { passive: true });

    return () => {
      document.removeEventListener('mouseover', handleLinkHover);
    };
  }, []);
}

export default ResourceHints;
