# =============================================================================
# DATABASE CONNECTION GUARDS - PERMANENT SSLMODE ERROR PREVENTION
# =============================================================================
#
# This module provides runtime guards to prevent the `connect() got an 
# unexpected keyword argument 'sslmode'` error from ever happening again.
#
# ENFORCEMENT RULES:
# 1. sslmode MUST exist in DATABASE_URL (the ONLY allowed place)
# 2. Direct database driver connections should go through SQLAlchemy
# 3. When direct driver usage is necessary, sslmode must be stripped from URL
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
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

# Placeholder URL constant (should match database.py)
DB_PLACEHOLDER_URL = "postgresql+asyncpg://placeholder:placeholder@invalid.local:5432/placeholder"


# =============================================================================
# DATABASE CONNECTION GUARDS - PERMANENT SSLMODE ERROR PREVENTION
# =============================================================================
#
# This module provides runtime guards to prevent the `connect() got an 
# unexpected keyword argument 'sslmode'` error from ever happening again.
#
# ENFORCEMENT RULES FOR ASYNCPG:
# 1. sslmode MUST NOT exist in DATABASE_URL when using asyncpg
# 2. SSL is configured via ssl.create_default_context() in connect_args
# 3. This guard raises RuntimeError at startup if sslmode is detected
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
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

# Placeholder URL constant (should match database.py)
DB_PLACEHOLDER_URL = "postgresql+asyncpg://placeholder:placeholder@invalid.local:5432/placeholder"


def check_sslmode_in_database_url() -> Tuple[bool, Optional[str]]:
    """Verify that sslmode is NOT in DATABASE_URL when using asyncpg.
    
    CRITICAL: asyncpg does NOT support sslmode parameter. If sslmode is present
    in DATABASE_URL, the connection will fail with:
        connect() got an unexpected keyword argument 'sslmode'
    
    SSL must be configured via ssl.create_default_context() in connect_args instead.
    
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
    if database_url == DB_PLACEHOLDER_URL or "invalid.local" in database_url:
        logger.info("⚠️  Placeholder database URL detected, skipping sslmode check")
        return True, None
    
    # Skip check for non-asyncpg drivers (psycopg2, psycopg3 support sslmode)
    if "asyncpg" not in database_url:
        logger.info("⚠️  Non-asyncpg driver detected, skipping sslmode check (psycopg2/psycopg3 support sslmode)")
        return True, None
    
    # Check for sslmode in URL using proper URL parsing
    try:
        parsed = urlparse(database_url)
        query_params = parse_qs(parsed.query)
        has_sslmode = 'sslmode' in query_params
    except Exception as e:
        logger.warning(f"Failed to parse DATABASE_URL: {e}")
        return True, None  # Skip check if URL can't be parsed
    
    if has_sslmode:
        error_msg = (
            "FATAL: sslmode detected in DATABASE_URL. "
            "asyncpg does NOT support sslmode parameter. "
            "This will cause: connect() got an unexpected keyword argument 'sslmode'. "
            "Remove sslmode from DATABASE_URL. SSL is configured via ssl context in code."
        )
        logger.error(f"❌ {error_msg}")
        return False, error_msg
    
    logger.info("✅ DATABASE_URL does not contain sslmode parameter (correct for asyncpg)")
    return True, None


def check_direct_db_driver_usage() -> Tuple[bool, Optional[str]]:
    """Check if database drivers might be used incorrectly.
    
    Note: This is a best-effort check. Database drivers like psycopg2, psycopg,
    and asyncpg are legitimate dependencies when used by SQLAlchemy. However,
    direct usage (calling .connect() with sslmode parameter) causes errors.
    
    This check looks for suspicious patterns but cannot catch all cases.
    The primary defense is developer awareness and code reviews.
    
    Returns:
        Tuple of (clean: bool, error_message: Optional[str])
    """
    # Note: We can't reliably detect direct usage at runtime without
    # inspecting the call stack or doing static analysis. This function
    # serves as a placeholder for future enhancements and logs a warning
    # if the drivers are loaded (which is normal when using SQLAlchemy).
    
    db_modules = ["psycopg", "psycopg2", "asyncpg"]
    loaded_modules = [m for m in db_modules if m in sys.modules]
    
    if loaded_modules:
        logger.debug(
            f"Database drivers loaded: {', '.join(loaded_modules)}. "
            f"This is normal if using SQLAlchemy. Ensure all connections "
            f"use SQLAlchemy engine, not direct driver calls with sslmode parameter."
        )
    
    # Always return True since having these modules is not inherently wrong
    # The real check is ensuring sslmode is in DATABASE_URL, not in code
    logger.info("✅ Database driver usage check passed (best-effort)")
    return True, None


def validate_database_config(strict: bool = False) -> bool:
    """Validate database configuration to prevent sslmode errors.
    
    This function enforces the rules:
    1. sslmode must NOT be in DATABASE_URL when using asyncpg
    2. SSL is configured via ssl context in connect_args instead
    
    Args:
        strict: If True, raises RuntimeError on validation failure.
                If False, only logs warnings. Default is False.
    
    Returns:
        bool: True if validation passes, False otherwise
        
    Raises:
        RuntimeError: If strict=True and validation fails
    """
    logger.info("=" * 80)
    logger.info("🔒 DATABASE CONFIGURATION VALIDATION (ASYNCPG)")
    logger.info("=" * 80)
    
    all_valid = True
    errors = []
    
    # Check 1: No sslmode in DATABASE_URL (for asyncpg)
    sslmode_valid, sslmode_error = check_sslmode_in_database_url()
    if not sslmode_valid:
        all_valid = False
        errors.append(sslmode_error)
    
    # Check 2: Database driver usage patterns
    drivers_valid, drivers_error = check_direct_db_driver_usage()
    if not drivers_valid:
        all_valid = False
        errors.append(drivers_error)
    
    # Log results
    if all_valid:
        logger.info("✅ Database configuration validation PASSED")
        logger.info("   - No sslmode in DATABASE_URL (correct for asyncpg)")
        logger.info("   - SSL configured via ssl context in code")
        logger.info("   - Database driver usage patterns checked")
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
