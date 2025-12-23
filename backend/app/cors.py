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


def get_vercel_preview_regex():
    """
    Get Vercel preview deployment regex pattern.
    
    The pattern can be customized via VERCEL_PROJECT_ID environment variable.
    Default: cliffs-projects-a84c76c9
    
    Returns:
        str: Regex pattern for Vercel preview URLs
    """
    project_id = os.getenv("VERCEL_PROJECT_ID", "cliffs-projects-a84c76c9")
    # Escape any special regex characters in the project ID
    project_id_escaped = re.escape(project_id)
    return f"^https://frontend-[a-z0-9-]+-{project_id_escaped}\\.vercel\\.app$"


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
        allow_origin_regex=get_vercel_preview_regex(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
