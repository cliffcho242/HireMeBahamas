from fastapi import APIRouter

from app.api.v1.analytics import router as analytics
from app.api.v1.auth import router as auth
from app.api.v1.debug import router as debug
from app.api.v1.feed import router as feed
from app.api.v1.health import router as health
from app.api.v1.hireme import router as hireme
from app.api.v1.jobs import router as jobs
from app.api.v1.messages import router as messages
from app.api.v1.notifications import router as notifications
from app.api.v1.posts import router as posts
from app.api.v1.profile_pictures import router as profile_pictures
from app.api.v1.reviews import router as reviews
from app.api.v1.upload import router as upload
from app.api.v1.users import router as users

router = APIRouter(prefix="/api/v1")

router.include_router(health)
router.include_router(auth)
router.include_router(users)
router.include_router(feed)
router.include_router(posts)
router.include_router(messages)
router.include_router(notifications)
router.include_router(jobs)
router.include_router(hireme)
router.include_router(reviews)
router.include_router(upload)
router.include_router(profile_pictures)
router.include_router(analytics)
router.include_router(debug)
