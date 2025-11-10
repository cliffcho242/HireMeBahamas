Frontend tests and quick checks

This project includes Node-based tests that can run in CI without browser dependencies, plus optional Playwright browser tests.

1) Run the Node.js sanity check

This ultra-minimal test validates that Node.js runtime, core modules, and basic file system access are working correctly.

From the `frontend` folder:

```bash
npm run test:node-sanity
```

Expected output on success:

```
✅ Node.js sanity check PASSED
```

2) Run the Node-based auth-logout test

This test verifies the frontend axios interceptor clears the auth token and dispatches an `auth:logout` event when a 401 is encountered.

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

3) (Optional) Browser-level test using Playwright Test

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

4) What the tests check

- The **Node.js sanity check** validates the basic Node.js environment is functioning (runtime, modules, file system, JSON parsing). This runs first in CI to catch environment issues early.
- The **Node auth-logout test** ensures that on a mocked 401 the client removes the `token` from `localStorage` and dispatches a `CustomEvent('auth:logout')`. This verifies the key behavior that prevents full-page reloads.
- The **Playwright test** (optional) additionally verifies that an in-memory marker survives (no hard reload) when a 401 occurs.

If tests fail, please open an issue or reach out on the PR and include the test output.
