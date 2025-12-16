"""
WebSocket notification system for real-time features (Facebook-style).

This module provides WebSocket support for:
- Live notifications (likes, comments, follows, messages)
- Real-time chat
- Live interaction counts (likes/comments)
- User presence (online/offline status)

Uses Flask-SocketIO for Flask backend and Redis pub/sub for scaling.
"""
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
import jwt

# Configure logging
logger = logging.getLogger(__name__)

# Optional dependencies - graceful degradation
HAS_SOCKETIO = False
HAS_REDIS = False

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
    HAS_SOCKETIO = True
except ImportError:
    logger.warning("Flask-SocketIO not available - WebSocket features disabled")
    SocketIO = None

try:
    import redis
    HAS_REDIS = True
except ImportError:
    logger.warning("Redis not available - using in-memory pub/sub (single worker only)")
    redis = None


class WebSocketNotificationManager:
    """
    Manages WebSocket connections and real-time notifications.
    
    Features:
    - JWT authentication for WebSocket connections
    - Redis pub/sub for multi-worker scaling
    - Room-based notifications (user rooms, conversation rooms)
    - Heartbeat/ping mechanism for connection health
    """
    
    def __init__(self, app=None, redis_url: Optional[str] = None):
        """
        Initialize the WebSocket notification manager.
        
        Args:
            app: Flask application instance
            redis_url: Redis connection URL for pub/sub (optional)
        """
        self.app = app
        self.socketio = None
        self.redis_client = None
        self.redis_pubsub = None
        self.active_connections: Dict[str, Dict[str, Any]] = {}  # sid -> user_data
        self.user_rooms: Dict[str, set] = {}  # user_id -> set of sids
        
        if app and HAS_SOCKETIO:
            self._init_socketio(app, redis_url)
    
    def _init_socketio(self, app, redis_url: Optional[str]):
        """Initialize Flask-SocketIO with the app."""
        if redis_url and HAS_REDIS:
            # Use Redis for message queue (supports multiple workers)
            self.socketio = SocketIO(
                app,
                cors_allowed_origins="*",
                async_mode='threading',
                message_queue=redis_url,
                logger=True,
                engineio_logger=False
            )
            logger.info(f"✅ WebSocket initialized with Redis pub/sub")
            
            # Initialize Redis client for pub/sub
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_pubsub = self.redis_client.pubsub()
                logger.info("✅ Redis pub/sub client initialized")
            except Exception as e:
                logger.warning(f"Redis pub/sub initialization failed: {e}")
        else:
            # Simple mode without Redis (single worker only)
            self.socketio = SocketIO(
                app,
                cors_allowed_origins="*",
                async_mode='threading',
                logger=True,
                engineio_logger=False
            )
            logger.info("✅ WebSocket initialized (single worker mode)")
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register WebSocket event handlers."""
        if not self.socketio:
            return
        
        @self.socketio.on('connect')
        def handle_connect(auth):
            """Handle client connection with JWT authentication."""
            from flask import request
            
            # Get token from auth data or query params
            token = None
            if auth and isinstance(auth, dict):
                token = auth.get('token')
            
            if not token:
                # Try to get from query params
                token = request.args.get('token')
            
            if not token:
                logger.warning(f"Connection attempt without token from {request.sid}")
                disconnect()
                return False
            
            # Verify JWT token
            user_data = self._verify_token(token)
            if not user_data:
                logger.warning(f"Invalid token for connection {request.sid}")
                disconnect()
                return False
            
            # Store connection info
            user_id = str(user_data.get('user_id'))
            self.active_connections[request.sid] = {
                'user_id': user_id,
                'user_data': user_data,
                'connected_at': datetime.utcnow().isoformat()
            }
            
            # Add to user room for targeted notifications
            user_room = f"user_{user_id}"
            join_room(user_room)
            
            # Track user connections
            if user_id not in self.user_rooms:
                self.user_rooms[user_id] = set()
            self.user_rooms[user_id].add(request.sid)
            
            logger.info(f"User {user_id} connected (sid: {request.sid})")
            
            # Send connection confirmation
            emit('connected', {
                'sid': request.sid,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Broadcast user online status
            self._broadcast_user_status(user_id, 'online')
            
            return True
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            from flask import request
            
            sid = request.sid
            if sid in self.active_connections:
                user_id = self.active_connections[sid]['user_id']
                
                # Remove from user rooms tracking
                if user_id in self.user_rooms:
                    self.user_rooms[user_id].discard(sid)
                    
                    # If no more connections, user is offline
                    if not self.user_rooms[user_id]:
                        del self.user_rooms[user_id]
                        self._broadcast_user_status(user_id, 'offline')
                
                # Remove connection
                del self.active_connections[sid]
                
                logger.info(f"User {user_id} disconnected (sid: {sid})")
        
        @self.socketio.on('ping')
        def handle_ping():
            """Handle heartbeat ping from client."""
            emit('pong', {'timestamp': datetime.utcnow().isoformat()})
        
        @self.socketio.on('join_conversation')
        def handle_join_conversation(data):
            """Join a conversation room for chat."""
            conversation_id = data.get('conversation_id')
            if conversation_id:
                room = f"conversation_{conversation_id}"
                join_room(room)
                logger.info(f"Client joined conversation {conversation_id}")
                emit('joined_conversation', {'conversation_id': conversation_id})
        
        @self.socketio.on('leave_conversation')
        def handle_leave_conversation(data):
            """Leave a conversation room."""
            conversation_id = data.get('conversation_id')
            if conversation_id:
                room = f"conversation_{conversation_id}"
                leave_room(room)
                logger.info(f"Client left conversation {conversation_id}")
                emit('left_conversation', {'conversation_id': conversation_id})
        
        @self.socketio.on('typing')
        def handle_typing(data):
            """Broadcast typing indicator to conversation."""
            from flask import request
            
            conversation_id = data.get('conversation_id')
            is_typing = data.get('is_typing', True)
            
            if conversation_id and request.sid in self.active_connections:
                user_id = self.active_connections[request.sid]['user_id']
                user_data = self.active_connections[request.sid]['user_data']
                
                room = f"conversation_{conversation_id}"
                emit('typing', {
                    'user_id': user_id,
                    'user_name': user_data.get('username', 'Unknown'),
                    'is_typing': is_typing,
                    'conversation_id': conversation_id
                }, room=room, skip_sid=request.sid)
    
    def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and extract user data.
        
        Args:
            token: JWT token string
            
        Returns:
            User data dict if valid, None otherwise
        """
        try:
            secret_key = os.getenv('SECRET_KEY')
            if not secret_key:
                logger.error("SECRET_KEY environment variable not set - WebSocket authentication disabled")
                return None
            
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # Extract user info from token
            user_id = payload.get('sub') or payload.get('user_id')
            if not user_id:
                return None
            
            return {
                'user_id': user_id,
                'username': payload.get('username', 'Unknown'),
                'email': payload.get('email', '')
            }
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def _broadcast_user_status(self, user_id: str, status: str):
        """
        Broadcast user online/offline status.
        
        Note: This broadcasts to all clients. For better scalability with many users,
        consider implementing selective broadcasting to only friends/followers or
        using rate limiting for status updates.
        
        Args:
            user_id: User ID
            status: 'online' or 'offline'
        """
        if not self.socketio:
            return
        
        # For now, broadcast to all clients
        # TODO: Implement selective broadcasting to friends/followers for better scaling
        self.socketio.emit('user_status', {
            'user_id': user_id,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True)
    
    def send_notification(self, user_id: str, notification_data: Dict[str, Any]):
        """
        Send notification to a specific user via WebSocket.
        
        Args:
            user_id: Target user ID
            notification_data: Notification payload
        """
        if not self.socketio:
            logger.debug("WebSocket not available, skipping notification")
            return
        
        room = f"user_{user_id}"
        
        # Add timestamp if not present
        if 'timestamp' not in notification_data:
            notification_data['timestamp'] = datetime.utcnow().isoformat()
        
        self.socketio.emit('notification', notification_data, room=room)
        logger.debug(f"Sent notification to user {user_id}: {notification_data.get('type')}")
    
    def broadcast_like_update(self, post_id: str, like_count: int, user_id: str = None):
        """
        Broadcast like count update for a post.
        
        Args:
            post_id: Post ID
            like_count: New like count
            user_id: User who liked (optional)
        """
        if not self.socketio:
            return
        
        self.socketio.emit('like_update', {
            'post_id': post_id,
            'like_count': like_count,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True)
    
    def broadcast_comment_update(self, post_id: str, comment_count: int, comment_data: Dict = None):
        """
        Broadcast comment count update for a post.
        
        Args:
            post_id: Post ID
            comment_count: New comment count
            comment_data: Comment details (optional)
        """
        if not self.socketio:
            return
        
        payload = {
            'post_id': post_id,
            'comment_count': comment_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if comment_data:
            payload['comment'] = comment_data
        
        self.socketio.emit('comment_update', payload, broadcast=True)
    
    def send_message(self, conversation_id: str, message_data: Dict[str, Any]):
        """
        Send chat message to conversation room.
        
        Args:
            conversation_id: Conversation ID
            message_data: Message payload
        """
        if not self.socketio:
            return
        
        room = f"conversation_{conversation_id}"
        
        if 'timestamp' not in message_data:
            message_data['timestamp'] = datetime.utcnow().isoformat()
        
        self.socketio.emit('new_message', message_data, room=room)
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is currently online."""
        return user_id in self.user_rooms
    
    def get_online_users(self) -> list:
        """Get list of currently online user IDs."""
        return list(self.user_rooms.keys())
    
    def get_connection_count(self) -> int:
        """Get total number of active WebSocket connections."""
        return len(self.active_connections)


# Global instance
_notification_manager: Optional[WebSocketNotificationManager] = None


def init_websocket_notifications(app, redis_url: Optional[str] = None) -> Optional[WebSocketNotificationManager]:
    """
    Initialize WebSocket notification system with Flask app.
    
    Args:
        app: Flask application instance
        redis_url: Redis connection URL for pub/sub (optional)
        
    Returns:
        WebSocketNotificationManager instance or None if not available
    """
    global _notification_manager
    
    if not HAS_SOCKETIO:
        logger.warning("Flask-SocketIO not available - WebSocket features disabled")
        # Return None instead of dummy instance to make it clear WebSocket is unavailable
        _notification_manager = None
        return None
    
    _notification_manager = WebSocketNotificationManager(app, redis_url)
    logger.info("✅ WebSocket notification system initialized")
    
    return _notification_manager


def get_notification_manager() -> Optional[WebSocketNotificationManager]:
    """Get the global notification manager instance."""
    return _notification_manager
