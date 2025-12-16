"""
Background Jobs Infrastructure for HireMeBahamas

Implements non-blocking background task processing for:
- Email notifications
- Push notifications  
- Feed fan-out operations
- Other async tasks that shouldn't block HTTP requests

This uses a thread pool executor for lightweight background processing
without blocking the main request/response cycle.

For scaling beyond 100K+ users, consider migrating to:
- Celery (with Redis/RabbitMQ)
- RQ (Redis Queue)
- FastAPI BackgroundTasks (if using FastAPI)
"""
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

# Thread pool for background jobs
# Size: Configurable via BACKGROUND_WORKERS environment variable (default: 4)
# This provides enough concurrency for typical background operations
# Increase for high-volume deployments (e.g., BACKGROUND_WORKERS=8)
_background_workers = int(os.getenv("BACKGROUND_WORKERS", "4"))
_background_executor = ThreadPoolExecutor(
    max_workers=_background_workers,
    thread_name_prefix="background_job"
)

logger.info(f"Background job executor initialized with {_background_workers} workers")


def run_in_background(func: Callable) -> Callable:
    """
    Decorator to run a function in the background without blocking the request.
    
    Usage:
        @run_in_background
        def send_email(to: str, subject: str, body: str):
            # Email sending logic here
            pass
            
        # Call it normally - it will run in background
        send_email("user@example.com", "Welcome", "Hello!")
        # Request returns immediately, email sends in background
    
    Args:
        func: Function to run in background
        
    Returns:
        Wrapper function that submits to thread pool
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        future = _background_executor.submit(func, *args, **kwargs)
        
        # Add error handling callback
        def handle_result(f):
            try:
                result = f.result()
                logger.info(f"Background job {func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Background job {func.__name__} failed: {e}", exc_info=True)
        
        future.add_done_callback(handle_result)
        return future
    
    return wrapper


def submit_background_job(func: Callable, *args, **kwargs) -> Any:
    """
    Submit a function to run in the background.
    
    This is an alternative to the decorator for one-off background tasks.
    
    Usage:
        def process_data(data):
            # Processing logic
            pass
            
        submit_background_job(process_data, my_data)
    
    Args:
        func: Function to execute in background
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Future object representing the background task
    """
    return _background_executor.submit(func, *args, **kwargs)


# =============================================================================
# Background Job Functions
# =============================================================================

@run_in_background
def send_email_async(to: str, subject: str, body: str, **options):
    """
    Send an email in the background without blocking the request.
    
    This is a placeholder implementation. In production, integrate with:
    - SendGrid
    - Amazon SES
    - Mailgun
    - SMTP server
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (can be HTML)
        **options: Additional email options (cc, bcc, attachments, etc.)
    """
    try:
        logger.info(f"Sending email to {to}: {subject}")
        
        # TODO: Implement actual email sending logic
        # Example:
        # import sendgrid
        # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        # message = Mail(from_email='noreply@hiremebahamas.com', to_emails=to, 
        #                subject=subject, html_content=body)
        # sg.send(message)
        
        # For now, just log it
        logger.info(f"Email sent successfully to {to}")
        
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}", exc_info=True)
        raise


@run_in_background
def send_push_notification_async(user_id: int, title: str, body: str, data: dict = None):
    """
    Send a push notification in the background.
    
    This is a placeholder implementation. In production, integrate with:
    - Firebase Cloud Messaging (FCM)
    - Apple Push Notification Service (APNS)
    - OneSignal
    - Pusher
    
    Args:
        user_id: Target user ID
        title: Notification title
        body: Notification body
        data: Optional data payload for the notification
    """
    try:
        logger.info(f"Sending push notification to user {user_id}: {title}")
        
        # TODO: Implement actual push notification logic
        # Example:
        # import firebase_admin
        # from firebase_admin import messaging
        # message = messaging.Message(
        #     notification=messaging.Notification(title=title, body=body),
        #     data=data or {},
        #     token=get_user_fcm_token(user_id)
        # )
        # messaging.send(message)
        
        # For now, just log it
        logger.info(f"Push notification sent successfully to user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send push notification to user {user_id}: {e}", exc_info=True)
        raise


@run_in_background
def fanout_feed_update_async(post_id: int, author_id: int, follower_ids: list[int]):
    """
    Fan out a new post to all followers' feeds in the background.
    
    This implements the "fan-out on write" pattern used by social networks
    like Twitter/X to populate follower feeds when a user posts.
    
    For 100K+ users, consider:
    - Batching updates in chunks
    - Using a message queue (Redis, RabbitMQ)
    - Hybrid fan-out (write for active users, read for inactive)
    
    Args:
        post_id: ID of the new post
        author_id: ID of the post author
        follower_ids: List of follower user IDs to update
    """
    try:
        start_time = time.time()
        logger.info(f"Fanning out post {post_id} to {len(follower_ids)} followers")
        
        # TODO: Implement actual feed fan-out logic
        # Example:
        # from backend.database import get_db_connection
        # conn = get_db_connection()
        # cursor = conn.cursor()
        # 
        # # Batch insert into feed_items table
        # for follower_id in follower_ids:
        #     cursor.execute(
        #         "INSERT INTO feed_items (user_id, post_id, created_at) VALUES (%s, %s, NOW())",
        #         (follower_id, post_id)
        #     )
        # conn.commit()
        # cursor.close()
        # conn.close()
        
        elapsed = time.time() - start_time
        logger.info(f"Feed fan-out completed for post {post_id} in {elapsed:.2f}s")
        
    except Exception as e:
        logger.error(f"Failed to fan out post {post_id}: {e}", exc_info=True)
        raise


@run_in_background
def process_image_async(image_path: str, sizes: list[tuple] = None):
    """
    Process and resize images in the background.
    
    Useful for profile pictures, post images, etc.
    
    Args:
        image_path: Path to the original image
        sizes: List of (width, height) tuples for thumbnails
    """
    try:
        logger.info(f"Processing image: {image_path}")
        
        # TODO: Implement image processing
        # Example:
        # from PIL import Image
        # img = Image.open(image_path)
        # for width, height in (sizes or [(200, 200), (500, 500)]):
        #     thumbnail = img.resize((width, height), Image.LANCZOS)
        #     thumbnail.save(f"{image_path}_thumb_{width}x{height}.jpg")
        
        logger.info(f"Image processing completed: {image_path}")
        
    except Exception as e:
        logger.error(f"Failed to process image {image_path}: {e}", exc_info=True)
        raise


def shutdown_background_jobs(wait: bool = True, timeout: float = 30.0):
    """
    Shutdown the background job executor gracefully.
    
    Call this when the application is shutting down to ensure
    all background jobs complete.
    
    Args:
        wait: If True, wait for jobs to complete before shutting down
        timeout: Maximum time to wait for jobs in seconds (Python 3.9+ only)
    """
    logger.info("Shutting down background job executor...")
    
    # Python 3.9+ supports timeout parameter
    import sys
    if sys.version_info >= (3, 9):
        _background_executor.shutdown(wait=wait, timeout=timeout)
    else:
        # Python 3.8 and earlier don't support timeout
        _background_executor.shutdown(wait=wait)
    
    logger.info("Background job executor shut down")


# =============================================================================
# Example Usage
# =============================================================================
"""
# In your Flask route:

from backend.background_jobs import send_email_async, fanout_feed_update_async

@app.route('/api/posts', methods=['POST'])
def create_post():
    # Create the post (fast, synchronous)
    post_id = save_post_to_database(data)
    
    # Fan out to followers (slow, background)
    follower_ids = get_follower_ids(current_user_id)
    fanout_feed_update_async(post_id, current_user_id, follower_ids)
    
    # Send notification email (slow, background)
    send_email_async(
        to="user@example.com",
        subject="New post from someone you follow",
        body="Check out the new post!"
    )
    
    # Return immediately without waiting for background tasks
    return jsonify({"post_id": post_id}), 201
"""
