"""
Notification Helpers - HireMeBahamas (Step 10)
================================================
Helper functions for creating notifications in background tasks.
"""
import logging
from typing import Optional
from datetime import datetime
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    user_id: int,
    actor_id: Optional[int],
    notification_type: str,
    content: str,
    related_id: Optional[int] = None
):
    """
    Create a notification in the database.
    
    This is a helper function that can be called directly or via background tasks.
    
    Args:
        db: Database session
        user_id: User receiving the notification
        actor_id: User who triggered the notification
        notification_type: Type of notification (from NotificationType enum)
        content: Notification message
        related_id: ID of related entity (job, post, etc.)
    """
    try:
        from app.models import Notification
        from sqlalchemy import insert
        
        # Create notification record
        stmt = insert(Notification).values(
            user_id=user_id,
            actor_id=actor_id,
            notification_type=notification_type,
            content=content,
            related_id=related_id,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        await db.execute(stmt)
        await db.commit()
        
        logger.info(f"Created notification for user {user_id}: {notification_type}")
        
    except Exception as e:
        logger.error(f"Failed to create notification for user {user_id}: {e}")
        await db.rollback()


def schedule_notification(
    background_tasks: BackgroundTasks,
    db: AsyncSession,
    user_id: int,
    actor_id: Optional[int],
    notification_type: str,
    content: str,
    related_id: Optional[int] = None,
    send_push: bool = True,
    send_email: bool = False,
    email_subject: Optional[str] = None,
    email_body: Optional[str] = None,
):
    """
    Schedule a notification to be created in the background.
    
    This function adds notification creation to the background tasks queue,
    preventing it from blocking the HTTP response.
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance
        db: Database session
        user_id: User receiving the notification
        actor_id: User who triggered the notification
        notification_type: Type of notification
        content: Notification message
        related_id: ID of related entity
        send_push: Whether to send push notification
        send_email: Whether to send email notification
        email_subject: Email subject (if send_email=True)
        email_body: Email body (if send_email=True)
    """
    # Add database notification creation to background tasks
    background_tasks.add_task(
        create_notification,
        db=db,
        user_id=user_id,
        actor_id=actor_id,
        notification_type=notification_type,
        content=content,
        related_id=related_id
    )
    
    # Optionally send push notification
    if send_push:
        from app.core.background_tasks import send_push_notification
        background_tasks.add_task(
            send_push_notification,
            user_id=user_id,
            title="New Notification",
            body=content,
            data={"type": notification_type, "related_id": related_id}
        )
    
    # Optionally send email notification
    if send_email and email_subject and email_body:
        # Need to fetch user email first - this should be passed in
        from app.core.background_tasks import send_email_notification
        # This is a placeholder - in practice, pass email address directly
        logger.info(f"Email notification scheduled for user {user_id}")


def schedule_follow_notification(
    background_tasks: BackgroundTasks,
    db: AsyncSession,
    followed_user_id: int,
    follower_id: int,
    follower_name: str
):
    """Schedule a follow notification."""
    schedule_notification(
        background_tasks=background_tasks,
        db=db,
        user_id=followed_user_id,
        actor_id=follower_id,
        notification_type="follow",
        content=f"{follower_name} started following you",
        send_push=True
    )


def schedule_like_notification(
    background_tasks: BackgroundTasks,
    db: AsyncSession,
    post_owner_id: int,
    liker_id: int,
    liker_name: str,
    post_id: int
):
    """Schedule a like notification."""
    schedule_notification(
        background_tasks=background_tasks,
        db=db,
        user_id=post_owner_id,
        actor_id=liker_id,
        notification_type="like",
        content=f"{liker_name} liked your post",
        related_id=post_id,
        send_push=True
    )


def schedule_comment_notification(
    background_tasks: BackgroundTasks,
    db: AsyncSession,
    post_owner_id: int,
    commenter_id: int,
    commenter_name: str,
    post_id: int
):
    """Schedule a comment notification."""
    schedule_notification(
        background_tasks=background_tasks,
        db=db,
        user_id=post_owner_id,
        actor_id=commenter_id,
        notification_type="comment",
        content=f"{commenter_name} commented on your post",
        related_id=post_id,
        send_push=True
    )


def schedule_message_notification(
    background_tasks: BackgroundTasks,
    db: AsyncSession,
    receiver_id: int,
    sender_id: int,
    sender_name: str,
    receiver_email: Optional[str] = None
):
    """Schedule a message notification."""
    schedule_notification(
        background_tasks=background_tasks,
        db=db,
        user_id=receiver_id,
        actor_id=sender_id,
        notification_type="message",
        content=f"New message from {sender_name}",
        send_push=True
    )
    
    # Optionally send email if provided
    if receiver_email:
        from app.core.background_tasks import send_message_notification_email
        background_tasks.add_task(
            send_message_notification_email,
            recipient_email=receiver_email,
            recipient_name="User",  # Should be passed in
            sender_name=sender_name
        )


def schedule_job_application_notification(
    background_tasks: BackgroundTasks,
    db: AsyncSession,
    employer_id: int,
    applicant_id: int,
    applicant_name: str,
    job_id: int,
    job_title: str,
    employer_email: Optional[str] = None,
    employer_name: Optional[str] = None
):
    """Schedule a job application notification."""
    schedule_notification(
        background_tasks=background_tasks,
        db=db,
        user_id=employer_id,
        actor_id=applicant_id,
        notification_type="job_application",
        content=f"{applicant_name} applied for {job_title}",
        related_id=job_id,
        send_push=True
    )
    
    # Send email to employer
    if employer_email and employer_name:
        from app.core.background_tasks import send_job_application_email
        background_tasks.add_task(
            send_job_application_email,
            employer_email=employer_email,
            employer_name=employer_name,
            job_title=job_title,
            applicant_name=applicant_name
        )
