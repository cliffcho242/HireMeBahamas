"""
Database URL utility functions for Vercel Postgres and other cloud databases.

This module provides shared utilities for processing database connection URLs,
including automatic SSL mode enforcement for Vercel Postgres (Neon).
"""
import logging
from typing import Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def validate_database_url_structure(db_url: str) -> Tuple[bool, str]:
    """Validate that DATABASE_URL meets strict requirements for cloud deployment.
    
    Requirements:
    1. Must contain a hostname (not localhost, 127.0.0.1, or empty)
    2. Must contain a port number
    3. Must use TCP connection (no Unix sockets)
    4. Must have SSL mode configured
    
    Args:
        db_url: Database connection URL to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
        If valid, error_message is empty. If invalid, contains explanation.
    
    Examples:
        ❌ BAD (causes socket usage):
        - postgresql://user:pass@/dbname
        - postgresql://user:pass@localhost/dbname
        - postgresql://user:pass@127.0.0.1/dbname
        
        ✅ CORRECT (Neon example):
        postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require
        ✔ Host present
        ✔ Port present
        ✔ TCP enforced
        ✔ SSL required
    """
    if not db_url:
        return False, "DATABASE_URL is empty or None"
    
    try:
        # Parse the URL
        parsed = urlparse(db_url)
        
        # Check 1: Must have a hostname
        if not parsed.hostname:
            return False, (
                "DATABASE_URL missing hostname. "
                "Format: postgresql://user:pass@hostname:port/dbname?sslmode=require"
            )
        
        # Check 2: Hostname must NOT be localhost or 127.0.0.1 (Unix socket usage)
        hostname = parsed.hostname.lower()
        if hostname in ('localhost', '127.0.0.1', '::1'):
            return False, (
                f"DATABASE_URL uses '{parsed.hostname}' which may cause socket usage. "
                "Use a remote database hostname instead. "
                "Example: ep-xxxx.us-east-1.aws.neon.tech"
            )
        
        # Check 3: Must have an explicit port number
        if not parsed.port:
            return False, (
                "DATABASE_URL missing port number. "
                "Add explicit port (e.g., :5432) after hostname. "
                "Example: postgresql://user:pass@hostname:5432/dbname?sslmode=require"
            )
        
        # Check 4: Must have sslmode parameter for SSL/TLS
        query_params = parsed.query.lower()
        if 'sslmode=' not in query_params:
            return False, (
                "DATABASE_URL missing sslmode parameter. "
                "Add ?sslmode=require to enforce SSL. "
                "Example: postgresql://user:pass@hostname:5432/dbname?sslmode=require"
            )
        
        # All checks passed
        return True, ""
        
    except Exception as e:
        return False, f"Failed to parse DATABASE_URL: {str(e)}"


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
