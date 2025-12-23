"""
CORS Configuration for Production + Vercel Preview Deployments
Forever lock: Ensures frontend never shows white screen due to CORS
"""
import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Vercel preview regex pattern - matches all preview deployments
VERCEL_PREVIEW_REGEX = r"^https://frontend-[a-z0-9-]+-cliffs-projects-a84c76c9\.vercel\.app$"


def get_allowed_origins():
    """Get explicit production origins from environment variable."""
    env = os.getenv("ALLOWED_ORIGINS", "")
    return [o.strip() for o in env.split(",") if o.strip()]


def apply_cors(app: FastAPI):
    """
    Apply CORS middleware with production domains + Vercel preview support.
    
    Configuration:
    - Explicit production domains: From ALLOWED_ORIGINS env var
    - Vercel preview URLs: Handled by regex pattern
    - Credentials: Enabled for authentication
    - Methods/Headers: All allowed
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_origin_regex=VERCEL_PREVIEW_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
