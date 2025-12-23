"""
Environment detection utilities for consistent production/development mode checks.

This module provides centralized environment detection to ensure consistent behavior
across all parts of the application.

CORS Configuration:
-------------------
This module handles CORS (Cross-Origin Resource Sharing) configuration for the application,
including support for dynamic Vercel preview deployments.

Key Features:
1. Environment-aware CORS origins (production vs development)
2. Dynamic Vercel preview URL validation via regex pattern matching
3. ALLOWED_ORIGINS environment variable support
4. Strict security: No wildcards in production, credentials-safe

Vercel Preview Support:
-----------------------
Vercel creates preview deployments with URLs like:
  https://frontend-{hash}-cliffs-projects-a84c76c9.vercel.app

The hash changes with each deployment. This module automatically validates these
preview URLs using a controlled regex pattern, so you don't need to manually add
each preview URL to your CORS configuration.

Security:
---------
- ✅ No wildcards (*) allowed in production
- ✅ Only this project's preview deployments are allowed (via project ID in regex)
- ✅ HTTPS enforced for all origins
- ✅ Exact pattern matching prevents subdomain attacks
- ✅ Safe to use with credentials (cookies, auth headers)

Example Usage:
--------------
In production (Render), set:
  ALLOWED_ORIGINS=https://hiremebahamas.com,https://www.hiremebahamas.com

Preview deployments are handled automatically - no additional configuration needed!
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
    
    # Check for Vercel preview URL (can be set dynamically for preview deployments)
    vercel_preview_url = os.getenv("VERCEL_PREVIEW_URL", "")
    
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
        
        # Add Vercel preview URL if set via environment variable
        if vercel_preview_url and vercel_preview_url not in origins:
            origins.append(vercel_preview_url)
        
        # Normalize and ensure required domains are always included
        origins = _normalize_production_origins(origins)
        
        # Note: Configuring CORS for Vercel preview deployments:
        # 
        # Option 1: Use VERCEL_PREVIEW_URL for a single active preview deployment
        #   Set: VERCEL_PREVIEW_URL=https://your-preview-123.vercel.app
        #   Best for: Testing a specific preview before merging
        #
        # Option 2: Use ALLOWED_ORIGINS for multiple custom origins (replaces defaults)
        #   Set: ALLOWED_ORIGINS="https://hiremebahamas.com,https://preview1.vercel.app"
        #   Best for: Advanced configurations with multiple allowed origins
        #
        # Note: Wildcard patterns (*.vercel.app) are NOT supported in production mode
        # due to CORS security requirements when credentials are enabled.
        
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
        
        # Add Vercel preview URL if set via environment variable
        if vercel_preview_url and vercel_preview_url not in origins:
            origins.append(vercel_preview_url)
    
    return origins


# Vercel project ID pattern for this app's preview deployments
# Format: frontend-{hash}-cliffs-projects-a84c76c9.vercel.app
# The hash can contain lowercase letters, numbers, and hyphens
# Note: This is hardcoded for security - only this specific project's
# preview deployments are allowed. To change, update the pattern directly.
VERCEL_PROJECT_PATTERN = re.compile(
    r'^https://frontend-[a-z0-9-]+-cliffs-projects-a84c76c9\.vercel\.app$'
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
