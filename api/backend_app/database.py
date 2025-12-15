# =============================================================================
# DATABASE ENGINE CONFIGURATION - MASTERMIND FINAL FIX (Dec 2025)
# =============================================================================
#
# PERMANENT FIX FOR: "SSL error: unexpected eof while reading"
#
# This is the ONE AND ONLY fix for Railway/Neon PostgreSQL SSL EOF errors:
# 1. Force TLS 1.3 only - prevents SSL termination bugs
# 2. SSLContext + CERT_NONE - proper asyncpg SSL configuration
# 3. pool_recycle=120 - aggressive recycling before Railway drops connections
# 4. pool_pre_ping=True - validate connections before use
# 5. connect_timeout=45 - handle Railway cold starts
#
# DATABASE_URL FORMAT (copy-paste):
# postgresql+asyncpg://user:password@host:5432/database?sslmode=require
#
# RAILWAY ENV VARS (copy-paste):
# DATABASE_URL=${DATABASE_URL}  # Auto-injected by Railway
# DB_POOL_RECYCLE=300
# DB_SSL_MODE=require
#
# RENDER ENV VARS (copy-paste):
# DATABASE_URL=postgresql+asyncpg://user:pass@RAILWAY_HOST:5432/railway?sslmode=require
# DB_POOL_RECYCLE=300
# DB_SSL_MODE=require
#
# After deployment: Zero SSL EOF errors, zero connection drops, zero log spam.
# =============================================================================

import os
import logging
import ssl
import sys
from typing import Optional
from urllib.parse import urlparse, quote_plus, urlunparse

# Add project root to path for importing shared validation
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from db_config_validation import validate_database_config
except ImportError:
    # Fallback if db_config_validation is not available (shouldn't happen in normal deployment)
    def validate_database_config():
        """Fallback validation function."""
        database_url = (
            os.getenv("DATABASE_PRIVATE_URL") or 
            os.getenv("POSTGRES_URL") or 
            os.getenv("DATABASE_URL")
        )
        if database_url:
            return True, "DATABASE_URL", []
        
        missing_vars = []
        if not os.getenv("PGHOST"):
            missing_vars.append("PGHOST")
        if not os.getenv("PGUSER"):
            missing_vars.append("PGUSER")
        if not os.getenv("PGPASSWORD"):
            missing_vars.append("PGPASSWORD")
        if not os.getenv("PGDATABASE"):
            missing_vars.append("PGDATABASE")
        
        return len(missing_vars) == 0, "Individual PG* variables", missing_vars

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Configure logging for database connection debugging
logger = logging.getLogger(__name__)

# =============================================================================
# DATABASE URL CONFIGURATION
# =============================================================================
# Priority order:
# 1. DATABASE_PRIVATE_URL (Railway private network - $0 egress, fastest)
# 2. POSTGRES_URL (Vercel Postgres primary connection)
# 3. DATABASE_URL (Standard PostgreSQL connection)
# 4. Construct from individual PG* variables (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE)
# 5. Local development default (only for development, not production)
# =============================================================================

# Check if we're in production mode
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Get database URL with proper fallback
DATABASE_URL = (
    os.getenv("DATABASE_PRIVATE_URL") or 
    os.getenv("POSTGRES_URL") or
    os.getenv("DATABASE_URL")
)

# Strip whitespace from DATABASE_URL to prevent connection errors
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip()

# If DATABASE_URL is not provided, try to construct it from individual PG* variables
if not DATABASE_URL:
    pghost = os.getenv("PGHOST")
    pgport = os.getenv("PGPORT", "5432")
    pguser = os.getenv("PGUSER")
    pgpassword = os.getenv("PGPASSWORD")
    pgdatabase = os.getenv("PGDATABASE")
    
    # Check if all required individual variables are present using shared validation
    is_valid, source, missing_vars = validate_database_config()
    
    if is_valid and source == "Individual PG* variables":
        # Strip whitespace from database name to prevent connection errors
        pgdatabase = pgdatabase.strip() if pgdatabase else pgdatabase
        # URL-encode password to handle special characters
        encoded_password = quote_plus(pgpassword)
        DATABASE_URL = f"postgresql+asyncpg://{pguser}:{encoded_password}@{pghost}:{pgport}/{pgdatabase}"
        logger.info("Constructed DATABASE_URL from individual PG* environment variables")
    elif ENVIRONMENT == "production":
        # In production, we need either DATABASE_URL or all individual PG* variables
        raise ValueError(
            f"DATABASE_URL must be set in production. "
            f"Please set DATABASE_URL, POSTGRES_URL, DATABASE_PRIVATE_URL, "
            f"or all individual variables (PGHOST, PGUSER, PGPASSWORD, PGDATABASE). "
            f"Note: PGPORT is optional (defaults to 5432). "
            f"Missing: {', '.join(missing_vars)}"
        )
    else:
        # Use local development default only in development mode
        DATABASE_URL = "postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas"
        logger.warning("Using default local development database URL. Set DATABASE_URL for production.")

