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
    4. Must not contain whitespace (leading, trailing, or embedded)
    5. Must not contain quotes (single or double)
    
    ⚠️  CRITICAL: This function does NOT validate or require sslmode parameter.
    For Neon pooled connections, sslmode is NOT supported and will cause crashes.
    
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
        
        ❌ BAD (contains whitespace):
        - postgresql://user:pass@ep-xxxx.neon.tech:5432/dbname ?param=value
        - postgresql://user:pass @ep-xxxx.neon.tech:5432/dbname
        -  postgresql://user:pass@ep-xxxx.neon.tech:5432/dbname
        
        ❌ BAD (contains quotes):
        - "postgresql://user:pass@ep-xxxx.neon.tech:5432/dbname"
        - 'postgresql://user:pass@ep-xxxx.neon.tech:5432/dbname'
        - postgresql://"user":pass@ep-xxxx.neon.tech:5432/dbname
        
        ✅ CORRECT (Neon pooled connection):
        postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname
        ✔ Real hostname (ep-xxxx.us-east-1.aws.neon.tech)
        ✔ Port present (:5432)
        ✔ TCP enforced
        ✔ No spaces
        ✔ No quotes
        ✔ NO sslmode parameter (not supported by Neon pooler)
    """
    if not db_url:
        return False, "DATABASE_URL is empty or None"
    
    # Check 0: Must not contain whitespace
    # Whitespace in URLs can cause parsing errors and connection failures
    if db_url != db_url.strip():
        return False, (
            "DATABASE_URL contains leading or trailing whitespace. "
            "Remove all spaces from the connection string. "
            "Example: postgresql://user:pass@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname"
        )
    
    # Check for embedded whitespace (spaces within the URL)
    if ' ' in db_url or '\t' in db_url or '\n' in db_url:
        return False, (
            "DATABASE_URL contains whitespace characters. "
            "Remove all spaces, tabs, and newlines from the connection string. "
            "Example: postgresql://user:pass@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname"
        )
    
    # Check for quotes (single or double)
    # Quotes should not be in the DATABASE_URL as they can cause parsing errors
    # and are often a sign of incorrect copy-paste from configuration files
    if any(quote in db_url for quote in ['"', "'"]):
        return False, (
            "DATABASE_URL contains quote characters (single or double quotes). "
            "Remove all quotes from the connection string. "
            "Do not wrap the URL in quotes - paste it directly without any surrounding quotes. "
            "Example: postgresql://user:pass@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname"
        )
    
    try:
        # Parse the URL
        parsed = urlparse(db_url)
        
        # Check 1: Must have a hostname
        if not parsed.hostname:
            return False, (
                "DATABASE_URL missing hostname. "
                "Format: postgresql://user:pass@hostname:port/dbname"
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
                "Example: postgresql://user:pass@hostname:5432/dbname"
            )
        
        # ⚠️  CRITICAL: sslmode validation REMOVED
        # Neon pooled connections (PgBouncer) do NOT support sslmode parameter
        # Adding sslmode will cause connection crashes
        # SSL is handled automatically by the Neon proxy
        
        # All checks passed
        return True, ""
        
    except Exception as e:
        return False, f"Failed to parse DATABASE_URL: {str(e)}"


def ensure_sslmode(db_url: str) -> str:
    """DEPRECATED: Do NOT use sslmode with Neon pooled connections.
    
    ⚠️  CRITICAL: This function is DEPRECATED and should NOT be used.
    
    Neon pooled connections (PgBouncer) do NOT support sslmode parameter.
    Adding sslmode to the URL will cause connection crashes.
    
    This function now returns the URL unchanged to prevent adding sslmode.
    It is kept only for backward compatibility and will be removed in a future version.
    
    For Neon pooled connections:
    - Use the URL exactly as provided by Neon (without modifications)
    - SSL is handled automatically by the Neon proxy
    - Do NOT add any SSL-related parameters
    
    Args:
        db_url: Database connection URL
        
    Returns:
        Database URL unchanged (sslmode is NOT added)
    """
    # Return URL unchanged - DO NOT add sslmode for Neon compatibility
    return db_url
