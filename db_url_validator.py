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
    
    Enhanced validation checks:
    1. Must contain a hostname (not localhost, 127.0.0.1, or empty)
    2. Must contain a port number
    3. Must use TCP connection (no Unix sockets)
    4. Must have SSL mode configured
    
    Args:
        url: Database URL to validate (or None)
        
    Returns:
        True if valid, False if invalid
    """
    if not url:
        logging.warning("DATABASE_URL is not set")
        return False

    parsed = urlparse(url)

    # Check for required fields
    missing = []
    if not parsed.hostname:
        missing.append("host")
    if not parsed.username:
        missing.append("user")
    if not parsed.password:
        missing.append("password")
    if not parsed.port:
        missing.append("port")

    if missing:
        logging.warning(
            f"Invalid DATABASE_URL (missing {', '.join(missing)}). "
            f"Required format: postgresql://user:pass@hostname:port/dbname?sslmode=require"
        )
        return False
    
    # Check hostname is not localhost (may cause socket usage)
    hostname = parsed.hostname.lower()
    if hostname in ('localhost', '127.0.0.1', '::1'):
        logging.warning(
            f"DATABASE_URL uses '{parsed.hostname}' which may cause socket usage. "
            "Use a remote database hostname instead."
        )
        return False
    
    # Check for SSL mode
    query_params = parsed.query.lower()
    if 'sslmode=' not in query_params:
        logging.warning(
            "DATABASE_URL missing sslmode parameter. "
            "Add ?sslmode=require to enforce SSL."
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
