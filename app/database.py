# =============================================================================
# DATABASE CONFIGURATION - SINGLE SOURCE OF TRUTH (SYNC SQLAlchemy)
# =============================================================================
#
# This module is the SINGLE SOURCE OF TRUTH for all database configuration
# in the HireMeBahamas application. All other database modules should import
# from this module to ensure consistent configuration across the application.
#
# ⚠️  SYNC SQLAlchemy (Option A): This module uses synchronous SQLAlchemy
# with psycopg2 driver instead of async SQLAlchemy with asyncpg.
#
# ✅ RULE: For PostgreSQL + SQLAlchemy with psycopg2, SSL belongs in the URL
#
# This configuration works on:
# - Render
# - Railway
# - Neon
# - Vercel Postgres
# - SQLAlchemy 1.4 / 2.0
#
# DATABASE_URL FORMAT (copy-paste):
# postgresql://user:password@host:5432/database?sslmode=require
#
# ENV VARS (for Railway/Render/Vercel deployment):
# DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
# DB_POOL_RECYCLE=300
#
# Key improvements:
# 1. SSL configured via URL query string (?sslmode=require) - portable across platforms
# 2. pool_recycle=300 - prevents stale connections
# 3. pool_pre_ping=True - validates connections before use
# 4. connect_timeout=5 - handles cold starts
# =============================================================================

import os
import logging
import threading
from typing import Optional
from urllib.parse import urlparse, urlunparse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import ArgumentError

# Configure logging for database connection debugging
logger = logging.getLogger(__name__)

# Placeholder value for invalid database configuration
# This allows the app to start for health checks even with invalid config
# IMPORTANT: Uses a non-routable address (not localhost) to prevent accidental connections
DB_PLACEHOLDER_URL = "postgresql://placeholder:placeholder@invalid.local:5432/placeholder"

# =============================================================================
# DATABASE URL CONFIGURATION (SYNC SQLAlchemy)
# =============================================================================
# Priority order:
# 1. DATABASE_URL (Standard PostgreSQL connection - REQUIRED)
# 2. Local development default (only for development, not production)
#
# SYNC SQLALCHEMY FORMAT:
# DATABASE_URL=postgresql://USER:ENCODED_PASSWORD@host:5432/DB_NAME?sslmode=require
# Note: Uses psycopg2 driver (synchronous) instead of asyncpg
# =============================================================================

# Check if we're in production mode
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
# Also check ENV for consistency
ENV = os.getenv("ENV", "development")

# Get database URL - only DATABASE_URL is supported
DATABASE_URL = os.getenv("DATABASE_URL")

# Strip whitespace from DATABASE_URL to prevent connection errors
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

# =============================================================================
# PRODUCTION SAFETY: WARN IF POSTGRES NOT CONFIGURED (PRODUCTION-SAFE)
# =============================================================================
# This prevents silent SQLite usage in production while allowing app to start
# Check both ENV and ENVIRONMENT variables for consistency across the application
if (ENV == "production" or ENVIRONMENT == "production") and not DATABASE_URL:
    logger.warning(
        "DATABASE_URL is required in production. "
        "Please set DATABASE_URL environment variable with your PostgreSQL connection string. "
        "Format: postgresql://USER:PASSWORD@host:5432/DB_NAME?sslmode=require"
    )
    # Use placeholder to prevent crashes, connections will fail gracefully
    DATABASE_URL = DB_PLACEHOLDER_URL
elif not DATABASE_URL:
    # Use local development default only in development mode
    DATABASE_URL = "postgresql://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
    logger.warning("Using default local development database URL. Set DATABASE_URL for production.")
# =============================================================================

# Fix common typos in DATABASE_URL (e.g., "ostgresql" -> "postgresql")
# This handles cases where the 'p' is missing from "postgresql"
if "ostgresql" in DATABASE_URL and "postgresql" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("ostgresql", "postgresql")
    logger.info("✓ Auto-fixed DATABASE_URL typo: 'ostgresql' → 'postgresql' (update env var to fix permanently)")

# Ensure postgresql:// format (sync driver)
# Remove any async driver specifications
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
    logger.info("Converted DATABASE_URL from asyncpg to sync psycopg2 driver format")

