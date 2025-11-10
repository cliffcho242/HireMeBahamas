const fs = require('fs');
const path = require('path');
const assert = require('assert');

function fileContains(relPath, substring) {
  const p = path.join(__dirname, '..', relPath);
  if (!fs.existsSync(p)) {
    throw new Error(`Missing file: ${p}`);
  }
  const txt = fs.readFileSync(p, 'utf8');
  return txt.indexOf(substring) !== -1;
}

try {
  // Check package.json contains playwright test script
  const pkgPath = path.join(__dirname, '..', 'package.json');
  assert.ok(fs.existsSync(pkgPath), 'package.json missing');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  assert.ok(pkg.scripts && pkg.scripts['test:playwright'], 'test:playwright script missing in package.json');

  // Check playwright config file exists and mentions defineConfig
  assert.ok(fileContains('playwright.config.ts', 'defineConfig'), 'playwright.config.ts does not contain defineConfig');

  // Basic check: Playwright tests folder exists and has at least one spec
  const testsDir = path.join(__dirname, '..', 'playwright-tests');
  assert.ok(fs.existsSync(testsDir), 'playwright-tests directory missing');
  const files = fs.readdirSync(testsDir).filter(f => f.endsWith('.js') || f.endsWith('.ts') || f.endsWith('.mjs') || f.endsWith('.cjs'));
  assert.ok(files.length > 0, 'no test files found in playwright-tests');

  console.log('ci-sanity-test: OK');
  process.exit(0);
} catch (err) {
  console.error('ci-sanity-test: FAIL', err && err.message);
  process.exit(2);
}
