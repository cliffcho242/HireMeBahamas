Frontend tests and quick checks

This project includes a light Node-based test that verifies the frontend axios interceptor clears the auth token and dispatches an `auth:logout` event when a 401 is encountered. This test is intentionally lightweight so it can run in CI without browser dependencies.

1) Run the Node-based auth-logout test

From the `frontend` folder:

```bash
# install deps (if not already installed)
npm install

# run the auth-logout test
npm run test:auth-logout
```

Expected output on success:

```
TEST PASS: token cleared and auth:logout dispatched
```

2) (Optional) Browser-level test using Playwright Test

If you want to verify the full browser behavior (marker preservation / no hard reload), use the Playwright Test spec in `frontend/playwright-tests/auth-logout.spec.js` and run it with the Playwright Test runner.

Notes:
- Playwright requires OS-level browser dependencies on Linux. Use `npx playwright install-deps` (requires sudo) if running on a fresh machine.
- Typical commands to run Playwright locally:

```bash
cd frontend
npm ci
npx playwright install-deps   # may require sudo
npx playwright install        # download browsers
npx http-server ./dist -p 3000 &
npm run test:playwright
```

3) What the tests check

- The Node test ensures that on a mocked 401 the client removes the `token` from `localStorage` and dispatches a `CustomEvent('auth:logout')`. This verifies the key behavior that prevents full-page reloads.
- The Playwright test (optional) additionally verifies that an in-memory marker survives (no hard reload) when a 401 occurs.

If tests fail, please open an issue or reach out on the PR and include the test output.
