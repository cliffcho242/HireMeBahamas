# 🎤 Demo Mode / Safe Mode

**Investor-Ready Demo Mode for HireMeBahamas**

## Overview

Demo Mode is a powerful feature that enables **zero-risk demonstrations** of the HireMeBahamas platform. When enabled, all data mutations (create, update, delete operations) are blocked and replaced with mock success responses. This ensures perfect demos during investor pitches, presentations, and product demonstrations without any risk of accidentally modifying real data.

## Features

✅ **Perfect Demos** - Present your platform with confidence  
✅ **No Data Mutations** - All write operations are blocked  
✅ **Mock Responses** - Mutations return realistic success responses  
✅ **Zero Risk** - No accidental writes during presentations  
✅ **Console Warnings** - Clear indicators when mutations are skipped  
✅ **Easy Toggle** - Enable/disable with a single environment variable

## Quick Start

### Enable Demo Mode

1. Add the environment variable to your `.env` file:
   ```bash
   VITE_DEMO_MODE=true
   ```

2. Restart your development server:
   ```bash
   npm run dev
   ```

3. You'll see a prominent console banner indicating demo mode is active:
   ```
   🎤 DEMO MODE ACTIVE 🎤
   All mutations are disabled. No data will be modified.
   Perfect for investor demos and presentations! ✨
   ```

### Disable Demo Mode (Production)

1. Remove or set to false in your `.env` file:
   ```bash
   VITE_DEMO_MODE=false
   ```
   Or simply remove/comment out the line:
   ```bash
   # VITE_DEMO_MODE=true
   ```

2. Restart your server - normal operation resumes

## How It Works

### Architecture

The demo mode implementation uses a **guard pattern** that wraps all mutation operations:

```typescript
import { DEMO_MODE, guardMutation } from './config/demo';

// Example: Creating a post
const createPost = async (postData) => {
  return guardMutation(
    async () => {
      // Real mutation - only executes if demo mode is OFF
      const response = await api.post('/api/posts', postData);
      return response.data;
    },
    {
      message: 'create post',
      mockResponse: { 
        success: true, 
        post_id: 'demo-post-id', 
        ...postData 
      }
    }
  );
};
```

### Protected Operations

All mutation operations are protected in demo mode:

**Authentication**
- ✓ Login
- ✓ Registration
- ✓ Profile updates
- ✓ Password changes
- ✓ OAuth (Google/Apple)

**Jobs**
- ✓ Create job
- ✓ Update job
- ✓ Delete job
- ✓ Apply to job
- ✓ Toggle job status

**Posts & Social**
- ✓ Create post
- ✓ Update post
- ✓ Delete post
- ✓ Like/unlike post
- ✓ Create comment
- ✓ Delete comment

**Messaging**
- ✓ Create conversation
- ✓ Send message
- ✓ Mark as read

**User Interactions**
- ✓ Follow user
- ✓ Unfollow user
- ✓ Upload files
- ✓ Upload profile pictures
- ✓ Update profile settings

**Reviews**
- ✓ Create review
- ✓ Update review
- ✓ Delete review

**Notifications**
- ✓ Mark as read
- ✓ Mark all as read

**Other**
- ✓ Toggle HireMe status
- ✓ All file uploads
- ✓ All delete operations

## Usage Examples

### In Components

```typescript
import { authAPI } from './services/api';

// This will be automatically guarded
async function handleLogin(email, password) {
  try {
    const result = await authAPI.login({ email, password });
    
    // In demo mode: receives mock response
    // In production: receives real response
    console.log('Login result:', result);
  } catch (error) {
    console.error('Login failed:', error);
  }
}
```

### Console Output in Demo Mode

When a mutation is attempted in demo mode:

```
🎤 Demo mode: create post - mutation skipped
Result: { success: true, post_id: 'demo-post-id', content: '...' }
```

### Testing Demo Mode

A test page is available at `frontend/test-demo-mode.html`:

