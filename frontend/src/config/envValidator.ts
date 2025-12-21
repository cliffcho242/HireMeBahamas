/**
 * 8️⃣ VERCEL ENV LOCK (MANDATORY): Environment Variable Validator
 * 
 * This script validates that environment variables are correctly configured
 * according to the VERCEL ENV LOCK mandatory rules.
 * 
 * 🚫 No backend secrets (DATABASE_URL, JWT_SECRET, etc.)
 * 🚫 No DATABASE_URL in Vercel frontend environment
 * 🚫 No localhost URLs in production
 * 
 * See: VERCEL_ENV_LOCK.md for complete documentation
 * 
 * Run this during build time to catch configuration errors early.
 */

import { isValidUrl, isSecureUrl } from '../lib/safeUrl';

interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

/**
 * List of environment variables that should NEVER have VITE_ prefix
 * (these are sensitive and should only be on the backend)
 * 
 * 🚫 VERCEL ENV LOCK (MANDATORY): No backend secrets
 * 
 * NOTE: This list is also defined in verify-env-config.sh for consistency.
 * Keep both lists synchronized when adding new forbidden variables.
 */
const FORBIDDEN_VITE_VARS = [
  'DATABASE_URL',
  'POSTGRES_URL',
  'JWT_SECRET',
  'JWT_SECRET_KEY',
  'SECRET_KEY',
  'PRIVATE_KEY',
  'API_SECRET',
  'DB_PASSWORD',
  'CRON_SECRET',
];

/**
 * List of environment variables that are incorrectly prefixed
 * (wrong framework)
 */
const WRONG_PREFIX_VARS = [
  'NEXT_PUBLIC_API_URL',
  'NEXT_PUBLIC_BACKEND_URL',
  'NEXT_PUBLIC_SOCKET_URL',
];

/**
 * Validate that environment variables follow the FOREVER FIX law
 */
