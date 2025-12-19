"""
Database URL utility functions for Vercel Postgres and other cloud databases.

This module provides shared utilities for processing database connection URLs.

⚠️ DEPRECATION NOTICE (Dec 2025):
The ensure_sslmode() function is DEPRECATED. asyncpg does NOT support sslmode
parameter. SSL must be configured via ssl.create_default_context() in connect_args.

For asyncpg-based connections:
- ❌ DO NOT use sslmode in DATABASE_URL
- ✅ USE ssl context in connect_args

For psycopg2/psycopg3 connections:
- ✅ sslmode in DATABASE_URL works fine
"""
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)


# Validation functions removed - DATABASE_URL is now used as-is from environment
# to improve startup performance and reduce potential startup failures.
# Users must ensure DATABASE_URL is properly formatted before deployment.


def ensure_sslmode(db_url: str) -> str:
    """DEPRECATED: Ensure SSL mode is set in the database URL.
    
    ⚠️ WARNING: This function is DEPRECATED and should NOT be used with asyncpg.
    asyncpg does NOT support sslmode parameter. Attempting to use sslmode with
    asyncpg will cause: connect() got an unexpected keyword argument 'sslmode'
    
    For asyncpg connections:
    - Remove this function call
    - Configure SSL via ssl.create_default_context() in connect_args
    
    For psycopg2/psycopg3 connections:
    - This function still works but is unnecessary
    - You can configure sslmode directly in DATABASE_URL
    
    Args:
        db_url: Database connection URL
        
    Returns:
        Database URL unchanged (this function no longer modifies URLs)
        
    Deprecated:
        Use ssl context in connect_args instead:
        
        import ssl
        ssl_context = ssl.create_default_context()
        engine = create_async_engine(
            db_url,
            connect_args={"ssl": ssl_context}
        )
    """
    logger.warning(
        "ensure_sslmode() is DEPRECATED. "
        "asyncpg does NOT support sslmode parameter. "
        "Use ssl.create_default_context() in connect_args instead."
    )
    # Return URL unchanged - do not add sslmode for asyncpg compatibility
    return db_url


def url_encode_password(password: str) -> str:
    """URL-encode a database password for safe use in connection strings.
    
    Special characters in passwords must be URL-encoded when used in DATABASE_URL.
    This function properly encodes common special characters that cause parsing issues.
    
    Args:
        password: Raw password that may contain special characters
        
    Returns:
        URL-encoded password safe for use in connection strings
        
    Examples:
        >>> url_encode_password("p@ss:word")
        'p%40ss%3Aword'
        
        >>> url_encode_password("my#secret")
        'my%23secret'
        
        >>> url_encode_password("simple123")
        'simple123'
    
    Common encodings:
        @ → %40
        : → %3A
        # → %23
        / → %2F
        ? → %3F
        & → %26
        % → %25
    """
    # Use quote() with safe='' to encode all special characters
    # This ensures characters like @, :, #, /, etc. are properly encoded
    return quote(password, safe='')


# Password encoding validation function removed - DATABASE_URL is now used as-is.
# Users should use the url_encode_password() function above to encode passwords
# with special characters before setting DATABASE_URL in their environment.
