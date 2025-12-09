"""
Database URL utility functions for Vercel Postgres and other cloud databases.

This module provides shared utilities for processing database connection URLs,
including automatic SSL mode enforcement for Vercel Postgres (Neon).
"""


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
