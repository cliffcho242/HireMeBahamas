"""
CORS Configuration for Vercel Preview + Production Deployments
Eliminates white screen by allowing ALL valid frontends (production + previews)
"""
import sys
from pathlib import Path
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import shared CORS utilities (no FastAPI dependency)
api_dir = Path(__file__).parent.parent
sys.path.insert(0, str(api_dir))
from cors_utils import get_vercel_preview_regex, get_allowed_origins as _get_allowed_origins


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
        allow_origins=_get_allowed_origins(),  # Explicit production domains
        allow_origin_regex=get_vercel_preview_regex(),  # All Vercel previews
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
        "explicit_origins": _get_allowed_origins(),
        "vercel_preview_regex": get_vercel_preview_regex(),
        "credentials_enabled": True,
        "methods": ["*"],
        "headers": ["*"],
    }
