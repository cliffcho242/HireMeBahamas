#!/usr/bin/env node
/**
 * Bundle Size Analyzer for HireMeBahamas
 * Analyzes build output and reports bundle sizes with warnings
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Performance budgets (in KB)
const BUDGETS = {
  vendor: 300,
  ui: 150,
  forms: 100,
  query: 80,
  utils: 50,
  total: 800,
  css: 50
};

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  bold: '\x1b[1m'
};

function formatBytes(bytes) {
  return (bytes / 1024).toFixed(2) + ' KB';
}

function getStatus(size, budget) {
  const percentage = (size / budget) * 100;
  if (percentage <= 80) return { status: 'GOOD', color: colors.green };
  if (percentage <= 100) return { status: 'WARN', color: colors.yellow };
  return { status: 'OVER', color: colors.red };
}

function analyzeBundle() {
  const distPath = path.join(__dirname, '..', 'dist');
  const assetsPath = path.join(distPath, 'assets');

  if (!fs.existsSync(assetsPath)) {
    console.error(`${colors.red}❌ Build directory not found at ${assetsPath}${colors.reset}`);
    console.log('Run "npm run build" first');
    return false;
  }

  console.log(`\n${colors.bold}${colors.blue}📊 Bundle Size Analysis${colors.reset}\n`);

  const files = fs.readdirSync(assetsPath);
  const stats = {
    js: {},
    css: {},
    totalJS: 0,
    totalCSS: 0,
    warnings: []
  };

  // Analyze JavaScript files
  files.forEach(file => {
    const filePath = path.join(assetsPath, file);
    const stat = fs.statSync(filePath);
    const sizeKB = stat.size / 1024;

    if (file.endsWith('.js')) {
      stats.totalJS += sizeKB;
      
      // Categorize chunk
      let category = 'other';
      if (file.includes('vendor')) category = 'vendor';
      else if (file.includes('ui')) category = 'ui';
      else if (file.includes('forms')) category = 'forms';
      else if (file.includes('query')) category = 'query';
      else if (file.includes('utils')) category = 'utils';
      else if (file.includes('index')) category = 'main';
      
      if (!stats.js[category]) stats.js[category] = { files: [], size: 0 };
      stats.js[category].files.push({ name: file, size: sizeKB });
      stats.js[category].size += sizeKB;
    } else if (file.endsWith('.css')) {
      stats.totalCSS += sizeKB;
      stats.css[file] = sizeKB;
    }
  });

  // Report JavaScript bundles
  console.log(`${colors.bold}JavaScript Bundles:${colors.reset}`);
  Object.entries(stats.js).forEach(([category, data]) => {
    const budget = BUDGETS[category] || 100;
    const { status, color } = getStatus(data.size, budget);
    const bar = '█'.repeat(Math.floor((data.size / budget) * 20));
    
    console.log(`  ${color}${category.padEnd(12)}${colors.reset} ${formatBytes(data.size * 1024).padEnd(12)} [${bar}] ${status}`);
    
    if (status !== 'GOOD') {
      stats.warnings.push(`${category} bundle exceeds ${status === 'WARN' ? '80%' : '100%'} of budget`);
    }
  });

  console.log(`\n${colors.bold}CSS Files:${colors.reset}`);
  Object.entries(stats.css).forEach(([file, size]) => {
    const { status, color } = getStatus(size, BUDGETS.css);
    console.log(`  ${color}${file.substring(0, 30).padEnd(32)}${colors.reset} ${formatBytes(size * 1024)}`);
  });

  // Total summary
  console.log(`\n${colors.bold}Summary:${colors.reset}`);
  const totalJSStatus = getStatus(stats.totalJS, BUDGETS.total);
  const totalCSSStatus = getStatus(stats.totalCSS, BUDGETS.css);
  
  console.log(`  Total JS:  ${totalJSStatus.color}${formatBytes(stats.totalJS * 1024).padEnd(12)}${colors.reset} (Budget: ${formatBytes(BUDGETS.total * 1024)})`);
  console.log(`  Total CSS: ${totalCSSStatus.color}${formatBytes(stats.totalCSS * 1024).padEnd(12)}${colors.reset} (Budget: ${formatBytes(BUDGETS.css * 1024)})`);
  console.log(`  Total:     ${colors.bold}${formatBytes((stats.totalJS + stats.totalCSS) * 1024)}${colors.reset}`);

  // Warnings
  if (stats.warnings.length > 0) {
    console.log(`\n${colors.yellow}⚠️  Warnings:${colors.reset}`);
    stats.warnings.forEach(warning => {
      console.log(`  - ${warning}`);
    });
  } else {
    console.log(`\n${colors.green}✅ All bundles within budget!${colors.reset}`);
  }

  // Recommendations
  if (stats.totalJS > BUDGETS.total * 0.8) {
    console.log(`\n${colors.bold}💡 Recommendations:${colors.reset}`);
    console.log('  - Consider code splitting for large features');
    console.log('  - Review and remove unused dependencies');
    console.log('  - Use dynamic imports for heavy components');
    console.log('  - Enable tree-shaking for library imports');
  }

  console.log();

  // Write JSON report
  const reportPath = path.join(distPath, 'bundle-report.json');
  fs.writeFileSync(reportPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    budgets: BUDGETS,
    stats: {
      totalJS: stats.totalJS,
      totalCSS: stats.totalCSS,
      categories: Object.entries(stats.js).map(([name, data]) => ({
        name,
        size: data.size,
        budget: BUDGETS[name] || 100,
        files: data.files.length
      }))
    },
    warnings: stats.warnings
  }, null, 2));

  console.log(`📄 Detailed report saved to: ${reportPath}\n`);

  return stats.warnings.length === 0 && stats.totalJS <= BUDGETS.total;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const success = analyzeBundle();
  process.exit(success ? 0 : 0); // Don't fail build, just warn
}

export { analyzeBundle };
