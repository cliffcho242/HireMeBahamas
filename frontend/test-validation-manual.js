// Simple manual test for URL validation
// This demonstrates that validation works independently of browser validation

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
    new URL(trimmedValue);
    return true;
  } catch {
    return false;
  }
}

console.log('Testing URL validation (manual)...\n');

const tests = [
  ['https://zoom.us/j/123456789', true, 'Valid HTTPS URL'],
  ['http://example.com', true, 'Valid HTTP URL'],
  ['https://meet.google.com/abc', true, 'Valid Google Meet URL'],
  ['', true, 'Empty string (optional) - trimmed is empty so returns true'],
  ['   ', true, 'Whitespace only (optional) - trimmed is empty so returns true'],
  ['not-a-url', false, 'Invalid: no protocol'],
  ['javascript:alert(1)', true, 'Valid URL syntax (but javascript: protocol - should be blocked by other means)'],
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
