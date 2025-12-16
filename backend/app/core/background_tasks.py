"""
Background Tasks Module - Non-Blocking Operations

Implements background task processing using FastAPI BackgroundTasks
to ensure API responses are not blocked by slow operations.

Use cases:
- Email notifications
- Push notifications  
- Feed fan-out operations
- Data aggregation
- Cleanup operations

DO NOT use this module for operations that block user requests.
All tasks should be fast, async, and non-critical to the immediate response.
"""
import logging
from typing import Optional, Dict, Any, List
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


# =============================================================================
# EMAIL NOTIFICATION TASKS
# =============================================================================

async def send_email_notification_task(
    recipient_email: str,
    subject: str,
    body: str,
    notification_type: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Background task for sending email notifications.
    
    This runs asynchronously and does not block the API response.
    Failures are logged but do not affect the API response.
    
    Args:
        recipient_email: Email address to send to
        subject: Email subject line
        body: Email body content
        notification_type: Type of notification (follow, like, comment, etc.)
        metadata: Additional metadata for the notification
    """
    try:
        logger.info(f"[Background] Sending {notification_type} email to {recipient_email}")
        
        # TODO: Implement actual email sending logic
        # Example integrations:
        # - SendGrid: await sendgrid.send(...)
        # - AWS SES: await ses_client.send_email(...)
        # - Mailgun: await mailgun.send(...)
        
        # For now, just log the action
        logger.info(f"[Background] Email notification queued: {subject}")
        
    except Exception as e:
        logger.error(f"[Background] Failed to send email notification: {e}", exc_info=True)
        # Don't raise - background tasks should not crash the application


async def send_welcome_email_task(
    recipient_email: str,
    first_name: str,
    username: str
):
    """Send welcome email to new users."""
    subject = f"Welcome to HireMeBahamas, {first_name}!"
    body = f"""
    Hi {first_name},
    
    Welcome to HireMeBahamas! Your account @{username} has been created successfully.
    
    Start exploring job opportunities and connecting with professionals in the Bahamas.
    
    Best regards,
    The HireMeBahamas Team
    """
    
    await send_email_notification_task(
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        notification_type="welcome",
        metadata={"username": username}
    )


async def send_job_application_email_task(
    employer_email: str,
    employer_name: str,
    applicant_name: str,
    job_title: str,
    job_id: int
):
    """Notify employer of new job application."""
    subject = f"New Application for {job_title}"
    body = f"""
    Hi {employer_name},
    
    {applicant_name} has applied for your job posting: {job_title}
    
    View the application in your dashboard.
    
    Best regards,
    The HireMeBahamas Team
    """
    
    await send_email_notification_task(
        recipient_email=employer_email,
        subject=subject,
        body=body,
        notification_type="job_application",
        metadata={"job_id": job_id, "applicant_name": applicant_name}
    )


# =============================================================================
# PUSH NOTIFICATION TASKS
# =============================================================================

async def send_push_notification_task(
    user_id: int,
    title: str,
    body: str,
    notification_type: str,
    data: Optional[Dict[str, Any]] = None
):
    """
    Background task for sending push notifications to mobile devices.
    
    This runs asynchronously and does not block the API response.
    
    Args:
        user_id: User ID to send notification to
        title: Notification title
        body: Notification body text
        notification_type: Type of notification
        data: Additional data payload for the notification
    """
    try:
        logger.info(f"[Background] Sending push notification to user {user_id}: {title}")
        
        # TODO: Implement actual push notification logic
        # Example integrations:
        # - Firebase Cloud Messaging (FCM): await fcm.send(...)
        # - Apple Push Notification Service (APNS): await apns.send(...)
        # - OneSignal: await onesignal.create_notification(...)
        
        # For now, just log the action
        logger.info(f"[Background] Push notification queued: {notification_type}")
        
    except Exception as e:
        logger.error(f"[Background] Failed to send push notification: {e}", exc_info=True)
        # Don't raise - background tasks should not crash the application


async def notify_new_follower_task(
    follower_id: int,
    follower_name: str,
    followed_user_id: int
):
    """Send push notification for new follower."""
    await send_push_notification_task(
        user_id=followed_user_id,
        title="New Follower",
        body=f"{follower_name} started following you",
        notification_type="follow",
        data={"follower_id": follower_id}
    )


async def notify_new_like_task(
    liker_id: int,
    liker_name: str,
    post_owner_id: int,
    post_id: int
):
    """Send push notification for post like."""
    await send_push_notification_task(
        user_id=post_owner_id,
        title="New Like",
        body=f"{liker_name} liked your post",
        notification_type="like",
        data={"liker_id": liker_id, "post_id": post_id}
    )


async def notify_new_comment_task(
    commenter_id: int,
    commenter_name: str,
    post_owner_id: int,
    post_id: int,
    comment_preview: str
):
    """Send push notification for new comment."""
    # Truncate comment preview to 50 characters
    preview = comment_preview[:50] + "..." if len(comment_preview) > 50 else comment_preview
    
    await send_push_notification_task(
        user_id=post_owner_id,
        title="New Comment",
        body=f"{commenter_name} commented: {preview}",
        notification_type="comment",
        data={"commenter_id": commenter_id, "post_id": post_id}
    )


async def notify_new_message_task(
    sender_id: int,
    sender_name: str,
    receiver_id: int,
    message_preview: str
):
    """Send push notification for new message."""
    # Truncate message preview to 50 characters
    preview = message_preview[:50] + "..." if len(message_preview) > 50 else message_preview
    
    await send_push_notification_task(
        user_id=receiver_id,
        title=f"Message from {sender_name}",
        body=preview,
        notification_type="message",
        data={"sender_id": sender_id}
    )


# =============================================================================
# FEED FAN-OUT TASKS
# =============================================================================

async def fanout_post_to_followers_task(
    post_id: int,
    author_id: int,
    db: AsyncSession
):
    """
    Background task to fan out post to followers' feeds.
    
    This is a write-heavy operation that should not block post creation.
    In a production system with millions of followers, this would use:
    - Message queues (RabbitMQ, Redis Streams)
    - Batch processing
    - Distributed task queues (Celery, RQ)
    
    Args:
        post_id: ID of the newly created post
        author_id: ID of the post author
        db: Database session
    """
    try:
        logger.info(f"[Background] Starting feed fan-out for post {post_id} by user {author_id}")
        
        # TODO: Implement actual fan-out logic
        # Example implementation:
        # 1. Get all followers of the author
        # 2. Create feed entries for each follower
        # 3. Batch insert feed entries
        # 4. Update follower notification counts
        
        # For now, just log the action
        logger.info(f"[Background] Feed fan-out completed for post {post_id}")
        
    except Exception as e:
        logger.error(f"[Background] Failed to fan out post {post_id}: {e}", exc_info=True)
        # Don't raise - background tasks should not crash the application


async def aggregate_user_stats_task(
    user_id: int,
    db: AsyncSession
):
    """
    Background task to aggregate user statistics.
    
    Updates cached counts for:
    - Total posts
    - Total followers
    - Total following
    - Total likes received
    
    Args:
        user_id: ID of the user to update stats for
        db: Database session
    """
    try:
        logger.info(f"[Background] Aggregating stats for user {user_id}")
        
        # TODO: Implement actual aggregation logic
        # Example:
        # 1. Count posts by user
        # 2. Count followers
        # 3. Count following
        # 4. Count likes on user's posts
        # 5. Update user record or cache
        
        logger.info(f"[Background] Stats aggregation completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"[Background] Failed to aggregate stats for user {user_id}: {e}", exc_info=True)


# =============================================================================
# CLEANUP TASKS
# =============================================================================

async def cleanup_expired_sessions_task(db: AsyncSession):
    """Background task to clean up expired sessions."""
    try:
        logger.info("[Background] Starting expired session cleanup")
        
        # TODO: Implement session cleanup logic
        # Example:
        # 1. Find sessions older than expiration time
        # 2. Delete expired sessions
        # 3. Log cleanup statistics
        
        logger.info("[Background] Session cleanup completed")
        
    except Exception as e:
        logger.error(f"[Background] Failed to cleanup expired sessions: {e}", exc_info=True)


async def cleanup_old_notifications_task(
    db: AsyncSession,
    days_to_keep: int = 90
):
    """
    Background task to clean up old notifications.
    
    Args:
        db: Database session
        days_to_keep: Number of days to keep notifications (default: 90)
    """
    try:
        logger.info(f"[Background] Starting notification cleanup (keeping {days_to_keep} days)")
        
        # TODO: Implement notification cleanup logic
        # Example:
        # 1. Find read notifications older than days_to_keep
        # 2. Delete old notifications in batches
        # 3. Log cleanup statistics
        
        logger.info("[Background] Notification cleanup completed")
        
    except Exception as e:
        logger.error(f"[Background] Failed to cleanup old notifications: {e}", exc_info=True)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def add_email_notification(
    background_tasks: BackgroundTasks,
    recipient_email: str,
    subject: str,
    body: str,
    notification_type: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Convenience function to add email notification to background tasks.
    
    Usage in API endpoints:
        add_email_notification(
            background_tasks=background_tasks,
            recipient_email="user@example.com",
            subject="Welcome!",
            body="Welcome to HireMeBahamas",
            notification_type="welcome"
        )
    """
    background_tasks.add_task(
        send_email_notification_task,
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        notification_type=notification_type,
        metadata=metadata
    )


def add_push_notification(
    background_tasks: BackgroundTasks,
    user_id: int,
    title: str,
    body: str,
    notification_type: str,
    data: Optional[Dict[str, Any]] = None
):
    """
    Convenience function to add push notification to background tasks.
    
    Usage in API endpoints:
        add_push_notification(
            background_tasks=background_tasks,
            user_id=123,
            title="New Follower",
            body="John Doe started following you",
            notification_type="follow"
        )
    """
    background_tasks.add_task(
        send_push_notification_task,
        user_id=user_id,
        title=title,
        body=body,
        notification_type=notification_type,
        data=data
    )


def add_fanout_task(
    background_tasks: BackgroundTasks,
    post_id: int,
    author_id: int,
    db: AsyncSession
):
    """
    Convenience function to add feed fan-out to background tasks.
    
    Usage in API endpoints:
        add_fanout_task(
            background_tasks=background_tasks,
            post_id=post.id,
            author_id=current_user.id,
            db=db
        )
    """
    background_tasks.add_task(
        fanout_post_to_followers_task,
        post_id=post_id,
        author_id=author_id,
        db=db
    )
