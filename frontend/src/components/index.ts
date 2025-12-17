/**
 * Barrel exports for major components
 * This enables cleaner imports and better code splitting
 */

// Layout components
export { default as Navbar } from './Navbar';
export { default as Footer } from './Footer';
export { default as MobileNavigation } from './MobileNavigation';
export { default as ResponsiveLayout } from './ResponsiveLayout';

// Auth components
export { default as AuthGuard } from './AuthGuard';
export { default as ProtectedRoute } from './ProtectedRoute';
export { default as SimpleAuth } from './SimpleAuth';
export { default as FacebookLikeAuth } from './FacebookLikeAuth';
export { default as FacebookLikeAuthFixed } from './FacebookLikeAuthFixed';

// Social components
export { default as PostFeed } from './PostFeed';
export { default as SocialFeed } from './SocialFeed';
export { default as Stories } from './Stories';
export { default as Notifications } from './Notifications';
export { default as Messages } from './Messages';

// Job components
export { default as JobCard } from './JobCard';

// User components
export { default as ProfilePictureGallery } from './ProfilePictureGallery';
export { default as FriendsOnline } from './FriendsOnline';

// Modal components
export { default as CreatePostModal } from './CreatePostModal';
export { default as CreateEventModal } from './CreateEventModal';

// Utility components
export { default as LazyImage } from './LazyImage';
export { default as OptimizedImage } from './OptimizedImage';
export { default as LazyEmojiPicker } from './LazyEmojiPicker';
export { default as InfiniteScroll } from './InfiniteScroll';
export { default as SmartSearchBar } from './SmartSearchBar';
export { default as HireMeTab } from './HireMeTab';

// Dashboard/Analytics components
export { default as AIDashboard } from './AIDashboard';
export { default as FacebookLikeDashboard } from './FacebookLikeDashboard';

// System components
export { default as ConnectionStatus } from './ConnectionStatus';
export { default as InstallPWA } from './InstallPWA';
export { default as ResourceHints } from './ResourceHints';
export { default as EventReminderSystem } from './EventReminderSystem';
export { AIErrorBoundary } from './AIErrorBoundary'; // Named export, not default
export { default as AISystemStatus } from './AISystemStatus';
export { default as QueryErrorBoundary } from './QueryErrorBoundary';
export { default as QueryErrorBoundaryTest } from './QueryErrorBoundaryTest';
export { default as ErrorFallback } from './ErrorFallback';

// Sendbird components
export { default as SendbirdMessages } from './SendbirdMessages';

// Aliases and fallbacks for components that may not exist
// These provide graceful fallbacks for lazy loading
export { default as AnalyticsDashboard } from './AIDashboard';
