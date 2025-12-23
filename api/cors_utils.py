"""
CORS utilities that can be used without FastAPI dependency.
Used for fallback handlers and testing.
"""
import os
import re


def get_vercel_preview_regex() -> str:
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


def get_allowed_origins() -> list:
    """
    Get explicit production origins from environment variable.
    
    Returns:
        list: List of explicit production origins
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
