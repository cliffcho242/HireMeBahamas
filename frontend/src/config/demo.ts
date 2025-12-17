/**
 * Demo Mode Configuration
 * 
 * Provides investor-safe demo mode that prevents real data mutation
 * during pitches and demonstrations.
 * 
 * When VITE_DEMO_MODE=true:
 * - All mutations (POST, PUT, DELETE, PATCH) are blocked
 * - Console warnings are logged for skipped mutations
 * - Mock success responses are returned
 * - No accidental writes to real data
 * 
 * @example
 * ```typescript
 * import { DEMO_MODE, isDemoMode, guardMutation } from './config/demo';
 * 
 * // Check if in demo mode
 * if (isDemoMode()) {
 *   console.warn("Demo mode active");
 * }
 * 
 * // Guard a mutation
 * const result = await guardMutation(
 *   () => api.post('/api/posts', data),
 *   { message: "Create post" }
 * );
 * ```
 */

/**
 * Demo mode flag from environment variable
 * Set VITE_DEMO_MODE=true to enable demo/safe mode
 */
export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === "true";

/**
 * Check if application is in demo mode
 * @returns {boolean} True if demo mode is enabled
 */
export function isDemoMode(): boolean {
  return DEMO_MODE;
}

/**
 * Guard a mutation operation in demo mode
 * 
 * If demo mode is active, the mutation is skipped and a mock success
 * response is returned. Otherwise, the mutation is executed normally.
 * 
 * @template T The expected return type of the mutation
 * @param {Function} mutation - The mutation function to guard
 * @param {Object} options - Configuration options
 * @param {string} options.message - Description of the mutation for logging
 * @param {T} options.mockResponse - Optional mock response to return in demo mode
 * @returns {Promise<T>} The mutation result or mock response
 * 
 * @example
 * ```typescript
 * const result = await guardMutation(
 *   () => api.post('/api/posts', postData),
 *   { 
 *     message: "Create post",
 *     mockResponse: { success: true, id: 'demo-123' }
 *   }
 * );
 * ```
 */
export async function guardMutation<T = any>(
  mutation: () => Promise<T>,
  options: {
    message: string;
    mockResponse?: T;
  }
): Promise<T> {
  if (DEMO_MODE) {
    console.warn(`🎤 Demo mode: ${options.message} - mutation skipped`);
    
    // Return mock response if provided, otherwise return generic success
    if (options.mockResponse) {
      return Promise.resolve(options.mockResponse);
    }
    
    // Return a generic success response
    return Promise.resolve({ success: true } as T);
  }
  
  // Not in demo mode, execute the mutation normally
  return mutation();
}

/**
 * Display demo mode status banner in console
 * Call this on app initialization to make demo mode visible
 */
export function logDemoModeStatus(): void {
  if (DEMO_MODE) {
    console.log(
      '%c🎤 DEMO MODE ACTIVE 🎤',
      'background: #ff6b6b; color: white; font-weight: bold; font-size: 16px; padding: 10px; border-radius: 5px;'
    );
    console.log(
      '%cAll mutations are disabled. No data will be modified.',
      'color: #ff6b6b; font-weight: bold; font-size: 12px;'
    );
    console.log(
      '%cPerfect for investor demos and presentations! ✨',
      'color: #51cf66; font-size: 12px;'
    );
  } else {
    console.log(
      '%c✅ Production Mode Active',
      'color: #51cf66; font-weight: bold;'
    );
  }
}

/**
 * Create a demo-safe version of an API object
 * Wraps all mutation methods with demo mode guards
 * 
 * @param {Object} api - The API object to wrap
 * @param {string} apiName - Name of the API for logging
 * @returns {Object} The wrapped API object
 * 
 * @example
 * ```typescript
 * const safeAPI = createDemoSafeAPI(userAPI, 'UserAPI');
 * // All mutations in safeAPI will be guarded automatically
 * ```
 */
export function createDemoSafeAPI<T extends Record<string, any>>(
  api: T,
  apiName: string
): T {
  if (!DEMO_MODE) {
    return api; // Return original API if not in demo mode
  }

  // Create a proxy that intercepts method calls
  return new Proxy(api, {
    get(target, prop) {
      const original = target[prop as keyof T];
      
      // Only wrap functions
      if (typeof original !== 'function') {
        return original;
      }

      // Return wrapped function that guards mutations
      return async (...args: any[]) => {
        // Check if this is a mutation based on method name
        const methodName = String(prop);
        const isMutation = 
          methodName.startsWith('create') ||
          methodName.startsWith('update') ||
          methodName.startsWith('delete') ||
          methodName.startsWith('remove') ||
          methodName.startsWith('post') ||
          methodName.startsWith('put') ||
          methodName.startsWith('patch');

        if (isMutation) {
          console.warn(
            `🎤 Demo mode: ${apiName}.${methodName}() - mutation skipped`
          );
          return { success: true, demo: true };
        }

        // Not a mutation, execute normally
        return original.apply(target, args);
      };
    },
  });
}
