# WebSocket Quick Start Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**New dependencies added:**
- `flask-socketio==5.4.1`
- `eventlet==0.37.0`

### 2. Set Environment Variables

```bash
# Required
export SECRET_KEY="your-secret-key-here"

# Optional (for scaling)
export REDIS_URL="redis://localhost:6379"
```

### 3. Start Server

```bash
# Development
python final_backend_postgresql.py

# Production
gunicorn --worker-class eventlet -w 1 app:application --bind 0.0.0.0:10000
```

### 4. Test Connection

```bash
# Check status
curl http://localhost:10000/api/ws/status
```

**Expected response:**
```json
{
  "success": true,
  "websocket_enabled": true,
  "active_connections": 0,
  "online_users": 0,
  "redis_enabled": false
}
```

---

## 📱 Client Integration

### JavaScript/React

```javascript
import io from 'socket.io-client';

// Get JWT token from your auth system
const token = localStorage.getItem('token');

// Connect
const socket = io('http://localhost:10000', {
  auth: { token: token },
  transports: ['websocket', 'polling']
});

// Listen for notifications
socket.on('notification', (data) => {
  console.log('🔔 Notification:', data);
  showToast(data.message);
});

// Listen for like updates
socket.on('like_update', (data) => {
  console.log('👍 Like:', data);
  updateLikeCount(data.post_id, data.like_count);
});
```

### Python Client

```python
import socketio

sio = socketio.Client()
token = "your-jwt-token"

@sio.event
def notification(data):
    print('🔔 Notification:', data)

sio.connect('http://localhost:10000', auth={'token': token})
```

---

## 🎯 Common Use Cases

### Send Notification

**Backend:**
```python
if notification_manager:
    notification_manager.send_notification(
        user_id="123",
        notification_data={
            'type': 'like',
            'message': 'Someone liked your post',
            'post_id': 456
        }
    )
```

### Broadcast Like Count

**Backend:**
```python
if notification_manager:
    notification_manager.broadcast_like_update(
        post_id="456",
        like_count=42,
        user_id="123"
    )
```

### Join Conversation

**Frontend:**
```javascript
socket.emit('join_conversation', {
  conversation_id: '123'
});

socket.on('new_message', (data) => {
  addMessage(data);
});
```

---

## 🧪 Testing

### Python Test

```bash
python test_websocket_notifications.py
```

### Browser Test

1. Open `test_websocket.html` in browser
2. Enter backend URL: `http://localhost:10000`
3. Get JWT token:
   ```bash
   curl -X POST http://localhost:10000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"password"}'
   ```
4. Paste token in browser
5. Click "Connect"
6. Click "Test Notification"

---

## 📋 Events Reference

### Server → Client

| Event | Description | Example |
|-------|-------------|---------|
| `notification` | Personal notification | `{type: 'like', message: '...'}` |
| `like_update` | Like count update | `{post_id: 123, like_count: 42}` |
| `comment_update` | Comment count update | `{post_id: 123, comment_count: 15}` |
| `user_status` | User online/offline | `{user_id: 123, status: 'online'}` |
| `new_message` | Chat message | `{conversation_id: 456, content: '...'}` |
| `typing` | Typing indicator | `{user_id: 123, is_typing: true}` |
| `pong` | Heartbeat response | `{timestamp: '...'}` |

### Client → Server

| Event | Description | Example |
|-------|-------------|---------|
| `ping` | Heartbeat | `socket.emit('ping')` |
| `join_conversation` | Join chat room | `{conversation_id: '123'}` |
| `leave_conversation` | Leave chat room | `{conversation_id: '123'}` |
| `typing` | Send typing status | `{conversation_id: '123', is_typing: true}` |

---

## 🔍 Troubleshooting

### Connection Failed

**Check WebSocket availability:**
```bash
curl http://localhost:10000/api/ws/status
```

**Common issues:**
- Flask-SocketIO not installed: `pip install flask-socketio eventlet`
- SECRET_KEY not set: `export SECRET_KEY="..."`
- Invalid JWT token: Get fresh token from login

### Not Receiving Events

**Check connection:**
```javascript
console.log('Connected:', socket.connected);
```

**Check logs:**
```bash
tail -f /var/log/hireme_backend.log | grep WebSocket
```

**Test notification:**
```bash
curl -X POST http://localhost:10000/api/ws/test-notification \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Test"}'
```

---

## 🔧 Configuration

### Single Worker (Development)

```bash
# No Redis needed
python final_backend_postgresql.py
```

**Supports:** Up to 1,000 connections

### Multiple Workers (Production)

```bash
# Start Redis
redis-server

# Set Redis URL
export REDIS_URL="redis://localhost:6379"

# Start with multiple workers
gunicorn --worker-class eventlet -w 4 app:application
```

**Supports:** 10,000+ connections

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **WEBSOCKET_REALTIME_FEATURES.md** | Complete feature guide |
| **WEBSOCKET_INTEGRATION_GUIDE.md** | Integration patterns |
| **WEBSOCKET_ARCHITECTURE_DIAGRAM.md** | Visual architecture |
| **STEP_9_WEBSOCKET_COMPLETION_SUMMARY.md** | Implementation summary |

---

## 💡 Tips

1. **Always test WebSocket availability:**
   ```python
   if notification_manager:
       # Send notification
   ```

2. **Use graceful error handling:**
   ```python
   try:
       notification_manager.send_notification(...)
   except Exception as e:
       logger.warning(f"WebSocket failed: {e}")
   ```

3. **Don't notify yourself:**
   ```python
   if post_author_id != current_user_id:
       notification_manager.send_notification(...)
   ```

4. **Test in browser first:**
   - Easier to debug
   - Visual feedback
   - See all events

5. **Monitor server status:**
   ```bash
   watch -n 5 'curl -s http://localhost:10000/api/ws/status | jq'
   ```

---

## 🎯 Next Steps

1. **Test with your app:**
   - Start backend server
   - Connect from your frontend
   - Like a post, see real-time update

2. **Add to more endpoints:**
   - Comments: Real-time comment notifications
   - Messages: Chat integration
   - Follows: More follow notifications

3. **Scale up:**
   - Add Redis for production
   - Use multiple workers
   - Enable load balancer sticky sessions

---

## 🆘 Support

**Quick checks:**
```bash
# Server running?
curl http://localhost:10000/health

# WebSocket available?
curl http://localhost:10000/api/ws/status

# Redis working?
redis-cli ping
```

**Test tools:**
- Python: `test_websocket_notifications.py`
- Browser: `test_websocket.html`
- API: `/api/ws/test-notification`

---

## ✅ Checklist

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] SECRET_KEY environment variable set
- [ ] Server starts without errors
- [ ] `/api/ws/status` returns success
- [ ] Can connect with JWT token
- [ ] Receive test notification
- [ ] Frontend integration works

**When all checked:** You're ready for production! 🚀

---

**Need help?** Check the full documentation in `WEBSOCKET_REALTIME_FEATURES.md`
