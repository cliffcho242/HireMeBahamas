"""
RQ (Redis Queue) Configuration - HireMeBahamas
===============================================
RQ for handling push notification tasks (non-blocking, simple queue)

Setup:
1. Install Redis: Redis is required as the queue backend
2. Set REDIS_URL environment variable
3. Start RQ worker: rq worker notifications --url redis://localhost:6379/0

Usage in endpoints:
    from backend_app.core.rq_app import notification_queue
    from backend_app.core.rq_tasks import send_push_notification_job
    
    notification_queue.enqueue(
        send_push_notification_job,
        user_id=user.id,
        title="New Follower",
        body="John Doe started following you"
    )
"""
import os
import logging
from redis import Redis
from rq import Queue
from rq.job import Job

logger = logging.getLogger(__name__)

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Redis connection
try:
    redis_conn = Redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
        health_check_interval=30
    )
    
    # Test connection
    redis_conn.ping()
    logger.info(f"RQ Redis connection established: {REDIS_URL}")
    
except Exception as e:
    logger.warning(f"Failed to connect to Redis for RQ: {e}")
    redis_conn = None

# Create RQ queues for different task types
notification_queue = Queue("notifications", connection=redis_conn) if redis_conn else None
analytics_queue = Queue("analytics", connection=redis_conn) if redis_conn else None
video_queue = Queue("video_processing", connection=redis_conn) if redis_conn else None

# Queue configuration
QUEUE_CONFIG = {
    "notifications": {
        "timeout": 300,  # 5 minutes
        "result_ttl": 600,  # Keep results for 10 minutes
        "failure_ttl": 86400,  # Keep failed jobs for 24 hours
    },
    "analytics": {
        "timeout": 600,  # 10 minutes
        "result_ttl": 3600,  # Keep results for 1 hour
        "failure_ttl": 86400,
    },
    "video_processing": {
        "timeout": 1800,  # 30 minutes (video processing can be slow)
        "result_ttl": 7200,  # Keep results for 2 hours
        "failure_ttl": 172800,  # Keep failed jobs for 48 hours
    }
}


def enqueue_job(queue_name: str, func, *args, **kwargs):
    """
    Enqueue a job to the specified queue.
    
    Args:
        queue_name: Name of the queue ("notifications", "analytics", "video_processing")
        func: Function to execute
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        Job object if successful, None if Redis is not available
    """
    if queue_name == "notifications" and notification_queue:
        config = QUEUE_CONFIG["notifications"]
        return notification_queue.enqueue(
            func,
            *args,
            timeout=config["timeout"],
            result_ttl=config["result_ttl"],
            failure_ttl=config["failure_ttl"],
            **kwargs
        )
    elif queue_name == "analytics" and analytics_queue:
        config = QUEUE_CONFIG["analytics"]
        return analytics_queue.enqueue(
            func,
            *args,
            timeout=config["timeout"],
            result_ttl=config["result_ttl"],
            failure_ttl=config["failure_ttl"],
            **kwargs
        )
    elif queue_name == "video_processing" and video_queue:
        config = QUEUE_CONFIG["video_processing"]
        return video_queue.enqueue(
            func,
            *args,
            timeout=config["timeout"],
            result_ttl=config["result_ttl"],
            failure_ttl=config["failure_ttl"],
            **kwargs
        )
    else:
        logger.warning(f"Queue '{queue_name}' not available or Redis not connected")
        return None


def get_job_status(job_id: str) -> dict:
    """
    Get status of a queued job.
    
    Args:
        job_id: Job ID returned when enqueueing
        
    Returns:
        Dictionary with job status information
    """
    if not redis_conn:
        return {"status": "unavailable", "message": "Redis not connected"}
    
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return {
            "id": job.id,
            "status": job.get_status(),
            "result": job.result if job.is_finished else None,
            "error": str(job.exc_info) if job.is_failed else None,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
        }
    except Exception as e:
        logger.error(f"Failed to get job status for {job_id}: {e}")
        return {"status": "error", "message": str(e)}


def cancel_job(job_id: str) -> bool:
    """
    Cancel a queued or running job.
    
    Args:
        job_id: Job ID to cancel
        
    Returns:
        True if successful, False otherwise
    """
    if not redis_conn:
        return False
    
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        job.cancel()
        logger.info(f"Job {job_id} cancelled successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to cancel job {job_id}: {e}")
        return False


# Health check function
def check_rq_health() -> dict:
    """
    Check RQ and Redis health status.
    
    Returns:
        Dictionary with health information
    """
    if not redis_conn:
        return {
            "status": "unhealthy",
            "redis": "disconnected",
            "queues": {}
        }
    
    try:
        redis_conn.ping()
        queues_info = {}
        
        for queue_name, queue in [
            ("notifications", notification_queue),
            ("analytics", analytics_queue),
            ("video_processing", video_queue)
        ]:
            if queue:
                queues_info[queue_name] = {
                    "count": len(queue),
                    "failed_count": queue.failed_job_registry.count,
                    "started_count": queue.started_job_registry.count,
                }
        
        return {
            "status": "healthy",
            "redis": "connected",
            "queues": queues_info
        }
    except Exception as e:
        logger.error(f"RQ health check failed: {e}")
        return {
            "status": "unhealthy",
            "redis": "error",
            "error": str(e)
        }


logger.info("RQ application initialized")
