"""
Environment detection utilities for consistent production/development mode checks.

This module provides centralized environment detection to ensure consistent behavior
across all parts of the application.
"""
import os
from typing import List


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
            # Default production origins
            origins = [
                "https://hiremebahamas.com",
                "https://www.hiremebahamas.com",
            ]
        
        # Note: Vercel preview deployments (*.vercel.app) should be added
        # to ALLOWED_ORIGINS environment variable if needed for testing
        
    else:
        # Development mode: includes localhost for testing
        origins = [
            "https://hiremebahamas.com",
            "https://www.hiremebahamas.com",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:5173",
        ]
    
    return origins
