import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

# Import APIs
from .api import auth, hireme, jobs, messages, notifications, profile_pictures, reviews, upload, users

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting HireMeBahamas API...")
    yield
    # Shutdown
    logger.info("Shutting down HireMeBahamas API...")


# Initialize FastAPI app
app = FastAPI(
    title="HireMeBahamas API",
    description="Job platform API for the Bahamas",
    version="1.0.0",
)

# Configure CORS - Allow development and production origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:5173",
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "https://*.vercel.app",  # Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "HireMeBahamas API is running"}


# Include routers with /api prefix to match frontend expectations
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(hireme.router, prefix="/api/hireme", tags=["hireme"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(profile_pictures.router, prefix="/api/profile-pictures", tags=["profile-pictures"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(upload.router, prefix="/api/upload", tags=["uploads"])
app.include_router(users.router, prefix="/api/users", tags=["users"])


# Initialize Socket.IO for real-time messaging
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
    ]
)

# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(sio, app)


# Socket.IO event handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    await sio.emit('connected', {'sid': sid}, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {sid}")


@sio.event
async def join_conversation(sid, data):
    """Join a conversation room"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        await sio.enter_room(sid, f"conversation_{conversation_id}")
        logger.info(f"Client {sid} joined conversation {conversation_id}")


@sio.event
async def leave_conversation(sid, data):
    """Leave a conversation room"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        await sio.leave_room(sid, f"conversation_{conversation_id}")
        logger.info(f"Client {sid} left conversation {conversation_id}")


@sio.event
async def typing(sid, data):
    """Handle typing indicator"""
    conversation_id = data.get('conversation_id')
    is_typing = data.get('is_typing')
    if conversation_id:
        await sio.emit('typing', data, room=f"conversation_{conversation_id}", skip_sid=sid)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to HireMeBahamas API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8005)
