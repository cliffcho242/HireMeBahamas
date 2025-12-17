/**
 * A/B Testing Framework (Lightweight)
 * 
 * Simple client-side A/B testing utility that stores variant assignments
 * in localStorage for persistent user experience across sessions.
 * 
 * Features:
 * - No backend required
 * - No redeploy needed for experiments
 * - Safe rollout with persistent assignment
 * - Works for UI, CTA, and onboarding tests
 * 
 * @example
 * ```tsx
 * import { abVariant } from '@/utils/abTest';
 * 
 * const ctaVariant = abVariant("signup-cta", ["A", "B"]);
 * return ctaVariant === "A" ? (
 *   <button>Join Now</button>
 * ) : (
 *   <button>Get Started</button>
 * );
 * ```
 */

/**
 * Gets or assigns an A/B test variant for a user.
 * The variant is stored in localStorage to ensure consistent
 * experience across sessions.
 * 
 * @param key - Unique identifier for the A/B test (e.g., "signup-cta")
 * @param variants - Array of variant names (e.g., ["A", "B"] or ["control", "variant1", "variant2"])
 * @returns The assigned variant for this user
 * 
 * @example
 * ```tsx
 * // Simple A/B test
 * const variant = abVariant("button-color", ["blue", "green"]);
 * 
 * // Multi-variant test
 * const layout = abVariant("homepage-layout", ["grid", "list", "card"]);
 * ```
 */
export function abVariant(key: string, variants: string[]): string {
  // Validate inputs
  if (!key || typeof key !== 'string') {
    console.warn('abVariant: invalid key provided, using first variant');
    return variants[0] || '';
  }

  if (!Array.isArray(variants) || variants.length === 0) {
    console.warn('abVariant: invalid variants array provided');
    return '';
  }

  // Check if localStorage is available
  if (typeof window === 'undefined' || !window.localStorage) {
    // Fallback for SSR or when localStorage is not available
    return variants[0];
  }

  const storageKey = `ab-${key}`;

  try {
    // Check if user already has an assigned variant
    const stored = localStorage.getItem(storageKey);
    if (stored && variants.includes(stored)) {
      return stored;
    }

    // Assign a random variant
    const choice = variants[Math.floor(Math.random() * variants.length)];
    localStorage.setItem(storageKey, choice);
    return choice;
  } catch (error) {
    // Handle localStorage errors (quota exceeded, privacy mode, etc.)
    console.warn('abVariant: localStorage error, using first variant', error);
    return variants[0];
  }
}

/**
 * Clears a specific A/B test variant assignment.
 * Useful for testing or resetting experiments.
 * 
 * @param key - The A/B test identifier
 * 
 * @example
 * ```tsx
 * clearAbVariant("signup-cta");
 * ```
 */
export function clearAbVariant(key: string): void {
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }

  try {
    localStorage.removeItem(`ab-${key}`);
  } catch (error) {
    console.warn('clearAbVariant: localStorage error', error);
  }
}

/**
 * Gets the current variant assignment without modifying it.
 * Returns null if no variant has been assigned yet.
 * 
 * @param key - The A/B test identifier
 * @returns The assigned variant or null
 * 
 * @example
 * ```tsx
 * const currentVariant = getAbVariant("signup-cta");
 * if (currentVariant) {
 *   console.log(`User is in variant: ${currentVariant}`);
 * }
 * ```
 */
export function getAbVariant(key: string): string | null {
  if (typeof window === 'undefined' || !window.localStorage) {
    return null;
  }

  try {
    return localStorage.getItem(`ab-${key}`);
  } catch (error) {
    console.warn('getAbVariant: localStorage error', error);
    return null;
  }
}

/**
 * Clears all A/B test variant assignments.
 * Useful for development or testing.
 * 
 * @example
 * ```tsx
 * clearAllAbVariants();
 * ```
 */
export function clearAllAbVariants(): void {
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }

  try {
    const keysToRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('ab-')) {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key));
  } catch (error) {
    console.warn('clearAllAbVariants: localStorage error', error);
  }
}