# Strip whitespace from database name in the URL path
# This fixes cases like postgresql://user:pass@host:5432/Vercel (with trailing space)
try:
    parsed_url = urlparse(DATABASE_URL)
    if parsed_url.path:
        # Strip leading slash and whitespace from database name
        db_name = parsed_url.path.lstrip('/').strip()
        if db_name and db_name != parsed_url.path.lstrip('/'):
            # Reconstruct URL with cleaned database name only if it was changed
            new_path = '/' + db_name
            DATABASE_URL = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                new_path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            logger.info(f"✓ Auto-stripped whitespace from database name in URL")
except Exception as e:
    # If URL parsing fails, log warning but continue with original URL
    logger.warning(f"Could not parse DATABASE_URL for database name sanitization: {e}")

# NOTE: SQLAlchemy's create_async_engine() automatically handles URL decoding for
# special characters in username/password. No manual decoding is needed here.
# For example, passwords with '@' or '%' are automatically decoded from URL-encoded form.

# Validate DATABASE_URL format - ensure all required fields are present
# Parse and validate required fields using production-safe validation
# Only validate if DATABASE_URL is actually configured (not placeholder or local dev default)
if DATABASE_URL and DATABASE_URL != DB_PLACEHOLDER_URL:
    parsed = urlparse(DATABASE_URL)
    missing_fields = []
    if not parsed.username:
        missing_fields.append("username")
    if not parsed.password:
        missing_fields.append("password")
    if not parsed.hostname:
        missing_fields.append("hostname")
    if not parsed.path or len(parsed.path) <= 1:
        # path should be /database_name, so length > 1
        missing_fields.append("path")

    if missing_fields:
        # Production-safe: log warning instead of raising exception
        # This allows the app to start for health checks and diagnostics
        logger.warning(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")

# Log which database URL we're using (mask password for security)
def _mask_database_url(url: str) -> str:
    """Mask the password in a database URL for logging.
    
    Args:
        url: Database connection URL
        
    Returns:
        URL with password replaced by ****
    """
    if "@" not in url:
        return url
    try:
        # Split at @ to get auth and host parts
        auth_part, host_part = url.rsplit("@", 1)
        # Split auth part at last : to get user and password
        user_part = auth_part.rsplit(":", 1)[0]
        return f"{user_part}:****@{host_part}"
    except (ValueError, IndexError):
        return url

_masked_url = _mask_database_url(DATABASE_URL)
logger.info(f"Database URL: {_masked_url}")

# =============================================================================
# POOL CONFIGURATION - OPTIMIZED FOR PRODUCTION (Dec 2025)
# =============================================================================
# CRITICAL: pool_recycle=300 prevents connection issues by recycling connections
# before they become stale. This is serverless-friendly and prevents SSL EOF errors.
# MAX_OVERFLOW=10 allows burst capacity for production load
# =============================================================================
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))  # Minimum connections (5 = production-ready)
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))  # Burst capacity
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # Wait max 30s for connection
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "300"))  # Recycle every 5 min (serverless-friendly)

# =============================================================================
# CONNECTION TIMEOUT CONFIGURATION - CRITICAL FOR RAILWAY
# =============================================================================
# These timeouts prevent the dreaded "Connection timed out" error
CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))  # 5s for Railway cold starts
COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))  # 30s per query
STATEMENT_TIMEOUT_MS = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "30000"))  # 30s in milliseconds

# =============================================================================
# SSL CONFIGURATION
# =============================================================================
# SSL is configured via the DATABASE_URL query string parameter: ?sslmode=require
# This is the correct and portable way to configure SSL for PostgreSQL connections.
# No additional SSL configuration is needed in connect_args.
# =============================================================================

