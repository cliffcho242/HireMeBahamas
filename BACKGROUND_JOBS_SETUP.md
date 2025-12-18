# Background Jobs Setup - HireMeBahamas

## Overview

HireMeBahamas implements a comprehensive background job system to ensure non-blocking API responses and improved user experience. This document describes the architecture, setup, and usage of background jobs.

## Architecture

### Task Distribution

| Task Type | Tool | Queue | Use Case |
|-----------|------|-------|----------|
| **Emails** | Celery | `emails` | Welcome emails, job application notifications, password resets |
| **Notifications** | RQ | `notifications` | Push notifications, in-app notifications |
| **Analytics** | RQ Worker | `analytics` | User event tracking, statistics aggregation |
| **Video Processing** | RQ Queue | `video_processing` | Video transcoding, thumbnail generation |

### Why Multiple Tools?

- **Celery**: Best for scheduled tasks and tasks requiring advanced retry logic (emails)
- **RQ (Redis Queue)**: Lightweight, simple Python queue for quick tasks (notifications)
- **Worker/Queue**: Generic pattern for CPU-intensive tasks (video processing, analytics)

## Prerequisites

### 1. Redis Installation

All background job systems require Redis as the message broker.

**Development (Local):**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

**Production:**
- Use managed Redis service:
  - Upstash Redis (recommended for Vercel)
  - Render Redis
  - Redis Cloud
  - AWS ElastiCache

### 2. Environment Variables

Add to your `.env` file:

```bash
# Redis connection
REDIS_URL=redis://localhost:6379/0

# Production
# REDIS_URL=redis://default:password@redis-host:6379

# Email service (choose one)
SENDGRID_API_KEY=your_sendgrid_key
# AWS_SES_ACCESS_KEY=your_aws_key
# AWS_SES_SECRET_KEY=your_aws_secret
# MAILGUN_API_KEY=your_mailgun_key
# MAILGUN_DOMAIN=your_mailgun_domain

# Push notifications (choose one)
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-adminsdk.json
# ONESIGNAL_APP_ID=your_onesignal_app_id
# ONESIGNAL_API_KEY=your_onesignal_api_key
```

## Installation

Dependencies are already added to `api/requirements.txt`:

```bash
celery[redis]==5.4.0
rq==2.0.0
kombu==5.4.2
flower==2.0.1  # Optional: for monitoring
```

Install:
```bash
cd api
pip install -r requirements.txt
```

## Starting Workers

### 1. Celery Worker (Emails)

```bash
# Start Celery worker for email tasks
celery -A backend_app.core.celery_app worker --loglevel=info -Q emails

# With concurrency (production)
celery -A backend_app.core.celery_app worker --loglevel=info -Q emails --concurrency=4

# With autoscaling
celery -A backend_app.core.celery_app worker --loglevel=info -Q emails --autoscale=10,3
```

### 2. Celery Beat (Scheduled Tasks)

For periodic tasks like cleaning up old notifications:

```bash
celery -A backend_app.core.celery_app beat --loglevel=info
```

### 3. RQ Worker (Notifications)

```bash
# Start RQ worker for notifications
rq worker notifications --url redis://localhost:6379/0

# For analytics
rq worker analytics --url redis://localhost:6379/0

# For video processing
rq worker video_processing --url redis://localhost:6379/0

# All queues
rq worker notifications analytics video_processing --url redis://localhost:6379/0
```

### 4. Flower (Optional - Monitoring)

Monitor Celery tasks in real-time:

```bash
celery -A backend_app.core.celery_app flower --port=5555
```

Access at: http://localhost:5555

## Usage in Code

### Celery (Emails)

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from backend_app.core.celery_tasks import send_welcome_email, send_job_application_email

router = APIRouter()

@router.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Create user in database
    db_user = User(**user.dict())
    db.add(db_user)
    await db.commit()
    
    # Send welcome email asynchronously (non-blocking)
    send_welcome_email.delay(
        user_email=user.email,
        user_name=user.first_name,
        username=user.username
    )
    
    return {"success": True, "user": db_user}


@router.post("/jobs/{job_id}/apply")
async def apply_for_job(job_id: int, db: AsyncSession = Depends(get_db)):
    # Create job application
    application = JobApplication(job_id=job_id, user_id=current_user.id)
    db.add(application)
    await db.commit()
    
    # Notify employer asynchronously
    send_job_application_email.delay(
        employer_email=job.employer.email,
        employer_name=job.employer.first_name,
        job_title=job.title,
        applicant_name=current_user.full_name,
        applicant_email=current_user.email,
        job_id=job_id
    )
    
    return {"success": True}
```

### RQ (Notifications)

```python
from backend_app.core.rq_app import notification_queue, enqueue_job
from backend_app.core.rq_tasks import send_new_follower_notification_job

