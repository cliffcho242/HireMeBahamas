"""
Database utility functions for URL manipulation and SSL configuration.

This module provides shared utilities for database configuration across
the application to avoid code duplication.
"""
import logging
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

logger = logging.getLogger(__name__)

# Default port for PostgreSQL
DEFAULT_POSTGRES_PORT = 5432


def strip_sslmode_from_url(database_url: str) -> str:
    """
    ⚠️  DEPRECATED: This function is no longer needed.
    
    ❌ OLD APPROACH (INCORRECT):
    Remove sslmode from URL and pass it in connect_args
    
    ✅ NEW APPROACH (CORRECT):
    Keep sslmode in DATABASE_URL query string: ?sslmode=require
    DO NOT pass sslmode as a kwarg in connect_args
    
    This function now returns the URL unchanged for backward compatibility.
    
    Args:
        database_url: Database connection URL
        
    Returns:
        URL unchanged (sslmode should stay in URL)
    """
    logger.warning(
        "strip_sslmode_from_url() is deprecated. "
        "Keep sslmode in DATABASE_URL: postgresql://...?sslmode=require"
    )
    return database_url


def ensure_port_in_url(database_url: str, default_port: int = DEFAULT_POSTGRES_PORT) -> str:
    """
    Ensure the DATABASE_URL includes an explicit port number.
    
    PostgreSQL connections require explicit ports for cloud deployments
    to avoid socket-based connections. This function adds the default
    PostgreSQL port (5432) if missing.
    
    Args:
        database_url: Database connection URL
        default_port: Default port to use if missing (default: 5432)
        
    Returns:
        URL with explicit port number added if it was missing
    """
    if not database_url:
        return database_url
    
    parsed_url = urlparse(database_url)
    
    # Check if port is already specified
    if parsed_url.port:
        return database_url
    
    # Port is missing - add default port
    if not parsed_url.hostname:
        # Can't add port without hostname
        return database_url
    
    # Construct new netloc with port
    # Format: username:password@hostname:port
    netloc = parsed_url.hostname
    if default_port is not None:
        netloc = f"{netloc}:{default_port}"
    
    # Add username and password if present
    if parsed_url.username:
        auth = parsed_url.username
        if parsed_url.password:
            auth = f"{auth}:{parsed_url.password}"
        netloc = f"{auth}@{netloc}"
    
    # Reconstruct URL with explicit port
    fixed_url = urlunparse((
        parsed_url.scheme,
        netloc,
        parsed_url.path,
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))
    
    logger.info(f"Added default port {default_port} to DATABASE_URL (explicit port required for cloud deployments)")
    
    return fixed_url


def get_ssl_config(environment: str) -> str:
    """
    ⚠️  DEPRECATED: This function is no longer needed.
    
    ❌ OLD APPROACH (INCORRECT):
    Pass SSL config in connect_args: connect_args={"ssl": "require"}
    
    ✅ NEW APPROACH (CORRECT):
    Configure SSL in DATABASE_URL: ?sslmode=require
    DO NOT pass sslmode as a kwarg in connect_args
    
    Args:
        environment: Application environment (production, development, test, etc.)
        
    Returns:
        Deprecated - raises error to prevent misuse
    """
    logger.error(
        "get_ssl_config() is deprecated and should not be used. "
        "Configure SSL in DATABASE_URL: postgresql://...?sslmode=require"
    )
    raise DeprecationWarning(
        "get_ssl_config() is deprecated. "
        "Use DATABASE_URL with ?sslmode=require instead."
    )
