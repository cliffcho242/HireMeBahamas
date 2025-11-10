import { test, expect } from '@playwright/test';

test('auth-logout preserves marker and clears token on 401', async ({ page, baseURL }) => {
  const DEV_URL = process.env.DEV_URL || baseURL || 'http://localhost:3000';

  // Mock any API requests to return 401 Unauthorized
  await page.route('**/api/**', async (route) => {
    await route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Unauthorized (mocked)' }),
    });
  });

  // Navigate and set marker + fake token
  await page.goto(DEV_URL, { waitUntil: 'domcontentloaded' });

  await page.evaluate(() => {
    // persist marker in localStorage so it survives navigation
    localStorage.setItem('token', 'FAKE_TOKEN_FOR_TEST');
    localStorage.setItem('__TEST_MARKER_VALUE', 'marker_before');
  });

  // Trigger a page flow that will call the API (home)
  // Use domcontentloaded instead of networkidle to avoid waiting on long-lived connections
  await page.goto(DEV_URL + '/', { waitUntil: 'domcontentloaded' });

  // Give app some time to process the 401 and run client-side logic
  await page.waitForTimeout(3000);

  const marker = await page.evaluate(() => localStorage.getItem('__TEST_MARKER_VALUE'));
  const token = await page.evaluate(() => localStorage.getItem('token'));

  expect(marker).toBe('marker_before');
  expect(token).toBeNull();
});
