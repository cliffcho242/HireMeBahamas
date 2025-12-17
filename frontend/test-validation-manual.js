// Simple manual test for URL validation
// This demonstrates that validation works independently of browser validation

// Allowed URL protocols for security
const ALLOWED_PROTOCOLS = ['http:', 'https:', 'mailto:'];

function isValidUrl(value) {
  // Handle null/undefined
  if (value === null || value === undefined || typeof value !== 'string') {
    return false;
  }

  const trimmedValue = value.trim();
  
  if (trimmedValue === '') {
    return true;
  }

  try {
    const url = new URL(trimmedValue);
    // Check if protocol is in the allowed list
    return ALLOWED_PROTOCOLS.includes(url.protocol);
  } catch {
    return false;
  }
}

console.log('Testing URL validation (manual)...\n');

const tests = [
  ['https://zoom.us/j/123456789', true, 'Valid HTTPS URL'],
  ['http://example.com', true, 'Valid HTTP URL'],
  ['https://meet.google.com/abc', true, 'Valid Google Meet URL'],
  ['mailto:test@example.com', true, 'Valid mailto URL'],
  ['', true, 'Empty string (optional) - trimmed is empty so returns true'],
  ['   ', true, 'Whitespace only (optional) - trimmed is empty so returns true'],
  ['not-a-url', false, 'Invalid: no protocol'],
  ['javascript:alert(1)', false, 'Invalid: dangerous javascript protocol (blocked for security)'],
  ['data:text/html,<script>alert(1)</script>', false, 'Invalid: dangerous data protocol (blocked for security)'],
  ['ftp://example.com', false, 'Invalid: ftp protocol not in allowed list'],
];

let passed = 0;
let failed = 0;

tests.forEach(([input, expected, description]) => {
  const result = isValidUrl(input);
  if (result === expected) {
    console.log(`✓ PASS: ${description}`);
    passed++;
  } else {
    console.log(`✗ FAIL: ${description}`);
    console.log(`  Input: "${input}"`);
    console.log(`  Expected: ${expected}, Got: ${result}`);
    failed++;
  }
});

console.log(`\n${passed} passed, ${failed} failed`);
