"""
Database utility functions for URL manipulation and SSL configuration.

This module provides shared utilities for database configuration across
the application to avoid code duplication.
"""
import logging
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

logger = logging.getLogger(__name__)


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
