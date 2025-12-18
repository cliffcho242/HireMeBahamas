"""
Database URL utility functions for Vercel Postgres and other cloud databases.

This module provides shared utilities for processing database connection URLs,
including automatic SSL mode enforcement for Vercel Postgres (Neon).
"""
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)


# Validation function removed - DATABASE_URL is used as-is


def ensure_sslmode(db_url: str) -> str:
    """Ensure SSL mode is set in the database URL.
    
    Vercel Postgres (Neon) and other cloud databases require SSL connections.
    This function automatically adds ?sslmode=require to URLs that don't have
    SSL mode specified.
    
    Args:
        db_url: Database connection URL
        
    Returns:
        Database URL with sslmode parameter added if it was missing
        
    Examples:
        >>> ensure_sslmode("postgresql://user:pass@host/db")
        'postgresql://user:pass@host/db?sslmode=require'
        
        >>> ensure_sslmode("postgresql://user:pass@host/db?timeout=10")
        'postgresql://user:pass@host/db?timeout=10&sslmode=require'
        
        >>> ensure_sslmode("postgresql://user:pass@host/db?sslmode=prefer")
        'postgresql://user:pass@host/db?sslmode=prefer'
    """
    if "?" not in db_url:
        # No query parameters - add sslmode=require
        return f"{db_url}?sslmode=require"
    elif "sslmode=" not in db_url:
        # Has query parameters but no sslmode - append it
        return f"{db_url}&sslmode=require"
    # else: sslmode is already present, don't override user's explicit setting
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


# Password encoding validation function removed - DATABASE_URL is used as-is
