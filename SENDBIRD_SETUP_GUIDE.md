# Sendbird Integration Guide for HireMeBahamas

This guide explains how to set up and use Sendbird Chat in the HireMeBahamas platform.

## What is Sendbird?

Sendbird is a powerful chat SDK that provides:
- **Real-time messaging** with low latency
- **Group channels** for team discussions
- **One-on-one conversations** between users
- **Message history** and persistence
- **Typing indicators** and read receipts
- **File sharing** and rich media support
- **Push notifications** for mobile apps
- **Moderation tools** for community management

## Installation

The Sendbird SDK has been installed with the following packages:

```bash
npm install @sendbird/uikit-react@3.17.3 @sendbird/chat@4.16.3
```

## Configuration

### Step 1: Create a Sendbird Account

1. Visit [Sendbird Dashboard](https://dashboard.sendbird.com/)
2. Sign up for a free account
3. Create a new application

### Step 2: Get Your Application ID

1. In the Sendbird Dashboard, go to your application
2. Copy the **Application ID** from the application settings
3. The Application ID looks like: `ABCDEF12-3456-7890-ABCD-EF1234567890`

### Step 3: Configure Environment Variables

Add your Sendbird Application ID to your environment configuration:

**Frontend (.env file):**
```bash
# Copy .env.example to .env if you haven't already
cp frontend/.env.example frontend/.env

# Edit the .env file and add your Sendbird App ID
VITE_SENDBIRD_APP_ID=your_sendbird_app_id_here
```

### Step 4: Restart Development Server

After adding the environment variable, restart your development server:

```bash
cd frontend
npm run dev
```

## Usage

### Using Sendbird Messages Component

The `SendbirdMessages` component provides a complete messaging interface:

```tsx
import SendbirdMessages from '../components/SendbirdMessages';

// In your routing or component
<SendbirdMessages />
```

### Using Sendbird Context (Advanced)

For more control, you can use the `SendbirdContext`:

```tsx
import { useSendbird } from '../contexts/SendbirdContext';

function MyComponent() {
  const { 
    sdk, 
    currentUser, 
    isConnected, 
    connect, 
    disconnect 
  } = useSendbird();

  useEffect(() => {
    if (user && !isConnected) {
      connect(user.id.toString(), `${user.first_name} ${user.last_name}`);
    }
  }, [user, isConnected]);

  // Use sdk to interact with Sendbird API
}
```

## Integration Options

### Option 1: Replace Existing Messages (Recommended)

Replace the existing custom messaging system with Sendbird:

1. Update the routing in `App.tsx` to use `SendbirdMessages` instead of `Messages`
2. Users will get a more robust messaging experience
3. All message data will be stored in Sendbird's cloud

### Option 2: Hybrid Approach

Keep both messaging systems and let users choose:

1. Add a settings option to switch between systems
2. Keep existing backend for basic messaging
3. Use Sendbird for advanced features

### Option 3: Feature-Specific Integration

Use Sendbird for specific features:

1. Keep existing 1-on-1 messages
2. Use Sendbird for group chats or channels
3. Use Sendbird for professional communities

## Features Provided by Sendbird UIKit

The `@sendbird/uikit-react` package provides:

### Channel List
- List of all conversations
- Unread message counts
- Last message preview
- User presence indicators

### Conversation View
- Message thread display
- Real-time message updates
- Typing indicators
- Read receipts
- File upload support
- Emoji reactions

### User Settings
- Profile customization
- Notification preferences
- Theme options

## Customization

### Theming

You can customize Sendbird's appearance by modifying the `colorSet` in `SendbirdMessages.tsx`:

```tsx
<SendbirdApp
  appId={appId}
  userId={userId}
  nickname={nickname}
  theme="light"  // or "dark"
  colorSet={{
    '--sendbird-light-primary-500': '#2563eb',  // Your brand color
    '--sendbird-light-primary-400': '#3b82f6',
    '--sendbird-light-primary-300': '#60a5fa',
  }}
/>
```

### Custom Styles

Add custom CSS to match your brand:

```css
/* In your component or global styles */
.sendbird-conversation__messages {
  background-color: #f9fafb;
}

.sendbird-message-content {
  border-radius: 1rem;
}
```

## User Synchronization

Sendbird users are automatically created when they first connect. To synchronize user data:

1. When a user logs in to HireMeBahamas, connect them to Sendbird
2. Use the user's ID from your database as the Sendbird user ID
3. Set their name as the nickname in Sendbird

Example:
```tsx
await connect(user.id.toString(), `${user.first_name} ${user.last_name}`);
```

## Production Considerations

### Pricing

- **Free Tier**: Up to 5,000 monthly active users
- **Paid Plans**: Scale based on usage
- Check [Sendbird Pricing](https://sendbird.com/pricing) for details

### Security

1. **API Tokens**: Use session tokens for authentication
2. **Access Control**: Configure user permissions in Sendbird Dashboard
3. **Moderation**: Set up automated moderation rules

### Performance

1. Sendbird handles message storage and delivery
2. No additional database required for messages
3. Built-in CDN for file sharing
4. Optimized for mobile and web

### Monitoring

Monitor your Sendbird usage in the dashboard:
- Active users
- Message volume
- API calls
- Storage usage

## Troubleshooting

### "Sendbird Not Configured" Error

**Problem**: The app shows a configuration error.

**Solution**: 
1. Check that `VITE_SENDBIRD_APP_ID` is set in your `.env` file
2. Verify the App ID is correct (no extra spaces)
3. Restart the development server

### Connection Errors

**Problem**: Cannot connect to Sendbird.

**Solution**:
1. Check your internet connection
2. Verify the App ID is valid
3. Check browser console for detailed errors
4. Ensure Sendbird services are operational

### Messages Not Appearing

**Problem**: Sent messages don't show up.

**Solution**:
1. Check that the user is properly connected
2. Verify channel access permissions
3. Check browser console for errors
4. Try refreshing the page

## Migration from Existing System

If migrating from the existing custom messaging system:

1. **Export existing messages** from your database (optional)
2. **Notify users** about the messaging upgrade
3. **Update routes** to use Sendbird components
4. **Keep old system** for a transition period (optional)
5. **Gradually migrate users** to ensure smooth transition

## Additional Resources

- [Sendbird Documentation](https://sendbird.com/docs)
- [Sendbird React UIKit Guide](https://sendbird.com/docs/uikit/v3/react/overview)
- [Sendbird Dashboard](https://dashboard.sendbird.com/)
- [Sendbird Community](https://community.sendbird.com/)

## Support

For Sendbird-specific issues:
- Visit [Sendbird Support](https://sendbird.com/support)
- Check [Sendbird Status](https://status.sendbird.com/)

For HireMeBahamas integration issues:
- Open an issue in the GitHub repository
- Contact the development team

## Next Steps

1. ✅ Install Sendbird packages
2. ✅ Configure environment variables
3. ✅ Create Sendbird components
4. ⏳ Test the integration
5. ⏳ Update routing (optional)
6. ⏳ Deploy to production

---

**Note**: Sendbird is a third-party service. Make sure to review their [Terms of Service](https://sendbird.com/terms-of-service) and [Privacy Policy](https://sendbird.com/privacy-policy) before using in production.
