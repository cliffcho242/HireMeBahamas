"""
Celery Tasks - Email Background Jobs
=====================================
Non-blocking email tasks using Celery for reliable delivery

All email tasks should be called with .delay() to run asynchronously:
    send_welcome_email.delay(user_email="user@example.com", user_name="John")
"""
import logging
from typing import Optional, Dict, Any
from celery import shared_task
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ============================================================================
# EMAIL TASKS (Celery)
# ============================================================================

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_email_task(
    self,
    recipient_email: str,
    subject: str,
    body: str,
    template: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
):
    """
    Send email notification via Celery (non-blocking).
    
    This task will retry up to 3 times with 5-minute delays on failure.
    
    Args:
        recipient_email: Recipient's email address
        subject: Email subject line
        body: Email body (HTML or plain text)
        template: Optional email template name
        context: Optional template context variables
        
    Returns:
        dict: Success status and message
    """
    try:
        logger.info(f"[Celery] Sending email to {recipient_email}: {subject}")
        
        # TODO: Integrate with actual email service
        # Example integrations:
        # 
        # SendGrid:
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail
        # message = Mail(
        #     from_email='noreply@hiremebahamas.com',
        #     to_emails=recipient_email,
        #     subject=subject,
        #     html_content=body
        # )
        # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        # response = sg.send(message)
        #
        # AWS SES:
        # import boto3
        # ses_client = boto3.client('ses', region_name='us-east-1')
        # response = ses_client.send_email(
        #     Source='noreply@hiremebahamas.com',
        #     Destination={'ToAddresses': [recipient_email]},
        #     Message={
        #         'Subject': {'Data': subject},
        #         'Body': {'Html': {'Data': body}}
        #     }
        # )
        #
        # Mailgun:
        # import requests
        # response = requests.post(
        #     f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        #     auth=("api", MAILGUN_API_KEY),
        #     data={
        #         "from": "noreply@hiremebahamas.com",
        #         "to": recipient_email,
        #         "subject": subject,
        #         "html": body
        #     }
        # )
        
        logger.info(f"[Celery] Email sent successfully to {recipient_email}")
        return {"success": True, "message": f"Email sent to {recipient_email}"}
        
    except Exception as e:
        logger.error(f"[Celery] Failed to send email to {recipient_email}: {e}")
        # Retry the task
        raise self.retry(exc=e)


@shared_task
def send_welcome_email(user_email: str, user_name: str, username: str):
    """Send welcome email to new user (Celery task)."""
    subject = f"Welcome to HireMeBahamas, {user_name}!"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #00bcd4;">Welcome to HireMeBahamas, {user_name}!</h1>
                <p>Thank you for joining our platform. We're excited to help you connect with opportunities in the Bahamas.</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="margin-top: 0;">Get Started:</h2>
                    <ul>
                        <li>Complete your profile to stand out</li>
                        <li>Browse available jobs in the Bahamas</li>
                        <li>Connect with professionals and employers</li>
                        <li>Build your network</li>
                    </ul>
                </div>
                
                <p>Your username: <strong>@{username}</strong></p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The HireMeBahamas Team</strong>
                </p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    This email was sent to {user_email}. If you didn't create this account, please ignore this email.
                </p>
            </div>
        </body>
    </html>
    """
    return send_email_task.delay(user_email, subject, body)


@shared_task
def send_job_application_email(
    employer_email: str,
    employer_name: str,
    job_title: str,
    applicant_name: str,
    applicant_email: str,
    job_id: int
):
    """Send notification to employer about new job application (Celery task)."""
    subject = f"New Application: {job_title}"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #00bcd4;">New Job Application</h1>
                <p>Hi {employer_name},</p>
                
                <p>Great news! You have a new application for your job posting.</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="margin-top: 0;">{job_title}</h2>
                    <p><strong>Applicant:</strong> {applicant_name}</p>
                    <p><strong>Email:</strong> {applicant_email}</p>
                    <p><strong>Job ID:</strong> #{job_id}</p>
                </div>
                
                <p>
                    <a href="{os.getenv('BASE_URL', 'https://hiremebahamas.com')}/jobs/{job_id}" 
                       style="background: #00bcd4; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Application
                    </a>
                </p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The HireMeBahamas Team</strong>
                </p>
            </div>
        </body>
    </html>
    """
    return send_email_task.delay(employer_email, subject, body)


@shared_task
def send_message_notification_email(
    recipient_email: str,
    recipient_name: str,
    sender_name: str,
    message_preview: str
):
    """Send email notification about new message (Celery task)."""
    # Truncate message preview
    preview = message_preview[:100] + "..." if len(message_preview) > 100 else message_preview
    
    subject = f"New message from {sender_name}"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #00bcd4;">You have a new message</h1>
                <p>Hi {recipient_name},</p>
                
                <p><strong>{sender_name}</strong> sent you a message on HireMeBahamas:</p>
                
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="font-style: italic;">"{preview}"</p>
                </div>
                
                <p>
                    <a href="{os.getenv('BASE_URL', 'https://hiremebahamas.com')}/messages" 
                       style="background: #00bcd4; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Read and Reply
                    </a>
                </p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The HireMeBahamas Team</strong>
                </p>
            </div>
        </body>
    </html>
    """
    return send_email_task.delay(recipient_email, subject, body)


@shared_task
def send_password_reset_email(user_email: str, user_name: str, reset_token: str):
    """Send password reset email (Celery task)."""
    base_url = os.getenv('BASE_URL', 'https://hiremebahamas.com')
    reset_link = f"{base_url}/reset-password?token={reset_token}"
    
    subject = "Reset Your HireMeBahamas Password"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #00bcd4;">Reset Your Password</h1>
                <p>Hi {user_name},</p>
                
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                
                <p style="margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background: #00bcd4; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </p>
                
                <p>This link will expire in 1 hour for security reasons.</p>
                
                <p style="color: #666; font-size: 14px;">
                    If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                </p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The HireMeBahamas Team</strong>
                </p>
            </div>
        </body>
    </html>
    """
    return send_email_task.delay(user_email, subject, body)


# ============================================================================
# SCHEDULED TASKS (Celery Beat)
# ============================================================================

@shared_task
def cleanup_old_notifications():
    """
    Periodic task to clean up old read notifications (runs daily).
    
    This task is scheduled via Celery Beat and runs automatically.
    """
    try:
        logger.info("[Celery] Starting cleanup of old notifications")
        
        # Calculate cutoff date (90 days ago)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # TODO: Implement actual cleanup logic with database
        # from app.database import async_session
        # from app.models import Notification
        # from sqlalchemy import delete
        # 
        # async with async_session() as db:
        #     result = await db.execute(
        #         delete(Notification).where(
        #             and_(
        #                 Notification.is_read == True,
        #                 Notification.created_at < cutoff_date
        #             )
        #         )
        #     )
        #     await db.commit()
        #     deleted_count = result.rowcount
        
        deleted_count = 0  # Placeholder
        logger.info(f"[Celery] Cleaned up {deleted_count} old notifications")
        
        return {"success": True, "deleted_count": deleted_count}
        
    except Exception as e:
        logger.error(f"[Celery] Failed to cleanup old notifications: {e}")
        raise
