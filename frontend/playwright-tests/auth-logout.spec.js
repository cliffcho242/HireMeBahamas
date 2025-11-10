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
    localStorage.setItem('token', 'FAKE_TOKEN_FOR_TEST');
    window.__TEST_MARKER = (window.__TEST_MARKER || 0) + 1;
    window.__TEST_MARKER_VALUE = 'marker_before';
  });

  // Trigger a page flow that will call the API (home)
  await page.goto(DEV_URL + '/', { waitUntil: 'networkidle' });

  // Give app some time to process the 401 and run client-side logic
  await page.waitForTimeout(3000);

  const marker = await page.evaluate(() => window.__TEST_MARKER_VALUE || null);
  const token = await page.evaluate(() => localStorage.getItem('token'));

  expect(marker).toBe('marker_before');
  expect(token).toBeNull();
});
