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
# Format: https://frontend-{hash}-{project-id}.vercel.app
# Default uses the project pattern, but can be overridden via VERCEL_PROJECT_ID env var
def get_vercel_preview_regex() -> str:
    """Get Vercel preview regex pattern from environment or use default."""
    project_id = os.getenv("VERCEL_PROJECT_ID", "cliffs-projects-a84c76c9")
    return f"^https://frontend-[a-z0-9\\-]+-{re.escape(project_id)}\\.vercel\\.app$"


def validate_origin(origin: str) -> bool:
    """
    Validate that an origin is a properly formatted URL.
    
    Args:
        origin: Origin URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not origin or not isinstance(origin, str):
        return False
    
    # Basic URL validation - must start with http:// or https://
    if not (origin.startswith("https://") or origin.startswith("http://")):
        return False
    
    # Don't allow whitespace
    if origin != origin.strip():
        return False
    
    return True


def get_allowed_origins() -> List[str]:
    """
    Get allowed CORS origins from environment variable.
    
    Returns:
        List of allowed origin URLs (validated)
    """
    env = os.getenv("ALLOWED_ORIGINS", "")
    origins = [o.strip() for o in env.split(",") if o.strip()]
    
    # Validate each origin
    validated_origins = []
    for origin in origins:
        if validate_origin(origin):
            validated_origins.append(origin)
        else:
            print(f"⚠️ Invalid origin in ALLOWED_ORIGINS: {origin}")
    
    # If no custom origins provided or all were invalid, use production defaults
    if not validated_origins:
        validated_origins = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
        ]
    
    return validated_origins


def apply_cors(app):
    """
    Apply CORS middleware to FastAPI app with support for Vercel preview deployments.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_origin_regex=get_vercel_preview_regex(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
