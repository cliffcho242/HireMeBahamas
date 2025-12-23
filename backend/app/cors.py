"""
Backend CORS Forever Lock (Render)

✅ Preview deployments automatically allowed
✅ Production origins safe
✅ Prevents CORS from silently breaking fetch → white screen
"""
import os
import re
from fastapi.middleware.cors import CORSMiddleware

# Get Vercel project identifier from environment or use default
VERCEL_PROJECT_ID = os.getenv("VERCEL_PROJECT_ID", "cliffs-projects-a84c76c9")

# Pattern for Vercel preview deployments
VERCEL_PREVIEW_REGEX = rf"^https://frontend-[a-z0-9-]+-{re.escape(VERCEL_PROJECT_ID)}\.vercel\.app$"


def get_allowed_origins():
    """Get allowed CORS origins from environment variable.
    
    Returns:
        list: List of allowed origin URLs
    """
    env = os.getenv("ALLOWED_ORIGINS", "")
    return [o.strip() for o in env.split(",") if o.strip()]


def is_vercel_preview(origin: str) -> bool:
    """Check if origin matches Vercel preview deployment pattern.
    
    Args:
        origin: The origin URL to check
        
    Returns:
        bool: True if origin matches Vercel preview pattern
    """
    if not origin:
        return False
    return bool(re.match(VERCEL_PREVIEW_REGEX, origin))


def apply_cors(app):
    """Apply CORS middleware to FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    allowed_origins = get_allowed_origins()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=VERCEL_PREVIEW_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
