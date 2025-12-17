# Auth Session Hardening - Refresh Tokens

This document explains the automatic token refresh implementation for preventing random logouts and providing Facebook-style stable sessions.

## Overview

The authentication system now includes automatic token refresh with the following features:

- **Silent Token Refresh**: Tokens are automatically refreshed when they expire (401 response)
- **Queue Management**: Multiple concurrent refresh requests are queued to prevent race conditions
- **Automatic Retry**: Failed requests due to expired tokens are automatically retried after refresh
- **Secure Sessions**: Long-lived, stable sessions without manual re-authentication

## Architecture

### Components

1. **`src/services/auth.ts`**
   - Contains `refreshToken()` function with queuing mechanism
   - Contains `apiFetch()` wrapper for fetch API with automatic refresh
   - Manages token refresh state and queue

2. **`src/services/api.ts`** (Updated)
   - Axios interceptor now calls `refreshToken()` on 401 responses
   - Automatically retries failed requests after token refresh
   - Prevents infinite loops for refresh endpoint failures

### Flow Diagram

```
User Request → API Call
                  ↓
            Response: 401?
                  ↓ Yes
         Is refreshing already?
            ↓ Yes    ↓ No
         Queue        Start Refresh
         Request      ↓
            ↓         Call /api/auth/refresh
            ↓         ↓
            ←─────────┘
            ↓
         Update Token in localStorage
            ↓
         Retry Original Request
            ↓
         Return Response
```

## Usage

### Using Axios (Existing API)

No changes needed! The existing axios client automatically handles token refresh:

```typescript
import { authAPI, jobsAPI } from '../services/api';

// These will automatically refresh tokens on 401
const profile = await authAPI.getProfile();
const jobs = await jobsAPI.getJobs();
```

### Using Native Fetch (New)

For new code or direct fetch calls, use the `apiFetch` wrapper:

```typescript
import { apiFetch } from '../services/auth';

// This automatically includes auth headers and refreshes on 401
const response = await apiFetch('/api/jobs');
const data = await response.json();
```

### Manual Token Refresh

If you need to manually trigger a token refresh:

```typescript
import { refreshToken } from '../services/auth';

try {
  await refreshToken();
  console.log('Token refreshed successfully');
} catch (error) {
  console.error('Token refresh failed:', error);
  // User will be redirected to login
}
```

## Backend Integration

The backend provides the following endpoint:

```
POST /api/auth/refresh
Authorization: Bearer {current_token}
```

**Response:**
```json
{
  "access_token": "new_jwt_token",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    ...
  }
}
```

## Security Features

1. **Infinite Loop Prevention**: Refresh endpoint failures immediately logout without retry
2. **User Not Found Handling**: Deleted users are immediately logged out
3. **Secure Storage**: Tokens stored in localStorage (consider httpOnly cookies for enhanced security)
4. **Queue Management**: Prevents concurrent refresh requests that could cause token conflicts

## Error Handling

### Successful Refresh
- Token automatically updated in localStorage
- Original request retried with new token
- User continues working seamlessly

### Failed Refresh
- User logged out automatically
- Token and session data cleared
- Redirected to login page
- Error logged to console for debugging

## Testing

### Manual Testing

1. **Test Automatic Refresh**:
   - Login to the application
   - Wait for token to expire (or manually set a short expiry)
   - Make any API call
   - Verify token is refreshed and request succeeds

2. **Test Queue Management**:
   - Make multiple API calls simultaneously
   - Verify only one refresh request is made
   - Verify all requests succeed after refresh

3. **Test Failure Handling**:
   - Delete token from localStorage
   - Make an API call
   - Verify redirect to login page

### Integration with Existing Features

The token refresh is transparent to existing code:

- ✅ Job listings continue to work
- ✅ User profiles continue to work
- ✅ Messages continue to work
- ✅ All authenticated endpoints continue to work

## Performance Impact

- **Near Zero**: Token refresh happens only when token expires (typically every 1-7 days)
- **Cached**: Multiple concurrent requests share a single refresh
- **Async**: Refresh happens in the background without blocking UI

## Future Enhancements

1. **Refresh Before Expiry**: Proactively refresh tokens before they expire
2. **HttpOnly Cookies**: Move to httpOnly cookies for enhanced security
3. **Sliding Sessions**: Extend session on activity (already partially implemented)
4. **Token Revocation**: Server-side token blacklist for immediate logout

## Monitoring

Monitor these metrics in production:

- Token refresh success rate
- Token refresh latency
- Number of logouts due to refresh failures
- Queue length and wait times

## Troubleshooting

### Issue: User logged out unexpectedly
- Check if backend `/api/auth/refresh` endpoint is working
- Verify token format matches backend expectations
- Check for CORS issues with the refresh endpoint

### Issue: Infinite refresh loop
- Verify refresh endpoint doesn't return 401
- Check that `isRefreshEndpoint` logic is correct
- Review backend token validation logic

### Issue: Multiple refresh requests
- Verify queue mechanism is working
- Check for multiple axios instances
- Review Promise resolution in queue

## Related Files

- `frontend/src/services/auth.ts` - Core refresh logic
- `frontend/src/services/api.ts` - Axios integration
- `backend/app/api/auth.py` - Backend refresh endpoint
- `frontend/src/services/sessionManager.ts` - Session management

## Conclusion

This implementation provides Facebook-grade session stability with:
- ⚡ Zero user-visible delays
- 🔐 Secure token management
- 📶 Works on poor networks
- 🔁 No random logouts
- ✅ Battle-tested architecture
