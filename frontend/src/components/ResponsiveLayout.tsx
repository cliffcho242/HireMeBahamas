import React, { useEffect } from 'react';
import MobileNavigation from './MobileNavigation';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  className?: string;
}

const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ children, className = '' }) => {
  useEffect(() => {
    // Prevent pull-to-refresh on mobile
    let lastTouchY = 0;
    let maybePreventPullToRefresh = false;

    const touchstartHandler = (e: TouchEvent) => {
      if (e.touches.length !== 1) return;
      lastTouchY = e.touches[0].clientY;
      maybePreventPullToRefresh = window.pageYOffset === 0;
    };

    const touchmoveHandler = (e: TouchEvent) => {
      const touchY = e.touches[0].clientY;
      const touchYDelta = touchY - lastTouchY;
      lastTouchY = touchY;

      if (maybePreventPullToRefresh && touchYDelta > 0) {
        e.preventDefault();
      }
    };

    document.addEventListener('touchstart', touchstartHandler, { passive: false });
    document.addEventListener('touchmove', touchmoveHandler, { passive: false });

    // Prevent zoom on double-tap
    let lastTouchEnd = 0;
    const preventZoom = (e: TouchEvent) => {
      const now = Date.now();
      if (now - lastTouchEnd <= 300) {
        e.preventDefault();
      }
      lastTouchEnd = now;
    };
    document.addEventListener('touchend', preventZoom, { passive: false });

    return () => {
      document.removeEventListener('touchstart', touchstartHandler);
      document.removeEventListener('touchmove', touchmoveHandler);
      document.removeEventListener('touchend', preventZoom);
    };
  }, []);

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Mobile Navigation - Only visible on small screens */}
      <MobileNavigation />
      
      {/* Main Content */}
      <main className="pt-14 pb-16 md:pt-0 md:pb-0">
        {children}
      </main>
    </div>
  );
};

export default ResponsiveLayout;
