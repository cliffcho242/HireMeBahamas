"""
CORS Configuration for Production + Vercel Preview Deployments
Forever lock: Ensures frontend never shows white screen due to CORS
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def get_vercel_preview_regex() -> str:
    """
    Get Vercel preview deployment regex pattern.
    
    The project ID can be customized via VERCEL_PROJECT_ID environment variable.
    Default: cliffs-projects-a84c76c9
    
    Returns:
        str: Regex pattern for Vercel preview URLs
    """
    import re
    project_id = os.getenv("VERCEL_PROJECT_ID", "cliffs-projects-a84c76c9")
    # Escape any special regex characters in the project ID
    project_id_escaped = re.escape(project_id)
    return f"^https://frontend-[a-z0-9-]+-{project_id_escaped}\\.vercel\\.app$"


def get_allowed_origins():
    """Get explicit production origins from environment variable."""
    env = os.getenv("ALLOWED_ORIGINS", "")
    return [o.strip() for o in env.split(",") if o.strip()]


def apply_cors(app: FastAPI):
    """
    Apply CORS middleware with production domains + Vercel preview support.
    
    Configuration:
    - Explicit production domains: From ALLOWED_ORIGINS env var
    - Vercel preview URLs: Handled by regex pattern (configurable via VERCEL_PROJECT_ID)
    - Credentials: Enabled for authentication
    - Methods/Headers: All allowed
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_allowed_origins(),
        allow_origin_regex=get_vercel_preview_regex(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
