import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './playwright-tests',
  timeout: 30 * 1000,
  expect: { timeout: 5000 },
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    headless: true,
    baseURL: process.env.DEV_URL || 'http://localhost:3000',
    viewport: { width: 1280, height: 720 },
    actionTimeout: 0,
    ignoreHTTPSErrors: true,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
