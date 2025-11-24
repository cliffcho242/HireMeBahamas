/**
 * Sendbird Configuration
 * 
 * This file contains the configuration for Sendbird Chat SDK.
 * Make sure to set VITE_SENDBIRD_APP_ID in your .env file.
 */

export const SENDBIRD_CONFIG = {
  appId: import.meta.env.VITE_SENDBIRD_APP_ID || '',
  // Optional: Add custom configurations here
  localCacheEnabled: true,
};

/**
 * Check if Sendbird is properly configured
 */
export const isSendbirdConfigured = (): boolean => {
  return Boolean(SENDBIRD_CONFIG.appId && SENDBIRD_CONFIG.appId !== '');
};

/**
 * Get Sendbird App ID
 */
export const getSendbirdAppId = (): string => {
  if (!isSendbirdConfigured()) {
    console.warn('Sendbird App ID is not configured. Please set VITE_SENDBIRD_APP_ID in your .env file.');
    return '';
  }
  return SENDBIRD_CONFIG.appId;
};