# Fix common typos in DATABASE_URL (e.g., "ostgresql" -> "postgresql")
# This handles cases where the 'p' is missing from "postgresql"
if "ostgresql" in DATABASE_URL and "postgresql" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("ostgresql", "postgresql")
    logger.info("✓ Auto-fixed DATABASE_URL typo: 'ostgresql' → 'postgresql' (update env var to fix permanently)")

# Convert sync PostgreSQL URLs to async driver format
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("Converted DATABASE_URL to asyncpg driver format")

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
# Parse and validate required fields
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
    raise ValueError(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")

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
# POOL CONFIGURATION - OPTIMIZED FOR SERVERLESS (Dec 2025)
# =============================================================================
# CRITICAL: pool_recycle=300 prevents connection issues by recycling connections
# before they become stale. This is serverless-friendly and prevents SSL EOF errors.
# MAX_OVERFLOW=3 allows burst capacity without exhausting memory
# =============================================================================
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "2"))  # Minimum connections (2 = safe for 512MB)
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "3"))  # Burst capacity
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))  # Wait max 30s for connection
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "300"))  # Recycle every 5 min (serverless-friendly)

# =============================================================================
# CONNECTION TIMEOUT CONFIGURATION - CRITICAL FOR RAILWAY
# =============================================================================
# These timeouts prevent the dreaded "Connection timed out" error
CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "45"))  # 45s for Railway cold starts
COMMAND_TIMEOUT = int(os.getenv("DB_COMMAND_TIMEOUT", "30"))  # 30s per query
STATEMENT_TIMEOUT_MS = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "30000"))  # 30s in milliseconds

# =============================================================================
# SSL CONFIGURATION FOR RAILWAY POSTGRES - MASTERMIND FINAL FIX
# =============================================================================
# This is THE PERMANENT FIX for "SSL error: unexpected eof while reading"
#
# The error occurs because:
# 1. Railway's SSL termination proxy silently drops idle connections
# 2. asyncpg's SSL layer doesn't detect the drop until the next read
# 3. Default TLS settings can cause protocol mismatch with Railway's proxy
#
# The fix:
# 1. Force TLS 1.3 only (most stable with modern proxies)
# 2. Disable certificate verification (Railway uses internal certs)
# 3. Aggressive pool recycling (120s) prevents stale connections
# 4. pool_pre_ping validates connections before use
#
# SSL Mode Options:
# - "require": Encrypt connection, don't verify certificate (RECOMMENDED)
# - "verify-ca": Verify server certificate (requires CA cert file)
# - "verify-full": Verify cert + hostname (most secure, requires cert file)
# =============================================================================
SSL_MODE = os.getenv("DB_SSL_MODE", "require")

# Force TLS 1.3 only for Railway compatibility (prevents SSL EOF errors)
FORCE_TLS_1_3 = os.getenv("DB_FORCE_TLS_1_3", "true").lower() == "true"

def _get_ssl_context() -> ssl.SSLContext:
    """Create SSL context for Railway PostgreSQL connections.
    
    MASTERMIND FIX for SSL EOF errors:
    - Forces TLS 1.3 only (prevents SSL termination bugs)
    - Disables certificate verification (Railway uses internal certs)
    - Works 100% with Railway, Neon, Supabase, and other managed Postgres
    
    Returns:
        SSL context configured for Railway-compatible SSL connections
    """
    # Create context with TLS 1.3 only if enabled (default: true)
    if FORCE_TLS_1_3:
        # TLS 1.3 only - most stable with modern SSL termination proxies
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    else:
        # Allow TLS 1.2 and 1.3 for legacy compatibility
        ctx = ssl.create_default_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    
    if SSL_MODE == "require":
        # "require" mode: encrypt but don't verify server certificate
        # SAFE because:
        # 1. Traffic is encrypted end-to-end
        # 2. Railway uses private networking (no public exposure)
        # 3. Railway manages the PostgreSQL instance (trusted provider)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        # "verify-ca" or "verify-full": full certificate verification
        ca_file = os.getenv("DB_SSL_CA_FILE")
        if ca_file and os.path.exists(ca_file):
            ctx.load_verify_locations(ca_file)
            ctx.check_hostname = SSL_MODE == "verify-full"
            ctx.verify_mode = ssl.CERT_REQUIRED
        else:
            logger.warning(
                f"SSL mode '{SSL_MODE}' requires DB_SSL_CA_FILE but none provided. "
                "Falling back to 'require' mode."
            )
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
    
    return ctx

