# WebSocket Real-Time Features (Facebook-Style)

## Overview

HireMeBahamas now supports real-time features using WebSockets (Socket.IO) for instant updates without polling. This provides a Facebook-like experience with:

- **Live Notifications**: Instant notification delivery for likes, comments, follows, and messages
- **Real-Time Chat**: Instant message delivery with typing indicators
- **Live Interaction Counts**: Like and comment counts update in real-time across all clients
- **User Presence**: See who's online/offline in real-time
- **Heartbeat/Ping**: Connection health monitoring

## Architecture

### Technology Stack

- **Flask-SocketIO**: WebSocket support for Flask backend
- **Socket.IO Client**: JavaScript/Python clients for WebSocket connections
- **Redis Pub/Sub**: Multi-worker scaling (optional but recommended)
- **JWT Authentication**: Secure WebSocket connections using existing JWT tokens

### Scaling

The WebSocket system supports multiple deployment modes:

1. **Single Worker** (Development): Direct in-memory message passing
2. **Multi-Worker** (Production): Redis pub/sub for message distribution across workers
3. **Multi-Server** (Enterprise): Redis pub/sub + sticky sessions for horizontal scaling

## Setup

### Requirements

Install the required dependencies:

```bash
pip install flask-socketio python-socketio redis
```

These are already included in `requirements.txt`.

### Configuration

Set environment variables:

```bash
# Optional: Redis for multi-worker scaling
REDIS_URL=redis://localhost:6379

# Standard Flask configuration
SECRET_KEY=your-secret-key-here
```

### Starting the Server

The WebSocket server starts automatically with the Flask application:

```bash
python final_backend_postgresql.py
```

Or with Gunicorn (production):

```bash
gunicorn --worker-class eventlet -w 1 app:application
```

**Note**: When using Gunicorn with Socket.IO, use `eventlet` or `gevent` worker class with a single worker, or use Redis message queue for multiple workers.

## Client Integration

### JavaScript/TypeScript (React Frontend)

Install the Socket.IO client:

```bash
npm install socket.io-client
```

Connect to WebSocket:

```javascript
import io from 'socket.io-client';

// Get JWT token from your auth system
const token = localStorage.getItem('token');

// Connect with authentication
const socket = io('http://localhost:10000', {
  auth: {
    token: token
  },
  transports: ['websocket', 'polling']
});

// Handle connection
socket.on('connect', () => {
  console.log('✅ WebSocket connected:', socket.id);
});

// Handle disconnection
socket.on('disconnect', () => {
  console.log('❌ WebSocket disconnected');
});

// Listen for notifications
socket.on('notification', (data) => {
  console.log('🔔 New notification:', data);
  // Update UI, show toast, etc.
  showNotification(data);
});

// Listen for like updates
socket.on('like_update', (data) => {
  console.log('👍 Like update:', data);
  // Update like count in UI
  updateLikeCount(data.post_id, data.like_count);
});

// Listen for comment updates
socket.on('comment_update', (data) => {
  console.log('💬 Comment update:', data);
  // Update comment count in UI
  updateCommentCount(data.post_id, data.comment_count);
});

// Listen for user status
socket.on('user_status', (data) => {
  console.log('👤 User status:', data);
  // Update online status indicator
  updateUserStatus(data.user_id, data.status);
});

// Heartbeat (optional)
setInterval(() => {
  socket.emit('ping');
}, 30000); // Every 30 seconds

socket.on('pong', (data) => {
  console.log('🏓 Pong:', data);
});
```

### Python Client

```python
import socketio

# Create a Socket.IO client
sio = socketio.Client()

# Get JWT token from your auth system
token = "your-jwt-token"

# Event handlers
@sio.event
def connect():
    print('✅ WebSocket connected')

@sio.event
def notification(data):
    print('🔔 Notification:', data)

@sio.event
def like_update(data):
    print('👍 Like update:', data)

# Connect with authentication
sio.connect('http://localhost:10000', auth={'token': token})

# Wait for events
sio.wait()
```

## API Reference

### WebSocket Events

#### Server → Client Events

##### `connected`
Sent when client successfully connects.

```json
{
  "sid": "socket-id",
  "user_id": "123",
  "timestamp": "2025-01-15T12:00:00Z"
}
```

##### `notification`
Real-time notification delivery.

```json
{
  "type": "like|comment|follow|message",
  "user_id": "456",
  "post_id": "789",
  "message": "Someone liked your post",
  "timestamp": "2025-01-15T12:00:00Z"
}
```

##### `like_update`
Live like count update for a post.

```json
{
  "post_id": "789",
  "like_count": 42,
  "user_id": "456",
  "timestamp": "2025-01-15T12:00:00Z"
}
```

##### `comment_update`
Live comment count update for a post.

```json
{
  "post_id": "789",
  "comment_count": 15,
  "comment": {
    "id": "101",
    "content": "Great post!",
    "user_id": "456"
  },
  "timestamp": "2025-01-15T12:00:00Z"
}
```

##### `user_status`
User online/offline status change.

```json
{
  "user_id": "456",
  "status": "online|offline",
  "timestamp": "2025-01-15T12:00:00Z"
}
```

##### `new_message`
New chat message in a conversation.

```json
{
  "conversation_id": "123",
  "message_id": "789",
  "sender_id": "456",
  "content": "Hello!",
  "timestamp": "2025-01-15T12:00:00Z"
}
```

##### `typing`
Typing indicator for chat.

```json
{
  "conversation_id": "123",
  "user_id": "456",
  "user_name": "John Doe",
  "is_typing": true
}
```

##### `pong`
Response to ping (heartbeat).

```json
{
  "timestamp": "2025-01-15T12:00:00Z"
}
```

