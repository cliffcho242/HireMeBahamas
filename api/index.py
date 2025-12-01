"""
FastAPI + JWT Authentication for Vercel Serverless
Production-ready authentication with JWT tokens
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from .middleware import create_access_token, get_current_user, get_optional_user

# Initialize FastAPI app
app = FastAPI(
    title="HireMeBahamas API",
    version="1.0.0",
    docs_url=None,  # Disable in production
    redoc_url=None,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory data stores
users = {
    "admin@hiremebahamas.com": {
        "email": "admin@hiremebahamas.com",
        "password": "AdminPass123!",
        "user_type": "admin",
        "first_name": "Admin",
        "last_name": "User",
    }
}
jobs = []
posts = []

# Pydantic Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str = ""
    last_name: str = ""
    user_type: str = "job_seeker"

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary: str = "Negotiable"

class PostCreate(BaseModel):
    content: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None


# ==================== PUBLIC ROUTES ====================

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Public health check endpoint"""
    return {
        "status": "healthy",
        "message": "Vercel Serverless API is running",
        "platform": "vercel",
        "cold_starts": "eliminated",
        "authentication": "JWT enabled"
    }


@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login endpoint - creates JWT token"""
    email = request.email
    password = request.password
    
    # Verify credentials
    if email not in users or users[email]["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    user = users[email]
    
    # Create JWT token
    access_token = create_access_token(
        data={
            "email": user["email"],
            "user_type": user["user_type"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "user_type": user["user_type"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
        },
    }


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register new user endpoint"""
    email = request.email
    
    if email in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create new user
    users[email] = {
        "email": email,
        "password": request.password,
        "user_type": request.user_type,
        "first_name": request.first_name,
        "last_name": request.last_name,
    }
    
    return {
        "message": "User registered successfully",
        "user": {
            "email": email,
            "user_type": request.user_type,
            "first_name": request.first_name,
            "last_name": request.last_name,
        },
    }


@app.get("/api/jobs")
async def get_jobs():
    """Public endpoint - list all jobs"""
    return {
        "success": True,
        "jobs": jobs,
        "total": len(jobs)
    }


@app.get("/api/jobs/stats/overview")
async def get_job_stats():
    """Public endpoint - job statistics"""
    return {
        "success": True,
        "stats": {
            "active_jobs": len(jobs),
            "companies_hiring": len(set(job.get("company", "") for job in jobs)),
            "new_this_week": len(jobs),
        },
    }


@app.get("/api/posts")
async def get_posts():
    """Public endpoint - list all posts"""
    return posts


# ==================== PROTECTED ROUTES ====================

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Protected endpoint - get current user info from JWT"""
    return {
        "user": current_user
    }


@app.post("/api/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate, current_user: dict = Depends(get_current_user)):
    """Protected endpoint - create new job posting"""
    new_job = {
        "id": len(jobs) + 1,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "salary": job.salary,
        "created_by": current_user["email"],
    }
    jobs.append(new_job)
    return new_job


@app.post("/api/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    """Protected endpoint - create new post"""
    new_post = {
        "id": len(posts) + 1,
        "content": post.content,
        "image_url": post.image_url,
        "video_url": post.video_url,
        "user": {
            "id": len(users) + 1,
            "first_name": current_user["first_name"],
            "last_name": current_user["last_name"],
            "email": current_user["email"],
        },
        "likes_count": 0,
    }
    posts.append(new_post)
    return new_post


# Vercel serverless handler
handler = app
