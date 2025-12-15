"""
Database configuration validation utilities.

This module provides shared validation logic for database configuration
that can be used by both startup validation and runtime database initialization.

NEON DATABASE FORMAT:
DATABASE_URL=postgresql://USER:ENCODED_PASSWORD@ep-xxxxx.REGION.aws.neon.tech:5432/DB_NAME?sslmode=require
"""

import os
from typing import Tuple, List, Optional


def validate_database_config() -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate database configuration from environment variables.
    
    Checks for DATABASE_URL only (PGHOST, PGUSER, PGPASSWORD, PGDATABASE are no longer supported).
    
    Returns:
        Tuple of (is_valid, connection_source, missing_variables):
        - is_valid: True if DATABASE_URL is set
        - connection_source: "DATABASE_URL" if valid, None otherwise
        - missing_variables: List containing "DATABASE_URL" if not set, empty otherwise
    """
    # Check for DATABASE_URL only
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        return True, "DATABASE_URL", []
    else:
        return False, None, ["DATABASE_URL"]


def get_database_host() -> Optional[str]:
    """
    Get the database hostname from configuration.
    
    Returns:
        Database hostname or None if not configured
    """
    database_url = os.getenv("DATABASE_URL")
    
    if database_url and "://" in database_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            return parsed.hostname
        except Exception:
            pass
    
    return None