1. Open the file in your browser
2. Click various test buttons
3. Observe console warnings and mock responses
4. No real data is modified

## Configuration

### Environment Variables

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `VITE_DEMO_MODE` | `true` \| `false` | `false` | Enable/disable demo mode |

### Programmatic Access

```typescript
import { DEMO_MODE, isDemoMode } from './config/demo';

// Check if demo mode is active
if (isDemoMode()) {
  console.log('Demo mode is active');
}

// Or use the constant directly
if (DEMO_MODE) {
  console.log('Demo mode is active');
}
```

## Best Practices

### For Investors Demos

1. **Enable demo mode** before the presentation
2. **Test all features** you plan to demonstrate
3. **Prepare sample data** in advance (read operations still work)
4. **Highlight the console warnings** to show the safety mechanism
5. **Disable demo mode** after the demo

### For Development

1. Use demo mode when testing UI flows without affecting data
2. Combine with mock data for realistic demonstrations
3. Test both demo and production modes before releases
4. Document which features are demo-safe

### For QA/Testing

1. Test with demo mode enabled to verify guard behavior
2. Test with demo mode disabled to verify actual mutations
3. Verify console warnings appear correctly
4. Ensure mock responses match expected formats

## Security

✅ **Client-side only** - Demo mode is a frontend feature  
✅ **No backend changes** - Backend still validates and protects data  
✅ **Cannot bypass** - All mutations go through the guard  
✅ **Visible warnings** - Console clearly shows when mutations are blocked  
⚠️ **Not for production** - Disable demo mode in production deployments

## Troubleshooting

### Demo mode not working

1. Check `.env` file has `VITE_DEMO_MODE=true`
2. Restart the development server
3. Clear browser cache
4. Check console for the demo mode banner

### Mutations still executing

1. Verify the environment variable is set correctly
2. Ensure you've imported from the updated `api.ts`
3. Check that the mutation is wrapped in `guardMutation()`

### Console warnings not appearing

1. Check browser console is open
2. Verify console warnings aren't filtered out
3. Ensure demo mode is actually enabled

## API Reference

### `DEMO_MODE`

```typescript
export const DEMO_MODE: boolean
```

Boolean constant indicating if demo mode is active.

### `isDemoMode()`

```typescript
export function isDemoMode(): boolean
```

Returns `true` if demo mode is active, `false` otherwise.

### `guardMutation<T>(mutation, options)`

```typescript
export async function guardMutation<T>(
  mutation: () => Promise<T>,
  options: {
    message: string;
    mockResponse?: T;
  }
): Promise<T>
```

Wraps a mutation operation with demo mode protection.

**Parameters:**
- `mutation`: The async function to execute (only runs if demo mode is off)
- `options.message`: Description of the mutation for logging
- `options.mockResponse`: Optional mock response to return in demo mode

**Returns:** Promise that resolves to either the real response or mock response

### `logDemoModeStatus()`

```typescript
export function logDemoModeStatus(): void
```

Displays a styled console banner showing the current mode status.

### `createDemoSafeAPI<T>(api, apiName)`

```typescript
export function createDemoSafeAPI<T extends Record<string, any>>(
  api: T,
  apiName: string
): T
```

Creates a proxy-wrapped version of an API object that automatically guards mutations.

## Support

For issues or questions about demo mode:
- Check this README first
- Review `frontend/src/config/demo.ts` implementation
- Test with `frontend/test-demo-mode.html`
- Check console for error messages

## Changelog

### v1.0.0 (Current)
- ✅ Initial demo mode implementation
- ✅ All mutations protected
- ✅ Mock response support
- ✅ Console warnings
- ✅ Status logging
- ✅ Test page included
- ✅ Full documentation

## Future Enhancements

Potential improvements for future versions:

- [ ] Demo mode indicator in UI
- [ ] Custom mock data sets
- [ ] Demo mode analytics tracking
- [ ] Recorded demo sessions
- [ ] Demo mode API statistics

---

**Made with ❤️ for perfect investor demos** 🎤✨