# =============================================================================
# CREATE SYNC ENGINE - LAZY INITIALIZATION FOR SERVERLESS (Vercel/Render)
# =============================================================================
# ✅ GOOD PATTERN: Lazy connection initialization
# - Defers connection until first request (not at module import)
# - Uses pool_pre_ping=True to validate connections before use
# - Uses pool_recycle=300 (5 min) to prevent stale connections
#
# This pattern PERMANENTLY FIXES serverless issues:
# 1. pool_pre_ping=True - validates connections before use (detects dead connections)
# 2. pool_recycle=300 - recycles connections (serverless-friendly)
# 3. connect_timeout=5 - allows Railway cold starts
# 4. SSL configured via URL query string (?sslmode=require)
#
# COPY-PASTE ENV VARS FOR RAILWAY/RENDER/VERCEL:
# DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
# DB_POOL_RECYCLE=300
# =============================================================================

# Global engine instance (initialized lazily on first use)
_engine = None
_engine_lock = threading.Lock()

def get_engine():
    """Get or create database engine (lazy initialization for serverless).
    
    ✅ GOOD PATTERN: Defers connection until first request.
    This prevents connection issues on Vercel/Render where connections
    at module import time can cause failures.
    
    Thread-safe: Uses a lock to ensure only one engine is created even
    when accessed from multiple threads simultaneously.
    
    CRITICAL BEHAVIOR: Returns None if engine creation fails, allowing the
    application to start even with invalid DATABASE_URL configuration.
    This fulfills the "apps must boot without the database" requirement.
    
    Returns:
        Engine | None: Database engine instance or None if creation fails
    """
    global _engine
    
    # Double-checked locking pattern for thread safety
    if _engine is None:
        with _engine_lock:
            # Check again inside the lock in case another thread created it
            if _engine is None:
                # Check if DATABASE_URL is the placeholder (invalid config)
                if DATABASE_URL == DB_PLACEHOLDER_URL:
                    logger.warning(
                        "Database engine not created: DATABASE_URL is placeholder. "
                        "Application will start but database operations will fail."
                    )
                    return None
                
                try:
                    _engine = create_engine(
                        DATABASE_URL,
                        # Pool configuration
                        pool_size=POOL_SIZE,
                        max_overflow=MAX_OVERFLOW,
                        pool_pre_ping=True,  # Validate connections before use (detects stale connections)
                        pool_recycle=POOL_RECYCLE,  # Recycle connections (default: 300s for serverless)
                        pool_timeout=POOL_TIMEOUT,  # Wait max 30s for connection from pool
                        
                        # Echo SQL for debugging (disabled in production)
                        echo=os.getenv("DB_ECHO", "false").lower() == "true",
                        
                        # psycopg2-specific connection arguments
                        # NOTE: SSL is configured via DATABASE_URL query string (?sslmode=require), NOT here
                        # For cloud deployments, always use ?sslmode=require to enforce encrypted connections
                        connect_args={
                            # Connection timeout (5s for Railway cold starts)
                            "connect_timeout": CONNECT_TIMEOUT,
                            
                            # PostgreSQL application name for pg_stat_activity
                            "application_name": "hiremebahamas",
                            
                            # PostgreSQL options for performance
                            # Note: statement_timeout expects milliseconds
                            "options": f"-c statement_timeout={STATEMENT_TIMEOUT_MS}ms",
                        }
                    )
                    logger.info("✅ Database engine initialized successfully (sync)")
                    logger.info(
                        f"Database engine created (lazy): pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
                        f"connect_timeout={CONNECT_TIMEOUT}s, pool_recycle={POOL_RECYCLE}s"
                    )
                except ArgumentError as e:
                    # Catch SQLAlchemy ArgumentError specifically (URL parsing errors)
                    logger.warning(
                        f"SQLAlchemy ArgumentError: Could not parse DATABASE_URL. "
                        f"The URL format is invalid or empty. "
                        f"Error: {str(e)}. "
                        f"Application will start but database operations will fail. "
                        f"Required format: postgresql://user:password@host:port/database?sslmode=require"
                    )
                    _engine = None
                    return None
                except Exception as e:
                    # Log warning instead of raising exception - allows app to start
                    logger.warning(
                        f"Failed to create database engine: {type(e).__name__}: {e}. "
                        f"Application will start but database operations will fail. "
                        f"Check your DATABASE_URL configuration."
                    )
                    _engine = None
                    return None
    
    return _engine