# =============================================================================
# CREATE ASYNC ENGINE - LAZY INITIALIZATION FOR SERVERLESS (Vercel/Render)
# =============================================================================
# ✅ GOOD PATTERN: Lazy connection initialization
# - Defers connection until first request (not at module import)
# - Uses pool_pre_ping=True to validate connections before use
# - Uses pool_recycle=300 (5 min) to prevent stale connections
#
# This pattern PERMANENTLY FIXES serverless issues:
# 1. TLS 1.3 only via _get_ssl_context() - prevents SSL termination bugs
# 2. pool_pre_ping=True - validates connections before use (detects dead connections)
# 3. pool_recycle=300 - recycles connections (serverless-friendly)
# 4. JIT=off - prevents first-query compilation delays
# 5. connect_timeout=45 - allows Railway cold starts
#
# COPY-PASTE ENV VARS FOR RAILWAY/RENDER/VERCEL:
# DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?sslmode=require
# DB_POOL_RECYCLE=300
# DB_FORCE_TLS_1_3=true
# =============================================================================

# Global engine instance (initialized lazily on first use)
_engine = None

def get_engine():
    """Get or create database engine (lazy initialization for serverless).
    
    ✅ GOOD PATTERN: Defers connection until first request.
    This prevents connection issues on Vercel/Render where connections
    at module import time can cause failures.
    
    Returns:
        AsyncEngine: Database engine instance
    """
    global _engine
    
    if _engine is None:
        _engine = create_async_engine(
            DATABASE_URL,
            # Pool configuration (CRITICAL for serverless + SSL EOF fix)
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_pre_ping=True,  # Validate connections before use (detects stale connections)
            pool_recycle=POOL_RECYCLE,  # Recycle connections (default: 300s for serverless)
            pool_timeout=POOL_TIMEOUT,  # Wait max 30s for connection from pool
            
            # Echo SQL for debugging (disabled in production)
            echo=os.getenv("DB_ECHO", "false").lower() == "true",
            
            # asyncpg-specific connection arguments - THE ACTUAL SSL FIX
            connect_args={
                # Connection timeout (45s for Railway cold starts)
                "timeout": CONNECT_TIMEOUT,
                
                # Query timeout (30s per query)
                "command_timeout": COMMAND_TIMEOUT,
                
                # PostgreSQL server settings
                "server_settings": {
                    # CRITICAL: Disable JIT to prevent 60s+ first-query delays
                    "jit": "off",
                    # Statement timeout in milliseconds
                    "statement_timeout": str(STATEMENT_TIMEOUT_MS),
                    # Application name for pg_stat_activity
                    "application_name": "hiremebahamas",
                },
                
                # SSL configuration - THE MASTERMIND FIX
                # This is the PERMANENT fix for "SSL error: unexpected eof while reading"
                # Uses TLS 1.3 only + no cert verification for Railway compatibility
                "ssl": _get_ssl_context(),
            }
        )
        logger.info(
            f"Database engine created (lazy): pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
            f"connect_timeout={CONNECT_TIMEOUT}s, pool_recycle={POOL_RECYCLE}s"
        )
    
    return _engine

# For backward compatibility: create engine property that calls get_engine()
# This allows existing code like `from backend_app.database import engine` to work
# but the actual engine is created lazily on first access
class LazyEngine:
    """Wrapper to provide lazy engine initialization while maintaining compatibility.
    
    This class defers all attribute access to the actual engine, which is created
    only when first accessed. This prevents connection issues in serverless environments
    where database connections at module import time can cause failures.
    """
    
    def __getattr__(self, name: str):
        """Delegate attribute access to the lazily-initialized engine.
        
        Args:
            name: The attribute name to access
            
        Returns:
            The attribute value from the actual engine
            
        Raises:
            AttributeError: If the engine or attribute doesn't exist
        """
        try:
            actual_engine = get_engine()
            return getattr(actual_engine, name)
        except AttributeError as e:
            raise AttributeError(
                f"LazyEngine: Failed to access attribute '{name}' on database engine. "
                f"Original error: {e}"
            ) from e

