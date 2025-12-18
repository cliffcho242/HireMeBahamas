"""
Database URL utility functions for Vercel Postgres and other cloud databases.

This module provides shared utilities for processing database connection URLs,
including automatic SSL mode enforcement for Vercel Postgres (Neon).
"""
import logging
import re
from typing import Tuple
from urllib.parse import urlparse, quote

logger = logging.getLogger(__name__)


def validate_database_url_structure(db_url: str) -> Tuple[bool, str]:
    """Validate that DATABASE_URL meets strict requirements for cloud deployment.
    
    Requirements:
    1. Must contain a hostname (not localhost, 127.0.0.1, or empty)
    2. Must contain a port number
    3. Must use TCP connection (no Unix sockets)
    4. Must not contain whitespace (leading, trailing, or embedded)
    5. Must not contain quotes (single or double)
    
    Note: SSL mode (sslmode parameter) is handled separately by the ensure_sslmode()
    function, which automatically adds ?sslmode=require if it's missing. This
    validation function does not check for sslmode to avoid redundancy.
    
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
        - postgresql://user:pass@ep-xxxx.neon.tech:5432/dbname ?sslmode=require
        - postgresql://user:pass @ep-xxxx.neon.tech:5432/dbname?sslmode=require
        -  postgresql://user:pass@ep-xxxx.neon.tech:5432/dbname?sslmode=require
        
        ❌ BAD (contains quotes):
        - "postgresql://user:pass@ep-xxxx.neon.tech:5432/dbname?sslmode=require"
        - 'postgresql://user:pass@ep-xxxx.neon.tech:5432/dbname?sslmode=require'
        - postgresql://"user":pass@ep-xxxx.neon.tech:5432/dbname?sslmode=require
        
        ✅ CORRECT (Neon example - before ensure_sslmode):
        postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname
        ✔ Real hostname (ep-xxxx.us-east-1.aws.neon.tech)
        ✔ Port present (:5432)
        ✔ TCP enforced
        ✔ No spaces
        ✔ No quotes
        
        After ensure_sslmode() is called, it becomes:
        postgresql://USER:PASSWORD@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require
    """
    if not db_url:
        return False, "DATABASE_URL is empty or None"
    
    # Check 0: Must not contain whitespace
    # Whitespace in URLs can cause parsing errors and connection failures
    if db_url != db_url.strip():
        return False, (
            "DATABASE_URL contains leading or trailing whitespace. "
            "Remove all spaces from the connection string. "
            "Example: postgresql://user:pass@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require"
        )
    
    # Check for embedded whitespace (spaces within the URL)
    if ' ' in db_url or '\t' in db_url or '\n' in db_url:
        return False, (
            "DATABASE_URL contains whitespace characters. "
            "Remove all spaces, tabs, and newlines from the connection string. "
            "Example: postgresql://user:pass@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require"
        )
    
    # Check for quotes (single or double)
    # Quotes should not be in the DATABASE_URL as they can cause parsing errors
    # and are often a sign of incorrect copy-paste from configuration files
    if any(quote in db_url for quote in ['"', "'"]):
        return False, (
            "DATABASE_URL contains quote characters (single or double quotes). "
            "Remove all quotes from the connection string. "
            "Do not wrap the URL in quotes - paste it directly without any surrounding quotes. "
            "Example: postgresql://user:pass@ep-xxxx.us-east-1.aws.neon.tech:5432/dbname?sslmode=require"
        )
    
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
        
        # Note: sslmode parameter validation removed as redundant
        # The ensure_sslmode() function automatically adds sslmode=require if missing
        # This validation would always pass after ensure_sslmode() is called
        
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


def validate_password_encoding(db_url: str) -> Tuple[bool, str]:
    """Validate that password in DATABASE_URL is properly URL-encoded.
    
    Checks for common unencoded special characters in the password portion
    of the URL that could cause parsing errors.
    
    Args:
        db_url: Database connection URL to validate
        
    Returns:
        Tuple of (is_valid: bool, warning_message: str)
        If valid, warning_message is empty. If invalid, contains guidance.
    
    Examples:
        >>> validate_password_encoding("postgresql://user:p@ss@host:5432/db")
        (False, "Password contains '@' which should be encoded as '%40'...")
        
        >>> validate_password_encoding("postgresql://user:p%40ss@host:5432/db")
        (True, "")
    """
    try:
        # Extract the password from URL if present
        parsed = urlparse(db_url)
        
        if not parsed.password:
            # No password in URL, nothing to validate
            return True, ""
        
        # Check for unencoded special characters in password
        # These characters MUST be URL-encoded in connection strings
        problematic_chars = {
            '@': '%40',
            ':': '%3A',
            '#': '%23',
            '/': '%2F',
            '?': '%3F',
            '&': '%26',
            '%': '%25',
            ' ': '%20',
        }
        
        found_issues = []
        for char, encoded in problematic_chars.items():
            # Skip % if it's already part of an encoding (e.g., %40)
            if char == '%':
                # Check if % is followed by two hex digits (proper encoding)
                if re.search(r'%[0-9A-Fa-f]{2}', parsed.password):
                    continue
            
            if char in parsed.password and encoded not in parsed.password:
                found_issues.append(f"'{char}' should be '{encoded}'")
        
        if found_issues:
            issues_str = ", ".join(found_issues)
            return False, (
                f"Password contains special characters that must be URL-encoded: {issues_str}. "
                f"Use the url_encode_password() function or manually encode special characters. "
                f"Example: password 'p@ss:word' should be 'p%40ss%3Aword'"
            )
        
        return True, ""
        
    except Exception as e:
        # If parsing fails, return generic warning
        return False, f"Could not validate password encoding: {str(e)}"
