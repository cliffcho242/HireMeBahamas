/**
 * Premium UI Components
 * 
 * A collection of premium, animated UI components for the HireMeBahamas platform.
 * Designed for maximum visual impact while maintaining <80ms LCP on mobile.
 * 
 * Features:
 * - Glass-morphism + soft neon gradient theme
 * - Micro-animations on all interactions
 * - Premium skeleton loaders
 * - Custom cursor for desktop
 * - Mobile bottom sheets and swipe gestures
 * - Avatar rings with status indicators
 * - 3D tilt cards and floating particles
 */

// Main layout wrapper
export { AppLayout, ThemeToggle, useTheme } from './AppLayout';

// Skeleton loaders
export { 
  PremiumSkeleton, 
  PremiumSkeletonCard, 
  PremiumSkeletonFeed 
} from './PremiumSkeleton';

// Animated buttons
export { 
  AnimatedButton, 
  LikeButton, 
  FollowButton 
} from './AnimatedButton';

// Profile components
export { 
  ProfileCard, 
  AvatarRing, 
  VerifiedBadge 
} from './ProfileCard';

// Custom cursor
export { CustomCursor } from './CustomCursor';

// Mobile components
export { 
  BottomSheet, 
  SwipeableItem 
} from './BottomSheet';

// Hero section
export { 
  HeroSection, 
  TiltCard 
} from './HeroSection';
