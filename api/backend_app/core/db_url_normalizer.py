"""
Database URL normalization utility for mixed sync/async driver compatibility.

This module provides a helper function to normalize DATABASE_URL for different
database drivers:
- Async connections (SQLAlchemy + asyncpg) need: postgresql+asyncpg://
- Sync connections (psycopg2, psycopg) need: postgresql://

This allows a single DATABASE_URL environment variable to work with both
connection types.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def normalize_database_url(url: Optional[str], for_async: bool = False) -> Optional[str]:
    """
    Normalize DATABASE_URL for the target driver.
    
    This function strips or adds driver-specific suffixes to make DATABASE_URL
    compatible with both async (asyncpg) and sync (psycopg2) database drivers.
    
    Args:
        url: The database URL to normalize. If None or empty, returns as-is.
        for_async: If True, ensure URL has +asyncpg suffix for async connections;
                   if False, remove driver suffix for sync connections (psycopg2)
        
    Returns:
        Normalized database URL, or None if input is None/empty
        
    Examples:
        >>> # For sync connections (psycopg2)
        >>> normalize_database_url("postgresql+asyncpg://user:pass@host/db", for_async=False)
        'postgresql://user:pass@host/db'
        
        >>> # For async connections (asyncpg)
        >>> normalize_database_url("postgresql://user:pass@host/db", for_async=True)
        'postgresql+asyncpg://user:pass@host/db'
        
        >>> # Already correct format
        >>> normalize_database_url("postgresql://user:pass@host/db", for_async=False)
        'postgresql://user:pass@host/db'
    
    Notes:
        - Handles postgres:// and postgresql:// schemes
        - Removes +asyncpg, +psycopg2, and other driver suffixes for sync mode
        - Adds +asyncpg suffix for async mode
        - Preserves all other URL components (host, port, database, parameters, etc.)
    """
    if not url:
        return url
    
    # Remove any existing driver suffix to get base URL
    # This handles: postgresql+asyncpg://, postgresql+psycopg2://, postgresql+psycopg://
    normalized = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    normalized = normalized.replace("postgresql+psycopg2://", "postgresql://", 1)
    normalized = normalized.replace("postgresql+psycopg://", "postgresql://", 1)
    
    # Also normalize postgres:// to postgresql:// for consistency
    # postgres:// is a valid scheme but postgresql:// is more explicit
    normalized = normalized.replace("postgres://", "postgresql://", 1)
    
    # Add asyncpg suffix if needed for async connections
    if for_async and normalized.startswith("postgresql://"):
        normalized = normalized.replace("postgresql://", "postgresql+asyncpg://", 1)
        logger.debug(f"Converted database URL to async format (postgresql+asyncpg://)")
    elif not for_async and "+" in normalized.split("://")[0]:
        # This shouldn't happen after our replacements above, but log it for safety
        logger.debug(f"Removed driver suffix for sync connection (postgresql://)")
    
    return normalized


def get_url_scheme(url: Optional[str]) -> Optional[str]:
    """
    Extract the scheme (protocol) from a database URL.
    
    Args:
        url: Database URL to extract scheme from
        
    Returns:
        The URL scheme (e.g., "postgresql+asyncpg", "postgresql"), or None if invalid
        
    Examples:
        >>> get_url_scheme("postgresql+asyncpg://host/db")
        'postgresql+asyncpg'
        
        >>> get_url_scheme("postgresql://host/db")
        'postgresql'
    """
    if not url or "://" not in url:
        return None
    
    return url.split("://")[0]


def is_async_url(url: Optional[str]) -> bool:
    """
    Check if a database URL is configured for async connections.
    
    Args:
        url: Database URL to check
        
    Returns:
        True if URL contains +asyncpg suffix, False otherwise
        
    Examples:
        >>> is_async_url("postgresql+asyncpg://host/db")
        True
        
        >>> is_async_url("postgresql://host/db")
        False
    """
    if not url:
        return False
    
    return "+asyncpg" in url
