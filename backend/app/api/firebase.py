"""
Firebase Realtime API Endpoints

This module provides API endpoints for Firebase Realtime Database operations.
These endpoints demonstrate how to use Firebase for real-time features.

Note: These endpoints will gracefully handle cases where Firebase is not configured.

SECURITY WARNING: These endpoints currently lack authentication and authorization.
In production, you should:
1. Add authentication middleware to verify user identity
2. Add authorization checks to ensure users can only access their own data
3. Implement Firebase security rules on the Firebase Console
4. Use the authenticated user's ID from the JWT token instead of accepting it in the request body

Example with authentication (to be implemented):
    from ..core.auth import get_current_user
    
    @router.post("/messages/{room_id}")
    async def send_message(
        room_id: str,
        message: FirebaseMessage,
        current_user = Depends(get_current_user)
    ):
        # Verify user has access to this room
        # Use current_user.id instead of message.userId
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from ..core.firebase_service import firebase_service

router = APIRouter()


class FirebaseMessage(BaseModel):
    """Model for a message in Firebase"""
    text: str
    userId: int
    username: str
    timestamp: str


class FirebasePresence(BaseModel):
    """Model for user presence tracking"""
    userId: int
    online: bool
    lastSeen: str


@router.get("/health")
async def firebase_health():
    """
    Check if Firebase is configured and available
    
    Returns:
        dict: Status of Firebase service
    """
    is_available = firebase_service.is_available()
    return {
        "firebase_available": is_available,
        "message": "Firebase Realtime Database is configured and ready" if is_available else "Firebase is not configured. Real-time features will use PostgreSQL fallback.",
        "status": "healthy" if is_available else "disabled"
    }


@router.post("/messages/{room_id}")
async def send_message(room_id: str, message: FirebaseMessage):
    """
    Send a message to a chat room using Firebase
    
    Args:
        room_id: Chat room identifier
        message: Message data
        
    Returns:
        dict: Message ID and status
    """
    if not firebase_service.is_available():
        # Fallback: could store in PostgreSQL instead
        raise HTTPException(
            status_code=503,
            detail="Firebase not configured. Please set up Firebase to use real-time chat."
        )
    
    message_data = message.model_dump()
    message_key = firebase_service.create(f'messages/{room_id}', message_data)
    
    if message_key is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to send message to Firebase"
        )
    
    return {
        "message_id": message_key,
        "status": "sent",
        "room_id": room_id
    }


@router.get("/messages/{room_id}")
async def get_messages(room_id: str, limit: Optional[int] = 50):
    """
    Get messages from a chat room
    
    Args:
        room_id: Chat room identifier
        limit: Maximum number of messages to retrieve (1-1000)
        
    Returns:
        list: List of messages
    """
    if not firebase_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Firebase not configured"
        )
    
    # Validate limit parameter
    if limit is not None and (limit <= 0 or limit > 1000):
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 1000"
        )
    
    messages = firebase_service.query(
        f'messages/{room_id}',
        order_by='timestamp',
        limit=limit
    )
    
    return messages


@router.put("/presence/{user_id}")
async def update_presence(user_id: int, presence: FirebasePresence):
    """
    Update user presence (online/offline status)
    
    Args:
        user_id: User identifier
        presence: Presence data
        
    Returns:
        dict: Status
    """
    if not firebase_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Firebase not configured"
        )
    
    presence_data = presence.model_dump()
    success = firebase_service.set(f'presence/{user_id}', presence_data)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to update presence"
        )
    
    return {"status": "updated", "user_id": user_id}


@router.get("/presence/{user_id}")
async def get_presence(user_id: int):
    """
    Get user presence status
    
    Args:
        user_id: User identifier
        
    Returns:
        dict: User presence data
    """
    if not firebase_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Firebase not configured"
        )
    
    presence = firebase_service.read(f'presence/{user_id}')
    
    if presence is None:
        return {"online": False, "lastSeen": None}
    
    return presence


@router.delete("/messages/{room_id}/{message_id}")
async def delete_message(room_id: str, message_id: str):
    """
    Delete a message from a chat room
    
    Args:
        room_id: Chat room identifier
        message_id: Message identifier
        
    Returns:
        dict: Status
    """
    if not firebase_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Firebase not configured"
        )
    
    success = firebase_service.delete(f'messages/{room_id}/{message_id}')
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete message"
        )
    
    return {"status": "deleted", "message_id": message_id}


@router.get("/rooms")
async def list_rooms():
    """
    List all available chat rooms
    
    Returns:
        list: List of room IDs
    """
    if not firebase_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="Firebase not configured"
        )
    
    rooms = firebase_service.read('messages')
    
    if rooms is None or not isinstance(rooms, dict):
        return []
    
    return [
        {"room_id": room_id, "message_count": len(messages) if isinstance(messages, (dict, list)) else 0}
        for room_id, messages in rooms.items()
    ]
