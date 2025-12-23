"""
🔒 STEP 6: BACKEND CORS FOREVER LOCK

This module provides CORS configuration for the backend API.
- Supports production domains
- Supports Vercel preview deployments via regex
- Enforces HTTPS
"""
import os
import re
from fastapi.middleware.cors import CORSMiddleware

VERCEL_PREVIEW_REGEX = r"^https://frontend-[a-z0-9-]+-cliffs-projects-a84c76c9\.vercel\.app$"


def get_allowed_origins():
    """
    Get explicit production origins from environment variable.
    
    Returns:
        list: List of allowed origins
    """
    env = os.getenv("ALLOWED_ORIGINS", "")
    return [o.strip() for o in env.split(",") if o.strip()]


def apply_cors(app):
    """
    Apply CORS middleware to the FastAPI app.
    
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
