# OAuth Authentication Setup Guide

This guide explains how to set up Google and Apple OAuth authentication for HireMeBahamas.

## Features Added

✅ Google Sign-In/Sign-Up on Login and Register pages
✅ Apple Sign-In/Sign-Up on Login and Register pages
✅ Backend OAuth endpoints for both providers
✅ Automatic account creation for new OAuth users
✅ Seamless integration with existing authentication system

## Google OAuth Setup

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Select "Web application"
   - Add authorized JavaScript origins:
     - `http://localhost:5173` (for local development)
     - `https://hiremebahamas.vercel.app` (for production)
     - `https://yourdomain.com` (your custom domain)
   - Add authorized redirect URIs (same as origins)
   - Click "Create"
5. Copy the Client ID

### 2. Configure Frontend

Add to `frontend/.env`:
```bash
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
```

### 3. Configure Backend (Optional)

If you need server-side verification, add to backend `.env`:
```bash
GOOGLE_CLIENT_ID=your_google_client_id_here
```

## Apple Sign-In Setup

### 1. Create Apple Service ID

1. Go to [Apple Developer Portal](https://developer.apple.com/account/resources/)
2. Register an App ID:
   - Identifiers → + → App IDs
   - Description: HireMeBahamas
   - Bundle ID: `com.hiremebahamas.app`
   - Enable "Sign In with Apple"
3. Create a Service ID:
   - Identifiers → + → Services IDs
   - Description: HireMeBahamas Sign In
   - Identifier: `com.hiremebahamas.signin`
   - Enable "Sign In with Apple"
   - Configure:
     - Primary App ID: Select your App ID
     - Domains and Subdomains: `hiremebahamas.vercel.app`, `yourdomain.com`
     - Return URLs: `https://hiremebahamas.vercel.app/auth/apple/callback`

### 2. Configure Frontend

Add to `frontend/.env`:
```bash
VITE_APPLE_CLIENT_ID=com.hiremebahamas.signin
```

### 3. Configure Backend

Add to backend `.env`:
```bash
APPLE_CLIENT_ID=com.hiremebahamas.signin
```

## Environment Variables Summary

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
VITE_APPLE_CLIENT_ID=com.hiremebahamas.signin
```

### Backend (.env)
```bash
GOOGLE_CLIENT_ID=your_google_client_id_here
APPLE_CLIENT_ID=com.hiremebahamas.signin
```

## Testing

### Local Development

1. Start the backend:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. Start the frontend:
```bash
cd frontend
npm run dev
```

3. Navigate to `http://localhost:5173/login` or `http://localhost:5173/register`
4. Click "Continue with Google" or "Sign in with Apple"

### Production

1. Ensure environment variables are set in:
   - Vercel (for frontend): Dashboard → Settings → Environment Variables
   - Railway/Render (for backend): Dashboard → Settings → Environment Variables

2. Deploy both frontend and backend

3. Test OAuth flows on production URLs

## How It Works

### Login Flow

1. User clicks "Continue with Google" or "Sign in with Apple"
2. OAuth provider authenticates user and returns a token
3. Frontend sends token to backend `/api/auth/oauth/google` or `/api/auth/oauth/apple`
4. Backend verifies token with OAuth provider
5. Backend checks if user exists:
   - If yes: Returns existing user with JWT token
   - If no: Creates new user account
6. Frontend stores JWT token and user data
7. User is redirected to home page

### Register Flow

1. User selects account type (Freelancer or Client)
2. User clicks "Sign up with Google" or "Sign up with Apple"
3. OAuth provider authenticates user and returns token
4. Same flow as login, but account type is passed to backend
5. New account is created with selected user type

## Database Changes

The following fields were added to the `users` table:

- `oauth_provider`: String (nullable) - 'google', 'apple', or null
- `oauth_provider_id`: String (nullable) - OAuth provider's user ID
- `hashed_password`: Now nullable for OAuth users

## Security Considerations

✅ Tokens are verified server-side with OAuth providers
✅ No passwords stored for OAuth users
✅ Same authentication flow as regular users after OAuth
✅ JWT tokens used for session management
✅ HTTPS required for production (enforced by OAuth providers)

## Troubleshooting

### Common Error: "Error 401: invalid_client"

**Symptoms:**
- Error message: "Error 401: invalid_client"
- Request details: "flowName=GeneralOAuthFlow"
- Appears when clicking Google Sign-In button

**Root Cause:**
This error occurs when the Google Client ID is not properly configured or is using a placeholder value.

**Solution:**
1. **If you haven't set up Google OAuth yet:**
   - The OAuth buttons will be automatically hidden if credentials are not configured
   - Users can still sign in with email/password
   - Follow the "Google OAuth Setup" section above to enable OAuth

2. **If you have a Google Client ID but still see the error:**
   - Verify your `VITE_GOOGLE_CLIENT_ID` environment variable is set correctly
   - Check that it's not set to `"placeholder-client-id"` or empty string
   - Ensure the Client ID matches your Google Cloud Console configuration
   - For Vercel deployments, add the variable in: Dashboard → Settings → Environment Variables
   - Redeploy your frontend after updating environment variables

3. **Check authorized origins in Google Cloud Console:**
   - Go to Google Cloud Console → APIs & Services → Credentials
   - Select your OAuth 2.0 Client ID
   - Verify these origins are listed:
     - `http://localhost:5173` (for development)
     - `https://yourdomain.com` (your production domain)
   - Authorized redirect URIs should match authorized origins

### Google Sign-In Issues

1. **"popup_closed_by_user"**: User closed the popup, this is normal
2. **"idpiframe_initialization_failed"**: Check that your domain is authorized in Google Console
3. **"access_denied"**: User declined permissions
4. **"invalid_client"**: See detailed solution above

### Apple Sign-In Issues

1. **"popup_closed_by_user"**: User closed the popup, this is normal
2. **"invalid_client"**: Check Service ID configuration in Apple Developer Portal
3. **"unauthorized_client"**: Verify redirect URIs match exactly

### Backend Issues

1. **"Invalid Google token"**: Token verification failed, check Google credentials
2. **"Invalid Apple token"**: Token verification failed, check Apple credentials
3. **"Email not provided"**: OAuth provider didn't return email, check scopes

## Dependencies Installed

### Frontend
- `@react-oauth/google` - Google OAuth React components
- `react-apple-signin-auth` - Apple Sign-In React components
- `jwt-decode` - JWT token decoding utility

### Backend
- `authlib` - OAuth library for Python
- `google-auth` - Google authentication library
- `google-auth-oauthlib` - Google OAuth library
- `PyJWT` - JWT token handling

## Support

For issues or questions:
- Check the troubleshooting section above
- Review OAuth provider documentation
- Check browser console for errors
- Verify environment variables are set correctly