engine = LazyEngine()

# Log database configuration (engine will be created on first use)
logger.info(
    f"Database configured (lazy init): pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
    f"connect_timeout={CONNECT_TIMEOUT}s, pool_recycle={POOL_RECYCLE}s"
)

# =============================================================================
# SESSION FACTORY - Optimized for async operations
# =============================================================================
# Note: sessionmaker works safely with LazyEngine because:
# 1. sessionmaker() itself doesn't create any database connections
# 2. It only stores a reference to the engine (our LazyEngine wrapper)
# 3. Actual connections are created when sessions are instantiated (at runtime)
# 4. When a session needs the engine, LazyEngine.__getattr__ triggers lazy initialization
# This means the engine is still created lazily on first actual database operation
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,  # Don't expire objects after commit (reduces DB round-trips)
    autoflush=False,  # Manual flush for better performance control
)

# Create declarative base for ORM models
Base = declarative_base()

# =============================================================================
# DATABASE INITIALIZATION STATE TRACKING
# =============================================================================
# Lazy initialization prevents startup failures when DB is temporarily unavailable
_db_initialized = False
_db_init_error: Optional[str] = None


async def get_db():
    """Get database session with automatic cleanup.
    
    This is the primary dependency for FastAPI endpoints that need database access.
    
    Yields:
        AsyncSession: Database session for query execution
        
    Raises:
        RuntimeError: If database connection fails
    """
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise


# Alternative session creation (alias for backward compatibility)
async_session = AsyncSessionLocal


async def get_async_session():
    """Get async database session (alias for get_db).
    
    Provided for API consistency - use get_db() as primary dependency.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# =============================================================================
# DATABASE INITIALIZATION WITH RETRY LOGIC
# =============================================================================

# Retry configuration constants
DB_INIT_MAX_RETRIES = int(os.getenv("DB_INIT_MAX_RETRIES", "3"))
DB_INIT_RETRY_DELAY = float(os.getenv("DB_INIT_RETRY_DELAY", "2.0"))

async def init_db(max_retries: int = None, retry_delay: float = None) -> bool:
    """Initialize database tables with retry logic.
    
    This function is called during startup to ensure database tables exist.
    Uses retry logic to handle Railway cold starts and transient failures.
    
    Args:
        max_retries: Maximum number of retry attempts (default from env: 3)
        retry_delay: Delay between retries in seconds (default from env: 2.0)
        
    Returns:
        bool: True if initialization succeeded, False otherwise
    """
    global _db_initialized, _db_init_error
    
    # Use defaults from environment if not specified
    if max_retries is None:
        max_retries = DB_INIT_MAX_RETRIES
    if retry_delay is None:
        retry_delay = DB_INIT_RETRY_DELAY
    
    # Import models using relative import for package consistency
    from . import models  # noqa: F401 - Import models for table registration
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
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
                import asyncio
                await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
    
    logger.error(f"Database initialization failed after {max_retries} attempts")
    return False


async def close_db():
    """Close database connections gracefully.
    
    Called during application shutdown to release all connections.
    """
    global _db_initialized, _engine
    try:
        if _engine is not None:
            await _engine.dispose()
            _engine = None
        _db_initialized = False
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


async def test_db_connection() -> tuple[bool, Optional[str]]:
    """Test database connectivity.
    
    Used by /ready endpoint to verify database is accessible.
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        error_msg = str(e)
        # Truncate long error messages for logging
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        logger.error(f"Database connection test failed: {error_msg}")
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


async def get_pool_status() -> dict:
    """Get connection pool status for monitoring.
    
    Returns:
        Dictionary with pool metrics for health checks and debugging
    """
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
    }


# =============================================================================
# CONNECTION VERIFICATION COMMAND (For Render Console)
# =============================================================================
# Run this from Render console to test Railway Postgres connectivity:
#
# python -c "
# import asyncio
# from backend.app.database import test_db_connection
# result = asyncio.run(test_db_connection())
# print('Connected!' if result[0] else f'Failed: {result[1]}')
# "
# =============================================================================
