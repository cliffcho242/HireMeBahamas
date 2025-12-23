"""
Environment detection utilities for consistent production/development mode checks.

This module provides centralized environment detection to ensure consistent behavior
across all parts of the application.
"""
import os
import re
from typing import List


def _normalize_production_origins(origins: List[str]) -> List[str]:
    """Ensure required production domains are always allowed with HTTPS."""
    required = [
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
    ]
    
    # Preserve wildcard handling separately (should never mix with credentials)
    if any(origin.strip() == "*" for origin in origins):
        return ["*"]
    
    normalized: List[str] = []
    
    for origin in origins:
        candidate = origin.strip()
        if not candidate:
            continue
        
        # Force HTTPS for production origins to avoid mixed-content issues
        if candidate.startswith("http://"):
            candidate = "https://" + candidate[len("http://"):]
        
        if candidate not in normalized:
            normalized.append(candidate)
    
    # Always include both primary domains for Safari/iOS compatibility
    for domain in required:
        if domain not in normalized:
            normalized.append(domain)
    
    return normalized


def is_production() -> bool:
    """Check if the application is running in production mode.
    
    Production mode is determined by:
    - ENVIRONMENT=production
    - VERCEL_ENV=production
    
    Returns:
        bool: True if running in production, False otherwise
    """
    env = os.getenv("ENVIRONMENT", "").lower()
    vercel_env = os.getenv("VERCEL_ENV", "").lower()
    return env == "production" or vercel_env == "production"


def is_development() -> bool:
    """Check if the application is running in development mode.
    
    Returns:
        bool: True if running in development, False otherwise
    """
    return not is_production()


def get_cors_origins() -> List[str]:
    """Get CORS allowed origins based on current environment.
    
    In production:
    - Only HTTPS origins for production domains
    - NO wildcard (*) allowed in production (security requirement)
    - Specific domains only
    
    In development:
    - Includes localhost origins for local development
    - Plus all production origins for testing
    
    Environment Variables:
    - ALLOWED_ORIGINS: Comma-separated list of additional origins (production only)
    
    Returns:
        List[str]: List of allowed CORS origins
    """
    # Check for custom origins from environment variable
    custom_origins_env = os.getenv("ALLOWED_ORIGINS", "")
    
    if is_production():
        # Production mode: strict domain whitelist only
        # 🚫 ABSOLUTE BAN: No wildcard (*) in production
        if custom_origins_env and custom_origins_env != "*":
            # Use custom origins if provided (and not wildcard)
            origins = [origin.strip() for origin in custom_origins_env.split(",") if origin.strip()]
        else:
            # Default production origins - specific domains only
            origins = [
                "https://hiremebahamas.com",
                "https://www.hiremebahamas.com",
                "https://hiremebahamas.vercel.app",  # Vercel production deployment
                "https://hire-me-bahamas.vercel.app",  # Canonical Vercel domain
                # Mobile app origins (Capacitor/Ionic)
                "capacitor://localhost",
                "ionic://localhost",
            ]
        
        # Normalize and ensure required domains are always included
        origins = _normalize_production_origins(origins)
        
        # Note: For additional Vercel preview deployments, add them to
        # ALLOWED_ORIGINS environment variable as comma-separated list.
        # Example: ALLOWED_ORIGINS="https://hiremebahamas.com,https://hiremebahamas-git-feature.vercel.app"
        # Wildcard patterns (*.vercel.app) are NOT supported in production mode.
        
    else:
        # Development mode: includes localhost for testing
        origins = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
            "https://hiremebahamas.vercel.app",
            "https://hire-me-bahamas.vercel.app",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:5173",
            # Mobile app origins (Capacitor/Ionic)
            "capacitor://localhost",
            "ionic://localhost",
        ]
    
    return origins


# Vercel project ID pattern for this app's preview deployments
# Format: frontend-{hash}-cliffs-projects-a84c76c9.vercel.app
# Note: This is hardcoded for security - only this specific project's
# preview deployments are allowed. To change, update the pattern directly.
VERCEL_PROJECT_PATTERN = re.compile(
    r'^https://frontend-[a-z0-9]+-cliffs-projects-a84c76c9\.vercel\.app$'
)


def is_valid_vercel_preview_origin(origin: str) -> bool:
    """Check if an origin is a valid Vercel preview deployment for this project.
    
    This allows dynamic CORS validation for Vercel preview deployments
    without requiring manual updates for each new deployment.
    
    Args:
        origin: The origin URL to validate
        
    Returns:
        bool: True if origin matches the Vercel preview pattern for this project
    """
    if not origin:
        return False
    return bool(VERCEL_PROJECT_PATTERN.match(origin))
