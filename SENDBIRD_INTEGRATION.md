# Sendbird Integration Instructions

This file contains step-by-step instructions for integrating Sendbird into the HireMeBahamas application.

## Quick Integration (5 minutes)

### Option 1: Add Sendbird Provider to App (Recommended)

1. **Update `App.tsx`** to include the SendbirdProvider:

```tsx
// At the top of App.tsx, add the import:
import { SendbirdProvider } from './contexts/SendbirdContext';

// Then wrap the SocketProvider with SendbirdProvider:
function App() {
  return (
    <AIMonitoringProvider>
      <AIErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <Router>
            <AuthProvider>
              <SendbirdProvider>  {/* Add this */}
                <SocketProvider>
                  <AppContent />
                </SocketProvider>
              </SendbirdProvider>  {/* Add this */}
            </AuthProvider>
          </Router>
        </QueryClientProvider>
      </AIErrorBoundary>
    </AIMonitoringProvider>
  );
}
```

2. **Add Sendbird route** (Optional - for separate Sendbird messages page):

```tsx
// In App.tsx, add the import:
import SendbirdMessages from './components/SendbirdMessages';

// Then add a new route:
<Route
  path="/messages-sendbird"
  element={
    <ProtectedRoute>
      <SendbirdMessages />
    </ProtectedRoute>
  }
/>
```

3. **Configure environment variables**:

```bash
# In frontend/.env file, add:
VITE_SENDBIRD_APP_ID=your_sendbird_app_id_here
```

4. **Restart the development server**:

```bash
cd frontend
npm run dev
```

5. **Access the Sendbird messages page**:

Navigate to `http://localhost:5173/messages-sendbird` (or your dev URL)

### Option 2: Replace Existing Messages Page

If you want to completely replace the existing messaging system:

1. **Update the Messages route in `App.tsx`**:

```tsx
// Change the import at the top:
import Messages from './pages/Messages';  // Old
import SendbirdMessages from './components/SendbirdMessages';  // New

// Then update the route:
<Route
  path="/messages"
  element={
    <ProtectedRoute>
      <SendbirdMessages />  {/* Changed from <Messages /> */}
    </ProtectedRoute>
  }
/>
```

2. **Configure environment variables** (same as Option 1)

3. **Restart and test**

## Connecting Users to Sendbird

To automatically connect users when they log in, update your `AuthContext.tsx`:

```tsx
import { useSendbird } from './SendbirdContext';

// Inside AuthContext component or hook:
const { connect: connectSendbird } = useSendbird();

// After successful login:
useEffect(() => {
  if (user && isAuthenticated) {
    // Connect to Sendbird
    connectSendbird(
      user.id.toString(),
      `${user.first_name} ${user.last_name}`
    ).catch(err => {
      console.error('Failed to connect to Sendbird:', err);
    });
  }
}, [user, isAuthenticated]);
```

## Testing the Integration

1. **Create a Sendbird account**: Visit https://dashboard.sendbird.com/
2. **Create an application**: Click "Create Application" in the dashboard
3. **Copy the App ID**: Found in Settings > Application > App ID
4. **Add to .env**: Set `VITE_SENDBIRD_APP_ID` in `frontend/.env`
5. **Restart server**: `npm run dev`
6. **Test messaging**: 
   - Login with two different accounts in different browsers
   - Start a conversation
   - Send messages back and forth
   - Test real-time updates

## Features You Get

✅ **Real-time messaging** - Messages appear instantly
✅ **Message history** - All messages are persisted in Sendbird
✅ **Typing indicators** - See when others are typing
✅ **Read receipts** - Know when messages are read
✅ **File sharing** - Upload and share files
✅ **Emojis & Reactions** - React to messages with emojis
✅ **Group channels** - Create group conversations
✅ **User presence** - See who's online
✅ **Push notifications** - Get notified of new messages (mobile)
✅ **Message search** - Search through conversation history
✅ **Moderation tools** - Block/report users, filter content

## Customization

### Update Colors

Edit `SendbirdMessages.tsx` to match your brand:

```tsx
colorSet={{
  '--sendbird-light-primary-500': '#2563eb',  // Primary blue
  '--sendbird-light-primary-400': '#3b82f6',  // Hover state
  '--sendbird-light-primary-300': '#60a5fa',  // Active state
}}
```

### Custom Styling

Add custom CSS to override Sendbird styles. See `SENDBIRD_SETUP_GUIDE.md` for examples.

## Production Deployment

1. **Add to Vercel/Railway environment variables**:
   - Go to your deployment dashboard
   - Add `VITE_SENDBIRD_APP_ID` environment variable
   - Redeploy

2. **Configure Sendbird for production**:
   - Set up push notifications (if needed)
   - Configure webhooks (if needed)
   - Set up moderation rules
   - Monitor usage in Sendbird dashboard

## Troubleshooting

**Problem**: "Sendbird Not Configured" error
- **Solution**: Check that `VITE_SENDBIRD_APP_ID` is set in `.env` and restart server

**Problem**: Cannot connect to Sendbird
- **Solution**: Verify App ID is correct, check browser console for errors

**Problem**: Messages not sending
- **Solution**: Check user is logged in, verify network connection, check Sendbird status

For more help, see `SENDBIRD_SETUP_GUIDE.md`

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── SendbirdMessages.tsx       # Main Sendbird UI component
│   ├── contexts/
│   │   └── SendbirdContext.tsx        # Sendbird SDK wrapper
│   ├── config/
│   │   └── sendbird.ts                # Configuration
│   └── ...
└── .env                                # Environment variables
```

## Need Help?

- 📚 Read: `SENDBIRD_SETUP_GUIDE.md` for detailed documentation
- 🔗 Visit: https://sendbird.com/docs for official documentation
- 💬 Ask: Open an issue in the GitHub repository

---

**Note**: Sendbird free tier supports up to 5,000 monthly active users. Review pricing at https://sendbird.com/pricing before scaling to production.
