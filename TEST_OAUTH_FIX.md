# Manual Testing Guide for OAuth Fix

This guide helps verify that the OAuth 401 invalid_client error fix is working correctly.

## What Was Fixed

The application previously showed Google and Apple OAuth buttons even when the credentials were not properly configured, leading to "Error 401: invalid_client" errors. Now, OAuth buttons are automatically hidden when credentials are missing or invalid.

## Test Scenarios

### Scenario 1: OAuth Credentials Not Configured (Default)
**Expected Behavior:** OAuth buttons should be hidden

**Steps:**
1. Ensure `VITE_GOOGLE_CLIENT_ID` and `VITE_APPLE_CLIENT_ID` are not set in environment variables
2. Start the frontend: `cd frontend && npm run dev`
3. Navigate to `/login` and `/register` pages
4. **Verify:** Google and Apple sign-in buttons are NOT visible
5. **Verify:** Only email/password login form and "Use Test Account" button are visible
6. **Verify:** No OAuth-related errors appear in browser console

### Scenario 2: OAuth With Placeholder Values
**Expected Behavior:** OAuth buttons should be hidden (treated as invalid)

**Steps:**
1. Set environment variables with placeholder values:
   ```bash
   export VITE_GOOGLE_CLIENT_ID="placeholder-client-id"
   export VITE_APPLE_CLIENT_ID="com.hiremebahamas.signin"
   ```
2. Start the frontend: `cd frontend && npm run dev`
3. Navigate to `/login` and `/register` pages
4. **Verify:** OAuth buttons are NOT visible (placeholders detected as invalid)
5. **Verify:** No OAuth-related errors in console

### Scenario 3: OAuth With Valid Credentials
**Expected Behavior:** OAuth buttons should be visible and functional

**Steps:**
1. Set environment variables with valid OAuth credentials:
   ```bash
   export VITE_GOOGLE_CLIENT_ID="your-actual-google-client-id"
   export VITE_APPLE_CLIENT_ID="your-actual-apple-client-id"
   ```
2. Start the frontend: `cd frontend && npm run dev`
3. Navigate to `/login` and `/register` pages
4. **Verify:** Google and Apple sign-in buttons ARE visible
5. **Verify:** Divider line "or continue with" is visible
6. **Verify:** Clicking OAuth buttons initiates the OAuth flow (if credentials are valid)

### Scenario 4: Only Google OAuth Configured
**Expected Behavior:** Only Google button visible, Apple hidden

**Steps:**
1. Set only Google credentials:
   ```bash
   export VITE_GOOGLE_CLIENT_ID="your-actual-google-client-id"
   unset VITE_APPLE_CLIENT_ID
   ```
2. Start the frontend
3. Navigate to `/login` and `/register` pages
4. **Verify:** Only Google sign-in button is visible
5. **Verify:** Apple sign-in button is NOT visible
6. **Verify:** Divider line "or continue with" is still visible

### Scenario 5: Only Apple OAuth Configured
**Expected Behavior:** Only Apple button visible, Google hidden

**Steps:**
1. Set only Apple credentials:
   ```bash
   unset VITE_GOOGLE_CLIENT_ID
   export VITE_APPLE_CLIENT_ID="your-actual-apple-client-id"
   ```
2. Start the frontend
3. Navigate to `/login` and `/register` pages
4. **Verify:** Only Apple sign-in button is visible
5. **Verify:** Google sign-in button is NOT visible
6. **Verify:** Divider line "or continue with" is still visible

## Production Testing (Vercel)

### Test on Vercel Deployment
1. Check Vercel environment variables:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Check if `VITE_GOOGLE_CLIENT_ID` and `VITE_APPLE_CLIENT_ID` are set
2. If NOT set or set to placeholder values:
   - OAuth buttons should be hidden on production site
   - Users can still login with email/password
3. If properly set:
   - OAuth buttons should be visible
   - OAuth flow should work correctly

## Validation Checklist

- [ ] OAuth buttons hidden when credentials not set
- [ ] OAuth buttons hidden when using placeholder values
- [ ] OAuth buttons shown when valid credentials are configured
- [ ] No "Error 401: invalid_client" errors when credentials not configured
- [ ] Email/password login always works regardless of OAuth configuration
- [ ] Test Account button always visible on login page
- [ ] UI layout looks good with and without OAuth buttons
- [ ] No console errors related to OAuth when buttons are hidden
- [ ] Divider only shown when at least one OAuth provider is enabled

## How to Check Browser Console

1. Open Developer Tools (F12 or Cmd+Option+I)
2. Go to Console tab
3. Look for any errors containing:
   - "invalid_client"
   - "401"
   - "OAuth"
   - "Google"
   - "Apple"

## Success Criteria

✅ **Fix is successful if:**
- No "Error 401: invalid_client" errors appear when OAuth is not configured
- OAuth buttons automatically hide when credentials are missing or invalid
- Users can still use email/password authentication regardless of OAuth status
- The application gracefully handles missing OAuth configuration

## Files Modified

1. `frontend/src/pages/Login.tsx` - Added OAuth credential validation
2. `frontend/src/pages/Register.tsx` - Added OAuth credential validation
3. `frontend/.env.example` - Improved documentation
4. `OAUTH_SETUP_GUIDE.md` - Added troubleshooting section

## For Developers

To enable OAuth in your local development:
1. Follow the setup guide in `OAUTH_SETUP_GUIDE.md`
2. Get real credentials from Google Cloud Console and Apple Developer Portal
3. Set them in `frontend/.env`:
   ```bash
   VITE_GOOGLE_CLIENT_ID=your_real_google_client_id
   VITE_APPLE_CLIENT_ID=your_real_apple_client_id
   ```
4. Restart the dev server

To disable OAuth (default):
1. Don't set the environment variables, or
2. Comment them out in `.env`, or
3. Delete `.env` file (will use `.env.example` defaults)
