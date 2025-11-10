#!/usr/bin/env node
/**
 * Ultra-minimal Node.js sanity test
 * Validates that Node.js is working and basic modules are available
 */

const assert = require('assert');
const fs = require('fs');
const path = require('path');

console.log('Running Node.js sanity check...');
console.log(`Node version: ${process.version}`);
console.log(`Platform: ${process.platform}`);

try {
  // Test 1: Basic Node.js runtime
  assert.ok(typeof process.version === 'string', 'Node version should be available');
  console.log('✓ Node.js runtime working');

  // Test 2: Core modules
  assert.ok(fs.existsSync, 'fs module should be available');
  assert.ok(path.join, 'path module should be available');
  console.log('✓ Core modules available');

  // Test 3: Basic file system access
  const pkgPath = path.join(__dirname, '..', 'package.json');
  assert.ok(fs.existsSync(pkgPath), 'package.json should exist');
  console.log('✓ File system access working');

  // Test 4: JSON parsing
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  assert.ok(pkg.name, 'package.json should have a name field');
  console.log(`✓ JSON parsing working (package: ${pkg.name})`);

  console.log('\n✅ Node.js sanity check PASSED');
  process.exit(0);
} catch (error) {
  console.error('\n❌ Node.js sanity check FAILED:', error.message);
  process.exit(1);
}
