# WebSocket Integration Guide

## Overview

This guide shows how to integrate real-time WebSocket notifications into your API endpoints.

## Integration Patterns

### Flask Backend (final_backend_postgresql.py)

The Flask backend uses the `notification_manager` global instance for WebSocket operations.

#### Example: Like Endpoint

```python
@app.route("/api/posts/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    # ... existing like logic ...
    
    # Add WebSocket notification after successful like
    if notification_manager and liked:
        try:
            # Get post author
            cursor.execute("SELECT user_id FROM posts WHERE id = %s", (post_id,))
            post_author = cursor.fetchone()
            
            if post_author and post_author['user_id'] != user_id:
                # Send notification to post author
                notification_manager.send_notification(
                    str(post_author['user_id']),
                    {
                        'type': 'like',
                        'post_id': post_id,
                        'user_id': user_id,
                        'message': 'Someone liked your post'
                    }
                )
            
            # Broadcast like count update to all clients
            notification_manager.broadcast_like_update(
                str(post_id),
                likes_count,
                str(user_id)
            )
        except Exception as ws_error:
            # Don't fail the request if WebSocket fails
            logger.warning(f"WebSocket notification failed: {ws_error}")
    
    return jsonify({"success": True, "liked": liked, "likes_count": likes_count})
```

#### Example: Comment Endpoint

```python
@app.route("/api/posts/<int:post_id>/comment", methods=["POST"])
def add_comment(post_id):
    # ... existing comment logic ...
    
    # Add WebSocket notification after successful comment
    if notification_manager:
        try:
            # Get post author
            cursor.execute("SELECT user_id FROM posts WHERE id = %s", (post_id,))
            post_author = cursor.fetchone()
            
            if post_author and post_author['user_id'] != user_id:
                # Send notification to post author
                notification_manager.send_notification(
                    str(post_author['user_id']),
                    {
                        'type': 'comment',
                        'post_id': post_id,
                        'user_id': user_id,
                        'comment_id': comment_id,
                        'message': 'Someone commented on your post'
                    }
                )
            
            # Broadcast comment count update
            notification_manager.broadcast_comment_update(
                str(post_id),
                comment_count,
                {
                    'id': comment_id,
                    'content': content,
                    'user_id': user_id
                }
            )
        except Exception as ws_error:
            logger.warning(f"WebSocket notification failed: {ws_error}")
    
    return jsonify({"success": True, "comment": comment_data})
```

#### Example: Follow Endpoint

```python
@app.route("/api/users/follow/<int:user_id>", methods=["POST"])
def follow_user(user_id):
    # ... existing follow logic ...
    
    # Send real-time notification to followed user
    if notification_manager:
        try:
            notification_manager.send_notification(
                str(user_id),
                {
                    'type': 'follow',
                    'user_id': current_user_id,
                    'message': 'Someone started following you'
                }
            )
        except Exception as ws_error:
            logger.warning(f"WebSocket notification failed: {ws_error}")
    
    return jsonify({"success": True})
```

### FastAPI Backend (api/backend_app)

The FastAPI backend can use the existing `SocketManager` or integrate a similar pattern.

#### Example: Using Socket Manager

```python
from app.core.socket_manager import get_socket_manager

@router.post("/{post_id}/like")
async def like_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # ... existing like logic ...
    
    # Get socket manager
    socket_manager = get_socket_manager()
    
    if socket_manager and liked:
        # Send notification to post author
        if post.user_id != current_user.id:
            await socket_manager.send_notification(
                str(post.user_id),
                {
                    'type': 'like',
                    'post_id': str(post_id),
                    'user_id': str(current_user.id),
                    'message': f'{current_user.full_name} liked your post'
                }
            )
        
        # Broadcast like count update
        await socket_manager.broadcast_like_update(
            str(post_id),
            likes_count,
            str(current_user.id)
        )
    
    return {"success": True, "liked": liked, "likes_count": likes_count}
```

## Notification Types

### Standard Notification Types

Use these consistent types across your application:

- `like`: Someone liked content
- `comment`: Someone commented on content
- `follow`: Someone followed the user
- `message`: New chat message
- `mention`: User was mentioned
- `friend_request`: New friend request
- `job_application`: Job application status update
- `system`: System announcements

### Notification Payload Structure

```json
{
  "type": "like",
  "user_id": "123",
  "post_id": "456",
  "message": "Someone liked your post",
  "timestamp": "2025-01-15T12:00:00Z",
  "data": {
    // Additional context-specific data
  }
}
```

## Best Practices

### 1. Graceful Degradation

Always wrap WebSocket calls in try-except to prevent failures:

```python
if notification_manager:
    try:
        notification_manager.send_notification(...)
    except Exception as e:
        logger.warning(f"WebSocket failed: {e}")
        # Continue with normal response
```

### 2. Don't Notify Self

Don't send notifications to the user who performed the action:

```python
if post_author['user_id'] != current_user_id:
    notification_manager.send_notification(...)
```

### 3. Broadcast vs Direct

Use appropriate method:

