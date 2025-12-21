/**
 * Environment Configuration
 * 
 * Centralizes environment variable access with proper TypeScript typing.
 * Compatible with Vite and Vercel deployments.
 */

/**
 * Backend API URL
 * 
 * This is the base URL for all API requests.
 * 
 * - For Vercel serverless: Leave VITE_API_URL unset, will use same-origin
 * - For separate backend (Render): Set VITE_API_BASE_URL in environment
 * - For local development: Set VITE_API_URL=http://localhost:8000
 * 
 * @example
 * // Vercel serverless (same-origin)
 * ENV_API = undefined (uses window.location.origin)
 * 
 * @example
 * // Render deployment
 * ENV_API = "https://your-app.onrender.com"
 * 
 * @example
 * // Local development
 * ENV_API = "http://localhost:8000"
 */
export const ENV_API = (import.meta.env.VITE_API_BASE_URL as string | undefined) ||
  (import.meta.env.VITE_API_URL as string | undefined);

/**
 * Socket URL for real-time connections
 * Falls back to API URL if not explicitly set
 */
export const ENV_SOCKET_URL = (import.meta.env.VITE_SOCKET_URL || ENV_API) as string | undefined;

/**
 * Cloudinary cloud name for image uploads
 */
export const ENV_CLOUDINARY_CLOUD_NAME = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME as string | undefined;

/**
 * Sendbird App ID for messaging
 */
export const ENV_SENDBIRD_APP_ID = import.meta.env.VITE_SENDBIRD_APP_ID as string | undefined;

/**
 * Whether to require backend URL to be explicitly set
 * Set to 'true' to enforce VITE_API_URL configuration
 */
export const ENV_REQUIRE_BACKEND_URL = import.meta.env.VITE_REQUIRE_BACKEND_URL === 'true';

/**
 * Google OAuth Client ID
 */
export const ENV_GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

/**
 * Apple OAuth Client ID
 */
export const ENV_APPLE_CLIENT_ID = import.meta.env.VITE_APPLE_CLIENT_ID as string | undefined;

/**
 * Check if app is in development mode
 */
export const isDev = import.meta.env.DEV;

/**
 * Check if app is in production mode
 */
export const isProd = import.meta.env.PROD;

/**
 * Demo mode flag for investor-safe demonstrations
 * When enabled, all mutations are blocked to prevent accidental data changes
 * Set VITE_DEMO_MODE=true to enable
 */
export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';
