from typing import Optional

from app.core.security import get_current_user
from app.database import get_db
from app.models import Notification, NotificationType, User
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get("/list")
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of notifications for current user"""
    query = select(Notification).options(
        selectinload(Notification.actor)
    ).where(Notification.user_id == current_user.id)

    if unread_only:
        query = query.where(Notification.is_read == False)

    # Order by created_at descending (newest first)
    query = query.order_by(Notification.created_at.desc())

    # Get total count
    count_result = await db.execute(
        select(func.count(Notification.id)).where(Notification.user_id == current_user.id)
    )
    total = count_result.scalar()

    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()

    # Format notifications with actor information
    notifications_data = []
    for notification in notifications:
        actor_data = None
        if notification.actor:
            actor_data = {
                "id": notification.actor.id,
                "first_name": notification.actor.first_name,
                "last_name": notification.actor.last_name,
                "username": notification.actor.username,
                "avatar_url": notification.actor.avatar_url,
            }

        notifications_data.append(
            {
                "id": notification.id,
                "type": notification.notification_type.value,
                "content": notification.content,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "related_id": notification.related_id,
                "actor": actor_data,
            }
        )

    return {
        "success": True,
        "notifications": notifications_data,
        "total": total,
    }


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get count of unread notifications for user interactions only (likes, comments, mentions)"""
    # Define notification types that represent direct user interactions
    interaction_types = [
        NotificationType.LIKE,
        NotificationType.COMMENT,
        NotificationType.MENTION,
    ]
    
    result = await db.execute(
        select(func.count())
        .select_from(Notification)
        .where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False,
                Notification.notification_type.in_(interaction_types),
            )
        )
    )
    count = result.scalar()

    return {"success": True, "unread_count": count}


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a notification as read"""
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id,
            )
        )
    )
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notification.is_read = True
    await db.commit()

    return {"success": True, "message": "Notification marked as read"}


@router.put("/mark-all-read")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read for current user"""
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False,
            )
        )
    )
    notifications = result.scalars().all()

    for notification in notifications:
        notification.is_read = True

    await db.commit()

    return {
        "success": True,
        "message": f"Marked {len(notifications)} notifications as read",
    }
