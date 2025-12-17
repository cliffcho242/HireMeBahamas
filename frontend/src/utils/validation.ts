/**
 * URL validation utility
 * 
 * This provides client-side validation that doesn't rely on browser-only validation.
 * The validation runs on form submit to ensure URL validity before sending to server.
 */

/**
 * Validates if a string is a valid URL
 * @param value - The URL string to validate
 * @returns true if valid URL, false otherwise
 */
export const isValidUrl = (value: string): boolean => {
  // Handle null/undefined
  if (value === null || value === undefined || typeof value !== 'string') {
    return false;
  }

  // Trim whitespace
  const trimmedValue = value.trim();
  
  // Empty string is considered valid (for optional fields)
  if (trimmedValue === '') {
    return true;
  }

  try {
    new URL(trimmedValue);
    return true;
  } catch {
    return false;
  }
};

/**
 * Validates if a string is a valid URL and required (non-empty)
 * @param value - The URL string to validate
 * @returns true if valid and non-empty URL, false otherwise
 */
export const isValidRequiredUrl = (value: string): boolean => {
  // Handle null/undefined
  if (value === null || value === undefined || typeof value !== 'string') {
    return false;
  }

  const trimmedValue = value.trim();
  
  // Must not be empty
  if (trimmedValue === '') {
    return false;
  }

  try {
    new URL(trimmedValue);
    return true;
  } catch {
    return false;
  }
};