export function validateEnvironmentVariables(): ValidationResult {
  const result: ValidationResult = {
    valid: true,
    errors: [],
    warnings: [],
  };

  console.log('\n🔍 Validating environment variables...\n');

  // Check for forbidden variables with VITE_ prefix
  FORBIDDEN_VITE_VARS.forEach(forbiddenVar => {
    const viteVar = `VITE_${forbiddenVar}`;
    if (import.meta.env[viteVar] !== undefined) {
      result.valid = false;
      result.errors.push(
        `❌ CRITICAL SECURITY ERROR: ${viteVar} is exposed to the frontend!\n` +
        `   🚫 VERCEL ENV LOCK VIOLATION: No backend secrets with VITE_ prefix\n` +
        `   This is a sensitive variable that should NEVER have VITE_ prefix.\n` +
        `   Remove this from your environment variables immediately.\n` +
        `   See VERCEL_ENV_LOCK.md for mandatory security rules.`
      );
    }
  });

  // Check for wrong framework prefix
  WRONG_PREFIX_VARS.forEach(wrongVar => {
    const value = import.meta.env[wrongVar];
    if (value !== undefined) {
      result.valid = false;
      result.errors.push(
        `❌ WRONG FRAMEWORK PREFIX: ${wrongVar}\n` +
        `   This is a Next.js variable name. This is a VITE project.\n` +
        `   Use VITE_API_URL instead of NEXT_PUBLIC_API_URL`
      );
    }
  });

  // Warn about unprefixed variables (these won't work)
  Object.keys(import.meta.env).forEach(key => {
    // Check if someone tried to use an unprefixed variable
    // Skip Vite's built-in environment variables
    const isBuiltIn = ['BASE_URL', 'MODE', 'DEV', 'PROD', 'SSR'].includes(key);
    
    if (!key.startsWith('VITE_') && !isBuiltIn) {
      result.warnings.push(
        `⚠️  WARNING: Found unprefixed variable: ${key}\n` +
        `   This variable won't be exposed to the frontend in production.\n` +
        `   If this is meant for the frontend, add VITE_ prefix.`
      );
    }
  });

  // Check for required variables
  // API URL is optional (can use same-origin for Vercel serverless)
  // But if VITE_REQUIRE_BACKEND_URL is true, then it's required
  if (import.meta.env.VITE_REQUIRE_BACKEND_URL === 'true') {
    if (!import.meta.env.VITE_API_URL) {
      result.errors.push(
        `❌ MISSING REQUIRED VARIABLE: VITE_API_URL\n` +
        `   VITE_REQUIRE_BACKEND_URL is set to 'true', but VITE_API_URL is not set.\n` +
        `   Either set VITE_API_URL or set VITE_REQUIRE_BACKEND_URL to 'false'.`
      );
      result.valid = false;
    }
  }

  // Validate API URL format if set
  if (import.meta.env.VITE_API_URL) {
    const apiUrl = import.meta.env.VITE_API_URL;
    
    // Check if it's a valid URL
    if (!isValidUrl(apiUrl)) {
      result.valid = false;
      result.errors.push(
        `❌ INVALID URL FORMAT: VITE_API_URL="${apiUrl}"\n` +
        `   URL must start with http:// or https://\n` +
        `   Example: VITE_API_URL=https://api.yourdomain.com`
      );
    } else {
      const lowerApiUrl = apiUrl.toLowerCase();
      const hostname = new URL(apiUrl).hostname.toLowerCase();
      if (hostname.includes('railway.app')) {
        result.valid = false;
        result.errors.push(
          `❌ INVALID BACKEND TARGET: VITE_API_URL points to Railway ("${apiUrl}")\n` +
          `   Render backend is required. Update to: https://your-backend.onrender.com`
        );
      }
      // 🚫 VERCEL ENV LOCK: No localhost in production
      const isLocalhost = apiUrl.includes('localhost') || apiUrl.includes('127.0.0.1');
      if (isLocalhost && import.meta.env.PROD) {
        result.valid = false;
        result.errors.push(
          `❌ LOCALHOST URL IN PRODUCTION: VITE_API_URL="${apiUrl}"\n` +
          `   🚫 VERCEL ENV LOCK VIOLATION: No localhost URLs in production\n` +
          `   Production users cannot access your local development server.\n` +
          `   Change to: VITE_API_URL=https://your-backend.onrender.com`
        );
      } else if (!isSecureUrl(apiUrl)) {
        // Check if using HTTPS in production
        result.valid = false;
        result.errors.push(
          `❌ INSECURE URL IN PRODUCTION: VITE_API_URL="${apiUrl}"\n` +
          `   Production deployments must use HTTPS.\n` +
          `   HTTP is only allowed for localhost in development.\n` +
          `   Change to: VITE_API_URL=https://your-domain.com`
        );
      } else if (import.meta.env.PROD && !lowerApiUrl.includes('onrender.com')) {
        result.valid = false;
        result.errors.push(
          `❌ INVALID BACKEND TARGET: VITE_API_URL="${apiUrl}"\n` +
          `   Frontend is locked to Render backend. Set to your Render URL (e.g., https://your-backend.onrender.com).`
        );
      }
    }
  }

  // Validate Socket URL if set
  if (import.meta.env.VITE_SOCKET_URL) {
    const socketUrl = import.meta.env.VITE_SOCKET_URL;
    
    if (!isValidUrl(socketUrl)) {
      result.valid = false;
      result.errors.push(
        `❌ INVALID URL FORMAT: VITE_SOCKET_URL="${socketUrl}"\n` +
        `   URL must start with http:// or https://`
      );
    } else if (!isSecureUrl(socketUrl)) {
      result.valid = false;
      result.errors.push(
        `❌ INSECURE URL IN PRODUCTION: VITE_SOCKET_URL="${socketUrl}"\n` +
        `   Production deployments must use HTTPS.`
      );
    }
  }

  // Report results
  if (result.errors.length > 0) {
    console.error('❌ Environment Variable Validation FAILED\n');
    result.errors.forEach(error => console.error(error + '\n'));
  }

  if (result.warnings.length > 0) {
    console.warn('⚠️  Environment Variable Warnings:\n');
    result.warnings.forEach(warning => console.warn(warning + '\n'));
  }

  if (result.valid && result.errors.length === 0) {
    console.log('✅ Environment variables validated successfully!\n');
    
    // Show what variables are configured
    console.log('📋 Configured frontend variables:');
    Object.keys(import.meta.env).forEach(key => {
      if (key.startsWith('VITE_')) {
        // Mask sensitive values
        const value = import.meta.env[key];
        const displayValue = typeof value === 'string' && value.length > 20
          ? value.substring(0, 20) + '...'
          : value;
        console.log(`   ✓ ${key} = ${displayValue}`);
      }
    });
    console.log('');
  }

  return result;
}

/**
 * Environment mode constants
 */
const ENV_MODE = {
  TEST: 'test',
  PRODUCTION: 'production',
  DEVELOPMENT: 'development',
} as const;

/**
 * Run validation immediately when this module is imported
 * This ensures validation happens during build time
 */
if (import.meta.env.MODE !== ENV_MODE.TEST) {
  const result = validateEnvironmentVariables();
  
  // In production builds, fail if validation fails
  if (!result.valid && import.meta.env.PROD) {
    throw new Error(
      '8️⃣ VERCEL ENV LOCK VIOLATION: Environment variable validation failed.\n' +
      'Check the errors above.\n\n' +
      '📖 See VERCEL_ENV_LOCK.md for mandatory configuration rules.\n' +
      '📖 See FOREVER_FIX_ENV_VARIABLES.md for detailed guidance.'
    );
  }
}

export default validateEnvironmentVariables;
