#!/usr/bin/env node

/**
 * Environment Configuration Validator
 * 
 * Validates that all required environment variables are set
 * and properly configured for deployment.
 */

const fs = require('fs');
const path = require('path');

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  bold: '\x1b[1m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function success(message) {
  log(`✅ ${message}`, colors.green);
}

function error(message) {
  log(`❌ ${message}`, colors.red);
}

function warning(message) {
  log(`⚠️  ${message}`, colors.yellow);
}

function info(message) {
  log(`ℹ️  ${message}`, colors.blue);
}

function header(message) {
  log(`\n${'='.repeat(60)}`, colors.bold);
  log(message, colors.bold);
  log('='.repeat(60), colors.bold);
}

// Validation results
let hasErrors = false;
let hasWarnings = false;

// Check if .env file exists
function checkEnvFile() {
  header('Checking .env Configuration');
  
  const envPath = path.join(__dirname, 'frontend', '.env');
  const envExamplePath = path.join(__dirname, 'frontend', '.env.example');
  
  if (!fs.existsSync(envPath)) {
    warning('.env file not found in frontend directory');
    info('This is OK for production (Vercel uses dashboard settings)');
    info('For local development, create .env from .env.example');
    hasWarnings = true;
    return null;
  }
  
  success('.env file found');
  
  // Read .env file
  const envContent = fs.readFileSync(envPath, 'utf-8');
  const envVars = {};
  
  envContent.split('\n').forEach(line => {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#')) {
      const [key, ...valueParts] = trimmed.split('=');
      if (key && valueParts.length > 0) {
        envVars[key.trim()] = valueParts.join('=').trim();
      }
    }
  });
  
  return envVars;
}

// Validate API URL
function validateApiUrl(url, varName) {
  if (!url) {
    error(`${varName} is not set`);
    hasErrors = true;
    return;
  }
  
  // Check if it's a placeholder
  if (url.includes('your_') || url.includes('example.com')) {
    error(`${varName} contains placeholder value: ${url}`);
    info('Replace with actual API URL');
    hasErrors = true;
    return;
  }
  
  // Check if it starts with https:// (required for production)
  if (!url.startsWith('https://') && !url.startsWith('http://localhost')) {
    error(`${varName} must start with https:// in production`);
    info(`Current value: ${url}`);
    hasErrors = true;
    return;
  }
  
  // Check for trailing slash
  if (url.endsWith('/')) {
    warning(`${varName} has trailing slash: ${url}`);
    info('This may cause API routing issues');
    hasWarnings = true;
  }
  
  // Check if URL is reachable (we can't do this synchronously, so just validate format)
  try {
    new URL(url);
    success(`${varName} is properly formatted: ${url}`);
  } catch (e) {
    error(`${varName} is not a valid URL: ${url}`);
    hasErrors = true;
  }
}

// Check required environment variables
function checkRequiredVars(envVars) {
  header('Validating Required Environment Variables');
  
  const requiredVars = [
    {
      name: 'VITE_API_BASE_URL',
      description: 'Backend API base URL',
      example: 'https://hiremebahamas-backend.onrender.com',
    },
  ];
  
  requiredVars.forEach(varConfig => {
    const value = envVars?.[varConfig.name] || process.env[varConfig.name];
    
    if (!value) {
      error(`${varConfig.name} is not set`);
      info(`Description: ${varConfig.description}`);
      info(`Example: ${varConfig.example}`);
      hasErrors = true;
    } else {
      info(`${varConfig.name} is set`);
      
      // Validate API URLs
      if (varConfig.name.includes('API') || varConfig.name.includes('URL')) {
        validateApiUrl(value, varConfig.name);
      }
    }
  });
}

