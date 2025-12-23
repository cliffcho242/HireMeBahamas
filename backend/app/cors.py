"""
CORS Configuration Module - Forever Lock
Handles CORS configuration with production domains and Vercel preview regex support
"""
import os
import re
from fastapi.middleware.cors import CORSMiddleware

# Vercel preview URL pattern for automatic CORS allowance
VERCEL_PREVIEW_REGEX = r"^https://frontend-[a-z0-9-]+-cliffs-projects-a84c76c9\.vercel\.app$"


def get_allowed_origins():
    """
    Get allowed origins from environment variable.
    Always includes production domains.
    """
    env = os.getenv("ALLOWED_ORIGINS", "")
    origins = [o.strip() for o in env.split(",") if o.strip()]
    
    # Ensure production domains are always included
    required_origins = [
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
    ]
    
    for domain in required_origins:
        if domain not in origins:
            origins.append(domain)
    
    return origins


def apply_cors(app):
    """
    Apply CORS middleware to FastAPI app with production-safe configuration.
    
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
