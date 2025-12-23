"""
Backend CORS Forever Lock (Render)

This module provides bulletproof CORS configuration for the backend API.

Features:
✅ Preview deployments automatically allowed via regex
✅ Production origins safe
✅ Prevents CORS from silently breaking fetch → white screen
✅ Environment variable enforcement
"""
import os
import re
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Pattern for Vercel preview deployments
# Format: https://frontend-{hash}-cliffs-projects-a84c76c9.vercel.app
VERCEL_PREVIEW_REGEX = r"^https://frontend-[a-z0-9\-]+-cliffs-projects-a84c76c9\.vercel\.app$"


def get_allowed_origins() -> List[str]:
    """
    Get allowed CORS origins from environment variable.
    
    Returns:
        List of allowed origin URLs
    """
    env = os.getenv("ALLOWED_ORIGINS", "")
    origins = [o.strip() for o in env.split(",") if o.strip()]
    
    # If no custom origins provided, use production defaults
    if not origins:
        origins = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
        ]
    
    return origins


def apply_cors(app):
    """
    Apply CORS middleware to FastAPI app with support for Vercel preview deployments.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_origin_regex=VERCEL_PREVIEW_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