# For backward compatibility: create engine property that calls get_engine()
# This allows existing code like `from app.database import engine` to work
# but the actual engine is created lazily on first access
class LazyEngine:
    """Wrapper to provide lazy engine initialization while maintaining compatibility.
    
    This class defers all attribute access to the actual engine, which is created
    only when first accessed. This prevents connection issues in serverless environments
    where database connections at module import time can cause failures.
    
    CRITICAL BEHAVIOR: When engine creation fails, this class logs warnings and 
    returns None for most attributes. This allows the application to start even 
    when DATABASE_URL is invalid or missing, fulfilling the "apps must boot without 
    the database" requirement.
    """
    
    def __getattr__(self, name: str):
        """Delegate attribute access to the lazily-initialized engine.
        
        Args:
            name: The attribute name to access
            
        Returns:
            The attribute value from the actual engine, or None if engine creation fails
            
        Note:
            This method handles engine creation failures gracefully by logging
            warnings instead of raising exceptions. This allows health endpoints
            to work even when the database is not configured.
        """
        try:
            actual_engine = get_engine()
        except Exception as e:
            # Engine creation failed - log warning instead of raising exception
            # This allows the app to start for health checks and diagnostics
            logger.warning(
                f"LazyEngine: Failed to create database engine during access to '{name}'. "
                f"Check your DATABASE_URL and network connectivity. "
                f"Original error: {type(e).__name__}: {e}"
            )
            # Return None to allow caller to handle missing database gracefully
            return None
        
        if actual_engine is None:
            logger.warning(
                f"LazyEngine: Database engine is None during access to '{name}'. "
                "Database operations will fail."
            )
            return None
        
        try:
            return getattr(actual_engine, name)
        except AttributeError as e:
            # Attribute doesn't exist on the engine
            logger.warning(
                f"LazyEngine: Database engine has no attribute '{name}'. "
                f"Original error: {e}"
            )
            return None

engine = LazyEngine()

# Log database configuration (engine will be created on first use)
logger.info(
    f"Database configured (lazy init): pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
    f"connect_timeout={CONNECT_TIMEOUT}s, pool_recycle={POOL_RECYCLE}s"
)

# =============================================================================
# SESSION FACTORY - Optimized for sync operations
# =============================================================================
# Note: sessionmaker works safely with LazyEngine because:
# 1. sessionmaker() itself doesn't create any database connections
# 2. It only stores a reference to the engine (our LazyEngine wrapper)
# 3. Actual connections are created when sessions are instantiated (at runtime)
# 4. When a session needs the engine, LazyEngine.__getattr__ triggers lazy initialization
# This means the engine is still created lazily on first actual database operation
SessionLocal = sessionmaker(
    bind=engine, 
    class_=Session, 
    expire_on_commit=False,  # Don't expire objects after commit (reduces DB round-trips)
    autoflush=False,  # Manual flush for better performance control
)

# Backward compatibility alias
AsyncSessionLocal = SessionLocal

# Create declarative base for ORM models
Base = declarative_base()

# =============================================================================
# DATABASE INITIALIZATION STATE TRACKING
# =============================================================================
# Lazy initialization prevents startup failures when DB is temporarily unavailable
_db_initialized = False
_db_init_error: Optional[str] = None