@router.post("/users/{user_id}/follow")
async def follow_user(user_id: int, db: AsyncSession = Depends(get_db)):
    # Create follow relationship
    follow = Follow(follower_id=current_user.id, following_id=user_id)
    db.add(follow)
    await db.commit()
    
    # Send push notification asynchronously
    job = enqueue_job(
        "notifications",
        send_new_follower_notification_job,
        follower_id=current_user.id,
        follower_name=current_user.full_name,
        followed_user_id=user_id
    )
    
    return {"success": True, "job_id": job.id if job else None}
```

### RQ (Analytics)

```python
from backend_app.core.rq_app import analytics_queue, enqueue_job
from backend_app.core.rq_tasks import track_user_event_job

@router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    # Get job details
    job = await db.get(Job, job_id)
    
    # Track page view asynchronously
    enqueue_job(
        "analytics",
        track_user_event_job,
        user_id=current_user.id,
        event_type="job_view",
        event_data={"job_id": job_id, "job_title": job.title}
    )
    
    return job
```

### RQ (Video Processing)

```python
from backend_app.core.rq_app import video_queue, enqueue_job
from backend_app.core.rq_tasks import process_video_job

@router.post("/videos/upload")
async def upload_video(file: UploadFile, db: AsyncSession = Depends(get_db)):
    # Save video file
    video_path = f"/uploads/videos/{file.filename}"
    # ... save file logic ...
    
    # Create video record
    video = Video(user_id=current_user.id, filename=file.filename)
    db.add(video)
    await db.commit()
    
    # Process video asynchronously (transcoding, thumbnails)
    job = enqueue_job(
        "video_processing",
        process_video_job,
        video_id=video.id,
        video_path=video_path,
        user_id=current_user.id,
        processing_options={"quality": ["720p", "480p"]}
    )
    
    return {"success": True, "video_id": video.id, "job_id": job.id if job else None}
```

## Production Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  celery_worker:
    build: .
    command: celery -A backend_app.core.celery_app worker --loglevel=info -Q emails
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - redis

  celery_beat:
    build: .
    command: celery -A backend_app.core.celery_app beat --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  rq_worker:
    build: .
    command: rq worker notifications analytics video_processing --url redis://redis:6379/0
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - redis

  flower:
    build: .
    command: celery -A backend_app.core.celery_app flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

volumes:
  redis_data:
```

### Render

1. Add Redis service in Render dashboard
2. Add worker services:
   - Celery Worker: `celery -A backend_app.core.celery_app worker --loglevel=info -Q emails`
   - RQ Worker: `rq worker notifications analytics --url $REDIS_URL`

### Vercel + Upstash

For serverless deployment:

1. Create Upstash Redis database
2. Add REDIS_URL to Vercel environment variables
3. Deploy workers on separate platform (Render, Render, or AWS Lambda)

## Monitoring

### Check Queue Status

```python
from backend_app.core.rq_app import check_rq_health

# In your health check endpoint
@router.get("/health/queues")
async def check_queues():
    rq_status = check_rq_health()
    return {
        "rq": rq_status,
        # Add Celery monitoring if needed
    }
```

### Celery Flower Dashboard

- URL: http://localhost:5555 (or your production domain)
- Features:
  - Real-time task monitoring
  - Task history
  - Worker management
  - Performance metrics

### RQ Dashboard

Install RQ Dashboard:
```bash
pip install rq-dashboard
rq-dashboard --redis-url redis://localhost:6379/0
```

Access at: http://localhost:9181

## Best Practices

1. **Always use .delay() for Celery tasks**
   ```python
   # ✅ Correct
   send_email.delay(email="user@example.com")
   
   # ❌ Wrong (blocks the request)
   send_email(email="user@example.com")
   ```

2. **Set appropriate timeouts**
   - Emails: 5 minutes
   - Notifications: 2 minutes
   - Video processing: 30 minutes

3. **Handle failures gracefully**
   - Don't fail API requests if background job fails
   - Log errors for monitoring
   - Set up retry logic for critical tasks

4. **Monitor queue lengths**
   - Set alerts for queue backlogs
   - Scale workers based on queue size

5. **Use appropriate concurrency**
   - CPU-bound: workers = CPU cores
   - I/O-bound: workers = 2-4x CPU cores

## Troubleshooting

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# Check if Redis is running
redis-cli info server
```

### Celery Worker Not Processing

```bash
# Check Celery worker status
celery -A backend_app.core.celery_app inspect active

# Check registered tasks
celery -A backend_app.core.celery_app inspect registered

# Purge all tasks (development only!)
celery -A backend_app.core.celery_app purge
```

### RQ Worker Not Processing

```bash
# Check RQ queues
rq info --url redis://localhost:6379/0

# Empty failed jobs
rq empty failed --url redis://localhost:6379/0
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/cliffcho242/HireMeBahamas/issues
- Documentation: See SCALING_STRATEGY.md for architecture details
