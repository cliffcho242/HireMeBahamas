/**
 * Test Suite for Safe URL Builder
 * 
 * Tests the URL validation and parsing utilities to ensure
 * they prevent the "pattern mismatch" errors in production.
 */

import { describe, it, expect } from 'vitest';
import {
  safeParseUrl,
  isValidUrl,
} from '../src/lib/safeUrl';

describe('safeParseUrl', () => {
  it('should successfully parse valid HTTPS URL', () => {
    const result = safeParseUrl('https://api.example.com/api/users');
    expect(result.success).toBe(true);
    expect(result.url).toBeDefined();
    expect(result.url?.protocol).toBe('https:');
    expect(result.url?.hostname).toBe('api.example.com');
  });

  it('should fail for undefined URL', () => {
    const result = safeParseUrl(undefined);
    expect(result.success).toBe(false);
    expect(result.error).toContain('undefined');
  });

  it('should prevent the "pattern mismatch" error scenario', () => {
    // This is the exact scenario that caused the original error
    const undefinedUrl = undefined;
    const result = safeParseUrl(undefinedUrl, 'API Request');
    
    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
    expect(result.error).toContain('undefined');
  });
});

describe('isValidUrl', () => {
  it('should return true for valid HTTPS URL', () => {
    expect(isValidUrl('https://api.example.com')).toBe(true);
  });

  it('should return false for undefined', () => {
    expect(isValidUrl(undefined)).toBe(false);
  });

  it('should return false for URL without protocol', () => {
    expect(isValidUrl('api.example.com')).toBe(false);
  });
});
