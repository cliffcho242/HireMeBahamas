"""
Production-safe DATABASE_URL validation utility.

This module provides validation functions that use logging warnings
instead of raising exceptions, allowing the application to start even
with invalid database configuration (useful for health checks and diagnostics).
"""

import os
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def validate_database_url(url: str | None) -> bool:
    """Validate DATABASE_URL without raising exceptions.
    
    This is production-safe validation that logs warnings instead of
    raising exceptions, allowing the app to start for health checks.
    
    Args:
        url: Database URL to validate (or None)
        
    Returns:
        True if valid, False if invalid
    """
    if not url:
        logging.warning("DATABASE_URL is not set")
        return False

    parsed = urlparse(url)

    missing = []
    if not parsed.hostname:
        missing.append("host")
    if not parsed.username:
        missing.append("user")
    if not parsed.password:
        missing.append("password")

    if missing:
        logging.warning(
            f"Invalid DATABASE_URL (missing {', '.join(missing)})"
        )
        return False

    return True


def get_validated_database_url() -> str | None:
    """Get DATABASE_URL from environment and validate it.
    
    Returns:
        DATABASE_URL if valid, None if invalid
    """
    database_url = os.environ.get("DATABASE_URL")
    
    if validate_database_url(database_url):
        return database_url
    
    return None
