/**
 * Barrel exports for all page components
 * This enables cleaner imports and better code splitting
 */

// Authentication pages
export { default as Login } from './Login';
export { default as Register } from './Register';

// Main pages
export { default as Home } from './Home';
export { default as LandingPage } from './LandingPage';
export { default as Dashboard } from './Dashboard';
export { default as Profile } from './Profile';

// Job pages
export { default as Jobs } from './Jobs';
export { default as JobDetail } from './JobDetail';
export { default as PostJob } from './PostJob';
export { default as HireMe } from './HireMe';

// Social features
export { default as Messages } from './Messages';
export { default as SendbirdDemo } from './SendbirdDemo';

// User pages
export { default as UserProfile } from './UserProfile';
export { default as UserAnalytics } from './UserAnalytics';
export { default as Users } from './Users';

// Download pages
export { default as Download } from './Download';
export { default as DownloadTest } from './DownloadTest';

// Error pages
export { default as NotFound } from './NotFound';

// Monetization pages
export { default as Pricing } from './Pricing';

// Aliases for components that are referenced differently
// Feed is actually the Home page with the feed
export { default as Feed } from './Home';
// JobPost is actually PostJob
export { default as JobPost } from './PostJob';