def get_db():
    """Get database session with automatic cleanup.
    
    This is the primary dependency for FastAPI endpoints that need database access.
    
    Yields:
        Session: Database session for query execution
        
    Raises:
        RuntimeError: If database connection fails
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# Alternative session creation (alias for backward compatibility)
async_session = SessionLocal


def get_async_session():
    """Get database session (alias for get_db).
    
    Provided for API consistency - use get_db() as primary dependency.
    Note: Despite the name, this yields a sync session for backward compatibility.
    
    Yields:
        Session: Database session for query execution
    """
    yield from get_db()


# =============================================================================
# DATABASE INITIALIZATION WITH RETRY LOGIC
# =============================================================================

# Retry configuration constants
DB_INIT_MAX_RETRIES = int(os.getenv("DB_INIT_MAX_RETRIES", "3"))
DB_INIT_RETRY_DELAY = float(os.getenv("DB_INIT_RETRY_DELAY", "2.0"))

def init_db(max_retries: int = None, retry_delay: float = None) -> bool:
    """Initialize database tables with retry logic.
    
    This function is called during startup to ensure database tables exist.
    Uses retry logic to handle Railway cold starts and transient failures.
    
    CRITICAL BEHAVIOR: Returns False if database is not configured, allowing
    the application to start without a database connection. This fulfills
    the "apps must boot without the database" requirement.
    
    Args:
        max_retries: Maximum number of retry attempts (default from env: 3)
        retry_delay: Delay between retries in seconds (default from env: 2.0)
        
    Returns:
        bool: True if initialization succeeded, False otherwise
    """
    global _db_initialized, _db_init_error
    
    # Check if engine is available
    # Note: get_engine() is called to trigger lazy initialization if needed
    actual_engine = get_engine()
    if actual_engine is None:
        _db_init_error = "Database engine not available (DATABASE_URL not configured). Check DATABASE_URL configuration and network connectivity."
        logger.warning(
            "Database initialization skipped: DATABASE_URL not configured. "
            "Application will start but database operations will fail. "
            "Check DATABASE_URL configuration and network connectivity."
        )
        return False
    
    # Use defaults from environment if not specified
    if max_retries is None:
        max_retries = DB_INIT_MAX_RETRIES
    if retry_delay is None:
        retry_delay = DB_INIT_RETRY_DELAY
    
    # Import models for table registration
    try:
        # Try to import models from common locations
        try:
            from app import models  # noqa: F401
        except ImportError:
            try:
                from . import models  # noqa: F401
            except ImportError:
                logger.warning("Could not import models for table creation. Tables may need to be created manually.")
    except Exception as e:
        logger.warning(f"Error importing models: {e}")
    
    for attempt in range(max_retries):
        try:
            with engine.begin() as conn:
                Base.metadata.create_all(bind=conn)
            _db_initialized = True
            _db_init_error = None
            logger.info("Database tables initialized successfully")
            return True
        except Exception as e:
            _db_init_error = str(e)
            logger.warning(
                f"Database initialization attempt {attempt + 1}/{max_retries} failed: {e}"
            )
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
    
    logger.warning(f"Database initialization failed after {max_retries} attempts. Application will start anyway.")
    return False


def close_db():
    """Close database connections gracefully.
    
    Called during application shutdown to release all connections.
    Handles race conditions and already-closed connections defensively.
    """
    global _db_initialized, _engine
    try:
        if _engine is not None:
            # Check if engine was actually initialized (not just the wrapper)
            # The LazyEngine wrapper may exist without an actual engine
            actual_engine = get_engine()
            if actual_engine is not None:
                try:
                    actual_engine.dispose()
                except OSError as e:
                    # Handle "Bad file descriptor" errors (errno 9) gracefully
                    # This occurs when connections are already closed
                    if getattr(e, 'errno', None) == 9:
                        logger.debug("Database connections already closed (file descriptor error)")
                    else:
                        logger.warning(f"OSError while closing database connections: {e}")
                except Exception as e:
                    # Handle other disposal errors (e.g., network issues)
                    logger.warning(f"Error disposing database engine: {e}")
                else:
                    # Only log success if no exception occurred
                    logger.info("Database connections closed")
            else:
                logger.debug("Database engine was never initialized, nothing to close")
            _engine = None
        _db_initialized = False
    except Exception as e:
        logger.error(f"Unexpected error in close_db: {e}")


def test_db_connection() -> tuple[bool, Optional[str]]:
    """Test database connectivity.
    
    Used by /ready endpoint to verify database is accessible.
    
    CRITICAL BEHAVIOR: Returns (False, error_message) if database is not
    configured, allowing health checks to work without crashing the app.
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    # Check if engine is available
    # Note: get_engine() is called to trigger lazy initialization if needed
    actual_engine = get_engine()
    if actual_engine is None:
        error_msg = "Database engine not available (DATABASE_URL not configured). Check DATABASE_URL configuration and network connectivity."
        logger.warning(f"Database connection test skipped: {error_msg}")
        return False, error_msg
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        error_msg = str(e)
        # Truncate long error messages for logging
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        logger.warning(f"Database connection test failed: {error_msg}")
        return False, error_msg


