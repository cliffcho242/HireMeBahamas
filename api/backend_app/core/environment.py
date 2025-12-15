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
    - Includes Vercel preview deployments (*.vercel.app)
    
    In development:
    - Includes localhost origins for local development
    - Plus all production origins for testing
    
    Returns:
        List[str]: List of allowed CORS origins
    """
    # Production origins (always included)
    origins = [
        "https://hiremebahamas.com",
        "https://www.hiremebahamas.com",
        "https://*.vercel.app",  # Vercel preview deployments
    ]
    
    # Add localhost origins only in development
    if is_development():
        origins.extend([
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:5173",
        ])
    
    return origins
