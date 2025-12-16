from typing import Optional

from app.core.security import get_current_user
from app.core.pagination import PaginationParams, get_pagination_metadata
from app.database import get_db
from app.models import Notification, NotificationType, User
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.get("/list")
async def get_notifications(
    response: Response,
    pagination: PaginationParams = Depends(),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of notifications for current user
    
    Mobile Optimization:
    - Supports both ?page=1&limit=20 and ?skip=0&limit=20 pagination
    - HTTP caching with Cache-Control: public, max-age=30
    - Small JSON payloads (max 100 items per page)
    - Optimized actor data loading with selectinload
    """
    query = select(Notification).options(
        selectinload(Notification.actor)
    ).where(Notification.user_id == current_user.id)

    if unread_only:
        query = query.where(Notification.is_read == False)

    # Order by created_at descending (newest first)
    query = query.order_by(Notification.created_at.desc())

    # Get total count efficiently
    count_query = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id
    )
    if unread_only:
        count_query = count_query.where(Notification.is_read == False)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    # Apply pagination
    query = query.offset(pagination.skip).limit(pagination.limit)
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

    # Add HTTP cache headers for mobile optimization
    response.headers["Cache-Control"] = "public, max-age=30"

    return {
        "success": True,
        "notifications": notifications_data,
        "pagination": get_pagination_metadata(
            total=total,
            page=pagination.page,
            skip=pagination.skip,
            limit=pagination.limit
        )
    }


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get count of unread notifications for user interactions only (likes, comments, mentions, messages)"""
    # Define notification types that represent direct user interactions
    interaction_types = [
        NotificationType.LIKE,
        NotificationType.COMMENT,
        NotificationType.MENTION,
        NotificationType.MESSAGE,
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