def get_db_status() -> dict:
    """Get current database initialization status.
    
    Returns:
        Dictionary with status information for health checks
    """
    return {
        "initialized": _db_initialized,
        "error": _db_init_error,
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "connect_timeout": CONNECT_TIMEOUT,
        "pool_recycle": POOL_RECYCLE,
    }


def get_pool_status() -> dict:
    """Get connection pool status for monitoring.
    
    CRITICAL BEHAVIOR: Returns empty metrics if database is not configured,
    allowing health checks to work without crashing the app.
    
    Returns:
        Dictionary with pool metrics for health checks and debugging
    """
    # Check if engine is available
    # Note: get_engine() is called to trigger lazy initialization if needed
    actual_engine = get_engine()
    if actual_engine is None:
        return {
            "pool_size": 0,
            "checked_in": 0,
            "checked_out": 0,
            "overflow": 0,
            "invalid": 0,
            "max_overflow": MAX_OVERFLOW,
            "pool_recycle_seconds": POOL_RECYCLE,
            "connect_timeout_seconds": CONNECT_TIMEOUT,
            "status": "unavailable",
            "error": "Database engine not configured. Check DATABASE_URL configuration and network connectivity."
        }
    
    pool = engine.pool
    return {
        "pool_size": pool.size() if hasattr(pool, 'size') else POOL_SIZE,
        "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else 0,
        "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else 0,
        "overflow": pool.overflow() if hasattr(pool, 'overflow') else 0,
        "invalid": pool.invalidatedcount() if hasattr(pool, 'invalidatedcount') else 0,
        "max_overflow": MAX_OVERFLOW,
        "pool_recycle_seconds": POOL_RECYCLE,
        "connect_timeout_seconds": CONNECT_TIMEOUT,
        "status": "available"
    }


# =============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# =============================================================================
# These functions provide backward compatibility with older code that may
# use different function names or signatures.
# =============================================================================

def warmup_db(engine_param=None) -> bool:
    """Warm up database connection pool.
    
    Performs a simple connection test to ensure the database is accessible
    and warms up the connection pool.
    
    Args:
        engine_param: Database engine instance (optional, for backward compatibility)
        
    Returns:
        True if warmup succeeded, False otherwise
    """
    # Use the global engine if no engine parameter is provided
    actual_engine = engine_param if engine_param is not None else get_engine()
    
    if actual_engine is None:
        logger.warning("Cannot warm up database - engine is None")
        return False
        
    try:
        # Perform a simple query to test connectivity and warm up the pool
        with actual_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info("Database warmup: Connection pool ready")
        return True
        
    except Exception as e:
        logger.warning(f"Database warmup failed: {e}")
        return False


def test_connection():
    """Test database connectivity (legacy alias).
    
    Alias for test_db_connection() that returns a boolean instead of a tuple.
    Maintained for backward compatibility with legacy code.
    
    Returns:
        bool: True if connection succeeded, False otherwise
    """
    success, _ = test_db_connection()
    return success


def close_engine():
    """Close database engine (legacy alias).
    
    Alias for close_db() maintained for backward compatibility.
    """
    close_db()


# =============================================================================
# EXPORTS
# =============================================================================
# Export all public API for easy importing
# =============================================================================

__all__ = [
    # Core engine and configuration
    "engine",
    "get_engine",
    "Base",
    "DATABASE_URL",
    "DB_PLACEHOLDER_URL",
    
    # Session management (sync)
    "SessionLocal",
    "AsyncSessionLocal",  # Backward compatibility alias
    "get_db",
    "get_async_session",  # Backward compatibility alias
    "async_session",  # Backward compatibility alias
    
    # Lifecycle management (sync)
    "init_db",
    "close_db",
    "close_engine",  # Legacy alias
    
    # Health and monitoring (sync)
    "test_db_connection",
    "test_connection",  # Legacy alias
    "warmup_db",
    "get_db_status",
    "get_pool_status",
    
    # Configuration constants
    "POOL_SIZE",
    "MAX_OVERFLOW",
    "POOL_TIMEOUT",
    "POOL_RECYCLE",
    "CONNECT_TIMEOUT",
    "COMMAND_TIMEOUT",
    "STATEMENT_TIMEOUT_MS",
]
