"""
Database configuration validation utilities.

This module provides shared validation logic for database configuration
that can be used by both startup validation and runtime database initialization.
"""

import os
from typing import Tuple, List, Optional


def validate_database_config() -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate database configuration from environment variables.
    
    Checks for either:
    1. A complete DATABASE_URL (or DATABASE_PRIVATE_URL/POSTGRES_URL), OR
    2. All individual PostgreSQL variables (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE)
    
    Returns:
        Tuple of (is_valid, connection_source, missing_variables):
        - is_valid: True if configuration is valid
        - connection_source: String describing which config method is used
          (e.g., "DATABASE_URL", "DATABASE_PRIVATE_URL", "Individual PG* variables")
        - missing_variables: List of missing variable names (empty if valid)
    """
    # Check for complete DATABASE_URL first
    database_url = (
        os.getenv("DATABASE_PRIVATE_URL") or 
        os.getenv("POSTGRES_URL") or 
        os.getenv("DATABASE_URL")
    )
    
    if database_url:
        # Found a complete DATABASE_URL
        if os.getenv("DATABASE_PRIVATE_URL"):
            return True, "DATABASE_PRIVATE_URL", []
        elif os.getenv("POSTGRES_URL"):
            return True, "POSTGRES_URL", []
        else:
            return True, "DATABASE_URL", []
    
    # DATABASE_URL not found, check for individual PG* variables
    pghost = os.getenv("PGHOST")
    pgport = os.getenv("PGPORT")  # Optional, defaults to 5432
    pguser = os.getenv("PGUSER")
    pgpassword = os.getenv("PGPASSWORD")
    pgdatabase = os.getenv("PGDATABASE")
    
    # PGPORT is optional (defaults to 5432), so only check required variables
    missing_vars = []
    if not pghost:
        missing_vars.append("PGHOST")
    if not pguser:
        missing_vars.append("PGUSER")
    if not pgpassword:
        missing_vars.append("PGPASSWORD")
    if not pgdatabase:
        missing_vars.append("PGDATABASE")
    
    if missing_vars:
        # Missing some required individual variables
        # Note: We mention PGPORT in the list even though it's optional
        # because users should know about all PG* variables
        return False, None, missing_vars
    else:
        # All required individual variables are present
        return True, "Individual PG* variables", []


def get_database_host() -> Optional[str]:
    """
    Get the database hostname from configuration.
    
    Returns:
        Database hostname or None if not configured
    """
    # Try DATABASE_URL first
    database_url = (
        os.getenv("DATABASE_PRIVATE_URL") or 
        os.getenv("POSTGRES_URL") or 
        os.getenv("DATABASE_URL")
    )
    
    if database_url and "://" in database_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            return parsed.hostname
        except Exception:
            pass
    
    # Fall back to PGHOST
    return os.getenv("PGHOST")