#### Client → Server Events

##### `ping`
Heartbeat to check connection health.

```javascript
socket.emit('ping');
```

##### `join_conversation`
Join a conversation room for chat.

```javascript
socket.emit('join_conversation', {
  conversation_id: '123'
});
```

##### `leave_conversation`
Leave a conversation room.

```javascript
socket.emit('leave_conversation', {
  conversation_id: '123'
});
```

##### `typing`
Send typing indicator to conversation.

```javascript
socket.emit('typing', {
  conversation_id: '123',
  is_typing: true
});
```

### REST API Endpoints

#### GET `/api/ws/status`
Get WebSocket server status and statistics.

**Response:**
```json
{
  "success": true,
  "websocket_enabled": true,
  "active_connections": 42,
  "online_users": 35,
  "redis_enabled": true
}
```

#### POST `/api/ws/test-notification`
Send a test notification (requires authentication).

**Request:**
```json
{
  "message": "Test notification message"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Test notification sent",
  "user_id": 123
}
```

## Integration Examples

### Like Button with Real-Time Updates

```javascript
// Like a post
async function likePost(postId) {
  const response = await fetch(`/api/posts/${postId}/like`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  // REST API returns immediate result
  updateLikeCount(postId, data.likes_count);
  
  // WebSocket will also broadcast update to other clients
}

// Listen for real-time updates from other users
socket.on('like_update', (data) => {
  // Update UI when someone else likes the post
  if (data.post_id === currentPostId) {
    updateLikeCount(data.post_id, data.like_count);
  }
});
```

### Notification Bell with Real-Time Updates

```javascript
// Initialize notification state
let unreadCount = 0;

// Listen for new notifications
socket.on('notification', (data) => {
  // Show toast notification
  showToast(data.message);
  
  // Update notification badge
  unreadCount++;
  updateNotificationBadge(unreadCount);
  
  // Add to notification list
  addNotificationToList(data);
});

// Notification bell component
function NotificationBell() {
  return (
    <div className="notification-bell">
      <BellIcon />
      {unreadCount > 0 && (
        <span className="badge">{unreadCount}</span>
      )}
    </div>
  );
}
```

### Chat with Typing Indicators

```javascript
// Join conversation when opening chat
socket.emit('join_conversation', {
  conversation_id: conversationId
});

// Send typing indicator
function handleTyping(isTyping) {
  socket.emit('typing', {
    conversation_id: conversationId,
    is_typing: isTyping
  });
}

// Listen for typing indicators
socket.on('typing', (data) => {
  if (data.conversation_id === conversationId) {
    showTypingIndicator(data.user_name, data.is_typing);
  }
});

// Listen for new messages
socket.on('new_message', (data) => {
  if (data.conversation_id === conversationId) {
    addMessageToChat(data);
  }
});

// Leave conversation when closing chat
socket.emit('leave_conversation', {
  conversation_id: conversationId
});
```

## Testing

### Test Script

Run the included test script:

```bash
python test_websocket_notifications.py
```

This will:
1. Register a test user
2. Connect to WebSocket with JWT authentication
3. Send test notifications
4. Display received events
5. Test ping/pong heartbeat

### Manual Testing

1. Start the backend server
2. Open browser console
3. Connect to WebSocket (see JavaScript example above)
4. Perform actions (like posts, send messages)
5. Watch for real-time updates in console

## Performance Considerations

### Connection Limits

- **Development**: Up to ~1,000 concurrent connections per worker
- **Production with Redis**: Up to ~10,000+ connections with multiple workers
- **Sticky Sessions**: Required for WebSocket with load balancer

### Bandwidth

Each WebSocket connection uses:
- **Idle**: ~50 bytes/second (heartbeat)
- **Active**: Variable based on notification frequency
- **Peak**: Up to 10 KB/second per user during high activity

### Scaling Recommendations

1. **< 1,000 users**: Single worker, no Redis needed
2. **1,000 - 10,000 users**: Multiple workers with Redis pub/sub
3. **> 10,000 users**: Dedicated Socket.IO service with Redis cluster

## Troubleshooting

### Connection Issues

**Problem**: WebSocket fails to connect

**Solutions**:
- Check if Flask-SocketIO is installed
- Verify JWT token is valid
- Check CORS configuration
- Ensure port 10000 is accessible

### Events Not Received

**Problem**: Not receiving real-time updates

**Solutions**:
- Check WebSocket connection status: `socket.connected`
- Verify event handler is registered before connection
- Check Redis pub/sub if using multiple workers
- Look for errors in server logs

### High Latency

**Problem**: Slow notification delivery

**Solutions**:
- Use Redis for pub/sub instead of in-memory
- Reduce heartbeat frequency
- Check network latency
- Consider geographic server distribution

## Security

### Authentication

- All WebSocket connections require JWT authentication
- Tokens are verified on connection
- Invalid tokens are immediately disconnected

### Authorization

- Users only receive notifications for their own account
- Room-based access control for conversations
- No broadcasting of sensitive data

### Rate Limiting

- Connection rate limiting prevents DoS attacks
- Event rate limiting prevents spam
- Automatic disconnect for abusive clients

## Future Enhancements

Planned features:

1. **Video Call Events**: Real-time signaling for WebRTC calls
2. **Live Document Collaboration**: Real-time editing notifications
3. **Job Application Updates**: Instant status updates for applications
4. **Analytics Events**: Real-time dashboard updates
5. **Admin Broadcasts**: System-wide announcements

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review server logs: `/tmp/hireme_backend.log`
3. Test with: `python test_websocket_notifications.py`
4. File an issue on GitHub

## License

Same as HireMeBahamas main application.