// Check optional environment variables
function checkOptionalVars(envVars) {
  header('Checking Optional Environment Variables');
  
  const optionalVars = [
    {
      name: 'VITE_SENTRY_DSN',
      description: 'Sentry error tracking',
      note: 'Recommended for production',
    },
    {
      name: 'VITE_GOOGLE_CLIENT_ID',
      description: 'Google OAuth sign-in',
      note: 'OAuth buttons hidden if not set',
    },
    {
      name: 'VITE_APPLE_CLIENT_ID',
      description: 'Apple OAuth sign-in',
      note: 'OAuth buttons hidden if not set',
    },
    {
      name: 'VITE_DEMO_MODE',
      description: 'Demo mode (blocks mutations)',
      note: 'Set to true for investor demos',
    },
  ];
  
  optionalVars.forEach(varConfig => {
    const value = envVars?.[varConfig.name] || process.env[varConfig.name];
    
    if (!value) {
      info(`${varConfig.name} is not set`);
      info(`  ${varConfig.note}`);
    } else {
      success(`${varConfig.name} is configured`);
    }
  });
}

// Check vercel.json configuration
function checkVercelConfig() {
  header('Checking Vercel Configuration');
  
  const vercelConfigPath = path.join(__dirname, 'vercel.json');
  
  if (!fs.existsSync(vercelConfigPath)) {
    error('vercel.json not found');
    hasErrors = true;
    return;
  }
  
  success('vercel.json found');
  
  try {
    const vercelConfig = JSON.parse(fs.readFileSync(vercelConfigPath, 'utf-8'));
    
    // Check for rewrites (API proxy)
    if (vercelConfig.rewrites && vercelConfig.rewrites.length > 0) {
      success(`API rewrites configured (${vercelConfig.rewrites.length})`);
      vercelConfig.rewrites.forEach(rewrite => {
        info(`  ${rewrite.source} → ${rewrite.destination}`);
      });
    } else {
      warning('No API rewrites configured');
      info('Frontend will make direct requests to backend');
      hasWarnings = true;
    }
    
    // Check for security headers
    if (vercelConfig.headers && vercelConfig.headers.length > 0) {
      success('Security headers configured');
    } else {
      warning('No security headers configured');
      hasWarnings = true;
    }
    
    // Check build command
    if (vercelConfig.buildCommand) {
      success(`Build command: ${vercelConfig.buildCommand}`);
    }
    
    // Check output directory
    if (vercelConfig.outputDirectory) {
      success(`Output directory: ${vercelConfig.outputDirectory}`);
    }
    
  } catch (e) {
    error(`Error parsing vercel.json: ${e.message}`);
    hasErrors = true;
  }
}

// Check package.json
function checkPackageJson() {
  header('Checking package.json');
  
  const packagePath = path.join(__dirname, 'frontend', 'package.json');
  
  if (!fs.existsSync(packagePath)) {
    error('frontend/package.json not found');
    hasErrors = true;
    return;
  }
  
  try {
    const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf-8'));
    
    // Check scripts
    const requiredScripts = ['dev', 'build', 'preview'];
    requiredScripts.forEach(script => {
      if (pkg.scripts[script]) {
        success(`Script '${script}' configured`);
      } else {
        error(`Script '${script}' missing`);
        hasErrors = true;
      }
    });
    
    // Check dependencies
    const criticalDeps = ['react', 'react-dom', 'react-router-dom', 'vite'];
    criticalDeps.forEach(dep => {
      if (pkg.dependencies[dep] || pkg.devDependencies[dep]) {
        success(`Dependency '${dep}' installed`);
      } else {
        error(`Dependency '${dep}' missing`);
        hasErrors = true;
      }
    });
    
  } catch (e) {
    error(`Error parsing package.json: ${e.message}`);
    hasErrors = true;
  }
}

// Main validation function
function main() {
  log('\n' + '='.repeat(60), colors.bold);
  log('HireMeBahamas - Environment Configuration Validator', colors.bold);
  log('='.repeat(60) + '\n', colors.bold);
  
  const envVars = checkEnvFile();
  checkRequiredVars(envVars);
  checkOptionalVars(envVars);
  checkVercelConfig();
  checkPackageJson();
  
  // Summary
  header('Validation Summary');
  
  if (hasErrors) {
    error('Validation failed with errors');
    info('Fix the errors above before deploying');
    process.exit(1);
  } else if (hasWarnings) {
    warning('Validation completed with warnings');
    info('Review the warnings above');
    info('Deployment should work but may have issues');
    process.exit(0);
  } else {
    success('All checks passed!');
    info('Configuration is ready for deployment');
    process.exit(0);
  }
}

// Run validation
main();
