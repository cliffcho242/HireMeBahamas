# Frontend tests — how to run locally

This document explains how to run the fast Node-only sanity tests and the Playwright end-to-end test(s) used by CI.

Quick checklist
- Node 20+ (recommended; Vite and some dev deps require Node >= 20)
- A working internet connection (for installing deps / Playwright browsers)

Run Node-only tests (fast)

```bash
# from repo root
cd frontend
# install node modules from lockfile
npm ci
# run the quick CI sanity test
node ./tests/ci-sanity-test.cjs
# run the Node auth-logout test
node ./tests/auth-logout-node-test.cjs
```

Run Playwright E2E (Chromium)

Notes:
- Playwright needs system libraries on Linux in order to run browser binaries. If Playwright prints a host-deps warning, run `sudo npx playwright install-deps` or install the packages listed in the warning.
- The tests use `DEV_URL` (or the Playwright `baseURL`) to find the app. If you run a dev server on a non-default port, export `DEV_URL`.

Commands

```bash
# from repo root
cd frontend
npm ci
# install system deps helper (may require sudo)
sudo npx playwright install-deps
# install Playwright browsers (Chromium)
npx playwright install chromium

# Build and serve (option A: serve built dist on port 3000)
npm run build
npx http-server ./dist -p 3000

# Run the single spec (adjust DEV_URL if needed)
# Example: DEV_URL=http://localhost:3000 npx playwright test ./playwright-tests/auth-logout.spec.js --project=chromium --reporter=list
npx playwright test ./playwright-tests/auth-logout.spec.js --project=chromium --reporter=list

# Or run the full Playwright test directory
npx playwright test ./playwright-tests --project=chromium
```

If Playwright fails to run Chromium on Linux, inspect the host-deps error message and install the packages it lists (common ones: libnss3, libgbm1, libasound2, libgtk-3-0, libx11-6, libxcomposite1, libxdamage1, libxrandr2).

Debugging tips
- Run `npx playwright show-report` to open the HTML report after a run.
- If a test hangs on `networkidle`, try switching to `domcontentloaded` in the spec or increase timeouts.
- Use `--workers=1` and `--debug` when investigating flakiness:

```bash
npx playwright test ./playwright-tests/auth-logout.spec.js --project=chromium --workers=1 --debug
```

CI notes
- CI uses `npm ci` and downloads Playwright browsers during the job. Ensure your runner image includes the required system packages or call `npx playwright install-deps` early in the job.

Contact
- If you hit an environment-specific error, paste the failing logs and I can help diagnose.

----
Created to document local test runs and to help reproduce the CI steps.
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
