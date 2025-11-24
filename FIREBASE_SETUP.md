# Firebase Realtime Database Integration Guide

This guide explains how to set up and use Firebase Realtime Database in HireMeBahamas.

## What is Firebase Realtime Database?

Firebase Realtime Database is a cloud-hosted NoSQL database that lets you store and sync data between your users in realtime. It's perfect for:

- **Real-time messaging and chat**
- **Live notifications**
- **Presence tracking (online/offline status)**
- **Collaborative features**
- **Live updates across devices**

## Why Firebase?

While HireMeBahamas uses PostgreSQL as its primary database, Firebase Realtime Database complements it by providing:

1. **Real-time Synchronization**: Data syncs instantly across all connected clients
2. **Offline Support**: Works offline with automatic sync when reconnected
3. **Scalability**: Handles millions of concurrent connections
4. **Security**: Built-in security rules and authentication
5. **No Server Management**: Fully managed by Google

## Installation

Firebase dependencies have been added to the project:

### Backend (Python)
```bash
pip install -r requirements.txt
```

This installs `firebase-admin==6.6.0` for server-side operations.

### Frontend (React/TypeScript)
```bash
cd frontend && npm install
```

This installs `firebase@11.10.0` for client-side real-time features.

## Setup Instructions

### Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select an existing project
3. Follow the setup wizard
4. Enable Google Analytics (optional)

### Step 2: Enable Realtime Database

1. In Firebase Console, navigate to **Build** → **Realtime Database**
2. Click **Create Database**
3. Choose a location (select closest to your users)
4. Start in **Test Mode** for development (⚠️ Remember to set proper security rules for production)
5. Note your database URL: `https://your-project-id.firebaseio.com`

### Step 3: Generate Service Account Credentials (Backend)

1. Go to **Project Settings** (gear icon) → **Service Accounts**
2. Click **Generate New Private Key**
3. Save the downloaded JSON file securely (e.g., `/secure/firebase-credentials.json`)
4. ⚠️ **NEVER commit this file to Git!** Add it to `.gitignore`

### Step 4: Get Web App Configuration (Frontend)

1. In Firebase Console, go to **Project Settings** → **General**
2. Scroll to **Your apps** section
3. Click the web icon (</>) to register a web app
4. Register app name (e.g., "HireMeBahamas Frontend")
5. Copy the configuration object - you'll need these values:
   - `apiKey`
   - `authDomain`
   - `databaseURL`
   - `projectId`
   - `storageBucket`
   - `messagingSenderId`
   - `appId`

### Step 5: Configure Environment Variables

#### Backend Configuration (.env)

Add these variables to your `.env` file:

```bash
# Firebase Realtime Database Configuration
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
```

#### Frontend Configuration (.env)

Add these variables to your frontend `.env` file:

```bash
# Firebase Configuration (use VITE_ prefix for Vite)
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

⚠️ **Security Note**: Frontend environment variables are exposed to clients. Never put sensitive keys in `VITE_*` variables.

## Usage

### Backend Usage (Python)

The backend includes a `FirebaseService` class for server-side operations:

```python
from backend.app.core.firebase_service import firebase_service

# Check if Firebase is available
if firebase_service.is_available():
    # Create a new record
    key = firebase_service.create('messages/room1', {
        'text': 'Hello, Firebase!',
        'userId': 123,
        'timestamp': '2024-01-01T12:00:00Z'
    })
    
    # Read data
    messages = firebase_service.read('messages/room1')
    
    # Update data
    firebase_service.update('messages/room1/abc123', {
        'text': 'Updated message'
    })
    
    # Delete data
    firebase_service.delete('messages/room1/abc123')
    
    # Query data
    recent_messages = firebase_service.query(
        'messages/room1',
        order_by='timestamp',
        limit=20
    )
else:
    # Fallback to PostgreSQL or handle gracefully
    print("Firebase not configured, using PostgreSQL")
```

### Frontend Usage (React/TypeScript)

The frontend includes custom React hooks for real-time data:

#### useFirebaseData - Read and Subscribe to Data

```typescript
import { useFirebaseData } from '@/hooks/useFirebase';

function ChatRoom({ roomId }) {
  const { data: messages, loading, error } = useFirebaseData(`messages/${roomId}`);
  
  if (loading) return <div>Loading messages...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return (
    <div>
      {messages && Object.entries(messages).map(([key, msg]) => (
        <div key={key}>{msg.text}</div>
      ))}
    </div>
  );
}
```

#### useFirebaseWrite - Write, Update, Delete Data

```typescript
import { useFirebaseWrite } from '@/hooks/useFirebase';

function SendMessage({ roomId }) {
  const { pushData, loading } = useFirebaseWrite(`messages/${roomId}`);
  
  const sendMessage = async (text: string) => {
    const key = await pushData({
      text,
      userId: currentUser.id,
      timestamp: new Date().toISOString(),
    });
    console.log('Message sent with key:', key);
  };
  
  return (
    <button onClick={() => sendMessage('Hello!')} disabled={loading}>
      Send Message
    </button>
  );
}
```

#### useFirebaseQuery - Query with Ordering and Limits

```typescript
import { useFirebaseQuery } from '@/hooks/useFirebase';

