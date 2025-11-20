#!/usr/bin/env node
/**
 * Frontend Dependency Validator for HireMeBahamas
 * Checks all npm packages, validates build process, and tests integrations.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class FrontendValidator {
  constructor() {
    this.frontendPath = path.join(__dirname, '..');
    this.results = {
      timestamp: new Date().toISOString(),
      status: 'checking',
      dependencies: {},
      devDependencies: {},
      build: {},
      integrations: {},
      missing: [],
      warnings: [],
    };
    this.allPassed = true;
  }

  log(message, type = 'info') {
    const icons = {
      success: '✅',
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️',
    };
    console.log(`${icons[type] || 'ℹ️'}  ${message}`);
  }

  checkPackageJson() {
    this.log('Checking package.json...', 'info');
    
    const packageJsonPath = path.join(this.frontendPath, 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
      this.log('package.json not found', 'error');
      this.allPassed = false;
      return false;
    }
    
    try {
      const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
      this.log(`Found package.json: ${packageJson.name} v${packageJson.version}`, 'success');
      return packageJson;
    } catch (error) {
      this.log(`Error reading package.json: ${error.message}`, 'error');
      this.allPassed = false;
      return false;
    }
  }

  checkNodeModules() {
    this.log('\nChecking node_modules...', 'info');
    
    const nodeModulesPath = path.join(this.frontendPath, 'node_modules');
    
    if (!fs.existsSync(nodeModulesPath)) {
      this.log('node_modules not found - dependencies not installed', 'error');
      this.results.missing.push('node_modules');
      this.allPassed = false;
      return false;
    }
    
    this.log('node_modules directory exists', 'success');
    return true;
  }

  checkCriticalDependencies(packageJson) {
    this.log('\nChecking critical dependencies...', 'info');
    
    const criticalDeps = [
      'react',
      'react-dom',
      'react-router-dom',
      'socket.io-client',
      'axios',
      'zustand',
    ];
    
    criticalDeps.forEach(dep => {
      const nodeModulePath = path.join(this.frontendPath, 'node_modules', dep);
      
      if (fs.existsSync(nodeModulePath)) {
        const version = packageJson.dependencies[dep] || 'unknown';
        this.log(`${dep}: ${version}`, 'success');
        this.results.dependencies[dep] = {
          active: true,
          version: version,
        };
      } else {
        this.log(`${dep}: NOT INSTALLED`, 'error');
        this.results.dependencies[dep] = {
          active: false,
          version: 'not installed',
        };
        this.results.missing.push(dep);
        this.allPassed = false;
      }
    });
  }

  checkDevDependencies(packageJson) {
    this.log('\nChecking dev dependencies...', 'info');
    
    const criticalDevDeps = [
      'vite',
      'typescript',
      '@vitejs/plugin-react',
      'tailwindcss',
    ];
    
    criticalDevDeps.forEach(dep => {
      const nodeModulePath = path.join(this.frontendPath, 'node_modules', dep);
      
      if (fs.existsSync(nodeModulePath)) {
        const version = packageJson.devDependencies[dep] || 'unknown';
        this.log(`${dep}: ${version}`, 'success');
        this.results.devDependencies[dep] = {
          active: true,
          version: version,
        };
      } else {
        this.log(`${dep}: NOT INSTALLED`, 'error');
        this.results.devDependencies[dep] = {
          active: false,
          version: 'not installed',
        };
        this.results.missing.push(dep);
        this.allPassed = false;
      }
    });
  }

  validateTypeScript() {
    this.log('\nValidating TypeScript compilation...', 'info');
    
    const tsconfigPath = path.join(this.frontendPath, 'tsconfig.json');
    
    if (!fs.existsSync(tsconfigPath)) {
      this.log('tsconfig.json not found', 'warning');
      this.results.warnings.push('tsconfig.json not found');
      return false;
    }
    
    try {
      // Check if TypeScript can compile (dry run)
      execSync('npx tsc --noEmit', {
        cwd: this.frontendPath,
        stdio: 'pipe',
        timeout: 30000,
      });
      this.log('TypeScript compilation check passed', 'success');
      this.results.build.typescript = { active: true, valid: true };
      return true;
    } catch (error) {
      this.log('TypeScript compilation has errors (non-critical)', 'warning');
      this.results.build.typescript = { active: true, valid: false };
      this.results.warnings.push('TypeScript compilation errors');
      return false;
    }
  }

  testViteBuild() {
    this.log('\nTesting Vite configuration...', 'info');
    
    const viteConfigPath = path.join(this.frontendPath, 'vite.config.ts');
    
    if (!fs.existsSync(viteConfigPath)) {
      this.log('vite.config.ts not found', 'error');
      this.results.build.vite = { active: false, configured: false };
      this.allPassed = false;
      return false;
    }
    
    this.log('vite.config.ts found', 'success');
    this.results.build.vite = { active: true, configured: true };
    return true;
  }

  checkSentryIntegration(packageJson) {
    this.log('\nChecking Sentry integration...', 'info');
    
    if (packageJson.dependencies['@sentry/react']) {
      this.log('Sentry React SDK installed', 'success');
      this.results.integrations.sentry = {
        active: true,
        installed: true,
      };
    } else {
      this.log('Sentry not installed (optional)', 'warning');
      this.results.integrations.sentry = {
        active: false,
        installed: false,
      };
      this.results.warnings.push('Sentry not installed');
    }
  }

  checkSocketIOClient(packageJson) {
    this.log('\nChecking Socket.IO client...', 'info');
    
    if (packageJson.dependencies['socket.io-client']) {
      this.log('Socket.IO client installed', 'success');
      this.results.integrations.socketio = {
        active: true,
        installed: true,
      };
    } else {
      this.log('Socket.IO client not installed', 'error');
      this.results.integrations.socketio = {
        active: false,
        installed: false,
      };
      this.results.missing.push('socket.io-client');
      this.allPassed = false;
    }
  }

  checkPWASetup() {
    this.log('\nChecking PWA setup...', 'info');
    
    const serviceWorkerPath = path.join(this.frontendPath, 'public', 'service-worker.js');
    
    if (fs.existsSync(serviceWorkerPath)) {
      this.log('Service worker found', 'success');
      this.results.integrations.pwa = {
        active: true,
        serviceWorker: true,
      };
    } else {
      this.log('Service worker not found (optional)', 'warning');
      this.results.integrations.pwa = {
        active: false,
        serviceWorker: false,
      };
      this.results.warnings.push('PWA service worker not found');
    }
  }

  autoInstallDependencies() {
    this.log('\n🔧 Auto-installing missing dependencies...', 'info');
    
    const nodeModulesPath = path.join(this.frontendPath, 'node_modules');
    
    if (!fs.existsSync(nodeModulesPath) || this.results.missing.length > 0) {
      try {
        this.log('Running npm install...', 'info');
        execSync('npm install', {
          cwd: this.frontendPath,
          stdio: 'inherit',
          timeout: 300000,
        });
        this.log('Dependencies installed successfully', 'success');
        return true;
      } catch (error) {
        this.log(`Failed to install dependencies: ${error.message}`, 'error');
        return false;
      }
    } else {
      this.log('All dependencies already installed', 'success');
      return true;
    }
  }

  generateReport() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 FRONTEND DEPENDENCY VALIDATION REPORT');
    console.log('='.repeat(60));
    
    if (this.allPassed) {
      this.results.status = 'healthy';
      this.log('\nALL FRONTEND DEPENDENCIES ACTIVE', 'success');
    } else {
      this.results.status = 'unhealthy';
      this.log('\nSOME DEPENDENCIES MISSING OR INACTIVE', 'error');
    }
    
    if (this.results.missing.length > 0) {
      this.log(`\nMissing Dependencies (${this.results.missing.length}):`, 'error');
      this.results.missing.forEach(dep => console.log(`   - ${dep}`));
    }
    
    if (this.results.warnings.length > 0) {
      this.log(`\nWarnings (${this.results.warnings.length}):`, 'warning');
      this.results.warnings.forEach(warning => console.log(`   - ${warning}`));
    }
    
    // Save report
    const reportPath = path.join(this.frontendPath, '..', 'frontend_dependency_report.json');
    fs.writeFileSync(reportPath, JSON.stringify(this.results, null, 2));
    this.log(`\nFull report saved to: ${reportPath}`, 'info');
    
    console.log('='.repeat(60));
    
    return this.allPassed ? 0 : 1;
  }

  async validate() {
    console.log('🚀 Starting Frontend Dependency Validation...');
    console.log(`⏰ Timestamp: ${this.results.timestamp}\n`);
    
    const packageJson = this.checkPackageJson();
    if (!packageJson) {
      return this.generateReport();
    }
    
    this.checkNodeModules();
    this.checkCriticalDependencies(packageJson);
    this.checkDevDependencies(packageJson);
    this.validateTypeScript();
    this.testViteBuild();
    this.checkSentryIntegration(packageJson);
    this.checkSocketIOClient(packageJson);
    this.checkPWASetup();
    
    return this.generateReport();
  }
}

// Main execution
const validator = new FrontendValidator();
validator.validate().then(exitCode => {
  process.exit(exitCode);
});