- `send_notification(user_id, data)`: Send to specific user
- `broadcast_like_update(post_id, count)`: Broadcast to all connected clients
- `send_message(conversation_id, data)`: Send to conversation room

### 4. Notification Aggregation

For high-frequency events (likes on popular posts), consider aggregating:

```python
# Instead of sending notification for every like
# Aggregate and send batch updates every few seconds
if likes_count % 10 == 0:  # Every 10 likes
    notification_manager.send_notification(...)
```

### 5. User Privacy

Only send notifications to authorized users:

```python
# Check privacy settings before sending
if user.notifications_enabled and not user.blocked_users.contains(sender_id):
    notification_manager.send_notification(...)
```

## Testing

### Test Individual Notifications

```python
# Test sending a notification
curl -X POST http://localhost:10000/api/ws/test-notification \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test notification"}'
```

### Test WebSocket Connection

1. Open `test_websocket.html` in browser
2. Enter backend URL and JWT token
3. Click "Connect"
4. Click "Test Notification"
5. Watch for real-time events in log

### Test with Python

```bash
python test_websocket_notifications.py
```

## Troubleshooting

### WebSocket Not Working

1. **Check Flask-SocketIO is installed:**
   ```bash
   pip install flask-socketio eventlet
   ```

2. **Check initialization:**
   ```python
   # Should see in logs:
   # ✅ WebSocket real-time features initialized
   ```

3. **Check connection:**
   ```bash
   curl http://localhost:10000/api/ws/status
   ```

### Notifications Not Received

1. **Verify authentication:**
   - WebSocket requires valid JWT token
   - Token must be passed in auth or query params

2. **Check user room:**
   - Users must be connected to receive notifications
   - Check online users: `/api/ws/status`

3. **Check Redis (if using multiple workers):**
   - Redis must be running for pub/sub
   - Verify REDIS_URL environment variable

### Performance Issues

1. **Too many connections:**
   - Use Redis for multi-worker scaling
   - Consider connection pooling

2. **High latency:**
   - Check network between server and Redis
   - Reduce heartbeat frequency
   - Use Redis closer to application

## Advanced Usage

### Custom Event Handlers

Add custom events in `websocket_notifications.py`:

```python
@self.socketio.on('custom_event')
def handle_custom_event(data):
    # Handle custom event
    user_id = self.active_connections[request.sid]['user_id']
    # ... process data ...
    emit('custom_response', response_data)
```

### Redis Pub/Sub for Scaling

Enable Redis for multi-worker support:

```bash
# Set in environment
export REDIS_URL=redis://localhost:6379

# Or in .env file
REDIS_URL=redis://localhost:6379
```

### Room-Based Broadcasting

Send to specific groups of users:

```python
# Join room
socket.emit('join_room', {'room': 'post_123_watchers'})

# Broadcast to room
socketio.emit('post_update', data, room='post_123_watchers')
```

## Migration from Polling

If migrating from polling-based updates:

1. **Keep REST endpoints:** WebSocket complements REST, doesn't replace it
2. **Add WebSocket notifications:** Add real-time events alongside REST responses
3. **Test both paths:** Ensure app works with and without WebSocket
4. **Gradual rollout:** Enable WebSocket for small percentage of users first

### Before (Polling)

```javascript
// Poll every 5 seconds
setInterval(async () => {
  const response = await fetch('/api/notifications');
  const data = await response.json();
  updateUI(data);
}, 5000);
```

### After (WebSocket + REST)

```javascript
// Initial load via REST
const response = await fetch('/api/notifications');
updateUI(await response.json());

// Real-time updates via WebSocket
socket.on('notification', (data) => {
  addNotification(data);
  updateUI();
});
```

## Security Considerations

1. **Authentication:** All WebSocket connections require JWT
2. **Rate Limiting:** Applied to both REST and WebSocket events
3. **Authorization:** Users can only receive their own notifications
4. **Validation:** All event data is validated before broadcasting
5. **Encryption:** Use WSS (WebSocket Secure) in production

## Production Deployment

### Gunicorn with Eventlet

```bash
gunicorn --worker-class eventlet -w 1 app:application --bind 0.0.0.0:10000
```

### Multiple Workers with Redis

```bash
# Start Redis
redis-server

# Set environment
export REDIS_URL=redis://localhost:6379

# Start with multiple workers
gunicorn --worker-class eventlet -w 4 app:application --bind 0.0.0.0:10000
```

### Load Balancer Configuration

For WebSocket with load balancer:

1. **Enable sticky sessions:** Required for WebSocket
2. **Configure timeout:** Set longer timeout for WebSocket (e.g., 60s)
3. **Enable WebSocket upgrade:** Allow HTTP upgrade to WebSocket protocol

### Monitoring

Monitor WebSocket health:

```bash
# Check status
curl http://localhost:10000/api/ws/status

# Check logs
tail -f /var/log/hireme_backend.log | grep WebSocket
```

## Support

For questions or issues:
- See main documentation: `WEBSOCKET_REALTIME_FEATURES.md`
- Test with: `test_websocket.html` or `test_websocket_notifications.py`
- Check examples in `final_backend_postgresql.py` (like_post, follow_user)
