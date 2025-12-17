/**
 * URL validation utility
 * 
 * This provides client-side validation that doesn't rely on browser-only validation.
 * The validation runs on form submit to ensure URL validity before sending to server.
 * 
 * Security: Only allows safe URL protocols (http, https, mailto) to prevent XSS attacks
 * via javascript:, data:, or vbscript: URLs.
 */

// Allowed URL protocols for security
const ALLOWED_PROTOCOLS = ['http:', 'https:', 'mailto:'];

/**
 * Helper function to check if value is a valid string
 */
const isValidString = (value: unknown): value is string => {
  return typeof value === 'string';
};

/**
 * Validates if a URL string has a safe protocol
 */
const hasAllowedProtocol = (urlString: string): boolean => {
  try {
    const url = new URL(urlString);
    return ALLOWED_PROTOCOLS.includes(url.protocol);
  } catch {
    return false;
  }
};

/**
 * Validates if a string is a valid URL with a safe protocol
 * @param value - The URL string to validate
 * @returns true if valid URL with safe protocol, false otherwise
 */
export const isValidUrl = (value: unknown): boolean => {
  // Validate input is a string
  if (!isValidString(value)) {
    return false;
  }

  // Trim whitespace
  const trimmedValue = value.trim();
  
  // Empty string is considered valid (for optional fields)
  if (trimmedValue === '') {
    return true;
  }

  return hasAllowedProtocol(trimmedValue);
};

/**
 * Validates if a string is a valid URL with a safe protocol and required (non-empty)
 * @param value - The URL string to validate
 * @returns true if valid and non-empty URL with safe protocol, false otherwise
 */
export const isValidRequiredUrl = (value: unknown): boolean => {
  // Validate input is a string
  if (!isValidString(value)) {
    return false;
  }

  const trimmedValue = value.trim();
  
  // Must not be empty
  if (trimmedValue === '') {
    return false;
  }

  return hasAllowedProtocol(trimmedValue);
};
