"""
CORS Configuration for Vercel Preview + Production Deployments
Eliminates white screen by allowing ALL valid frontends (production + previews)
"""
import os
import re
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Vercel preview deployment pattern
# Matches URLs like: https://frontend-[hash]-cliffs-projects-a84c76c9.vercel.app
VERCEL_PREVIEW_REGEX = (
    r"^https://frontend-[a-z0-9-]+-cliffs-projects-a84c76c9\.vercel\.app$"
)


def get_allowed_origins() -> List[str]:
    """
    Get explicit production origins from environment variable.
    
    Returns:
        List[str]: List of explicit production origins
    """
    env = os.getenv("ALLOWED_ORIGINS", "")
    if not env:
        # Default production domains
        return [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
        ]
    
    # Parse comma-separated origins
    origins = [o.strip() for o in env.split(",") if o.strip()]
    return origins


def apply_cors(app: FastAPI) -> None:
    """
    Apply CORS middleware to FastAPI app with Vercel preview support.
    
    This configuration:
    - Allows explicit production domains (from ALLOWED_ORIGINS env var)
    - Allows ALL Vercel preview deployments via regex pattern
    - Maintains security by NOT using wildcards
    - Supports credentials for authentication
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),  # Explicit production domains
        allow_origin_regex=VERCEL_PREVIEW_REGEX,  # All Vercel previews
        allow_credentials=True,  # Required for authentication cookies
        allow_methods=["*"],  # All HTTP methods
        allow_headers=["*"],  # All headers
    )


def get_cors_config_summary() -> dict:
    """
    Get summary of current CORS configuration for debugging.
    
    Returns:
        dict: Configuration summary
    """
    return {
        "explicit_origins": get_allowed_origins(),
        "vercel_preview_regex": VERCEL_PREVIEW_REGEX,
        "credentials_enabled": True,
        "methods": ["*"],
        "headers": ["*"],
    }
