"""
Celery Application Configuration - HireMeBahamas
=================================================
Celery for handling email and scheduled background tasks (non-blocking)

Setup:
1. Install Redis: Redis is required as the message broker
2. Set REDIS_URL environment variable
3. Start Celery worker: celery -A backend_app.core.celery_app worker --loglevel=info
4. (Optional) Start Flower for monitoring: celery -A backend_app.core.celery_app flower

Usage in endpoints:
    from backend_app.core.celery_tasks import send_welcome_email
    send_welcome_email.delay(user_email="user@example.com", user_name="John")
"""
import os
import logging
from celery import Celery

logger = logging.getLogger(__name__)

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app instance
celery_app = Celery(
    "hiremebahamas",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["backend_app.core.celery_tasks"]
)

# Celery Configuration
celery_app.conf.update(
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task result settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",  # For Redis Sentinel
    },
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks (prevent memory leaks)
    
    # Task routing - send email tasks to email queue
    task_routes={
        "backend_app.core.celery_tasks.send_*": {"queue": "emails"},
        "backend_app.core.celery_tasks.process_*": {"queue": "processing"},
    },
    
    # Task time limits
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit
    
    # Task retry settings
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
    
    # Broker connection settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        "cleanup-old-notifications": {
            "task": "backend_app.core.celery_tasks.cleanup_old_notifications",
            "schedule": 86400.0,  # Run daily (24 hours)
        },
    },
)

# Graceful shutdown
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True

logger.info(f"Celery app configured with broker: {REDIS_URL}")
