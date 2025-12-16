"""
WebSocket handlers for real-time features.

Provides Socket.IO event handlers for real-time messaging and notifications.
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

import socketio
from sqlalchemy import select

from app.auth.jwt import decode_access_token
from app.database import AsyncSessionLocal
from app.models import Message, User

logger = logging.getLogger(__name__)


class SocketManager:
    """Manager for Socket.IO connections and events."""
    
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        # sid -> {user_id, user_data}
        self.active_connections: Dict[str, Dict] = {}
        # user_id -> [sid1, sid2, ...]
        self.user_connections: Dict[str, List[str]] = {}
        # conversation_id -> [sid1, sid2, ...]
        self.conversation_rooms: Dict[str, List[str]] = {}

    async def authenticate_socket(self, token: Optional[str]) -> Optional[User]:
        """Authenticate socket connection using JWT token."""
        if not token:
            return None

        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")

            if not user_id:
                return None

            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(User).where(User.id == user_id, User.is_active.is_(True))
                )
                user = result.scalar_one_or_none()
                return user

        except Exception as e:
            logger.error(f"Socket authentication error: {e}")
            return None

    async def connect_user(self, sid: str, user: User):
        """Register a new socket connection for a user."""
        self.active_connections[sid] = {
            "user_id": str(user.id),
            "user_data": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }
        
        user_id_str = str(user.id)
        if user_id_str not in self.user_connections:
            self.user_connections[user_id_str] = []
        self.user_connections[user_id_str].append(sid)
        
        logger.info(f"User {user.id} connected via socket {sid}")

    async def disconnect_user(self, sid: str):
        """Unregister a socket connection."""
        if sid in self.active_connections:
            user_id = self.active_connections[sid]["user_id"]
            
            # Remove from user connections
            if user_id in self.user_connections:
                self.user_connections[user_id].remove(sid)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from active connections
            del self.active_connections[sid]
            
            logger.info(f"Socket {sid} disconnected")

    async def join_conversation_room(self, sid: str, conversation_id: str):
        """Add a socket to a conversation room."""
        room_name = f"conversation_{conversation_id}"
        await self.sio.enter_room(sid, room_name)
        
        if conversation_id not in self.conversation_rooms:
            self.conversation_rooms[conversation_id] = []
        if sid not in self.conversation_rooms[conversation_id]:
            self.conversation_rooms[conversation_id].append(sid)
        
        logger.info(f"Socket {sid} joined conversation {conversation_id}")

    async def leave_conversation_room(self, sid: str, conversation_id: str):
        """Remove a socket from a conversation room."""
        room_name = f"conversation_{conversation_id}"
        await self.sio.leave_room(sid, room_name)
        
        if conversation_id in self.conversation_rooms:
            if sid in self.conversation_rooms[conversation_id]:
                self.conversation_rooms[conversation_id].remove(sid)
            if not self.conversation_rooms[conversation_id]:
                del self.conversation_rooms[conversation_id]
        
        logger.info(f"Socket {sid} left conversation {conversation_id}")

    async def emit_to_user(self, user_id: str, event: str, data: dict):
        """Emit an event to all sockets connected for a specific user."""
        if user_id in self.user_connections:
            for sid in self.user_connections[user_id]:
                await self.sio.emit(event, data, room=sid)

    async def emit_to_conversation(self, conversation_id: str, event: str, data: dict, skip_sid: Optional[str] = None):
        """Emit an event to all sockets in a conversation room."""
        room_name = f"conversation_{conversation_id}"
        await self.sio.emit(event, data, room=room_name, skip_sid=skip_sid)


def setup_socket_handlers(sio: socketio.AsyncServer) -> SocketManager:
    """Set up Socket.IO event handlers.
    
    Args:
        sio: Socket.IO server instance
        
    Returns:
        SocketManager instance for managing connections
    """
    manager = SocketManager(sio)
    
    @sio.event
    async def connect(sid, environ, auth_data):
        """Handle client connection."""
        logger.info(f"Client attempting to connect: {sid}")
        
        # Authenticate user
        token = auth_data.get('token') if auth_data else None
        user = await manager.authenticate_socket(token)
        
        if not user:
            logger.warning(f"Connection rejected for {sid}: authentication failed")
            return False  # Reject connection
        
        await manager.connect_user(sid, user)
        await sio.emit('connected', {'sid': sid}, room=sid)
        
        return True  # Accept connection
    
    @sio.event
    async def disconnect(sid):
        """Handle client disconnection."""
        await manager.disconnect_user(sid)
    
    @sio.event
    async def join_conversation(sid, data):
        """Join a conversation room."""
        conversation_id = data.get('conversation_id')
        if conversation_id:
            await manager.join_conversation_room(sid, conversation_id)
    
    @sio.event
    async def leave_conversation(sid, data):
        """Leave a conversation room."""
        conversation_id = data.get('conversation_id')
        if conversation_id:
            await manager.leave_conversation_room(sid, conversation_id)
    
    @sio.event
    async def typing(sid, data):
        """Handle typing indicator."""
        conversation_id = data.get('conversation_id')
        is_typing = data.get('is_typing')
        
        if conversation_id:
            await manager.emit_to_conversation(
                conversation_id,
                'typing',
                data,
                skip_sid=sid
            )
    
    return manager
