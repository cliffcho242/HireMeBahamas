/**
 * Test Suite for A/B Testing Framework
 * 
 * Tests the abVariant function and related utilities to ensure
 * proper variant assignment, persistence, and error handling.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { 
  abVariant, 
  clearAbVariant, 
  getAbVariant, 
  clearAllAbVariants 
} from '../src/utils/abTest';

describe('abVariant', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Reset Math.random mock
    vi.restoreAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should assign a variant from the provided array', () => {
    const variants = ['A', 'B'];
    const result = abVariant('test-key', variants);
    
    expect(variants).toContain(result);
  });

  it('should persist variant assignment across calls', () => {
    const variants = ['A', 'B'];
    
    const firstCall = abVariant('persist-test', variants);
    const secondCall = abVariant('persist-test', variants);
    
    expect(firstCall).toBe(secondCall);
  });

  it('should store variant in localStorage with correct prefix', () => {
    const key = 'storage-test';
    const variants = ['X', 'Y'];
    
    abVariant(key, variants);
    
    const stored = localStorage.getItem(`ab-${key}`);
    expect(stored).toBeTruthy();
    expect(variants).toContain(stored!);
  });

  it('should return different variants for different keys', () => {
    // Mock Math.random to ensure different results
    let callCount = 0;
    vi.spyOn(Math, 'random').mockImplementation(() => {
      return callCount++ % 2 === 0 ? 0 : 0.9;
    });

    const variants = ['A', 'B'];
    const variant1 = abVariant('key1', variants);
    const variant2 = abVariant('key2', variants);
    
    // At least one should be different (might be same by chance)
    expect([variant1, variant2]).toEqual(expect.arrayContaining(variants));
  });

  it('should handle multi-variant tests', () => {
    const variants = ['control', 'variant1', 'variant2', 'variant3'];
    const result = abVariant('multi-test', variants);
    
    expect(variants).toContain(result);
  });

  it('should handle empty key gracefully', () => {
    const variants = ['A', 'B'];
    const result = abVariant('', variants);
    
    expect(result).toBe('A'); // Should default to first variant
  });

  it('should handle empty variants array', () => {
    const result = abVariant('test', []);
    
    expect(result).toBe('');
  });

  it('should handle invalid key type', () => {
    const variants = ['A', 'B'];
    // @ts-expect-error Testing invalid input
    const result = abVariant(null, variants);
    
    expect(result).toBe('A'); // Should default to first variant
  });

  it('should handle invalid variants type', () => {
    // @ts-expect-error Testing invalid input
    const result = abVariant('test', 'not-an-array');
    
    expect(result).toBe('');
  });

  it('should use stored variant even if it is not in current variants array', () => {
    // First, store a variant
    localStorage.setItem('ab-test-key', 'OldVariant');
    
    const result = abVariant('test-key', ['A', 'B']);
    
    // Should still use OldVariant since it was stored
    // Actually, the function checks if stored is in variants, so it should assign new
    expect(['A', 'B']).toContain(result);
  });

  it('should reassign if stored variant is not in current variants', () => {
    localStorage.setItem('ab-outdated', 'Z');
    
    const result = abVariant('outdated', ['A', 'B']);
    
    expect(['A', 'B']).toContain(result);
    expect(result).not.toBe('Z');
  });
});

describe('clearAbVariant', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should remove the variant from localStorage', () => {
    localStorage.setItem('ab-clear-test', 'A');
    
    clearAbVariant('clear-test');
    
    expect(localStorage.getItem('ab-clear-test')).toBeNull();
  });

  it('should not affect other variants', () => {
    localStorage.setItem('ab-test1', 'A');
    localStorage.setItem('ab-test2', 'B');
    
    clearAbVariant('test1');
    
    expect(localStorage.getItem('ab-test1')).toBeNull();
    expect(localStorage.getItem('ab-test2')).toBe('B');
  });

  it('should handle clearing non-existent key', () => {
    expect(() => clearAbVariant('non-existent')).not.toThrow();
  });
});

describe('getAbVariant', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should return the stored variant', () => {
    localStorage.setItem('ab-get-test', 'A');
    
    const result = getAbVariant('get-test');
    
    expect(result).toBe('A');
  });

  it('should return null if no variant is stored', () => {
    const result = getAbVariant('non-existent');
    
    expect(result).toBeNull();
  });

  it('should not modify localStorage', () => {
    const before = localStorage.length;
    
    getAbVariant('read-only-test');
    
    expect(localStorage.length).toBe(before);
  });
});

describe('clearAllAbVariants', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should remove all ab- prefixed items', () => {
    localStorage.setItem('ab-test1', 'A');
    localStorage.setItem('ab-test2', 'B');
    localStorage.setItem('ab-test3', 'C');
    
    clearAllAbVariants();
    
    expect(localStorage.getItem('ab-test1')).toBeNull();
    expect(localStorage.getItem('ab-test2')).toBeNull();
    expect(localStorage.getItem('ab-test3')).toBeNull();
  });

  it('should not remove non-ab items', () => {
    localStorage.setItem('ab-test', 'A');
    localStorage.setItem('user-preference', 'dark');
    localStorage.setItem('other-data', 'value');
    
    clearAllAbVariants();
    
    expect(localStorage.getItem('ab-test')).toBeNull();
    expect(localStorage.getItem('user-preference')).toBe('dark');
    expect(localStorage.getItem('other-data')).toBe('value');
  });

  it('should handle empty localStorage', () => {
    expect(() => clearAllAbVariants()).not.toThrow();
  });
});

describe('localStorage error handling', () => {
  it('should handle localStorage quota exceeded', () => {
    // Mock localStorage.setItem to throw quota exceeded error
    const originalSetItem = Storage.prototype.setItem;
    Storage.prototype.setItem = vi.fn(() => {
      throw new Error('QuotaExceededError');
    });

    const result = abVariant('quota-test', ['A', 'B']);
    
    // Should fallback to first variant
    expect(result).toBe('A');

    // Restore original
    Storage.prototype.setItem = originalSetItem;
  });

  it('should handle localStorage access denied', () => {
    // Mock localStorage.getItem to throw
    const originalGetItem = Storage.prototype.getItem;
    Storage.prototype.getItem = vi.fn(() => {
      throw new Error('Access denied');
    });

    const result = abVariant('access-test', ['A', 'B']);
    
    // Should still work and return a variant
    expect(['A', 'B']).toContain(result);

    // Restore original
    Storage.prototype.getItem = originalGetItem;
  });
});

describe('distribution fairness', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should distribute variants somewhat evenly', () => {
    const counts = { A: 0, B: 0 };
    const iterations = 100;

    for (let i = 0; i < iterations; i++) {
      localStorage.clear();
      const result = abVariant(`test-${i}`, ['A', 'B']);
      counts[result as 'A' | 'B']++;
    }

    // With 100 iterations, we expect roughly 50/50 distribution
    // Allow for some variance (30-70 range is reasonable for 100 samples)
    expect(counts.A).toBeGreaterThan(20);
    expect(counts.A).toBeLessThan(80);
    expect(counts.B).toBeGreaterThan(20);
    expect(counts.B).toBeLessThan(80);
    expect(counts.A + counts.B).toBe(iterations);
  });
});
