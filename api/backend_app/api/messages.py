from typing import List, Optional

from app.core.security import get_current_user
from app.database import get_db
from app.models import Conversation, Message, Notification, NotificationType, User
from app.schemas.message import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or get existing conversation between two users"""
    # Check if conversation already exists
    existing_conversation = await db.execute(
        select(Conversation).where(
            or_(
                and_(
                    Conversation.participant_1_id == current_user.id,
                    Conversation.participant_2_id == conversation.participant_id,
                ),
                and_(
                    Conversation.participant_1_id == conversation.participant_id,
                    Conversation.participant_2_id == current_user.id,
                ),
            )
        )
    )

    existing = existing_conversation.scalar_one_or_none()
    if existing:
        # Load participants
        result = await db.execute(
            select(Conversation)
            .options(
                selectinload(Conversation.participant_1),
                selectinload(Conversation.participant_2),
            )
            .where(Conversation.id == existing.id)
        )
        return result.scalar_one()

    # Create new conversation
    db_conversation = Conversation(
        participant_1_id=current_user.id, participant_2_id=conversation.participant_id
    )
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)

    # Load participants
    result = await db.execute(
        select(Conversation)
        .options(
            selectinload(Conversation.participant_1),
            selectinload(Conversation.participant_2),
        )
        .where(Conversation.id == db_conversation.id)
    )

    return result.scalar_one()


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get all conversations for the current user"""
    result = await db.execute(
        select(Conversation)
        .options(
            selectinload(Conversation.participant_1),
            selectinload(Conversation.participant_2),
            selectinload(Conversation.messages).selectinload(Message.sender),
        )
        .where(
            or_(
                Conversation.participant_1_id == current_user.id,
                Conversation.participant_2_id == current_user.id,
            )
        )
        .order_by(desc(Conversation.updated_at))
    )

    conversations = result.scalars().all()
    return conversations


@router.get(
    "/conversations/{conversation_id}/messages", response_model=List[MessageResponse]
)
async def get_conversation_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=50),  # Max 50 for mobile optimization
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get messages in a conversation (optimized for mobile)"""
    # Check if user is participant in conversation
    conversation_result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                or_(
                    Conversation.participant_1_id == current_user.id,
                    Conversation.participant_2_id == current_user.id,
                ),
            )
        )
    )

    conversation = conversation_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied",
        )

    # Get messages
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.sender), selectinload(Message.receiver))
        .where(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
        .offset(skip)
        .limit(limit)
    )

    messages = result.scalars().all()
    return messages


@router.post(
    "/conversations/{conversation_id}/messages", response_model=MessageResponse
)
async def send_message(
    conversation_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message in a conversation"""
    # Check if user is participant in conversation
    conversation_result = await db.execute(
        select(Conversation).where(
            and_(
                Conversation.id == conversation_id,
                or_(
                    Conversation.participant_1_id == current_user.id,
                    Conversation.participant_2_id == current_user.id,
                ),
            )
        )
    )

    conversation = conversation_result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied",
        )

    # Determine receiver
    receiver_id = (
        conversation.participant_2_id
        if conversation.participant_1_id == current_user.id
        else conversation.participant_1_id
    )

    # Create message
    db_message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=message.content,
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)

    # Create notification for the receiver
    # Use sender name with fallback values for null safety
    sender_first_name = current_user.first_name or "Someone"
    sender_last_name = current_user.last_name or ""
    sender_display_name = f"{sender_first_name} {sender_last_name}".strip()
    
    try:
        notification = Notification(
            user_id=receiver_id,
            actor_id=current_user.id,
            notification_type=NotificationType.MESSAGE,
            content=f"{sender_display_name} sent you a message",
            related_id=conversation_id,
        )
        db.add(notification)
        await db.commit()
    except Exception:
        # Log notification failure but don't fail the message send
        # The message was already saved successfully
        pass

    # Load relationships
    result = await db.execute(
        select(Message)
        .options(selectinload(Message.sender), selectinload(Message.receiver))
        .where(Message.id == db_message.id)
    )

    message_with_relations = result.scalar_one()
    return message_with_relations


@router.put("/messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a message as read"""
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
        )

    if message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only mark your own received messages as read",
        )

    message.is_read = True
    await db.commit()

    return {"message": "Message marked as read"}


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get count of unread messages for current user"""
    result = await db.execute(
        select(Message).where(
            and_(Message.receiver_id == current_user.id, Message.is_read.is_(False))
        )
    )

    unread_messages = result.scalars().all()
    return {"unread_count": len(unread_messages)}
