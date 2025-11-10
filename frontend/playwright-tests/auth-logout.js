const { chromium } = require('playwright');

(async () => {
  const DEV_URL = process.env.DEV_URL || 'http://localhost:3000';
  console.log('Starting Playwright test against', DEV_URL);

  try {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    // Install route to mock API responses with 401 for any /api/* request
    await page.route('**/api/**', async (route) => {
      console.log('Intercepted request:', route.request().url());
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Unauthorized (mocked)' }),
      });
    });

    // Navigate to the app and set a test marker and a fake token
    await page.goto(DEV_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });

    await page.evaluate(() => {
      localStorage.setItem('token', 'FAKE_TOKEN_FOR_TEST');
      // marker to detect if page fully reloads
      window.__TEST_MARKER = (window.__TEST_MARKER || 0) + 1;
      window.__TEST_MARKER_VALUE = 'marker_before';
    });

    // Cause the app to fetch posts (navigate to home)
    await page.goto(DEV_URL + '/', { waitUntil: 'networkidle', timeout: 30000 });

    // Wait a bit for interceptor to run and app to process 401
    await page.waitForTimeout(3000);

    const marker = await page.evaluate(() => window.__TEST_MARKER_VALUE || null);
    const token = await page.evaluate(() => localStorage.getItem('token'));

    console.log('Marker after mocked 401:', marker);
    console.log('Token after mocked 401:', token);

    await browser.close();

    if (marker === 'marker_before' && token === null) {
      console.log('TEST PASS: No full reload (marker preserved) and token cleared on 401');
      process.exit(0);
    } else {
      console.error('TEST FAIL: marker=', marker, ' token=', token);
      process.exit(2);
    }
  } catch (err) {
    console.error('Playwright test failed:', err);
    process.exit(3);
  }
})();
