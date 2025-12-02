import { useEffect, useState, createContext, useContext, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CustomCursor } from './CustomCursor';

// Theme context for dark/light mode
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: 'light',
  toggleTheme: () => {},
  setTheme: () => {},
});

// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = () => useContext(ThemeContext);

interface AppLayoutProps {
  children: React.ReactNode;
  enableCustomCursor?: boolean;
  enableSmoothScroll?: boolean;
  enablePageTransitions?: boolean;
  defaultTheme?: 'light' | 'dark' | 'system';
}

/**
 * Premium AppLayout wrapper that applies global magic:
 * - Glass-morphism + neon gradient theme
 * - Dark/light mode with system preference
 * - Custom cursor on desktop
 * - Smooth scroll (Lenis-like behavior)
 * - Page transitions with blur fade
 * - Pull-to-refresh glow on mobile
 */
export function AppLayout({
  children,
  enableCustomCursor = true,
  enableSmoothScroll = true,
  enablePageTransitions = true,
  defaultTheme = 'system',
}: AppLayoutProps) {
  // Initialize theme state with proper initial value
  const [theme, setThemeState] = useState<'light' | 'dark'>(() => {
    if (typeof window === 'undefined') return 'light';
    
    const stored = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (stored) return stored;
    
    if (defaultTheme === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      return prefersDark ? 'dark' : 'light';
    }
    
    return defaultTheme === 'dark' ? 'dark' : 'light';
  });
  
  const [isPulling, setIsPulling] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('theme')) {
        setThemeState(e.matches ? 'dark' : 'light');
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  const setTheme = useCallback((newTheme: 'light' | 'dark') => {
    setThemeState(newTheme);
  }, []);

  // Smooth scroll enhancement
  useEffect(() => {
    if (!enableSmoothScroll) return;

    // Add smooth scroll class
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Enhanced overscroll behavior
    document.body.style.overscrollBehavior = 'none';

    return () => {
      document.documentElement.style.scrollBehavior = '';
      document.body.style.overscrollBehavior = '';
    };
  }, [enableSmoothScroll]);

  // Pull-to-refresh detection for mobile
  useEffect(() => {
    let startY = 0;
    let currentY = 0;

    const handleTouchStart = (e: TouchEvent) => {
      if (window.scrollY === 0) {
        startY = e.touches[0].clientY;
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (window.scrollY === 0 && startY > 0) {
        currentY = e.touches[0].clientY;
        const distance = currentY - startY;
        
        if (distance > 0) {
          setIsPulling(true);
          setPullDistance(Math.min(distance, 100));
        }
      }
    };

    const handleTouchEnd = () => {
      setIsPulling(false);
      setPullDistance(0);
      startY = 0;
    };

    document.addEventListener('touchstart', handleTouchStart, { passive: true });
    document.addEventListener('touchmove', handleTouchMove, { passive: true });
    document.addEventListener('touchend', handleTouchEnd);

    return () => {
      document.removeEventListener('touchstart', handleTouchStart);
      document.removeEventListener('touchmove', handleTouchMove);
      document.removeEventListener('touchend', handleTouchEnd);
    };
  }, []);

  // Page transition effect - removed to prevent cascading renders
  // Transitions should be triggered by route changes, not by component mount

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {/* Custom cursor for desktop */}
      {enableCustomCursor && (
        <CustomCursor
          enabled={enableCustomCursor}
          color={theme === 'dark' ? 'rgba(0, 212, 255, 0.6)' : 'rgba(99, 102, 241, 0.6)'}
        />
      )}

      {/* Pull-to-refresh glow indicator */}
      <AnimatePresence>
        {isPulling && (
          <motion.div
            className="fixed top-0 inset-x-0 z-[100] h-1"
            initial={{ opacity: 0, scaleX: 0 }}
            animate={{
              opacity: pullDistance / 100,
              scaleX: pullDistance / 100,
              background: 'linear-gradient(90deg, #00d4ff, #a855f7, #ec4899)',
            }}
            exit={{ opacity: 0, scaleX: 0 }}
            style={{ transformOrigin: 'center' }}
          />
        )}
      </AnimatePresence>

      {/* Main content with page transition */}
      <AnimatePresence mode="wait">
        <motion.div
          key="main-content"
          className="min-h-screen"
          initial={enablePageTransitions ? { opacity: 0, filter: 'blur(10px)', scale: 0.98 } : undefined}
          animate={{ opacity: 1, filter: 'blur(0px)', scale: 1 }}
          exit={enablePageTransitions ? { opacity: 0, filter: 'blur(10px)', scale: 0.98 } : undefined}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        >
          {children}
        </motion.div>
      </AnimatePresence>
    </ThemeContext.Provider>
  );
}

/**
 * Theme toggle button component
 */
export function ThemeToggle({ className }: { className?: string }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <motion.button
      className={`p-2 rounded-xl glass-card ${className || ''}`}
      onClick={toggleTheme}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      <motion.div
        initial={false}
        animate={{ rotate: theme === 'dark' ? 180 : 0 }}
        transition={{ duration: 0.3 }}
      >
        {theme === 'light' ? (
          <svg className="w-5 h-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        ) : (
          <svg className="w-5 h-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        )}
      </motion.div>
    </motion.button>
  );
}

export default AppLayout;
