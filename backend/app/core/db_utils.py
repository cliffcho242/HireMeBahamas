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
    Remove sslmode parameter from DATABASE_URL for asyncpg compatibility.
    
    asyncpg does NOT accept sslmode in URL - it must be in connect_args.
    sslmode in URL causes: connect() got an unexpected keyword argument 'sslmode'
    
    Args:
        database_url: Database connection URL
        
    Returns:
        URL with sslmode parameter removed
    """
    if not database_url or "sslmode=" not in database_url:
        return database_url
    
    parsed_url = urlparse(database_url)
    # Parse query parameters
    query_params = parse_qs(parsed_url.query)
    
    # Remove sslmode parameter if present
    if 'sslmode' in query_params:
        del query_params['sslmode']
        logger.info("Removed sslmode from DATABASE_URL (asyncpg requires SSL in connect_args)")
    
    # Reconstruct query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct URL
    cleaned_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))
    
    return cleaned_url


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
    if default_port:
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
    Get SSL configuration value based on environment.
    
    Args:
        environment: Application environment (production, development, test, etc.)
        
    Returns:
        SSL configuration value: 'require' for production, True for others
    """
    # In production, enforce SSL with 'require'
    # In development/test, enable SSL with True (allows unencrypted fallback)
    return "require" if environment == "production" else True
