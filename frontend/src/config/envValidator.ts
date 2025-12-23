/**
 * Production environment validator for Vercel builds.
 * Fails fast when required variables are missing or insecure.
 */

import { isSecureUrl, isValidUrl } from '../lib/safeUrl';

interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

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

const WRONG_PREFIX_VARS = [
  'NEXT_PUBLIC_API_URL',
  'NEXT_PUBLIC_BACKEND_URL',
  'NEXT_PUBLIC_SOCKET_URL',
];

export function validateEnvironmentVariables(): ValidationResult {
  const result: ValidationResult = {
    valid: true,
    errors: [],
    warnings: [],
  };

  console.log('\n🔍 Validating environment variables...\n');

  FORBIDDEN_VITE_VARS.forEach((forbiddenVar) => {
    const viteVar = `VITE_${forbiddenVar}`;
    if (import.meta.env[viteVar] !== undefined) {
      result.valid = false;
      result.errors.push(
        `❌ CRITICAL SECURITY ERROR: ${viteVar} is exposed to the frontend!\n` +
          `   Remove this from your environment variables immediately.`,
      );
    }
  });

  WRONG_PREFIX_VARS.forEach((wrongVar) => {
    const value = import.meta.env[wrongVar];
    if (value !== undefined) {
      result.valid = false;
      result.errors.push(
        `❌ WRONG FRAMEWORK PREFIX: ${wrongVar}\n` +
          `   This is a Vite project. Use VITE_API_BASE_URL instead.`,
      );
    }
  });

  Object.keys(import.meta.env).forEach((key) => {
    const isBuiltIn = ['BASE_URL', 'MODE', 'DEV', 'PROD', 'SSR'].includes(key);
    if (!key.startsWith('VITE_') && !isBuiltIn) {
      result.warnings.push(
        `⚠️  WARNING: Found unprefixed variable: ${key}\n` +
          `   If this is meant for the frontend, add VITE_ prefix.`,
      );
    }
  });

  const apiUrl = import.meta.env.VITE_API_BASE_URL;
  const apiVarName = 'VITE_API_BASE_URL';

  if (!apiUrl) {
    result.valid = false;
    result.errors.push(
      `❌ MISSING REQUIRED VARIABLE: ${apiVarName}\n` +
        `   Set ${apiVarName}=https://hiremebahamas-backend.onrender.com`,
    );
  } else {
    if (!isValidUrl(apiUrl)) {
      result.valid = false;
      result.errors.push(
        `❌ INVALID URL FORMAT: ${apiVarName}="${apiUrl}"\n` +
          `   URL must start with https://`,
      );
    } else {
      const hostname = new URL(apiUrl).hostname.toLowerCase();
      const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';
      if (!apiUrl.startsWith('https://') || isLocalhost) {
        result.valid = false;
        result.errors.push(
          `❌ VITE_API_BASE_URL must be HTTPS and non-localhost (found "${apiUrl}")`,
        );
      }
      if (apiUrl.endsWith('/')) {
        result.valid = false;
        result.errors.push(
          `❌ Do NOT include trailing slash in ${apiVarName} (received "${apiUrl}")`,
        );
      }
    }
  }

  if (import.meta.env.VITE_SOCKET_URL) {
    const socketUrl = import.meta.env.VITE_SOCKET_URL;
    if (!isValidUrl(socketUrl)) {
      result.valid = false;
      result.errors.push(
        `❌ INVALID URL FORMAT: VITE_SOCKET_URL="${socketUrl}"\n` +
          `   URL must start with http:// or https://`,
      );
    } else if (!isSecureUrl(socketUrl)) {
      result.valid = false;
      result.errors.push(
        `❌ INSECURE URL IN PRODUCTION: VITE_SOCKET_URL="${socketUrl}"\n` +
          `   Production deployments must use HTTPS.`,
      );
    }
  }

  if (result.errors.length > 0) {
    console.error('❌ Environment Variable Validation FAILED\n');
    result.errors.forEach((error) => console.error(error + '\n'));
  }

  if (result.warnings.length > 0) {
    console.warn('⚠️  Environment Variable Warnings:\n');
    result.warnings.forEach((warning) => console.warn(warning + '\n'));
  }

  if (result.valid && result.errors.length === 0) {
    console.log('✅ Environment variables validated successfully!\n');
    console.log('📋 Configured frontend variables:');
    Object.keys(import.meta.env).forEach((key) => {
      if (key.startsWith('VITE_')) {
        const value = import.meta.env[key];
        const displayValue =
          typeof value === 'string' && value.length > 20 ? value.substring(0, 20) + '...' : value;
        console.log(`   ✓ ${key} = ${displayValue}`);
      }
    });
    console.log('');
  }

  return result;
}

const ENV_MODE = {
  TEST: 'test',
  PRODUCTION: 'production',
  DEVELOPMENT: 'development',
} as const;

if (import.meta.env.MODE !== ENV_MODE.TEST) {
  const result = validateEnvironmentVariables();
  if (!result.valid && import.meta.env.PROD) {
    console.error(
      '⚠️  Environment variable validation failed for production build.\n' +
        'The app will attempt to render but some features may not work.\n' +
        'Check the errors above and contact the site administrator if issues persist.',
    );
    if (typeof window !== 'undefined') {
      (window as any).__HIREME_ENV_INVALID__ = true;
    }
    // Don't throw - just log the errors and let the app try to render
  }
}

export default validateEnvironmentVariables;
