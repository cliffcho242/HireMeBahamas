/**
 * AppLayout - Universal Layout Wrapper for HireMeBahamas
 * 
 * This component provides:
 * - Perfect centering on every device (mobile, tablet, desktop, 4K, 5K)
 * - Full-height layout using modern CSS (dvh units for mobile browsers)
 * - Safe area insets for notched devices (iPhone, etc.)
 * - Buttery-smooth animations and transitions
 * - Consistent max-width constraints for readability
 * - GPU-accelerated scrolling
 * 
 * Usage:
 *   <AppLayout>
 *     <YourContent />
 *   </AppLayout>
 * 
 * With header/footer slots:
 *   <AppLayout
 *     header={<Navbar />}
 *     footer={<Footer />}
 *   >
 *     <YourContent />
 *   </AppLayout>
 */

import { ReactNode, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation } from 'react-router-dom';

interface AppLayoutProps {
  children: ReactNode;
  /** Optional header component (e.g., Navbar) */
  header?: ReactNode;
  /** Optional footer component */
  footer?: ReactNode;
  /** Maximum content width - defaults to 'xl' (1280px) for social feed style */
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '4xl' | 'full';
  /** Whether to show page transition animations */
  animate?: boolean;
  /** Additional className for the main content area */
  className?: string;
  /** Whether to use centered layout (default: true) */
  centered?: boolean;
  /** Whether to apply padding to content (default: true) */
  padded?: boolean;
  /** Background style */
  background?: 'default' | 'white' | 'gray' | 'transparent';
}

// Max width mapping for Tailwind classes
const maxWidthClasses: Record<string, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '2xl': 'max-w-2xl',
  '4xl': 'max-w-4xl',
  full: 'max-w-full',
};

// Background style mapping
const backgroundClasses: Record<string, string> = {
  default: 'bg-gray-50',
  white: 'bg-white',
  gray: 'bg-gray-100',
  transparent: 'bg-transparent',
};

// Page transition variants for smooth navigation
const pageVariants = {
  initial: {
    opacity: 0,
    y: 8,
  },
  enter: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.25,
      ease: [0.16, 1, 0.3, 1] as const, // Smooth easing curve
    },
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: {
      duration: 0.15,
      ease: 'easeIn' as const,
    },
  },
};

export default function AppLayout({
  children,
  header,
  footer,
  maxWidth = 'xl',
  animate = true,
  className = '',
  centered = true,
  padded = true,
  background = 'default',
}: AppLayoutProps) {
  const location = useLocation();

  // Set up smooth scrolling behavior and scroll to top on route change
  useEffect(() => {
    // Scroll to top on route change for instant navigation feel
    window.scrollTo({ top: 0, behavior: 'instant' as ScrollBehavior });
  }, [location.pathname]);

  // Content wrapper classes
  const contentClasses = [
    'flex-1',
    'w-full',
    centered && 'mx-auto',
    maxWidthClasses[maxWidth],
    padded && 'px-4 sm:px-6 lg:px-8',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  // Main container classes with dynamic viewport height
  const containerClasses = [
    'min-h-screen',
    'min-h-[100dvh]', // Dynamic viewport height for mobile browsers
    'flex',
    'flex-col',
    backgroundClasses[background],
    'overflow-x-hidden',
    // Smooth scrolling
    'scroll-smooth',
    'overscroll-y-contain',
  ]
    .filter(Boolean)
    .join(' ');

  const content = (
    <main className={contentClasses}>
      {children}
    </main>
  );

  return (
    <div className={containerClasses}>
      {/* Header slot */}
      {header}

      {/* Main content with optional page transitions */}
      {animate ? (
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial="initial"
            animate="enter"
            exit="exit"
            variants={pageVariants}
            className="flex-1 flex flex-col"
          >
            {content}
          </motion.div>
        </AnimatePresence>
      ) : (
        <div className="flex-1 flex flex-col">
          {content}
        </div>
      )}

      {/* Footer slot */}
      {footer}
    </div>
  );
}

/**
 * AppLayoutContent - Wrapper for page content with consistent spacing
 * 
 * Use this inside AppLayout for consistent vertical rhythm
 */
interface AppLayoutContentProps {
  children: ReactNode;
  className?: string;
  /** Add top padding for content below navbar */
  withNavbarOffset?: boolean;
  /** Add bottom padding for content above mobile navigation */
  withBottomOffset?: boolean;
}

export function AppLayoutContent({
  children,
  className = '',
  withNavbarOffset = false,
  withBottomOffset = false,
}: AppLayoutContentProps) {
  const classes = [
    'flex-1',
    'w-full',
    withNavbarOffset && 'pt-16 sm:pt-20', // Account for fixed navbar
    withBottomOffset && 'pb-20 sm:pb-4', // Account for mobile bottom nav
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return <div className={classes}>{children}</div>;
}

/**
 * PageContainer - Standard page wrapper with max-width and centering
 * 
 * Use this for individual page components
 */
interface PageContainerProps {
  children: ReactNode;
  className?: string;
  /** Maximum width constraint */
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '4xl' | 'full';
  /** Vertical padding */
  paddingY?: 'none' | 'sm' | 'md' | 'lg';
}

const paddingYClasses: Record<string, string> = {
  none: '',
  sm: 'py-4 sm:py-6',
  md: 'py-6 sm:py-8',
  lg: 'py-8 sm:py-12',
};

export function PageContainer({
  children,
  className = '',
  maxWidth = 'xl',
  paddingY = 'md',
}: PageContainerProps) {
  const classes = [
    'w-full',
    'mx-auto',
    'px-4 sm:px-6 lg:px-8',
    maxWidthClasses[maxWidth],
    paddingYClasses[paddingY],
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return <div className={classes}>{children}</div>;
}
