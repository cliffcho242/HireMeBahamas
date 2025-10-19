from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy import select
import socketio

from app.database import AsyncSessionLocal
from app.models import User, Message
from app.core.security import verify_token


class SocketManager:
    def __init__(self, sio: socketio.AsyncServer):
        self.sio = sio
        # sid -> {user_id, user_data}
        self.active_connections: Dict[str, Dict] = {}
        # user_id -> [sid1, sid2, ...]
        self.user_connections: Dict[str, List[str]] = {}
        # conversation_id -> [sid1, sid2, ...]
        self.conversation_rooms: Dict[str, List[str]] = {}

    async def authenticate_socket(
        self, token: Optional[str]
    ) -> Optional[User]:
        """Authenticate socket connection using JWT token"""
        if not token:
            return None
        
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                return None
            
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(User).where(
                        User.id == user_id, User.is_active.is_(True)
                    )
                )
                user = result.scalar_one_or_none()
                return user
                
        except Exception as e:
            print(f"Socket authentication error: {e}")
            return None

    async def connect_user(self, sid: str, user: User):
        """Register a new socket connection for a user"""
        self.active_connections[sid] = {
            "user_id": str(user.id),
            "user_data": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "profile_image": user.profile_image
            }
        }
        
        # Track user connections
        user_id = str(user.id)
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(sid)
        
        # Notify user is online
        await self.broadcast_user_status(user_id, "online")

    async def disconnect_user(self, sid: str):
        """Handle user disconnection"""
        if sid in self.active_connections:
            user_id = self.active_connections[sid]["user_id"]
            
            # Remove from active connections
            del self.active_connections[sid]
            
            # Remove from user connections
            if user_id in self.user_connections:
                self.user_connections[user_id].remove(sid)
                
                # If no more connections, user is offline
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
                    await self.broadcast_user_status(user_id, "offline")

    async def join_conversation(self, sid: str, conversation_id: str):
        """Join a conversation room"""
        if sid not in self.active_connections:
            return
        
        # Add to Socket.IO room
        await self.sio.enter_room(sid, f"conversation_{conversation_id}")
        
        # Track conversation participants
        if conversation_id not in self.conversation_rooms:
            self.conversation_rooms[conversation_id] = []
        
        if sid not in self.conversation_rooms[conversation_id]:
            self.conversation_rooms[conversation_id].append(sid)

    async def leave_conversation(self, sid: str, conversation_id: str):
        """Leave a conversation room"""
        await self.sio.leave_room(sid, f"conversation_{conversation_id}")
        
        if conversation_id in self.conversation_rooms:
            if sid in self.conversation_rooms[conversation_id]:
                self.conversation_rooms[conversation_id].remove(sid)

    async def handle_message(self, sid: str, data: Dict) -> Optional[Message]:
        """Handle incoming message from socket"""
        if sid not in self.active_connections:
            return None
        
        try:
            user_id = self.active_connections[sid]["user_id"]
            conversation_id = data.get("conversation_id")
            receiver_id = data.get("receiver_id")
            content = data.get("content")
            
            if not all([conversation_id, receiver_id, content]):
                raise ValueError("Missing required message data")
            
            # Save message to database
            async with async_session() as session:
                message = Message(
                    conversation_id=conversation_id,
                    sender_id=user_id,
                    receiver_id=receiver_id,
                    content=content
                )
                session.add(message)
                await session.commit()
                await session.refresh(message)
                
                # Load sender data
                sender_result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                sender = sender_result.scalar_one()
                
                # Prepare message data for broadcast
                message_data = {
                    "id": str(message.id),
                    "conversation_id": str(message.conversation_id),
                    "sender_id": str(message.sender_id),
                    "receiver_id": str(message.receiver_id),
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                    "sender": {
                        "id": str(sender.id),
                        "full_name": sender.full_name,
                        "profile_image": sender.profile_image
                    }
                }
                
                return message_data
                
        except Exception as e:
            print(f"Error handling message: {e}")
            raise e

    async def broadcast_message(self, message_data: Dict):
        """Broadcast message to conversation participants"""
        conversation_id = message_data["conversation_id"]
        room = f"conversation_{conversation_id}"
        
        await self.sio.emit("new_message", message_data, room=room)

    async def broadcast_user_status(self, user_id: str, status: str):
        """Broadcast user online/offline status"""
        await self.sio.emit("user_status", {
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def send_typing_indicator(
        self, sid: str, conversation_id: str, is_typing: bool
    ):
        """Send typing indicator to conversation"""
        if sid not in self.active_connections:
            return
        
        user_data = self.active_connections[sid]["user_data"]
        room = f"conversation_{conversation_id}"
        
        await self.sio.emit("typing", {
            "user_id": user_data["id"],
            "user_name": user_data["full_name"],
            "is_typing": is_typing
        }, room=room, skip_sid=sid)

    def get_online_users(self) -> List[str]:
        """Get list of currently online user IDs"""
        return list(self.user_connections.keys())

    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is currently online"""
        return user_id in self.user_connections