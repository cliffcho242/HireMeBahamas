/**
 * OAuth Configuration Utilities
 * 
 * Utilities for validating and checking OAuth provider configuration.
 */

/**
 * Known placeholder values that should be treated as invalid credentials
 */
const PLACEHOLDER_VALUES = {
  google: ['placeholder-client-id', 'your_google_client_id_here', 'your-google-client-id'],
  apple: ['com.hiremebahamas.signin', 'your_apple_client_id_here', 'your-apple-client-id'],
};

/**
 * Check if a credential value is valid (not empty, not a placeholder)
 * 
 * @param value - The credential value to check
 * @param placeholders - Array of known placeholder values
 * @returns true if the credential is valid, false otherwise
 */
const isValidCredential = (value: string | undefined, placeholders: string[]): boolean => {
  if (!value) return false;
  const trimmedValue = value.trim();
  if (trimmedValue === '') return false;
  if (placeholders.includes(trimmedValue)) return false;
  return true;
};

/**
 * Check if Google OAuth is properly configured
 * 
 * @param clientId - The Google Client ID from environment variables
 * @returns true if Google OAuth is properly configured
 */
export const isGoogleOAuthConfigured = (clientId: string | undefined): boolean => {
  return isValidCredential(clientId, PLACEHOLDER_VALUES.google);
};

/**
 * Check if Apple OAuth is properly configured
 * 
 * @param clientId - The Apple Client ID from environment variables
 * @returns true if Apple OAuth is properly configured
 */
export const isAppleOAuthConfigured = (clientId: string | undefined): boolean => {
  return isValidCredential(clientId, PLACEHOLDER_VALUES.apple);
};

/**
 * Get OAuth configuration status
 * 
 * @returns Object with OAuth provider configuration status
 */
export const getOAuthConfig = () => {
  const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const appleClientId = import.meta.env.VITE_APPLE_CLIENT_ID;
  
  const isGoogleEnabled = isGoogleOAuthConfigured(googleClientId);
  const isAppleEnabled = isAppleOAuthConfigured(appleClientId);
  
  return {
    google: {
      enabled: isGoogleEnabled,
      clientId: isGoogleEnabled ? googleClientId : undefined,
    },
    apple: {
      enabled: isAppleEnabled,
      clientId: isAppleEnabled ? appleClientId : undefined,
    },
    isAnyEnabled: isGoogleEnabled || isAppleEnabled,
  };
};