function RecentMessages({ roomId }) {
  const { data: messages, loading } = useFirebaseQuery(
    `messages/${roomId}`,
    'timestamp',
    20  // Last 20 messages
  );
  
  return (
    <div>
      {messages.map((msg) => (
        <div key={msg.key}>{msg.text}</div>
      ))}
    </div>
  );
}
```

## Security Rules

Set up security rules in Firebase Console to protect your data:

### Development Rules (Test Mode)
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```
⚠️ **WARNING**: These rules allow anyone to read and write. Only use for development!

### Production Rules (Recommended)
```json
{
  "rules": {
    "messages": {
      "$roomId": {
        ".read": "auth != null",
        ".write": "auth != null",
        "$messageId": {
          ".validate": "newData.hasChildren(['text', 'userId', 'timestamp'])"
        }
      }
    },
    "users": {
      "$userId": {
        ".read": "auth != null",
        ".write": "auth.uid === $userId"
      }
    }
  }
}
```

## Use Cases in HireMeBahamas

### 1. Real-time Messaging
```typescript
// components/Chat/ChatRoom.tsx
import { useFirebaseData, useFirebaseWrite } from '@/hooks/useFirebase';

export function ChatRoom({ conversationId }) {
  const { data: messages } = useFirebaseData(`chats/${conversationId}`);
  const { pushData } = useFirebaseWrite(`chats/${conversationId}`);
  
  // Messages update in real-time across all connected users
}
```

### 2. Online Presence Tracking
```typescript
// Track which users are online
const { updateData } = useFirebaseWrite(`presence/${userId}`);

useEffect(() => {
  // Set user as online
  updateData({ online: true, lastSeen: Date.now() });
  
  // Set offline when component unmounts
  return () => {
    updateData({ online: false, lastSeen: Date.now() });
  };
}, [userId]);
```

### 3. Live Notifications
```typescript
// Real-time notification badge
const { data: notifications } = useFirebaseData(`notifications/${userId}`);
const unreadCount = notifications ? Object.values(notifications).filter(n => !n.read).length : 0;
```

### 4. Collaborative Features
```typescript
// Multiple users editing same document
const { data: document, loading } = useFirebaseData(`documents/${docId}`);
const { updateData } = useFirebaseWrite(`documents/${docId}`);

// Changes sync across all users in real-time
```

## Deployment

### Railway/Render (Backend)

Add environment variables to your deployment platform:

1. `FIREBASE_CREDENTIALS_PATH`: Path to credentials file
2. `FIREBASE_DATABASE_URL`: Your Firebase database URL

**For credentials file**: Upload the JSON file to your server or use Railway's secret files feature.

### Vercel (Frontend)

Add environment variables in Vercel Dashboard:

1. Go to Project Settings → Environment Variables
2. Add all `VITE_FIREBASE_*` variables
3. Redeploy your application

## Troubleshooting

### Firebase Not Initialized

**Problem**: "Firebase is not configured" error

**Solution**: 
- Check that all environment variables are set correctly
- Verify the credentials file exists at the specified path
- Check Firebase Console for any service issues

### Permission Denied

**Problem**: "Permission denied" when reading/writing data

**Solution**:
- Update security rules in Firebase Console
- Ensure users are properly authenticated
- Check that your rules match your data structure

### Data Not Syncing

**Problem**: Data not updating in real-time

**Solution**:
- Check your internet connection
- Verify Firebase Console shows active connections
- Check browser console for errors
- Ensure you're using the hooks correctly (not fetching once)

### Quota Exceeded

**Problem**: "Quota exceeded" error

**Solution**:
- Check Firebase Console → Usage tab
- Free tier limits: 100 simultaneous connections, 1GB stored, 10GB downloaded/month
- Upgrade to Blaze (pay-as-you-go) plan for higher limits

## Best Practices

1. **Use Firebase for Real-time Features Only**: Keep PostgreSQL for permanent data storage
2. **Implement Proper Security Rules**: Never use test mode in production
3. **Structure Data Efficiently**: Avoid deep nesting (max 32 levels)
4. **Use Indexes**: For large datasets, enable indexing in Firebase Console
5. **Monitor Usage**: Keep track of reads, writes, and bandwidth in Firebase Console
6. **Handle Offline State**: Design UI to work when Firebase is unavailable
7. **Pagination**: Use queries with limits for large datasets
8. **Clean Up Listeners**: Always unsubscribe when components unmount (hooks handle this automatically)

## Cost Considerations

Firebase Realtime Database has a free tier (Spark plan) that includes:
- 1 GB stored data
- 10 GB downloaded per month
- 100 simultaneous connections

For production, consider the Blaze (pay-as-you-go) plan:
- $5/GB stored per month
- $1/GB downloaded
- No connection limit

## Additional Resources

- [Firebase Realtime Database Docs](https://firebase.google.com/docs/database)
- [Security Rules Guide](https://firebase.google.com/docs/database/security)
- [Best Practices](https://firebase.google.com/docs/database/usage/best-practices)
- [Firebase Console](https://console.firebase.google.com/)

## Support

If you encounter any issues with Firebase integration:

1. Check the logs: Backend logs will show Firebase initialization status
2. Review environment variables: Ensure all Firebase configs are set
3. Test with Firebase Console: Try reading/writing directly in the console
4. Fallback gracefully: The code handles Firebase being unavailable

---

**Note**: Firebase Realtime Database is optional. HireMeBahamas works perfectly with just PostgreSQL. Firebase adds real-time capabilities for enhanced user experience.
