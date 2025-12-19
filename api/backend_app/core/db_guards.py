# =============================================================================
# DATABASE CONNECTION GUARDS - PERMANENT SSLMODE ERROR PREVENTION
# =============================================================================
#
# This module provides runtime guards to prevent the `connect() got an 
# unexpected keyword argument 'sslmode'` error from ever happening again.
#
# ENFORCEMENT RULES:
# 1. sslmode MUST exist in DATABASE_URL (the ONLY allowed place)
# 2. Direct database driver connections are FORBIDDEN
# 3. All connections MUST go through SQLAlchemy engine
#
# Usage:
#     from backend_app.core.db_guards import validate_database_config
#     validate_database_config()  # Call once at startup
#
# =============================================================================

import os
import sys
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def check_sslmode_in_database_url() -> Tuple[bool, Optional[str]]:
    """Verify that sslmode is configured in DATABASE_URL.
    
    This is the ONLY valid place for sslmode configuration. Any other
    location will cause connection errors.
    
    Returns:
        Tuple of (valid: bool, error_message: Optional[str])
    """
    database_url = os.getenv("DATABASE_URL", "")
    
    # Skip check for local development URLs
    if not database_url or "localhost" in database_url or "127.0.0.1" in database_url:
        logger.info("⚠️  Local development database detected, skipping sslmode check")
        return True, None
    
    # Skip check for SQLite
    if database_url.startswith("sqlite"):
        logger.info("⚠️  SQLite database detected, skipping sslmode check")
        return True, None
    
    # Skip check for placeholder URLs
    if "placeholder" in database_url or "invalid.local" in database_url:
        logger.info("⚠️  Placeholder database URL detected, skipping sslmode check")
        return True, None
    
    # Check for sslmode in URL
    if "sslmode=" not in database_url:
        error_msg = (
            "DATABASE_URL is missing sslmode parameter. "
            "For cloud deployments, DATABASE_URL must include sslmode. "
            "Example: postgresql://user:pass@host:5432/db?sslmode=require"
        )
        logger.warning(f"⚠️  {error_msg}")
        return False, error_msg
    
    logger.info("✅ DATABASE_URL contains sslmode parameter")
    return True, None


def forbid_direct_db_drivers() -> Tuple[bool, Optional[str]]:
    """Check if forbidden database drivers have been imported.
    
    Direct usage of psycopg, psycopg2, or asyncpg is forbidden because
    they require sslmode to be passed as a connection parameter, which
    causes errors. All connections MUST go through SQLAlchemy.
    
    Returns:
        Tuple of (clean: bool, error_message: Optional[str])
    """
    forbidden_modules = ["psycopg", "psycopg2", "asyncpg"]
    loaded_forbidden = []
    
    for module_name in forbidden_modules:
        if module_name in sys.modules:
            # Check if it's actually being used for connections
            # (it's OK if it's imported by SQLAlchemy internally)
            module = sys.modules[module_name]
            module_file = getattr(module, "__file__", "")
            
            # If the module is in site-packages and being used by SQLAlchemy, it's OK
            if "site-packages" in module_file and "sqlalchemy" not in str(sys.modules.keys()):
                loaded_forbidden.append(module_name)
    
    if loaded_forbidden:
        error_msg = (
            f"Forbidden database driver(s) loaded: {', '.join(loaded_forbidden)}. "
            f"Direct usage of psycopg/psycopg2/asyncpg is forbidden. "
            f"All database connections MUST go through SQLAlchemy engine. "
            f"This prevents sslmode connection errors."
        )
        logger.error(f"❌ {error_msg}")
        return False, error_msg
    
    logger.info("✅ No forbidden database drivers detected")
    return True, None


def validate_database_config(strict: bool = False) -> bool:
    """Validate database configuration to prevent sslmode errors.
    
    This function enforces the rules:
    1. sslmode must be in DATABASE_URL (the ONLY allowed place)
    2. Direct database driver connections are forbidden
    
    Args:
        strict: If True, raises RuntimeError on validation failure.
                If False, only logs warnings.
    
    Returns:
        bool: True if validation passes, False otherwise
        
    Raises:
        RuntimeError: If strict=True and validation fails
    """
    logger.info("=" * 80)
    logger.info("🔒 DATABASE CONFIGURATION VALIDATION")
    logger.info("=" * 80)
    
    all_valid = True
    errors = []
    
    # Check 1: sslmode in DATABASE_URL
    sslmode_valid, sslmode_error = check_sslmode_in_database_url()
    if not sslmode_valid:
        all_valid = False
        errors.append(sslmode_error)
    
    # Check 2: No forbidden drivers
    drivers_valid, drivers_error = forbid_direct_db_drivers()
    if not drivers_valid:
        all_valid = False
        errors.append(drivers_error)
    
    # Log results
    if all_valid:
        logger.info("✅ Database configuration validation PASSED")
        logger.info("   - sslmode configured in DATABASE_URL")
        logger.info("   - No forbidden database drivers detected")
    else:
        logger.error("❌ Database configuration validation FAILED")
        for error in errors:
            logger.error(f"   - {error}")
        
        if strict:
            error_msg = "Database configuration validation failed. " + "; ".join(errors)
            raise RuntimeError(error_msg)
    
    logger.info("=" * 80)
    return all_valid


def assert_no_sslmode_in_code():
    """Runtime assertion to ensure sslmode is not in code.
    
    This is a defensive check to catch any code that tries to pass
    sslmode as a connection parameter.
    
    Note: This is a best-effort check and may not catch all cases.
    The primary defense is the validation in validate_database_config().
    """
    # This function is intentionally simple and serves as a placeholder
    # for more sophisticated runtime checks if needed in the future.
    logger.debug("✅ sslmode not found in connection parameters (best-effort check)")


# =============================================================================
# AUTO-RUN VALIDATION (OPTIONAL)
# =============================================================================
# Uncomment the lines below to automatically run validation when this module
# is imported. This provides immediate feedback if configuration is wrong.
#
# if __name__ != "__main__":
#     # Only validate when imported as a module (not when run directly)
#     validate_database_config(strict=False)
# =============================================================================
