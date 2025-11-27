import atexit
import os
import random
import signal
import sqlite3
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from urllib.parse import urlparse, parse_qs

import bcrypt
import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, g
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from .env file
load_dotenv()

print("Initializing Flask app with PostgreSQL support...")
app = Flask(__name__)

# Production configuration
app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY", "your-secret-key-here-change-in-production"
)
app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max file size

# JWT token expiration configuration (in days)
# Set to 365 days (1 year) to prevent frequent re-login
# Users stay logged in for a full year unless they manually log out
TOKEN_EXPIRATION_DAYS = int(os.getenv("TOKEN_EXPIRATION_DAYS", "365"))

# Rate limiting configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# Caching configuration
cache = Cache(
    app,
    config={
        "CACHE_TYPE": "simple",
        "CACHE_DEFAULT_TIMEOUT": 300,
    },
)

# Enhanced CORS configuration
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=False,
    max_age=3600,
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-Retry-Count",
    ],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

# File upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
STORIES_FOLDER = os.path.join(UPLOAD_FOLDER, "stories")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["STORIES_FOLDER"] = STORIES_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webm"}

# Ensure upload directories exist
os.makedirs(STORIES_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Serve uploaded files with caching
@app.route("/uploads/<path:filename>")
@cache.cached(timeout=3600)
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ==========================================
# REQUEST LOGGING MIDDLEWARE
# ==========================================

# Logging configuration constants
AUTH_ENDPOINTS_PREFIX = '/api/auth/'
SLOW_REQUEST_THRESHOLD_MS = 3000  # 3 seconds
VERY_SLOW_REQUEST_THRESHOLD_MS = 10000  # 10 seconds


@app.before_request
def log_request_start():
    """
    Log incoming requests and track timing information.
    
    This middleware captures detailed information about each request to help diagnose
    performance issues like HTTP 499 (Client Closed Request) errors that occur when
    requests take too long to complete.
    
    Captures:
    - Request ID for tracking through logs
    - Start time for duration calculation
    - Client IP and User-Agent for debugging
    """
    # Generate unique request ID
    g.request_id = str(uuid.uuid4())[:8]
    g.start_time = time.time()
    
    # Get client information
    client_ip = request.remote_addr or 'unknown'
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    # Log incoming request with context (truncate long user agents)
    user_agent_display = user_agent if len(user_agent) <= 100 else f"{user_agent[:100]}..."
    print(
        f"[{g.request_id}] --> {request.method} {request.path} "
        f"clientIP=\"{client_ip}\" userAgent=\"{user_agent_display}\""
    )


@app.after_request
def log_request_end(response):
    """
    Log completed requests with timing and status information.
    
    This middleware logs response status and duration to help identify slow requests
    that may cause timeout issues. For authentication endpoints, it provides additional
    context to help diagnose login failures.
    
    Logs:
    - Response status code
    - Request duration in milliseconds
    - Warnings for slow requests (> 3 seconds)
    - Critical warnings for very slow requests (> 10 seconds)
    - Error details for authentication failures
    """
    if not hasattr(g, 'request_id') or not hasattr(g, 'start_time'):
        # Request logging was bypassed (e.g., for static files or middleware chain broken)
        # Log a warning to help identify when middleware chain is interrupted
        if request.path and not request.path.startswith('/static/'):
            print(f"⚠️ Warning: Request logging bypassed for {request.method} {request.path}")
        return response
    
    duration_ms = int((time.time() - g.start_time) * 1000)
    client_ip = request.remote_addr or 'unknown'
    
    # Determine log level based on status code
    if response.status_code < 400:
        # Success - log at INFO level
        print(
            f"[{g.request_id}] <-- {response.status_code} {request.method} {request.path} "
            f"responseTimeMS={duration_ms} responseBytes={response.content_length or 0} "
            f"clientIP=\"{client_ip}\""
        )
    else:
        # Client/Server error - log with more detail
        error_detail = ""
        
        # For authentication endpoints, try to extract error message
        if request.path.startswith(AUTH_ENDPOINTS_PREFIX):
            try:
                # Try to get error detail from response JSON (parse once)
                if response.is_json:
                    error_data = response.get_json(silent=True)
                    if isinstance(error_data, dict) and 'message' in error_data:
                        error_detail = f" errorDetail=\"{error_data['message']}\""
            except Exception:
                pass
        
        print(
            f"[{g.request_id}] <-- {response.status_code} {request.method} {request.path} "
            f"responseTimeMS={duration_ms} clientIP=\"{client_ip}\"{error_detail}"
        )
    
    # Warn about slow requests with appropriate severity level
    is_slow = duration_ms > SLOW_REQUEST_THRESHOLD_MS
    is_very_slow = duration_ms > VERY_SLOW_REQUEST_THRESHOLD_MS
    
    if is_slow:
        severity = "VERY SLOW REQUEST" if is_very_slow else "SLOW REQUEST"
        threshold_note = f">{SLOW_REQUEST_THRESHOLD_MS}ms threshold"
        
        print(
            f"[{g.request_id}] ⚠️ {severity}: {request.method} {request.path} "
            f"took {duration_ms}ms ({threshold_note}). "
            f"This may cause HTTP 499 (Client Closed Request) errors. "
            f"Check database connection pool, bcrypt rounds, and query performance."
        )
    
    return response


# ==========================================
# DATABASE CONNECTION MANAGEMENT
# ==========================================

# Check if running on Railway with PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
USE_POSTGRESQL = DATABASE_URL is not None

# PostgreSQL extensions to initialize during database setup
# Pre-defined SQL statements prevent SQL injection by avoiding string formatting
# Each extension requires server-side configuration (shared_preload_libraries)
POSTGRESQL_EXTENSIONS = {
    "pg_stat_statements": {
        "sql": "CREATE EXTENSION IF NOT EXISTS pg_stat_statements",
        "description": "Query performance statistics tracking",
    },
}

# Check if this is a production environment
# Detect Railway environment using Railway-specific variables:
# - RAILWAY_ENVIRONMENT: Set by Railway to indicate the environment (e.g., "production")
# - RAILWAY_PROJECT_ID: Always present in Railway deployments, used as fallback detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
RAILWAY_ENVIRONMENT = os.getenv("RAILWAY_ENVIRONMENT", "").lower()
IS_RAILWAY = os.getenv("RAILWAY_PROJECT_ID") is not None

# Production is determined by:
# 1. Explicit ENVIRONMENT=production setting, OR
# 2. Running on Railway (Railway is inherently a production platform)
# Railway deployments automatically enable production mode to ensure:
# - Database keepalive is active (prevents Railway PostgreSQL from sleeping)
# - Production-level logging and error handling
# - Proper data persistence with PostgreSQL
IS_PRODUCTION = (
    ENVIRONMENT in ["production", "prod"] or 
    IS_RAILWAY  # Railway deployments are always considered production
)

# Track if database configuration is valid for production
# Don't crash at startup - allow health check to report issues
DATABASE_CONFIG_WARNING = None

# For production, PostgreSQL is REQUIRED - but don't crash, just warn
if IS_PRODUCTION and not USE_POSTGRESQL:
    DATABASE_CONFIG_WARNING = (
        "DATABASE_URL must be set in production. "
        "PostgreSQL is required for data persistence."
    )
    print("⚠️" * 50)
    print("⚠️  WARNING: Production environment REQUIRES PostgreSQL!")
    print("⚠️  DATABASE_URL environment variable is not set.")
    print("⚠️")
    print("⚠️  SQLite is NOT suitable for production use because:")
    print("⚠️  - No data persistence in containerized environments (Railway, Docker)")
    print("⚠️  - Users and data will be lost on every deployment/restart")
    print("⚠️  - No concurrent access support at scale")
    print("⚠️")
    print("⚠️  Please set DATABASE_URL to a PostgreSQL connection string:")
    print("⚠️  DATABASE_URL=postgresql://username:password@hostname:5432/database")
    print("⚠️" * 50)
    # Don't raise an exception - allow the app to start so health check can report the issue
    # This prevents Gunicorn worker boot failures while still warning about the misconfiguration

print(
    f"🗄️ Database Mode: {'PostgreSQL (Production)' if USE_POSTGRESQL else 'SQLite (Development Only)'}"
)
if IS_PRODUCTION:
    print(f"🌍 Environment: PRODUCTION")
else:
    print(f"💻 Environment: Development")

if not USE_POSTGRESQL:
    print("⚠️  Note: Using SQLite for local development only.")
    print("⚠️  Set DATABASE_URL to use PostgreSQL.")

# Track database initialization status
_db_initialized = False
_db_init_lock = threading.Lock()

# Error message length limit for health checks
MAX_ERROR_MESSAGE_LENGTH = 500

if USE_POSTGRESQL:
    print(f"✅ PostgreSQL URL detected: {DATABASE_URL[:30]}...")

    # Expected DATABASE_URL format message
    DATABASE_URL_FORMAT = "postgresql://username:password@hostname:5432/database"

    # Parse DATABASE_URL with defensive error handling
    parsed = urlparse(DATABASE_URL)

    # Safely parse port with error handling
    try:
        port = int(parsed.port) if parsed.port else 5432
    except (ValueError, TypeError):
        port = 5432
        print(f"⚠️  Invalid port '{parsed.port}' in DATABASE_URL, using default 5432")

    # Safely parse database name (remove leading '/' from path)
    try:
        database = parsed.path[1:] if parsed.path and len(parsed.path) > 1 else None
        if not database:
            raise ValueError("Database name is missing from DATABASE_URL")
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        print(f"DATABASE_URL format should be: {DATABASE_URL_FORMAT}")
        raise

    # Parse query string for SSL mode and other options
    query_params = parse_qs(parsed.query)
    # Get sslmode from URL if present, otherwise default to "require"
    # Handles empty values like ?sslmode= by checking if the list is non-empty
    sslmode_list = query_params.get("sslmode", [])
    sslmode = sslmode_list[0] if sslmode_list and sslmode_list[0] else "require"
    
    # Application name for PostgreSQL connection identification
    # This appears in PostgreSQL logs as 'app=...' instead of 'app=[unknown]'
    # Helps identify the application source in database logs and pg_stat_activity
    APPLICATION_NAME = os.getenv("APPLICATION_NAME", "hiremebahamas-backend")

    DB_CONFIG = {
        "host": parsed.hostname,
        "port": port,
        "database": database,
        "user": parsed.username,
        "password": parsed.password,
        "sslmode": sslmode,
        "application_name": APPLICATION_NAME,
    }

    # Validate all required fields are present
    required_fields = ["host", "database", "user", "password"]
    missing_fields = [field for field in required_fields if not DB_CONFIG.get(field)]
    if missing_fields:
        print(
            f"❌ Missing required DATABASE_URL components: {', '.join(missing_fields)}"
        )
        print(f"DATABASE_URL format should be: {DATABASE_URL_FORMAT}")
        raise ValueError(f"Invalid DATABASE_URL: missing {', '.join(missing_fields)}")

    print(
        f"✅ Database config parsed: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']} "
        f"(sslmode={sslmode}, app={DB_CONFIG['application_name']})"
    )
else:
    # SQLite for local development
    DB_PATH = Path(__file__).parent / "hiremebahamas.db"
    print(f"📁 SQLite database path: {DB_PATH}")

# Connection pool for PostgreSQL
# This reduces connection overhead and improves performance for concurrent requests
_connection_pool = None
_pool_lock = threading.Lock()

# Connection pool timeout in seconds
# This prevents requests from blocking indefinitely waiting for a connection
# If no connection is available within this time, fall back to direct connection
# Reduced from 10s to 5s to fail faster and prevent HTTP 499 timeouts
POOL_TIMEOUT_SECONDS = 5


def _get_env_int(env_var: str, default: int, min_val: int, max_val: int) -> int:
    """
    Get an integer value from environment variable with validation.
    
    Args:
        env_var: Name of the environment variable
        default: Default value if env var is not set or invalid
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
    
    Returns:
        Validated integer value, or default if validation fails
    """
    raw_value = os.getenv(env_var, str(default))
    try:
        value = int(raw_value)
        if value < min_val or value > max_val:
            print(f"⚠️ {env_var}={value} out of bounds [{min_val}, {max_val}], using default {default}")
            return default
        return value
    except (ValueError, TypeError):
        print(f"⚠️ Invalid {env_var}='{raw_value}', using default {default}")
        return default


# Statement timeout in milliseconds for PostgreSQL queries
# This prevents long-running queries from blocking connections
# Set to 30 seconds to allow complex queries but prevent indefinite blocking
# Configurable via environment variable for different deployment environments
# PostgreSQL interprets integer values as milliseconds
STATEMENT_TIMEOUT_MS = _get_env_int("STATEMENT_TIMEOUT_MS", 30000, 1000, 300000)

# Maximum connection pool size
# Configurable via environment variable for different deployment environments
DB_POOL_MAX_CONNECTIONS = _get_env_int("DB_POOL_MAX_CONNECTIONS", 20, 5, 100)

# Connection retry configuration for database recovery scenarios
# When PostgreSQL is recovering from improper shutdown, connections may fail temporarily
# These settings allow the application to retry connections with exponential backoff
DB_CONNECT_MAX_RETRIES = _get_env_int("DB_CONNECT_MAX_RETRIES", 3, 1, 10)
DB_CONNECT_BASE_DELAY_MS = _get_env_int("DB_CONNECT_BASE_DELAY_MS", 100, 50, 2000)
DB_CONNECT_MAX_DELAY_MS = _get_env_int("DB_CONNECT_MAX_DELAY_MS", 2000, 500, 10000)

# Jitter factor for retry delay - adds randomness to prevent thundering herd
# The actual jitter added is between 0 and (JITTER_FACTOR * delay_ms)
DB_CONNECT_JITTER_FACTOR = 0.2

# TCP Keepalive configuration for PostgreSQL connections
# These settings prevent "SSL error: unexpected eof while reading" errors that occur
# when idle TCP connections are silently dropped by network intermediaries (load balancers,
# firewalls, NAT devices) without properly closing the SSL connection.
#
# How it works:
# - TCP keepalive sends periodic probe packets on idle connections
# - If the connection is still alive, the remote end responds
# - If no response after keepalives_count probes, the connection is marked dead
# - This allows the application to detect and recover from stale connections
#
# Recommended values for cloud environments like Railway:
# - keepalives_idle: 60s (start probing after 60 seconds of idle)
# - keepalives_interval: 30s (probe every 30 seconds)
# - keepalives_count: 3 (mark dead after 3 failed probes)
#
# Total detection time = idle + (interval * count) = 60 + (30 * 3) = 150 seconds
# This is well under typical cloud load balancer idle timeouts (5-10 minutes)
TCP_KEEPALIVE_ENABLED = _get_env_int("TCP_KEEPALIVE_ENABLED", 1, 0, 1)
TCP_KEEPALIVE_IDLE = _get_env_int("TCP_KEEPALIVE_IDLE", 60, 10, 300)
TCP_KEEPALIVE_INTERVAL = _get_env_int("TCP_KEEPALIVE_INTERVAL", 30, 5, 60)
TCP_KEEPALIVE_COUNT = _get_env_int("TCP_KEEPALIVE_COUNT", 3, 1, 10)

# Login request timeout in seconds
# This prevents login requests from blocking indefinitely
# If a login request takes longer than this, it returns a timeout error
# This helps prevent HTTP 499 errors by returning a proper response before
# the client or load balancer times out
# Set to 25 seconds (below typical client/proxy timeouts of 30s)
LOGIN_REQUEST_TIMEOUT_SECONDS = _get_env_int("LOGIN_REQUEST_TIMEOUT_SECONDS", 25, 5, 60)


def _check_request_timeout(start_time: float, timeout_seconds: int, operation: str) -> bool:
    """
    Check if a request has exceeded its timeout.
    
    This function is used to implement early timeout detection in long-running
    operations like login. By checking elapsed time at key points, we can
    return a proper timeout response before the client disconnects.
    
    Args:
        start_time: The timestamp when the request started (from time.time())
        timeout_seconds: Maximum allowed time for the request (in seconds)
        operation: Name of the operation being checked (for logging)
        
    Returns:
        True if the request has timed out, False otherwise
    """
    elapsed = time.time() - start_time
    if elapsed >= timeout_seconds:
        request_id = getattr(g, 'request_id', 'unknown')
        print(
            f"[{request_id}] ⚠️ REQUEST TIMEOUT: {operation} took {elapsed:.2f}s "
            f"(timeout: {timeout_seconds}s). Returning timeout response to prevent HTTP 499."
        )
        return True
    return False


def _is_transient_connection_error(error: Exception) -> bool:
    """
    Check if a database connection error is transient and may succeed on retry.
    
    Transient errors occur during:
    - Database recovery after improper shutdown
    - Temporary network issues
    - Connection pool exhaustion
    - Database restarts or failovers
    
    Args:
        error: The exception that occurred during connection attempt
        
    Returns:
        True if the error is likely transient and worth retrying
    """
    if not isinstance(error, psycopg2.Error):
        return False
    
    error_msg = str(error).lower()
    
    # Transient error patterns
    transient_patterns = [
        "connection refused",           # Database not yet accepting connections
        "could not connect",             # General connection failure
        "server closed the connection",  # Server restart/recovery
        "connection reset",              # Network interruption
        "timeout expired",               # Connection timeout
        "the database system is starting up",  # Explicit startup message
        "the database system is in recovery",  # Database recovery mode
        "too many connections",          # Temporary pool exhaustion
        "connection is closed",          # Stale connection
        "terminating connection",        # Server-initiated disconnect
        "unexpected eof",                # SSL EOF error from dropped connection
        "ssl connection has been closed unexpectedly",  # Specific SSL closure error
    ]
    
    return any(pattern in error_msg for pattern in transient_patterns)


def _get_connection_pool():
    """
    Get or create the PostgreSQL connection pool.
    Uses ThreadedConnectionPool for thread-safe connection management.
    Pool is created lazily on first request.
    
    Pool configuration optimized for preventing HTTP 499 timeouts:
    - maxconn configurable via DB_POOL_MAX_CONNECTIONS env var (default 20)
    - Reduced connect_timeout to 10s for faster failure detection
    - Added options for statement timeout on all connections
    - TCP keepalive to prevent SSL EOF errors from stale connections
    """
    global _connection_pool
    
    if not USE_POSTGRESQL:
        return None
    
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                try:
                    # Create a threaded connection pool
                    # minconn=2: Start with 2 connections for faster initial requests
                    # maxconn: Configurable via DB_POOL_MAX_CONNECTIONS env var
                    # This helps prevent pool exhaustion during traffic spikes
                    #
                    # TCP keepalive parameters prevent "SSL error: unexpected eof while reading"
                    # by detecting and handling stale connections before they cause SSL errors
                    _connection_pool = pool.ThreadedConnectionPool(
                        minconn=2,
                        maxconn=DB_POOL_MAX_CONNECTIONS,
                        host=DB_CONFIG["host"],
                        port=DB_CONFIG["port"],
                        database=DB_CONFIG["database"],
                        user=DB_CONFIG["user"],
                        password=DB_CONFIG["password"],
                        sslmode=DB_CONFIG["sslmode"],
                        application_name=DB_CONFIG["application_name"],
                        cursor_factory=RealDictCursor,
                        connect_timeout=10,  # Reduced from 15s for faster failure detection
                        # TCP keepalive settings to prevent SSL EOF errors on idle connections
                        # psycopg2 expects integer (1=enabled, 0=disabled)
                        keepalives=1 if TCP_KEEPALIVE_ENABLED else 0,
                        keepalives_idle=TCP_KEEPALIVE_IDLE,
                        keepalives_interval=TCP_KEEPALIVE_INTERVAL,
                        keepalives_count=TCP_KEEPALIVE_COUNT,
                        # Set statement_timeout on connection to prevent long-running queries
                        options=f"-c statement_timeout={STATEMENT_TIMEOUT_MS}",
                    )
                    keepalive_status = "enabled" if TCP_KEEPALIVE_ENABLED == 1 else "disabled"
                    print(f"✅ PostgreSQL connection pool created (min=2, max={DB_POOL_MAX_CONNECTIONS}, tcp_keepalive={keepalive_status})")
                except Exception as e:
                    print(f"⚠️ Failed to create connection pool: {e}")
                    # Pool creation failed, will fall back to direct connections
                    return None
    
    return _connection_pool


# Thread pool executor for connection timeout handling
# Increased from 2 to 4 workers to handle more concurrent timeout checks
# This prevents blocking when many requests are waiting for connections
_timeout_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="db-conn-timeout")


def _shutdown_executor():
    """
    Shutdown the connection timeout executor during application exit.
    
    Called via atexit to ensure proper cleanup of executor threads.
    Uses wait=False to avoid blocking on pending tasks during shutdown.
    """
    try:
        # cancel_futures parameter requires Python 3.9+
        # For Python < 3.9, just use wait=False
        import sys
        if sys.version_info >= (3, 9):
            _timeout_executor.shutdown(wait=False, cancel_futures=True)
        else:
            _timeout_executor.shutdown(wait=False)
    except Exception:
        pass  # Ignore errors during shutdown


# Register executor shutdown on application exit
atexit.register(_shutdown_executor)


def _shutdown_connection_pool():
    """
    Shutdown the PostgreSQL connection pool during application exit.
    
    This ensures all connections are properly closed before the application exits,
    preventing PostgreSQL from reporting "database system was not properly shut down"
    and requiring automatic recovery on next startup.
    
    Called via atexit and signal handlers to ensure cleanup happens for:
    - Normal application termination (atexit)
    - SIGTERM from container orchestrators (Railway, Docker)
    - SIGINT from Ctrl+C during development
    """
    global _connection_pool
    
    try:
        with _pool_lock:
            if _connection_pool is not None:
                print("🔌 Closing PostgreSQL connection pool...")
                _connection_pool.closeall()
                _connection_pool = None
                print("✅ PostgreSQL connection pool closed successfully")
    except Exception as e:
        print(f"⚠️ Error closing connection pool: {e}")


# Register connection pool shutdown on application exit
atexit.register(_shutdown_connection_pool)


def _signal_handler(signum, frame):
    """
    Handle termination signals to ensure graceful shutdown.
    
    This handler is called when the application receives SIGTERM or SIGINT.
    It performs cleanup and then exits the application.
    
    Args:
        signum: Signal number (e.g., signal.SIGTERM)
        frame: Current stack frame (not used)
    """
    # Get signal name with fallback for compatibility
    try:
        signal_name = signal.Signals(signum).name
    except (ValueError, AttributeError):
        # Fallback for unsupported signals or older Python versions
        signal_names = {signal.SIGTERM: "SIGTERM", signal.SIGINT: "SIGINT"}
        signal_name = signal_names.get(signum, f"Signal {signum}")
    
    print(f"\n🛑 Received {signal_name}, shutting down gracefully...")
    
    # Cleanup will happen via atexit handlers
    # Exit with status 0 for graceful shutdown
    sys.exit(0)


# Register signal handlers for graceful shutdown
# SIGTERM: Sent by container orchestrators (Railway, Docker) to stop the container
# SIGINT: Sent by Ctrl+C during development
signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def _return_orphaned_connection(future, conn_pool):
    """
    Callback to return an orphaned connection to the pool.
    
    Called when a getconn() future completes after the timeout has expired.
    This prevents connection leaks when pool exhaustion causes timeouts.
    """
    try:
        # Check if the future completed successfully (not cancelled and no exception)
        if not future.cancelled() and future.exception() is None:
            # The future is already done, so result() will return immediately
            # Using no timeout since we've verified the future is complete
            conn = future.result()
            if conn:
                try:
                    conn_pool.putconn(conn)
                except Exception:
                    # If putconn fails, close the connection directly
                    try:
                        conn.close()
                    except Exception:
                        pass
    except Exception:
        # Ignore any errors during cleanup
        pass


def _get_pooled_connection_with_timeout(conn_pool, timeout_seconds):
    """
    Attempt to get a connection from the pool with a timeout.
    
    The psycopg2 ThreadedConnectionPool.getconn() blocks indefinitely
    when the pool is exhausted. This wrapper adds a timeout to prevent
    requests from hanging for minutes when under heavy load.
    
    Uses ThreadPoolExecutor for proper thread management and cleanup.
    If timeout occurs, registers a callback to return any orphaned
    connection to the pool when getconn() eventually completes.
    
    Args:
        conn_pool: The ThreadedConnectionPool instance
        timeout_seconds: Maximum seconds to wait for a connection
        
    Returns:
        A database connection, or None if timeout is reached
        
    Raises:
        Exception: Re-raises any exception from getconn() except timeout
    """
    # Submit the getconn call to the executor with timeout
    future = _timeout_executor.submit(conn_pool.getconn)
    
    try:
        conn = future.result(timeout=timeout_seconds)
        return conn
    except FuturesTimeoutError:
        # Timeout waiting for connection - pool is exhausted
        print(f"⚠️ Connection pool exhausted, waited {timeout_seconds}s")
        
        # Register callback to return the connection to pool when it becomes available
        # This prevents connection leaks when getconn() eventually completes
        future.add_done_callback(
            lambda f: _return_orphaned_connection(f, conn_pool)
        )
        return None
    except Exception as e:
        # Re-raise any other exceptions (e.g., pool errors)
        raise


def _create_direct_postgresql_connection(sslmode: str = None):
    """
    Create a direct PostgreSQL connection with the specified SSL mode.
    
    Includes TCP keepalive settings to prevent "SSL error: unexpected eof while reading"
    errors that occur when idle connections are silently dropped by network intermediaries.
    
    Args:
        sslmode: SSL mode to use. If None, uses the configured default.
        
    Returns:
        A psycopg2 connection object
        
    Raises:
        psycopg2.Error: If connection fails
    """
    return psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        sslmode=sslmode or DB_CONFIG["sslmode"],
        application_name=DB_CONFIG["application_name"],
        cursor_factory=RealDictCursor,
        connect_timeout=10,
        # TCP keepalive settings to prevent SSL EOF errors on idle connections
        # psycopg2 expects integer (1=enabled, 0=disabled)
        keepalives=1 if TCP_KEEPALIVE_ENABLED else 0,
        keepalives_idle=TCP_KEEPALIVE_IDLE,
        keepalives_interval=TCP_KEEPALIVE_INTERVAL,
        keepalives_count=TCP_KEEPALIVE_COUNT,
        options=f"-c statement_timeout={STATEMENT_TIMEOUT_MS}",
    )


def get_db_connection():
    """Get database connection (PostgreSQL on Railway, SQLite locally)
    
    For PostgreSQL, uses connection pool for better performance.
    Falls back to direct connection if pool is unavailable or exhausted.
    
    Includes:
    - Timeout handling to prevent indefinite blocking when pool is exhausted
    - Exponential backoff retry for transient connection errors during database recovery
    - SSL fallback for certificate-related connection issues
    
    The retry mechanism handles scenarios where PostgreSQL is recovering from
    an improper shutdown and temporarily refuses connections.
    """
    if USE_POSTGRESQL:
        # Try to get connection from pool first with timeout
        conn_pool = _get_connection_pool()
        if conn_pool:
            try:
                conn = _get_pooled_connection_with_timeout(
                    conn_pool, POOL_TIMEOUT_SECONDS
                )
                if conn:
                    return conn
                # If timeout occurred, fall through to direct connection
                print("⚠️ Pool timeout, creating direct connection")
            except psycopg2.pool.PoolError as e:
                print(f"⚠️ Pool error: {e}, falling back to direct connection")
            except Exception as e:
                print(f"⚠️ Pool connection failed, falling back to direct: {e}")
        
        # Fallback to direct connection with retry logic for transient errors
        # This handles database recovery scenarios after improper shutdown
        last_error = None
        delay_ms = DB_CONNECT_BASE_DELAY_MS
        
        for attempt in range(DB_CONNECT_MAX_RETRIES):
            try:
                conn = _create_direct_postgresql_connection()
                if attempt > 0:
                    print(f"✅ Connection succeeded on attempt {attempt + 1}")
                return conn
            except psycopg2.OperationalError as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Handle SSL-related errors by trying with sslmode=prefer
                if "ssl" in error_msg or "certificate" in error_msg:
                    print(f"⚠️ SSL connection failed, attempting with sslmode=prefer...")
                    try:
                        conn = _create_direct_postgresql_connection(sslmode="prefer")
                        return conn
                    except Exception as fallback_error:
                        print(f"❌ SSL fallback connection also failed: {fallback_error}")
                        last_error = fallback_error
                
                # Check if this is a transient error worth retrying
                # Use last_error to check the most recent error (may be from SSL fallback)
                if _is_transient_connection_error(last_error) and attempt < DB_CONNECT_MAX_RETRIES - 1:
                    # Calculate delay with exponential backoff and additive jitter
                    # Additive jitter prevents retries from being too aggressive
                    # while still helping prevent thundering herd
                    jitter = random.uniform(0, DB_CONNECT_JITTER_FACTOR * delay_ms)
                    actual_delay_ms = min(delay_ms + jitter, DB_CONNECT_MAX_DELAY_MS)
                    
                    print(f"⚠️ Transient connection error (attempt {attempt + 1}/{DB_CONNECT_MAX_RETRIES}): {last_error}")
                    print(f"   Retrying in {actual_delay_ms:.0f}ms...")
                    
                    time.sleep(actual_delay_ms / 1000.0)
                    delay_ms *= 2  # Exponential backoff
                else:
                    # Non-transient error or last attempt - don't retry
                    break
            except Exception as e:
                last_error = e
                # Non-psycopg2 errors are not retried
                break
        
        # All retries exhausted, raise the last error
        if last_error:
            raise last_error
        raise psycopg2.OperationalError("Failed to connect to PostgreSQL after retries")
    else:
        conn = sqlite3.connect(str(DB_PATH), timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrent access and crash recovery
        result = conn.execute("PRAGMA journal_mode=WAL").fetchone()
        if result[0].lower() != 'wal':
            print(f"⚠️  Warning: Failed to enable WAL mode, got: {result[0]}")
        
        # Set synchronous to NORMAL for better performance while maintaining safety
        conn.execute("PRAGMA synchronous=NORMAL")
        
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys=ON")
        result = conn.execute("PRAGMA foreign_keys").fetchone()
        if not result or not result[0]:
            print(f"⚠️  Warning: Failed to enable foreign keys, got: {result[0] if result else 'None'}")
        
        return conn


def return_db_connection(conn):
    """Return a connection to the pool or close it.
    
    Handles both pooled and non-pooled (fallback) connections correctly:
    - For pooled connections: Returns to pool for reuse
    - For non-pooled/fallback connections: Closes the connection
    
    If putconn() fails (e.g., connection wasn't from pool), falls through
    to close the connection, ensuring proper cleanup in all cases.
    """
    if conn is None:
        return
    
    if USE_POSTGRESQL:
        conn_pool = _get_connection_pool()
        if conn_pool:
            try:
                # Try to return to pool - will fail for non-pooled connections
                conn_pool.putconn(conn)
                return
            except Exception:
                # Connection wasn't from pool (fallback connection)
                # Fall through to close it
                pass
    
    # Close the connection if not using pool, not PostgreSQL, or pool return failed
    try:
        conn.close()
    except Exception:
        pass


def execute_query(query, params=None, fetch=False, fetchone=False, commit=False):
    """
    Universal query executor for both PostgreSQL and SQLite
    """
    conn = get_db_connection()

    try:
        if USE_POSTGRESQL:
            cursor = conn.cursor()
            # Convert SQLite ? placeholders to PostgreSQL %s
            query = query.replace("?", "%s")
        else:
            cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetch:
            result = cursor.fetchall()

        if commit:
            conn.commit()
            if USE_POSTGRESQL:
                # Get last inserted ID for PostgreSQL
                if "INSERT" in query.upper() and "RETURNING" not in query.upper():
                    result = cursor.fetchone()

        cursor.close()
        return_db_connection(conn)

        return result

    except Exception as e:
        conn.rollback()
        return_db_connection(conn)
        raise e


def _get_psycopg2_error_details(e):
    """
    Extract detailed error information from a psycopg2 exception.
    
    psycopg2 exceptions contain additional attributes that provide more
    context than the default string representation:
    - pgerror: The full error message from PostgreSQL
    - pgcode: The PostgreSQL error code (e.g., '42501' for permission denied)
    - diag: Additional diagnostic information
    
    This function combines these to provide a comprehensive error message
    that is more useful for debugging than just `str(e)`.
    
    Args:
        e: A psycopg2 exception (Error, OperationalError, ProgrammingError, etc.)
        
    Returns:
        A string with the full error details
    """
    parts = []
    
    # Helper to check if a string is just a numeric value (integer or float)
    # This is used to detect unhelpful error messages that are just error codes
    def is_numeric_string(s):
        if not s:
            return False
        # Use lstrip('-') to handle negative numbers correctly
        stripped = s.lstrip('-')
        if not stripped:
            return False  # Handle case of just "-"
        # Check for integer or simple decimal (handles "0", "-1", "3.14", "-2.5")
        return stripped.isdigit() or (stripped.count('.') == 1 and stripped.replace('.', '').isdigit())
    
    # Primary error message - use pgerror if available as it's more detailed
    pgerror = getattr(e, 'pgerror', None)
    pgerror_stripped = pgerror.strip() if pgerror else ""
    pgerror_is_numeric = is_numeric_string(pgerror_stripped)
    
    # Only add pgerror if it's not just a numeric code
    if pgerror_stripped and not pgerror_is_numeric:
        parts.append(pgerror_stripped)
    
    # Get the string representation
    str_repr = str(e).strip() if str(e) else ""
    str_repr_is_numeric = is_numeric_string(str_repr)
    
    # Only add str_repr if:
    # 1. We don't have useful pgerror (so we need some information), or
    # 2. str_repr contains useful information not already in pgerror
    # Skip if it's just a numeric code and we already have useful pgerror
    has_useful_pgerror = pgerror_stripped and not pgerror_is_numeric
    
    if str_repr and not str_repr_is_numeric and (not has_useful_pgerror or str_repr not in pgerror_stripped):
        parts.append(str_repr)
    elif str_repr and str_repr_is_numeric and not has_useful_pgerror:
        # Only include numeric code if we have no other useful information
        # Provide more context about what the code means
        parts.append(f"Error code: {str_repr} (extension may not be available or requires server configuration)")
    
    # Include the PostgreSQL error code if available
    pgcode = getattr(e, 'pgcode', None)
    if pgcode:
        parts.append(f"[Code: {pgcode}]")
    
    # If we still have no information, provide a fallback
    if not parts:
        parts.append(f"Unknown error (type: {type(e).__name__})")
    
    return " ".join(parts)


def _is_psycopg2_exception(e):
    """
    Check if an exception is a psycopg2 exception.
    
    psycopg2 exceptions have special attributes (pgerror, pgcode) that
    provide more detailed error information than the standard string
    representation. This helper is used to detect when we should use
    _get_psycopg2_error_details() for better error messages.
    
    Args:
        e: Any exception
        
    Returns:
        True if the exception has psycopg2-specific attributes
    """
    return hasattr(e, 'pgerror') or hasattr(e, 'pgcode')


def _safe_rollback(conn):
    """
    Safely rollback a database connection.
    Handles connection state issues gracefully.
    """
    try:
        conn.rollback()
    except psycopg2.InterfaceError as e:
        # Connection is closed or in a bad state
        print(f"⚠️  Cannot rollback: connection interface error: {_get_psycopg2_error_details(e)}")
    except psycopg2.OperationalError as e:
        # Connection lost or other operational issue
        print(f"⚠️  Cannot rollback: operational error: {_get_psycopg2_error_details(e)}")
    except Exception as e:
        # Unexpected error during rollback
        print(f"⚠️  Rollback failed with unexpected error: {e}")


def init_postgresql_extensions(cursor, conn):
    """
    Initialize PostgreSQL extensions including pg_stat_statements.
    
    pg_stat_statements provides query performance statistics and is useful for:
    - Monitoring slow queries
    - Identifying frequently executed queries
    - Performance tuning
    
    Note: pg_stat_statements requires shared_preload_libraries configuration
    on the PostgreSQL server. On managed services like Railway, this is typically
    pre-configured, but we still need to CREATE EXTENSION.
    
    Returns True if all extensions initialized successfully, False otherwise.
    Extension failures are non-fatal - the application continues regardless.
    """
    success = True
    
    for ext_name, ext_config in POSTGRESQL_EXTENSIONS.items():
        ext_sql = ext_config["sql"]
        ext_description = ext_config["description"]
        
        try:
            # Check if extension is available in the system
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_available_extensions 
                    WHERE name = %s
                ) as is_available
                """,
                (ext_name,)
            )
            is_available = cursor.fetchone()["is_available"]
            
            if not is_available:
                print(f"⚠️  Extension '{ext_name}' is not available on this PostgreSQL server")
                print(f"   This is normal for some managed database providers")
                continue
            
            # Check if extension is already installed
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = %s
                ) as is_installed
                """,
                (ext_name,)
            )
            is_installed = cursor.fetchone()["is_installed"]
            
            if is_installed:
                print(f"✅ Extension '{ext_name}' is already installed")
            else:
                # Execute pre-defined SQL statement from the POSTGRESQL_EXTENSIONS constant
                # This ensures only validated, pre-defined SQL is executed
                cursor.execute(ext_sql)
                conn.commit()
                print(f"✅ Extension '{ext_name}' installed successfully ({ext_description})")
                
        except psycopg2.OperationalError as e:
            error_details = _get_psycopg2_error_details(e)
            error_msg = error_details.lower()
            success = False
            
            # Handle specific known errors gracefully
            if "shared_preload_libraries" in error_msg:
                print(f"⚠️  Extension '{ext_name}' requires server-side configuration")
                print(f"   The extension must be added to shared_preload_libraries in postgresql.conf")
                print(f"   On Railway/managed PostgreSQL: Contact your provider to enable this extension")
            else:
                print(f"⚠️  Database operation error for extension '{ext_name}': {error_details}")
            
            _safe_rollback(conn)
            
        except psycopg2.ProgrammingError as e:
            error_details = _get_psycopg2_error_details(e)
            error_msg = error_details.lower()
            success = False
            
            if "permission denied" in error_msg:
                print(f"⚠️  Insufficient permissions to create extension '{ext_name}'")
                print(f"   This is normal for non-superuser database roles")
            elif "does not exist" in error_msg:
                print(f"⚠️  Extension '{ext_name}' is not installed on the PostgreSQL server")
            else:
                print(f"⚠️  Programming error for extension '{ext_name}': {error_details}")
            
            _safe_rollback(conn)
            
        except psycopg2.Error as e:
            # Catch other psycopg2 errors
            error_details = _get_psycopg2_error_details(e)
            print(f"⚠️  Database error initializing extension '{ext_name}': {error_details}")
            success = False
            _safe_rollback(conn)
            
        except Exception as e:
            # Catch any unexpected errors
            # Check if it's a psycopg2 exception that wasn't caught above
            if _is_psycopg2_exception(e):
                error_details = _get_psycopg2_error_details(e)
                print(f"⚠️  Unexpected error initializing extension '{ext_name}': {error_details}")
            else:
                # Include exception type for better debugging of unexpected errors
                print(f"⚠️  Unexpected error initializing extension '{ext_name}': {type(e).__name__}: {e}")
            success = False
            _safe_rollback(conn)
    
    return success


def init_database():
    """Initialize database with all required tables"""
    global _db_initialized

    print("🚀 Initializing database...")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Initialize PostgreSQL extensions if using PostgreSQL
        # Extension initialization is non-fatal - the app continues even if extensions fail
        if USE_POSTGRESQL:
            ext_success = init_postgresql_extensions(cursor, conn)
            if not ext_success:
                print("⚠️  Some extensions could not be initialized, but this is non-fatal")
                # Ensure connection is in a clean state before continuing
                _safe_rollback(conn)
                # Recreate cursor after rollback to ensure it's in a valid state
                cursor.close()
                cursor = conn.cursor()
        
        # Detect if we need to create tables
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                ) as table_exists
            """
            )
            table_exists = cursor.fetchone()["table_exists"]
        else:
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """
            )
            table_exists = cursor.fetchone() is not None

        if not table_exists:
            print("📦 Creating database tables...")

            # Adjust syntax for PostgreSQL vs SQLite
            if USE_POSTGRESQL:
                # PostgreSQL uses SERIAL instead of AUTOINCREMENT
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        first_name VARCHAR(100),
                        last_name VARCHAR(100),
                        user_type VARCHAR(50) DEFAULT 'user',
                        location TEXT,
                        phone VARCHAR(20),
                        bio TEXT,
                        avatar_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        is_available_for_hire BOOLEAN DEFAULT FALSE,
                        trade VARCHAR(100) DEFAULT '',
                        username VARCHAR(100),
                        occupation VARCHAR(100),
                        company_name VARCHAR(200)
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS posts (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        image_url TEXT,
                        video_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS jobs (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        company VARCHAR(255) NOT NULL,
                        location VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        requirements TEXT,
                        salary_range VARCHAR(100),
                        job_type VARCHAR(50) DEFAULT 'full-time',
                        category VARCHAR(100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS comments (
                        id SERIAL PRIMARY KEY,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS likes (
                        id SERIAL PRIMARY KEY,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(post_id, user_id),
                        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS stories (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        media_url TEXT NOT NULL,
                        media_type VARCHAR(20) NOT NULL,
                        caption TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        views INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS follows (
                        id SERIAL PRIMARY KEY,
                        follower_id INTEGER NOT NULL,
                        followed_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(follower_id, followed_id),
                        FOREIGN KEY (follower_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (followed_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

            else:
                # SQLite syntax (original)
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        first_name TEXT,
                        last_name TEXT,
                        user_type TEXT DEFAULT 'user',
                        location TEXT,
                        phone TEXT,
                        bio TEXT,
                        avatar_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        is_available_for_hire BOOLEAN DEFAULT 0,
                        trade TEXT DEFAULT '',
                        username TEXT,
                        occupation TEXT,
                        company_name TEXT
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        image_url TEXT,
                        video_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        company TEXT NOT NULL,
                        location TEXT NOT NULL,
                        description TEXT NOT NULL,
                        requirements TEXT,
                        salary_range TEXT,
                        job_type TEXT DEFAULT 'full-time',
                        category TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS likes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(post_id, user_id),
                        FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS stories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        media_url TEXT NOT NULL,
                        media_type TEXT NOT NULL,
                        caption TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        views INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS follows (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        follower_id INTEGER NOT NULL,
                        followed_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(follower_id, followed_id),
                        FOREIGN KEY (follower_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (followed_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

            conn.commit()
            print("✅ Database tables created successfully!")
            
            # Create indexes for new database
            create_database_indexes(cursor, conn)

        else:
            print("✅ Database tables already exist")

            # Run migrations to add missing columns
            migrate_user_columns(cursor, conn)
            
            # Ensure indexes exist (idempotent)
            create_database_indexes(cursor, conn)

        cursor.close()
        conn.close()

        # Mark database as successfully initialized
        _db_initialized = True
        print("✅ Database initialization completed successfully")

    except psycopg2.Error as e:
        # Use detailed error extraction for psycopg2 errors
        error_details = _get_psycopg2_error_details(e)
        print(f"❌ Database initialization error: {error_details}")
        try:
            conn.rollback()
            cursor.close()
            conn.close()
        except Exception:
            pass  # Connection might already be closed
        raise
    except Exception as e:
        # Check if it's a psycopg2 exception that wasn't caught above
        if _is_psycopg2_exception(e):
            error_details = _get_psycopg2_error_details(e)
            print(f"❌ Database initialization error: {error_details}")
        else:
            # Include exception type for better debugging of unexpected errors
            print(f"❌ Database initialization error: {type(e).__name__}: {e}")
        try:
            conn.rollback()
            cursor.close()
            conn.close()
        except Exception:
            pass  # Connection might already be closed
        raise


def create_database_indexes(cursor, conn):
    """
    Create database indexes to optimize query performance.
    
    HTTP 499 "Client Closed Request" errors occur when clients timeout waiting
    for server responses. For the login endpoint, slow database queries are a
    primary cause. Without indexes, queries like "SELECT * FROM users WHERE 
    LOWER(email) = ?" require full table scans, which become increasingly slow
    as the user base grows.
    
    These indexes ensure queries complete in milliseconds instead of seconds:
    - users_email_lower_idx: Speeds up LOWER(email) lookups in login queries
    - users_is_active_idx: Speeds up active user queries (partial index)
    - posts_user_id_idx: Speeds up user's posts queries
    - posts_created_at_idx: Speeds up posts ordering
    
    All indexes use IF NOT EXISTS to be idempotent.
    
    Note: SQLite indexes are simpler because SQLite's LIKE is case-insensitive
    by default for ASCII characters.
    """
    if USE_POSTGRESQL:
        indexes = [
            # Critical for login performance - avoids full table scan on LOWER(email)
            ("users_email_lower_idx", "CREATE INDEX IF NOT EXISTS users_email_lower_idx ON users (LOWER(email))"),
            # Speeds up queries filtering by active users
            ("users_is_active_idx", "CREATE INDEX IF NOT EXISTS users_is_active_idx ON users (is_active) WHERE is_active = TRUE"),
            # Speeds up user's posts queries
            ("posts_user_id_idx", "CREATE INDEX IF NOT EXISTS posts_user_id_idx ON posts (user_id)"),
            # Speeds up posts ordering by date
            ("posts_created_at_idx", "CREATE INDEX IF NOT EXISTS posts_created_at_idx ON posts (created_at DESC)"),
            # Speeds up job searches
            ("jobs_is_active_idx", "CREATE INDEX IF NOT EXISTS jobs_is_active_idx ON jobs (is_active) WHERE is_active = TRUE"),
            ("jobs_created_at_idx", "CREATE INDEX IF NOT EXISTS jobs_created_at_idx ON jobs (created_at DESC)"),
        ]
        
        for index_name, index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Index '{index_name}' created or already exists")
            except Exception as e:
                # Index creation errors are non-fatal
                print(f"⚠️  Could not create index '{index_name}': {e}")
        
        conn.commit()
    else:
        # SQLite indexes - note SQLite's LIKE is case-insensitive by default
        # for ASCII characters, and email column has UNIQUE constraint which
        # implicitly creates an index. These additional indexes help with
        # queries not covered by the UNIQUE constraint.
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS posts_user_id_idx ON posts (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS posts_created_at_idx ON posts (created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS jobs_is_active_idx ON jobs (is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS jobs_created_at_idx ON jobs (created_at)")
            conn.commit()
            print("✅ SQLite indexes created or already exist")
        except Exception as e:
            print(f"⚠️  Could not create SQLite indexes: {e}")


def migrate_user_columns(cursor, conn):
    """Add missing columns to users table if they don't exist"""
    try:
        columns_to_add = [
            ("username", "VARCHAR(100)" if USE_POSTGRESQL else "TEXT"),
            ("occupation", "VARCHAR(100)" if USE_POSTGRESQL else "TEXT"),
            ("company_name", "VARCHAR(200)" if USE_POSTGRESQL else "TEXT"),
        ]

        for column_name, column_type in columns_to_add:
            try:
                if USE_POSTGRESQL:
                    cursor.execute(
                        f"""
                        ALTER TABLE users 
                        ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                    """
                    )
                else:
                    # Check if column exists in SQLite
                    cursor.execute("PRAGMA table_info(users)")
                    columns = [row[1] for row in cursor.fetchall()]
                    if column_name not in columns:
                        cursor.execute(
                            f"""
                            ALTER TABLE users 
                            ADD COLUMN {column_name} {column_type}
                        """
                        )
                        print(f"✅ Added {column_name} column to users table")

                conn.commit()
            except Exception as e:
                if (
                    "duplicate column" not in str(e).lower()
                    and "already exists" not in str(e).lower()
                ):
                    print(f"⚠️ Migration warning for {column_name}: {e}")

    except Exception as e:
        print(f"⚠️ Migration warning: {e}")


def ensure_database_initialized():
    """
    Ensure database is initialized.
    If initialization failed on startup, retry it here.
    This is thread-safe and will only initialize once.
    """
    global _db_initialized

    if not _db_initialized:
        with _db_init_lock:
            # Double-check inside the lock
            if not _db_initialized:
                try:
                    print("🔧 Retrying database initialization...")
                    init_database()
                    print("✅ Database initialization successful on retry")
                except psycopg2.Error as e:
                    error_details = _get_psycopg2_error_details(e)
                    print(f"⚠️ Database initialization retry failed: {error_details}")
                    # Don't raise - let the endpoint handle it
                except Exception as e:
                    # Include exception type for better debugging of unexpected errors
                    print(f"⚠️ Database initialization retry failed: {type(e).__name__}: {e}")
                    # Don't raise - let the endpoint handle it

    return _db_initialized


def requires_database(f):
    """
    Decorator that ensures database is initialized before endpoint execution.
    
    Use this decorator on endpoints that require database access.
    If the database is not initialized, returns a 503 response asking the user
    to try again.
    
    Example:
        @app.route("/api/users")
        @requires_database
        def get_users():
            # Database is guaranteed to be initialized here
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ensure_database_initialized():
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Database is initializing. Please try again.",
                    }
                ),
                503,
            )
        return f(*args, **kwargs)
    return decorated_function


def get_connection_pool_stats():
    """
    Get connection pool statistics for monitoring and debugging.
    
    Returns information about pool usage to help diagnose
    connection exhaustion issues that can cause HTTP 499 timeouts.
    
    Note: This function accesses private attributes of the psycopg2 
    ThreadedConnectionPool (_used and _pool). This is necessary because
    psycopg2 doesn't provide public methods for pool introspection.
    If psycopg2's internal implementation changes, this function will
    gracefully return an error status instead of crashing.
    
    Returns:
        dict with pool statistics, or error status if stats unavailable
    """
    if not USE_POSTGRESQL:
        return {"type": "sqlite", "pooled": False}
    
    conn_pool = _get_connection_pool()
    if conn_pool is None:
        return {"type": "postgresql", "pooled": False, "status": "pool_not_initialized"}
    
    try:
        # ThreadedConnectionPool internal attributes:
        # - _used: dict of connections currently checked out
        # - _pool: list of connections available for checkout
        # These are implementation details that may change in future versions.
        used_count = len(getattr(conn_pool, '_used', {}))
        available_count = len(getattr(conn_pool, '_pool', []))
        
        return {
            "type": "postgresql",
            "pooled": True,
            "max_connections": DB_POOL_MAX_CONNECTIONS,
            "connections_in_use": used_count,
            "connections_available": available_count,
            "pool_timeout_seconds": POOL_TIMEOUT_SECONDS,
            "statement_timeout_ms": STATEMENT_TIMEOUT_MS,
        }
    except Exception as e:
        return {
            "type": "postgresql",
            "pooled": True,
            "status": "error_reading_stats",
            "error": str(e)[:100],
        }


def _get_cursor_value(result, key_or_index, default=None):
    """
    Extract a value from a cursor result, handling both dict and tuple types.
    
    PostgreSQL with RealDictCursor returns dict-like objects, while other
    cursors may return tuples. This helper provides consistent access.
    
    Args:
        result: The cursor fetchone() result (dict-like or tuple)
        key_or_index: The key (for dict) or index (for tuple) to access
        default: Default value if key/index doesn't exist
        
    Returns:
        The extracted value or default if not found
    """
    if result is None:
        return default
    
    if hasattr(result, 'get'):
        # Dict-like object (RealDictCursor result)
        return result.get(key_or_index, default)
    else:
        # Tuple-like object
        try:
            # key_or_index should be an integer for tuple access
            idx = key_or_index if isinstance(key_or_index, int) else 0
            return result[idx] if len(result) > idx else default
        except (TypeError, IndexError):
            return default


def get_database_recovery_status():
    """
    Check if PostgreSQL database is in recovery mode.
    
    After an improper shutdown (e.g., container killed without SIGTERM,
    power failure, or crash), PostgreSQL performs automatic recovery by
    replaying Write-Ahead Log (WAL) records.
    
    During recovery:
    - The database may be slower as it replays transactions
    - Some connections might be temporarily refused
    - Normal operation resumes after recovery completes
    
    This function queries pg_is_in_recovery() which returns:
    - True: Database is in recovery mode (read-only on standby, or recovering)
    - False: Database is in normal operation mode
    
    Returns:
        dict with recovery status information
    """
    if not USE_POSTGRESQL:
        return {
            "type": "sqlite",
            "in_recovery": False,
            "status": "not_applicable",
            "message": "SQLite does not have a recovery mode like PostgreSQL"
        }
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if in recovery mode
        cursor.execute("SELECT pg_is_in_recovery() as in_recovery")
        result = cursor.fetchone()
        in_recovery = _get_cursor_value(result, "in_recovery", None)
        
        # Get additional recovery information if available
        recovery_info = {
            "type": "postgresql",
            "in_recovery": in_recovery,
            "status": "recovering" if in_recovery else "normal",
        }
        
        if in_recovery:
            # Try to get more recovery details (may not be available on all versions)
            try:
                cursor.execute("""
                    SELECT 
                        pg_last_wal_receive_lsn() as last_receive_lsn,
                        pg_last_wal_replay_lsn() as last_replay_lsn
                """)
                wal_info = cursor.fetchone()
                if wal_info:
                    # Use helper function for consistent result handling
                    receive_lsn = _get_cursor_value(wal_info, "last_receive_lsn", "unknown")
                    replay_lsn = _get_cursor_value(wal_info, "last_replay_lsn", "unknown")
                    recovery_info["wal_receive_lsn"] = str(receive_lsn)
                    recovery_info["wal_replay_lsn"] = str(replay_lsn)
            except Exception:
                # WAL functions may not be available in all configurations
                pass
            
            recovery_info["message"] = (
                "Database is recovering from improper shutdown. "
                "This is normal and the database will return to full operation "
                "once WAL replay is complete."
            )
        
        cursor.close()
        return_db_connection(conn)
        
        return recovery_info
        
    except psycopg2.OperationalError as e:
        error_msg = str(e).lower()
        
        # Check if error indicates database is still starting up or recovering
        if "starting up" in error_msg or "recovery" in error_msg:
            return {
                "type": "postgresql",
                "in_recovery": True,
                "status": "startup_or_recovery",
                "message": "Database is starting up or recovering. Connections may be temporarily unavailable."
            }
        
        return {
            "type": "postgresql",
            "in_recovery": None,
            "status": "connection_error",
            "error": str(e)[:200]
        }
        
    except Exception as e:
        return {
            "type": "postgresql",
            "in_recovery": None,
            "status": "error",
            "error": str(e)[:200]
        }


def _log_startup_recovery_status():
    """
    Log database recovery status during startup.
    
    This function checks if the PostgreSQL database is in or recently was in
    recovery mode and logs appropriate messages. This helps operators understand
    when they see PostgreSQL recovery logs like:
    - "database system was interrupted"
    - "database system was not properly shut down; automatic recovery in progress"
    
    These logs are normal and expected after container restarts or deployments
    on platforms like Railway where the database container may be stopped
    without a graceful shutdown signal.
    """
    if not USE_POSTGRESQL:
        return  # SQLite doesn't have recovery mode
    
    try:
        recovery_status = get_database_recovery_status()
        in_recovery = recovery_status.get("in_recovery")
        
        if in_recovery is True:
            print("📊 Database Recovery Status: RECOVERING")
            print("   └─ PostgreSQL is replaying WAL logs after improper shutdown")
            print("   └─ This is normal on Railway/Docker after container restarts")
            print("   └─ Database will be fully operational once recovery completes")
        elif in_recovery is False:
            print("📊 Database Recovery Status: NORMAL")
            print("   └─ PostgreSQL is running in normal operation mode")
        else:
            # Could not determine recovery status
            status = recovery_status.get("status", "unknown")
            if status == "connection_error":
                print("📊 Database Recovery Status: CONNECTION_ERROR")
                print("   └─ Could not connect to check recovery status")
            else:
                print(f"📊 Database Recovery Status: {status.upper()}")
    except Exception as e:
        # Non-fatal: just log and continue
        print(f"📊 Database Recovery Status: UNKNOWN (check failed: {e})")


# Initialize database in background thread to avoid blocking healthcheck
def init_database_background():
    """Initialize database in background thread to allow app to start quickly"""
    global _db_initialized

    with _db_init_lock:
        # Check if already initialized by another thread
        if _db_initialized:
            print("✅ Database already initialized")
            return

        try:
            init_database()
            # After successful initialization, check and log database recovery status
            # This helps operators understand if the database recently recovered
            # from an improper shutdown (which would explain recovery logs)
            _log_startup_recovery_status()
        except psycopg2.Error as e:
            error_details = _get_psycopg2_error_details(e)
            print(f"⚠️ Database initialization warning: {error_details}")
            print("⚠️ Database will be initialized on first request")
        except Exception as e:
            # Check if it's a psycopg2 exception that wasn't caught above
            if _is_psycopg2_exception(e):
                error_details = _get_psycopg2_error_details(e)
                print(f"⚠️ Database initialization warning: {error_details}")
            else:
                # Include exception type for better debugging of unexpected errors
                print(f"⚠️ Database initialization warning: {type(e).__name__}: {e}")
            print("⚠️ Database will be initialized on first request")

# Start database initialization in background thread
_db_init_thread = None
try:
    print("🚀 Starting database initialization in background thread...")
    _db_init_thread = threading.Thread(target=init_database_background, daemon=True, name="db-init")
    _db_init_thread.start()
except Exception as e:
    print(f"⚠️ Failed to start database initialization thread: {e}")
    print("⚠️ Database will be initialized on first request")

print("✅ Application ready to serve requests")


# ==========================================
# DATABASE KEEPALIVE
# ==========================================

# Database keepalive configuration
# Prevents Railway PostgreSQL from sleeping after 15 minutes of inactivity
# Enabled when:
# - Running on Railway (IS_RAILWAY=True, detected via RAILWAY_PROJECT_ID), OR
# - Running in production environment (IS_PRODUCTION=True)
# AND PostgreSQL is configured (USE_POSTGRESQL=True)
#
# This ensures keepalive runs on Railway even if RAILWAY_ENVIRONMENT is not explicitly
# set to "production", since Railway is inherently a production platform and database
# sleeping is a Railway-specific issue.
DB_KEEPALIVE_ENABLED = (IS_PRODUCTION or IS_RAILWAY) and USE_POSTGRESQL
DB_KEEPALIVE_INTERVAL_SECONDS = int(os.getenv("DB_KEEPALIVE_INTERVAL_SECONDS", "600"))  # 10 minutes
DB_KEEPALIVE_FAILURE_THRESHOLD = 3  # Number of consecutive failures before warning
DB_KEEPALIVE_ERROR_RETRY_DELAY_SECONDS = 60  # Delay before retrying after unexpected error
DB_KEEPALIVE_SHUTDOWN_TIMEOUT_SECONDS = 5  # Max time to wait for graceful shutdown

# Track keepalive thread and status
_keepalive_thread = None
_keepalive_running = False
_keepalive_last_ping = None
_keepalive_consecutive_failures = 0


def database_keepalive_worker():
    """
    Background worker that periodically pings the database to prevent it from sleeping.
    
    Railway databases on free/hobby tiers sleep after 15 minutes of inactivity.
    This worker pings the database every 10 minutes to keep it active.
    
    The keepalive uses a simple SELECT 1 query that:
    - Wakes up sleeping connections
    - Verifies connection pool health
    - Minimal resource overhead
    - Non-intrusive to production operations
    """
    global _keepalive_running, _keepalive_last_ping, _keepalive_consecutive_failures
    
    _keepalive_running = True
    print(f"🔄 Database keepalive started (interval: {DB_KEEPALIVE_INTERVAL_SECONDS}s)")
    
    # Perform initial ping immediately to verify connection on startup
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        return_db_connection(conn)
        _keepalive_last_ping = datetime.now(timezone.utc)
        print(f"✅ Initial database keepalive ping successful")
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"⚠️ Initial database keepalive ping failed: {error_msg}")
        _keepalive_consecutive_failures += 1
    
    while _keepalive_running:
        try:
            # Wait for the interval before next ping
            time.sleep(DB_KEEPALIVE_INTERVAL_SECONDS)
            
            if not _keepalive_running:
                break
            
            # Ping the database
            conn = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return_db_connection(conn)
                
                # Update success status
                _keepalive_last_ping = datetime.now(timezone.utc)
                _keepalive_consecutive_failures = 0
                print(f"✅ Database keepalive ping successful at {_keepalive_last_ping.isoformat()}")
                
            except Exception as e:
                _keepalive_consecutive_failures += 1
                error_msg = str(e)[:100]  # Truncate long errors
                print(f"⚠️ Database keepalive ping failed (attempt {_keepalive_consecutive_failures}): {error_msg}")
                
                # Return connection to pool even on error
                if conn:
                    try:
                        return_db_connection(conn)
                    except Exception:
                        pass
                
                # If we have multiple consecutive failures, log warning
                if _keepalive_consecutive_failures >= DB_KEEPALIVE_FAILURE_THRESHOLD:
                    print("⚠️ Multiple keepalive failures, connection pool may need refresh")
                    # Don't crash the keepalive thread - it will keep trying
                    
        except Exception as e:
            print(f"⚠️ Unexpected error in database keepalive worker: {e}")
            time.sleep(DB_KEEPALIVE_ERROR_RETRY_DELAY_SECONDS)  # Wait before retrying on unexpected errors
    
    print("🛑 Database keepalive stopped")


def start_database_keepalive():
    """
    Start the database keepalive background thread.
    
    Only starts if:
    - Running in production environment (IS_PRODUCTION=True), OR
    - Running on Railway (IS_RAILWAY=True)
    - AND PostgreSQL is configured (USE_POSTGRESQL=True)
    - Keepalive is not already running
    
    The keepalive prevents Railway PostgreSQL databases from sleeping
    after periods of inactivity.
    """
    global _keepalive_thread, _keepalive_running
    
    if not DB_KEEPALIVE_ENABLED:
        # Only log keepalive disabled message when PostgreSQL is configured
        # but environment conditions prevent keepalive from running.
        # Skip message for SQLite/development since keepalive is not applicable.
        if USE_POSTGRESQL:
            print("ℹ️ Database keepalive disabled (not in production or Railway environment)")
        return
    
    if _keepalive_thread is not None and _keepalive_thread.is_alive():
        print("ℹ️ Database keepalive already running")
        return
    
    try:
        _keepalive_thread = threading.Thread(
            target=database_keepalive_worker,
            daemon=True,
            name="db-keepalive"
        )
        _keepalive_thread.start()
        print("✅ Database keepalive thread started")
    except Exception as e:
        print(f"⚠️ Failed to start database keepalive thread: {e}")


def stop_database_keepalive():
    """
    Stop the database keepalive background thread.
    
    Called during application shutdown to gracefully stop the keepalive worker.
    """
    global _keepalive_running, _keepalive_thread
    
    if _keepalive_thread is None or not _keepalive_thread.is_alive():
        return
    
    print("🛑 Stopping database keepalive...")
    _keepalive_running = False
    
    # Wait for the thread to stop gracefully
    _keepalive_thread.join(timeout=DB_KEEPALIVE_SHUTDOWN_TIMEOUT_SECONDS)
    
    if _keepalive_thread.is_alive():
        print("⚠️ Database keepalive thread did not stop gracefully")
    else:
        print("✅ Database keepalive stopped")


# Register keepalive shutdown on application exit
atexit.register(stop_database_keepalive)

# Start database keepalive if enabled
start_database_keepalive()


# ==========================================
# HEALTH CHECK ENDPOINT
# ==========================================


@app.route("/", methods=["GET"])
@limiter.exempt
def root():
    """
    Root endpoint - returns API information
    Provides a welcome message and basic API status for monitoring tools
    Exempt from rate limiting to allow monitoring services to check frequently
    """
    return (
        jsonify(
            {
                "name": "HireMeBahamas API",
                "status": "running",
                "version": "1.0.0",
                "message": "Welcome to the HireMeBahamas API",
                "endpoints": {
                    "health": "/health",
                    "health_detailed": "/api/health",
                },
            }
        ),
        200,
    )


@app.route("/health", methods=["GET"])
@limiter.exempt
def health_check():
    """
    Health check endpoint for Railway
    Returns 200 OK immediately to ensure Railway healthcheck passes
    The app is healthy if this endpoint responds - database initialization
    happens asynchronously and doesn't need to block the healthcheck
    Exempt from rate limiting to allow monitoring services to check frequently
    """
    return (
        jsonify(
            {
                "status": "healthy",
                "message": "HireMeBahamas API is running",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ),
        200,
    )


@app.route("/api/health", methods=["GET"])
@limiter.exempt
def api_health_check():
    """
    Detailed health check endpoint with database status
    This can be used for monitoring but won't block Railway healthcheck
    Attempts to retry database initialization if it failed on startup
    Exempt from rate limiting to allow monitoring services to check frequently
    """
    # Determine HTTP status code based on service availability
    # 200: Service is healthy or degraded but functional
    # 503: Service is unavailable (cannot connect to database)
    http_status = 200
    
    response = {
        "status": "healthy",
        "message": "HireMeBahamas API is running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "db_initialized": _db_initialized,
        "environment": ENVIRONMENT,
        "is_production": IS_PRODUCTION,
        "is_railway": IS_RAILWAY,
        "database_url_configured": USE_POSTGRESQL,
    }

    # Report database configuration warning if present
    # Use 200 status with 'degraded' state - the service is still functional
    if DATABASE_CONFIG_WARNING:
        response["status"] = "degraded"
        response["config_warning"] = DATABASE_CONFIG_WARNING
        # Keep http_status = 200 since the service is still functional

    # Try to ensure database is initialized
    if not _db_initialized:
        ensure_database_initialized()
        response["db_initialized"] = _db_initialized

    # Try to check database connection
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        
        # Check if PostgreSQL is in recovery mode (after improper shutdown)
        # This helps diagnose database recovery issues in production
        if USE_POSTGRESQL:
            try:
                cursor.execute("SELECT pg_is_in_recovery() as in_recovery")
                is_in_recovery = cursor.fetchone()
                if is_in_recovery:
                    # Use helper function with correct key (matching query alias)
                    recovery_value = _get_cursor_value(is_in_recovery, "in_recovery", False)
                    response["database_recovery"] = {
                        "in_recovery": recovery_value,
                        "status": "recovering" if recovery_value else "normal"
                    }
                    if recovery_value:
                        response["status"] = "degraded"
                        response["recovery_message"] = (
                            "Database is in recovery mode after improper shutdown. "
                            "Requests may be slower until recovery completes."
                        )
            except Exception as recovery_check_error:
                # Non-fatal: recovery check failed but database is still connected
                response["database_recovery"] = {
                    "in_recovery": None,
                    "status": "unknown",
                    "error": str(recovery_check_error)[:100]
                }
        
        cursor.close()
        return_db_connection(conn)
        response["database"] = "connected"
        response["db_type"] = "PostgreSQL" if USE_POSTGRESQL else "SQLite"
        
        # Add connection pool stats for monitoring
        pool_stats = get_connection_pool_stats()
        if pool_stats:
            response["connection_pool"] = pool_stats
        
        # Add keepalive status for monitoring
        if DB_KEEPALIVE_ENABLED:
            keepalive_status = {
                "enabled": True,
                "running": _keepalive_running,
                "interval_seconds": DB_KEEPALIVE_INTERVAL_SECONDS,
                "consecutive_failures": _keepalive_consecutive_failures,
            }
            if _keepalive_last_ping:
                keepalive_status["last_ping"] = _keepalive_last_ping.isoformat()
                keepalive_status["seconds_since_last_ping"] = (
                    datetime.now(timezone.utc) - _keepalive_last_ping
                ).total_seconds()
            response["keepalive"] = keepalive_status
            
    except Exception as e:
        response["database"] = "error"
        response["status"] = "unhealthy"
        http_status = 503  # Service Unavailable - actual database connection failure
        # Keep meaningful error information up to MAX_ERROR_MESSAGE_LENGTH
        error_msg = str(e)
        if len(error_msg) <= MAX_ERROR_MESSAGE_LENGTH:
            response["error"] = error_msg
        else:
            # Truncate with ellipsis
            response["error"] = error_msg[: (MAX_ERROR_MESSAGE_LENGTH - 3)] + "..."

    return jsonify(response), http_status


@app.route("/api/database/recovery-status", methods=["GET"])
@limiter.exempt
def database_recovery_status():
    """
    Check PostgreSQL database recovery status.
    
    This endpoint provides detailed information about whether the database
    is in recovery mode after an improper shutdown. Useful for:
    - Monitoring dashboards to track database health
    - Debugging slow responses during recovery
    - Understanding WAL replay progress
    
    Returns:
        JSON with recovery status:
        - in_recovery: bool or None (if check failed)
        - status: "normal", "recovering", "startup_or_recovery", "error"
        - message: Human-readable explanation
        - wal_receive_lsn: WAL receive position (if in recovery)
        - wal_replay_lsn: WAL replay position (if in recovery)
    
    Exempt from rate limiting to allow monitoring services to check frequently.
    """
    recovery_status = get_database_recovery_status()
    
    # Determine HTTP status based on recovery state
    if recovery_status.get("status") == "error" or recovery_status.get("status") == "connection_error":
        http_status = 503  # Service unavailable
    elif recovery_status.get("in_recovery"):
        http_status = 200  # OK, but degraded - service is still functional
    else:
        http_status = 200  # Normal operation
    
    return jsonify({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "recovery": recovery_status,
    }), http_status


# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================


@app.route("/api/auth/register", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")  # Allow reasonable registration attempts
@requires_database
def register():
    """Register a new user
    
    Performance optimizations to prevent HTTP 499 timeouts:
    - Uses single database connection for all operations
    - Proper try/finally pattern ensures connection is always returned to pool
    - Uses return_db_connection() for proper pool management
    - Uses RETURNING clause in PostgreSQL to avoid second query
    - Validates all input before acquiring database connection
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None

    try:
        # Handle invalid JSON or empty body
        # silent=True returns None for invalid JSON instead of raising exception
        data = request.get_json(silent=True)
        
        if not data:
            return (
                jsonify(
                    {"success": False, "message": "Invalid request body"}
                ),
                400,
            )

        required_fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "user_type",
            "location",
        ]
        for field in required_fields:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"{field.replace('_', ' ').title()} is required",
                        }
                    ),
                    400,
                )

        email = data["email"].strip().lower()
        password = data["password"]

        # Validate password strength
        if (
            len(password) < 8
            or not any(c.isdigit() for c in password)
            or not any(c.isalpha() for c in password)
        ):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Password must be at least 8 characters with at least one letter and one number",
                    }
                ),
                400,
            )

        # Hash password before acquiring database connection to avoid holding
        # connection during CPU-intensive operation
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Get database connection - use single connection for all operations
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already exists
        if USE_POSTGRESQL:
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = %s", (email,))
        else:
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,))

        if cursor.fetchone():
            return (
                jsonify(
                    {"success": False, "message": "User with this email already exists"}
                ),
                409,
            )

        # Insert new user and get all fields in one query (PostgreSQL)
        # or insert and fetch separately (SQLite)
        now = datetime.now(timezone.utc)
        first_name = data["first_name"].strip()
        last_name = data["last_name"].strip()
        user_type = data["user_type"]
        location = data["location"].strip()
        phone = data.get("phone", "").strip()
        bio = data.get("bio", "").strip()

        if USE_POSTGRESQL:
            # Use RETURNING * to get all user data in a single query
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, first_name, last_name, user_type, location, phone, bio, is_active, created_at, last_login, is_available_for_hire)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s, FALSE)
                RETURNING id, email, first_name, last_name, user_type, location, phone, bio, avatar_url, is_available_for_hire
                """,
                (
                    email,
                    password_hash,
                    first_name,
                    last_name,
                    user_type,
                    location,
                    phone,
                    bio,
                    now,
                    now,
                ),
            )
            user = cursor.fetchone()
            user_id = user["id"]
        else:
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, first_name, last_name, user_type, location, phone, bio, is_active, created_at, last_login, is_available_for_hire)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, 0)
                """,
                (
                    email,
                    password_hash,
                    first_name,
                    last_name,
                    user_type,
                    location,
                    phone,
                    bio,
                    now,
                    now,
                ),
            )
            user_id = cursor.lastrowid
            # Fetch the created user for SQLite
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()

        conn.commit()

        # Create JWT token
        token_payload = {
            "user_id": user["id"],
            "email": user["email"],
            "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRATION_DAYS),
        }

        token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Registration successful",
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "first_name": user["first_name"] or "",
                        "last_name": user["last_name"] or "",
                        "user_type": user["user_type"] or "user",
                        "location": user["location"] or "",
                        "phone": user["phone"] or "",
                        "bio": user["bio"] or "",
                        "avatar_url": user["avatar_url"] or "",
                        "is_available_for_hire": bool(user["is_available_for_hire"]),
                    },
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Registration failed: {str(e)}",
                }
            ),
            500,
        )
    finally:
        # Always clean up database resources
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
@limiter.limit("10 per minute")  # Prevent rapid login attempts that can exhaust connection pool
@requires_database
def login():
    """Login user
    
    Performance optimizations to prevent HTTP 499 timeouts:
    - Rate limited to 10 requests per minute per IP to prevent pool exhaustion
    - Uses connection pool with 5-second timeout to fail fast
    - Pool expanded to 20 max connections for high concurrency
    - Statement timeout of 30 seconds prevents long-running queries
    - Proper connection cleanup with try/finally pattern
    - Returns connections to pool instead of closing to improve reuse
    - All database operations have timeout protection
    - Email lookup uses LOWER(email) index for fast queries
    - Detailed timing logs for performance monitoring
    - Request-level timeout check to return proper response before client disconnects
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    request_id = getattr(g, 'request_id', 'unknown')
    login_start = time.time()
    
    try:
        # Handle invalid JSON or empty body
        # silent=True returns None for invalid JSON instead of raising exception
        data = request.get_json(silent=True)
        
        if not data:
            return (
                jsonify(
                    {"success": False, "message": "Invalid request body"}
                ),
                400,
            )

        if not data.get("email") or not data.get("password"):
            return (
                jsonify(
                    {"success": False, "message": "Email and password are required"}
                ),
                400,
            )

        email = data["email"].strip().lower()
        password = data["password"]

        # Check for request timeout before database operation
        if _check_request_timeout(login_start, LOGIN_REQUEST_TIMEOUT_SECONDS, "login (before db)"):
            return (
                jsonify({
                    "success": False,
                    "message": "Login request timed out. Please try again."
                }),
                504,  # Gateway Timeout
            )

        # Get user from database with connection pool timeout protection
        db_start = time.time()
        conn = get_db_connection()
        
        if conn is None:
            # Connection pool exhausted - return 503 to indicate temporary unavailability
            print(
                f"[{request_id}] ⚠️ Connection pool exhausted for login attempt: {email}"
            )
            return (
                jsonify({
                    "success": False,
                    "message": "Service temporarily unavailable. Please try again in a moment."
                }),
                503,
            )
        
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = %s", (email,))
        else:
            cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,))

        user = cursor.fetchone()
        db_query_ms = int((time.time() - db_start) * 1000)
        
        print(
            f"[{request_id}] Database query (email lookup) completed in {db_query_ms}ms for {email}"
        )

        # Check for request timeout after database query
        if _check_request_timeout(login_start, LOGIN_REQUEST_TIMEOUT_SECONDS, "login (after db query)"):
            return (
                jsonify({
                    "success": False,
                    "message": "Login request timed out. Please try again."
                }),
                504,  # Gateway Timeout
            )

        if not user:
            print(
                f"[{request_id}] Login failed - User not found: {email}"
            )
            return (
                jsonify({"success": False, "message": "Invalid email or password"}),
                401,
            )

        # Check if user has a password (OAuth users may not have one)
        # Using falsy check to handle both None and empty string cases
        if not user["password_hash"]:
            print(
                f"[{request_id}] Login failed - OAuth user attempting password login: {email}"
            )
            return (
                jsonify({
                    "success": False,
                    "message": "This account was created with social login. Please use Google or Apple sign-in."
                }),
                401,
            )

        # Verify password (bcrypt checkpw is CPU-intensive but shouldn't block long)
        password_start = time.time()
        password_valid = bcrypt.checkpw(
            password.encode("utf-8"), user["password_hash"].encode("utf-8")
        )
        password_verify_ms = int((time.time() - password_start) * 1000)
        
        print(
            f"[{request_id}] Password verification completed in {password_verify_ms}ms"
        )

        # Check for request timeout after password verification
        if _check_request_timeout(login_start, LOGIN_REQUEST_TIMEOUT_SECONDS, "login (after password verify)"):
            return (
                jsonify({
                    "success": False,
                    "message": "Login request timed out. Please try again."
                }),
                504,  # Gateway Timeout
            )
        
        if not password_valid:
            print(
                f"[{request_id}] Login failed - Invalid password for user: {email}"
            )
            return (
                jsonify({"success": False, "message": "Invalid email or password"}),
                401,
            )

        # Update last login
        now = datetime.now(timezone.utc)
        if USE_POSTGRESQL:
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE id = %s", (now, user["id"])
            )
        else:
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE id = ?", (now, user["id"])
            )

        conn.commit()

        # Create JWT token
        token_start = time.time()
        token_payload = {
            "user_id": user["id"],
            "email": user["email"],
            "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRATION_DAYS),
        }

        token = jwt.encode(token_payload, app.config["SECRET_KEY"], algorithm="HS256")
        token_create_ms = int((time.time() - token_start) * 1000)
        
        print(
            f"[{request_id}] Token creation completed in {token_create_ms}ms"
        )
        
        # Calculate total login time from start of endpoint (captured by middleware)
        if hasattr(g, 'start_time'):
            total_login_ms = int((time.time() - g.start_time) * 1000)
            
            print(
                f"[{request_id}] Login successful - user: {user['email']}, user_id: {user['id']}, "
                f"user_type: {user['user_type']}, total_time: {total_login_ms}ms "
                f"(db: {db_query_ms}ms, password_verify: {password_verify_ms}ms, "
                f"token_create: {token_create_ms}ms)"
            )
            
            # Warn about slow login operations
            if total_login_ms > 1000:  # Over 1 second
                print(
                    f"[{request_id}] ⚠️ SLOW LOGIN: Total time {total_login_ms}ms - "
                    f"Breakdown: DB={db_query_ms}ms, Password={password_verify_ms}ms, "
                    f"Token={token_create_ms}ms. Consider checking connection pool, "
                    f"database performance, or bcrypt configuration."
                )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login successful",
                    "access_token": token,
                    "token_type": "bearer",
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "first_name": user["first_name"] or "",
                        "last_name": user["last_name"] or "",
                        "user_type": user["user_type"] or "user",
                        "location": user["location"] or "",
                        "phone": user["phone"] or "",
                        "bio": user["bio"] or "",
                        "avatar_url": user["avatar_url"] or "",
                        "is_available_for_hire": bool(user["is_available_for_hire"]),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        print(f"[{request_id}] Login error: {type(e).__name__}: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Login failed: {str(e)}"}),
            500,
        )
    finally:
        # Always cleanup database resources to prevent connection leaks
        # This ensures connections are returned to pool even if exceptions occur
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/auth/refresh", methods=["POST", "OPTIONS"])
def refresh_token():
    """Refresh authentication token"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        token = auth_header.split(" ")[1]

        # Decode token to get user info
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return (
                jsonify({"success": False, "message": "Token has expired"}),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify({"success": False, "message": "Invalid token"}),
                401,
            )

        # Get user from database
        conn = get_db_connection()
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return (
                jsonify({"success": False, "message": "User not found"}),
                404,
            )

        # Create new JWT token with extended expiration
        new_token_payload = {
            "user_id": user["id"],
            "email": user["email"],
            "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRATION_DAYS),
        }

        new_token = jwt.encode(
            new_token_payload, app.config["SECRET_KEY"], algorithm="HS256"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Token refreshed successfully",
                    "access_token": new_token,
                    "token_type": "bearer",
                    "user": {
                        "id": user["id"],
                        "email": user["email"],
                        "first_name": user["first_name"] or "",
                        "last_name": user["last_name"] or "",
                        "user_type": user["user_type"] or "user",
                        "location": user["location"] or "",
                        "phone": user["phone"] or "",
                        "bio": user["bio"] or "",
                        "avatar_url": user["avatar_url"] or "",
                        "is_available_for_hire": bool(user["is_available_for_hire"]),
                    },
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Token refresh error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Token refresh failed: {str(e)}"}),
            500,
        )


@app.route("/api/auth/verify", methods=["GET", "OPTIONS"])
def verify_session():
    """Verify if the current session is valid"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        token = auth_header.split(" ")[1]

        # Decode token to verify validity
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")

            # Check if user exists
            conn = get_db_connection()
            cursor = conn.cursor()

            if USE_POSTGRESQL:
                cursor.execute("SELECT id, email FROM users WHERE id = %s", (user_id,))
            else:
                cursor.execute("SELECT id, email FROM users WHERE id = ?", (user_id,))

            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if not user:
                return (
                    jsonify({"success": False, "message": "User not found"}),
                    404,
                )

            return (
                jsonify(
                    {
                        "success": True,
                        "valid": True,
                        "message": "Session is valid",
                        "user_id": user["id"],
                        "email": user["email"],
                    }
                ),
                200,
            )

        except jwt.ExpiredSignatureError:
            return (
                jsonify(
                    {"success": False, "valid": False, "message": "Token has expired"}
                ),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify({"success": False, "valid": False, "message": "Invalid token"}),
                401,
            )

    except Exception as e:
        print(f"Session verification error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Verification failed: {str(e)}"}),
            500,
        )


@app.route("/api/auth/profile", methods=["GET", "OPTIONS"])
def get_profile():
    """Get user profile"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        token = auth_header.split(" ")[1]

        # Decode token
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return (
                jsonify({"success": False, "message": "Token has expired"}),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify({"success": False, "message": "Invalid token"}),
                401,
            )

        # Get user from database
        conn = get_db_connection()
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return (
                jsonify({"success": False, "message": "User not found"}),
                404,
            )

        return (
            jsonify(
                {
                    "id": user["id"],
                    "email": user["email"],
                    "first_name": user["first_name"] or "",
                    "last_name": user["last_name"] or "",
                    "user_type": user["user_type"] or "user",
                    "location": user["location"] or "",
                    "phone": user["phone"] or "",
                    "bio": user["bio"] or "",
                    "avatar_url": user["avatar_url"] or "",
                    "is_available_for_hire": bool(user["is_available_for_hire"]),
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Profile fetch error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Profile fetch failed: {str(e)}"}),
            500,
        )


# ==========================================
# POSTS ENDPOINTS
# ==========================================


@app.route("/api/posts", methods=["GET", "OPTIONS"])
def get_posts():
    """
    Get posts with user information
    
    Posts are PERMANENTLY stored - never automatically deleted.
    Supports pagination for handling millions of posts efficiently.
    
    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Posts per page (default: 20, max: 100)
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        if per_page > 100:
            per_page = 100  # Max 100 posts per page
        
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM posts")
        total_posts = cursor.fetchone()["total"]

        # Get paginated posts with user information
        if USE_POSTGRESQL:
            # PostgreSQL requires all non-aggregate columns in GROUP BY
            cursor.execute(
                """
                SELECT 
                    p.id, p.content, p.image_url, p.video_url, p.created_at,
                    u.id as user_id, u.email, u.first_name, u.last_name, u.avatar_url,
                    u.username, u.occupation, u.company_name,
                    COUNT(DISTINCT l.id) as likes_count,
                    COUNT(DISTINCT c.id) as comments_count
                FROM posts p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN likes l ON p.id = l.post_id
                LEFT JOIN comments c ON p.id = c.post_id
                GROUP BY p.id, p.content, p.image_url, p.video_url, p.created_at, 
                         u.id, u.email, u.first_name, u.last_name, u.avatar_url,
                         u.username, u.occupation, u.company_name
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """,
                (per_page, offset)
            )
        else:
            # SQLite allows grouping by primary key only (functionally dependent columns)
            cursor.execute(
                """
                SELECT 
                    p.id, p.content, p.image_url, p.video_url, p.created_at,
                    u.id as user_id, u.email, u.first_name, u.last_name, u.avatar_url,
                    u.username, u.occupation, u.company_name,
                    COUNT(DISTINCT l.id) as likes_count,
                    COUNT(DISTINCT c.id) as comments_count
                FROM posts p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN likes l ON p.id = l.post_id
                LEFT JOIN comments c ON p.id = c.post_id
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            """,
                (per_page, offset)
            )

        posts_data = cursor.fetchall()
        cursor.close()
        conn.close()

        # Format posts for response
        posts = []
        for post in posts_data:
            posts.append(
                {
                    "id": post["id"],
                    "content": post["content"],
                    "image_url": post["image_url"],
                    "video_url": post["video_url"],
                    "created_at": post["created_at"],
                    "likes_count": post["likes_count"],
                    "comments_count": post["comments_count"],
                    "user": {
                        "id": post["user_id"],
                        "email": post["email"],
                        "first_name": post["first_name"] or "",
                        "last_name": post["last_name"] or "",
                        "avatar_url": post["avatar_url"] or "",
                        "username": post["username"],
                        "occupation": post["occupation"],
                        "company_name": post["company_name"],
                    },
                }
            )
        
        # Calculate pagination info
        total_pages = (total_posts + per_page - 1) // per_page  # Ceiling division

        return jsonify({
            "success": True, 
            "posts": posts,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_posts": total_posts,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }), 200

    except Exception as e:
        print(f"Get posts error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Failed to fetch posts: {str(e)}"}),
            500,
        )


@app.route("/api/posts", methods=["POST"])
def create_post():
    """Create a new post"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        parts = auth_header.split(" ")
        if len(parts) != 2:
            return (
                jsonify({"success": False, "message": "Invalid authorization header format"}),
                401,
            )
        
        token = parts[1]

        # Decode token to get user_id
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return (
                jsonify({"success": False, "message": "Token has expired"}),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify({"success": False, "message": "Invalid token"}),
                401,
            )

        # Get post data
        data = request.get_json()
        content = data.get("content", "").strip()
        image_url = data.get("image_url", "")
        video_url = data.get("video_url", "")

        if not content:
            return (
                jsonify({"success": False, "message": "Post content is required"}),
                400,
            )

        # Create post in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify user exists before creating post
        if USE_POSTGRESQL:
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return (
                jsonify({"success": False, "message": "User not found. Please log in again."}),
                401,
            )

        if USE_POSTGRESQL:
            cursor.execute(
                """
                INSERT INTO posts (user_id, content, image_url, video_url, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
            """,
                (user_id, content, image_url, video_url, datetime.now(timezone.utc)),
            )
        else:
            cursor.execute(
                """
                INSERT INTO posts (user_id, content, image_url, video_url, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (user_id, content, image_url, video_url, datetime.now(timezone.utc)),
            )

        if USE_POSTGRESQL:
            result = cursor.fetchone()
            post_id = result["id"]
            created_at = result["created_at"]
        else:
            post_id = cursor.lastrowid
            created_at = datetime.now(timezone.utc)

        # Get user information for response
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT id, email, first_name, last_name, avatar_url FROM users WHERE id = %s",
                (user_id,),
            )
        else:
            cursor.execute(
                "SELECT id, email, first_name, last_name, avatar_url FROM users WHERE id = ?",
                (user_id,),
            )

        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Post created successfully",
                    "post": {
                        "id": post_id,
                        "content": content,
                        "image_url": image_url,
                        "video_url": video_url,
                        "created_at": created_at,
                        "likes_count": 0,
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "first_name": user["first_name"] or "",
                            "last_name": user["last_name"] or "",
                            "avatar_url": user["avatar_url"] or "",
                        },
                    },
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Create post error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Failed to create post: {str(e)}"}),
            500,
        )


@app.route("/api/posts/<int:post_id>/like", methods=["POST", "OPTIONS"])
def like_post(post_id):
    """Like or unlike a post"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        parts = auth_header.split(" ")
        if len(parts) != 2:
            return (
                jsonify({"success": False, "message": "Invalid authorization header format"}),
                401,
            )
        
        token = parts[1]

        # Decode token to get user_id
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return (
                jsonify({"success": False, "message": "Token has expired"}),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify({"success": False, "message": "Invalid token"}),
                401,
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already liked the post
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT id FROM likes WHERE post_id = %s AND user_id = %s",
                (post_id, user_id),
            )
        else:
            cursor.execute(
                "SELECT id FROM likes WHERE post_id = ? AND user_id = ?",
                (post_id, user_id),
            )

        existing_like = cursor.fetchone()

        if existing_like:
            # Unlike - remove the like
            if USE_POSTGRESQL:
                cursor.execute(
                    "DELETE FROM likes WHERE post_id = %s AND user_id = %s",
                    (post_id, user_id),
                )
            else:
                cursor.execute(
                    "DELETE FROM likes WHERE post_id = ? AND user_id = ?",
                    (post_id, user_id),
                )
            message = "Post unliked"
            liked = False
        else:
            # Like - add a new like
            if USE_POSTGRESQL:
                cursor.execute(
                    "INSERT INTO likes (post_id, user_id, created_at) VALUES (%s, %s, %s)",
                    (post_id, user_id, datetime.now(timezone.utc)),
                )
            else:
                cursor.execute(
                    "INSERT INTO likes (post_id, user_id, created_at) VALUES (?, ?, ?)",
                    (post_id, user_id, datetime.now(timezone.utc)),
                )
            message = "Post liked"
            liked = True

        # Get updated likes count
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT COUNT(*) as count FROM likes WHERE post_id = %s", (post_id,)
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) as count FROM likes WHERE post_id = ?", (post_id,)
            )

        likes_count = cursor.fetchone()["count"]

        conn.commit()
        cursor.close()
        conn.close()

        return (
            jsonify(
                {
                    "success": True,
                    "message": message,
                    "liked": liked,
                    "likes_count": likes_count,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Like post error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Failed to like post: {str(e)}"}),
            500,
        )


@app.route("/api/posts/<int:post_id>", methods=["DELETE", "OPTIONS"])
def delete_post(post_id):
    """
    Delete a post - MANUAL DELETION ONLY
    
    Posts are permanently stored and should NEVER be automatically deleted.
    This endpoint only allows:
    1. User to manually delete their own posts
    2. No automatic deletion based on age, pagination, or number of posts
    
    Even with millions of posts, they remain in database.
    Use pagination on GET /api/posts to handle large datasets.
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "No token provided"}),
                401,
            )

        parts = auth_header.split(" ")
        if len(parts) != 2:
            return (
                jsonify({"success": False, "message": "Invalid authorization header format"}),
                401,
            )
        
        token = parts[1]

        # Decode token to get user_id
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return (
                jsonify({"success": False, "message": "Token has expired"}),
                401,
            )
        except jwt.InvalidTokenError:
            return (
                jsonify({"success": False, "message": "Invalid token"}),
                401,
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if post exists and belongs to user
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT user_id FROM posts WHERE id = %s", (post_id,)
            )
        else:
            cursor.execute(
                "SELECT user_id FROM posts WHERE id = ?", (post_id,)
            )

        post = cursor.fetchone()

        if not post:
            cursor.close()
            conn.close()
            return (
                jsonify({"success": False, "message": "Post not found"}),
                404,
            )

        if post["user_id"] != user_id:
            cursor.close()
            conn.close()
            return (
                jsonify(
                    {"success": False, "message": "You can only delete your own posts"}
                ),
                403,
            )

        # Delete the post (likes and comments will be cascade deleted)
        if USE_POSTGRESQL:
            cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        else:
            cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return (
            jsonify({"success": True, "message": "Post deleted successfully"}),
            200,
        )

    except Exception as e:
        print(f"Delete post error: {str(e)}")
        return (
            jsonify({"success": False, "message": f"Failed to delete post: {str(e)}"}),
            500,
        )


# ==========================================
# USER ENDPOINTS
# ==========================================

@app.route("/api/users/<int:user_id>", methods=["GET", "OPTIONS"])
def get_user(user_id):
    """
    Get a specific user's profile by ID
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user details
        cursor.execute(
            """
            SELECT id, email, first_name, last_name, username, avatar_url, bio,
                   occupation, company_name, location, phone, user_type, 
                   is_available_for_hire, created_at
            FROM users
            WHERE id = %s AND is_active = TRUE
            """ if USE_POSTGRESQL else """
            SELECT id, email, first_name, last_name, username, avatar_url, bio,
                   occupation, company_name, location, phone, user_type, 
                   is_available_for_hire, created_at
            FROM users
            WHERE id = ? AND is_active = 1
            """,
            (user_id,)
        )
        
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "User not found"}), 404

        # Check if current user follows this user
        cursor.execute(
            """
            SELECT id FROM follows
            WHERE follower_id = %s AND followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT id FROM follows
            WHERE follower_id = ? AND followed_id = ?
            """,
            (current_user_id, user_id)
        )
        is_following = cursor.fetchone() is not None

        # Get follower count
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM follows
            WHERE followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT COUNT(*) as count FROM follows
            WHERE followed_id = ?
            """,
            (user_id,)
        )
        followers_count = cursor.fetchone()["count"]

        # Get following count
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM follows
            WHERE follower_id = %s
            """ if USE_POSTGRESQL else """
            SELECT COUNT(*) as count FROM follows
            WHERE follower_id = ?
            """,
            (user_id,)
        )
        following_count = cursor.fetchone()["count"]

        # Get posts count
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM posts
            WHERE user_id = %s
            """ if USE_POSTGRESQL else """
            SELECT COUNT(*) as count FROM posts
            WHERE user_id = ?
            """,
            (user_id,)
        )
        posts_count = cursor.fetchone()["count"]

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "username": user["username"],
                "avatar_url": user["avatar_url"],
                "bio": user["bio"],
                "occupation": user["occupation"],
                "company_name": user["company_name"],
                "location": user["location"],
                "phone": user["phone"],
                "user_type": user["user_type"] or "user",
                "is_available_for_hire": user["is_available_for_hire"] or False,
                "created_at": user["created_at"],
                "posts_count": posts_count,
                "is_following": is_following,
                "followers_count": followers_count,
                "following_count": following_count,
            }
        }), 200

    except Exception as e:
        print(f"Get user error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch user: {str(e)}"}), 500


@app.route("/api/users/list", methods=["GET", "OPTIONS"])
def get_users_list():
    """
    Get list of users with optional search
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        # Get search parameter and sanitize it
        search = request.args.get("search", "").strip()
        
        # Validate search input (max 100 chars, no SQL special chars that aren't escaped by parameterization)
        if search and len(search) > 100:
            return jsonify({"success": False, "message": "Search query too long"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query based on search
        if search:
            # Escape wildcards in search pattern to prevent injection
            # The % and _ are already safely parameterized, but we sanitize for clarity
            search_pattern = f"%{search}%"
            cursor.execute(
                """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, location
                FROM users
                WHERE is_active = TRUE AND id != %s
                AND (first_name ILIKE %s OR last_name ILIKE %s OR email ILIKE %s 
                     OR occupation ILIKE %s OR location ILIKE %s)
                LIMIT 50
                """ if USE_POSTGRESQL else """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, location
                FROM users
                WHERE is_active = 1 AND id != ?
                AND (first_name LIKE ? OR last_name LIKE ? OR email LIKE ? 
                     OR occupation LIKE ? OR location LIKE ?)
                LIMIT 50
                """,
                (current_user_id, search_pattern, search_pattern, search_pattern, 
                 search_pattern, search_pattern)
            )
        else:
            cursor.execute(
                """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, location
                FROM users
                WHERE is_active = TRUE AND id != %s
                LIMIT 50
                """ if USE_POSTGRESQL else """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, location
                FROM users
                WHERE is_active = 1 AND id != ?
                LIMIT 50
                """,
                (current_user_id,)
            )

        users = cursor.fetchall()

        # Get follow status for each user (batch query)
        user_ids = [u["id"] for u in users]
        following_ids = set()
        
        if user_ids:
            placeholders = ",".join(["%s" if USE_POSTGRESQL else "?" for _ in user_ids])
            cursor.execute(
                """
                SELECT followed_id FROM follows
                WHERE follower_id = %s AND followed_id IN ({})
                """.format(placeholders) if USE_POSTGRESQL else """
                SELECT followed_id FROM follows
                WHERE follower_id = ? AND followed_id IN ({})
                """.format(placeholders),
                [current_user_id] + user_ids
            )
            following_ids = {row["followed_id"] for row in cursor.fetchall()}
            
            # Get follower counts for all users in one query
            cursor.execute(
                """
                SELECT followed_id, COUNT(*) as count
                FROM follows
                WHERE followed_id IN ({})
                GROUP BY followed_id
                """.format(placeholders) if USE_POSTGRESQL else """
                SELECT followed_id, COUNT(*) as count
                FROM follows
                WHERE followed_id IN ({})
                GROUP BY followed_id
                """.format(placeholders),
                user_ids
            )
            followers_counts = {row["followed_id"]: row["count"] for row in cursor.fetchall()}
            
            # Get following counts for all users in one query
            cursor.execute(
                """
                SELECT follower_id, COUNT(*) as count
                FROM follows
                WHERE follower_id IN ({})
                GROUP BY follower_id
                """.format(placeholders) if USE_POSTGRESQL else """
                SELECT follower_id, COUNT(*) as count
                FROM follows
                WHERE follower_id IN ({})
                GROUP BY follower_id
                """.format(placeholders),
                user_ids
            )
            following_counts = {row["follower_id"]: row["count"] for row in cursor.fetchall()}
        else:
            followers_counts = {}
            following_counts = {}

        # Build user list with follow status and counts
        users_data = []
        for user in users:
            followers_count = followers_counts.get(user["id"], 0)
            following_count = following_counts.get(user["id"], 0)

            users_data.append({
                "id": user["id"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "email": user["email"],
                "username": user["username"],
                "avatar_url": user["avatar_url"],
                "bio": user["bio"],
                "occupation": user["occupation"],
                "location": user["location"],
                "is_following": user["id"] in following_ids,
                "followers_count": followers_count,
                "following_count": following_count,
            })

        cursor.close()
        conn.close()

        return jsonify({"success": True, "users": users_data, "total": len(users_data)}), 200

    except Exception as e:
        print(f"Get users list error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch users: {str(e)}"}), 500


@app.route("/api/users/follow/<int:user_id>", methods=["POST", "OPTIONS"])
def follow_user(user_id):
    """
    Follow a user
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        if current_user_id == user_id:
            return jsonify({"success": False, "message": "Cannot follow yourself"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute(
            """
            SELECT id FROM users WHERE id = %s
            """ if USE_POSTGRESQL else """
            SELECT id FROM users WHERE id = ?
            """,
            (user_id,)
        )
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "User not found"}), 404

        # Check if already following
        cursor.execute(
            """
            SELECT id FROM follows
            WHERE follower_id = %s AND followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT id FROM follows
            WHERE follower_id = ? AND followed_id = ?
            """,
            (current_user_id, user_id)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Already following this user"}), 400

        # Create follow relationship
        cursor.execute(
            """
            INSERT INTO follows (follower_id, followed_id)
            VALUES (%s, %s)
            """ if USE_POSTGRESQL else """
            INSERT INTO follows (follower_id, followed_id)
            VALUES (?, ?)
            """,
            (current_user_id, user_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "User followed successfully"}), 200

    except Exception as e:
        print(f"Follow user error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to follow user: {str(e)}"}), 500


@app.route("/api/users/unfollow/<int:user_id>", methods=["POST", "OPTIONS"])
def unfollow_user(user_id):
    """
    Unfollow a user
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if following
        cursor.execute(
            """
            SELECT id FROM follows
            WHERE follower_id = %s AND followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT id FROM follows
            WHERE follower_id = ? AND followed_id = ?
            """,
            (current_user_id, user_id)
        )
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Not following this user"}), 400

        # Delete follow relationship
        cursor.execute(
            """
            DELETE FROM follows
            WHERE follower_id = %s AND followed_id = %s
            """ if USE_POSTGRESQL else """
            DELETE FROM follows
            WHERE follower_id = ? AND followed_id = ?
            """,
            (current_user_id, user_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "User unfollowed successfully"}), 200

    except Exception as e:
        print(f"Unfollow user error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to unfollow user: {str(e)}"}), 500


@app.route("/api/users/following/list", methods=["GET", "OPTIONS"])
def get_following_list():
    """
    Get list of users that current user is following
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get users that current user is following
        cursor.execute(
            """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.followed_id
            WHERE f.follower_id = %s
            """ if USE_POSTGRESQL else """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.followed_id
            WHERE f.follower_id = ?
            """,
            (current_user_id,)
        )

        following_users = cursor.fetchall()
        
        following_data = [
            {
                "id": user["id"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "email": user["email"],
                "username": user["username"],
                "avatar_url": user["avatar_url"],
                "bio": user["bio"],
                "occupation": user["occupation"],
                "location": user["location"],
            }
            for user in following_users
        ]

        cursor.close()
        conn.close()

        return jsonify({"success": True, "following": following_data}), 200

    except Exception as e:
        print(f"Get following list error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch following list: {str(e)}"}), 500


@app.route("/api/users/followers/list", methods=["GET", "OPTIONS"])
def get_followers_list():
    """
    Get list of users that follow current user
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get users that follow current user
        cursor.execute(
            """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.follower_id
            WHERE f.followed_id = %s
            """ if USE_POSTGRESQL else """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.follower_id
            WHERE f.followed_id = ?
            """,
            (current_user_id,)
        )

        followers = cursor.fetchall()
        
        followers_data = [
            {
                "id": user["id"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "email": user["email"],
                "username": user["username"],
                "avatar_url": user["avatar_url"],
                "bio": user["bio"],
                "occupation": user["occupation"],
                "location": user["location"],
            }
            for user in followers
        ]

        cursor.close()
        conn.close()

        return jsonify({"success": True, "followers": followers_data}), 200

    except Exception as e:
        print(f"Get followers list error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch followers list: {str(e)}"}), 500


# ==========================================
# JOBS ENDPOINTS
# ==========================================


@app.route("/api/jobs", methods=["GET", "OPTIONS"])
def get_jobs():
    """
    Get all active jobs with optional filtering
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get query parameters
        search = request.args.get("search", "").strip()
        category = request.args.get("category", "").strip()
        location = request.args.get("location", "").strip()
        
        # Build query
        if USE_POSTGRESQL:
            base_query = """
                SELECT j.id, j.title, j.company, j.location, j.description, 
                       j.requirements, j.salary_range, j.job_type, j.category,
                       j.created_at, j.expires_at, j.is_active,
                       u.id as employer_id, u.first_name, u.last_name, 
                       u.email, u.avatar_url, u.company_name
                FROM jobs j
                JOIN users u ON j.user_id = u.id
                WHERE j.is_active = TRUE
            """
            params = []
            
            if search:
                base_query += " AND (j.title ILIKE %s OR j.description ILIKE %s OR j.company ILIKE %s)"
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            if category:
                base_query += " AND j.category ILIKE %s"
                params.append(f"%{category}%")
            
            if location:
                base_query += " AND j.location ILIKE %s"
                params.append(f"%{location}%")
            
            base_query += " ORDER BY j.created_at DESC LIMIT 100"
            
            if params:
                cursor.execute(base_query, params)
            else:
                cursor.execute(base_query)
        else:
            base_query = """
                SELECT j.id, j.title, j.company, j.location, j.description, 
                       j.requirements, j.salary_range, j.job_type, j.category,
                       j.created_at, j.expires_at, j.is_active,
                       u.id as employer_id, u.first_name, u.last_name, 
                       u.email, u.avatar_url, u.company_name
                FROM jobs j
                JOIN users u ON j.user_id = u.id
                WHERE j.is_active = 1
            """
            params = []
            
            if search:
                base_query += " AND (j.title LIKE ? OR j.description LIKE ? OR j.company LIKE ?)"
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            if category:
                base_query += " AND j.category LIKE ?"
                params.append(f"%{category}%")
            
            if location:
                base_query += " AND j.location LIKE ?"
                params.append(f"%{location}%")
            
            base_query += " ORDER BY j.created_at DESC LIMIT 100"
            
            if params:
                cursor.execute(base_query, params)
            else:
                cursor.execute(base_query)

        jobs_data = cursor.fetchall()
        cursor.close()
        conn.close()

        # Format jobs for response
        jobs = []
        for job in jobs_data:
            jobs.append({
                "id": job["id"],
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "description": job["description"],
                "requirements": job["requirements"],
                "salary_range": job["salary_range"],
                "job_type": job["job_type"],
                "category": job["category"],
                "created_at": job["created_at"],
                "expires_at": job["expires_at"],
                "is_active": job["is_active"],
                "employer": {
                    "id": job["employer_id"],
                    "first_name": job["first_name"] or "",
                    "last_name": job["last_name"] or "",
                    "email": job["email"],
                    "avatar_url": job["avatar_url"],
                    "company_name": job["company_name"],
                },
            })

        return jsonify({"success": True, "jobs": jobs, "total": len(jobs)}), 200

    except Exception as e:
        print(f"Get jobs error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch jobs: {str(e)}"}), 500


@app.route("/api/jobs/stats/overview", methods=["GET", "OPTIONS"])
def get_job_stats():
    """
    Get job statistics overview
    Returns counts of active jobs, companies hiring, and new jobs this week
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get total active jobs count
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT COUNT(*) as count FROM jobs WHERE is_active = TRUE"
            )
        else:
            cursor.execute(
                "SELECT COUNT(*) as count FROM jobs WHERE is_active = 1"
            )
        active_jobs = cursor.fetchone()["count"]

        # Get unique companies/employers count
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) as count FROM jobs WHERE is_active = TRUE"
            )
        else:
            cursor.execute(
                "SELECT COUNT(DISTINCT user_id) as count FROM jobs WHERE is_active = 1"
            )
        companies_count = cursor.fetchone()["count"]

        # Get jobs created in the last 7 days
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT COUNT(*) as count FROM jobs 
                WHERE is_active = TRUE 
                AND created_at >= NOW() - INTERVAL '7 days'
                """
            )
        else:
            cursor.execute(
                """
                SELECT COUNT(*) as count FROM jobs 
                WHERE is_active = 1 
                AND created_at >= datetime('now', '-7 days')
                """
            )
        new_this_week = cursor.fetchone()["count"]

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "stats": {
                "active_jobs": active_jobs,
                "companies_hiring": companies_count,
                "new_this_week": new_this_week,
            },
        }), 200

    except Exception as e:
        print(f"Get job stats error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to fetch job stats: {str(e)}",
            "stats": {
                "active_jobs": 0,
                "companies_hiring": 0,
                "new_this_week": 0,
            },
        }), 500


@app.route("/api/jobs/<int:job_id>", methods=["GET", "OPTIONS"])
def get_job(job_id):
    """
    Get a specific job by ID
    """
    if request.method == "OPTIONS":
        return "", 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT j.id, j.title, j.company, j.location, j.description, 
                       j.requirements, j.salary_range, j.job_type, j.category,
                       j.created_at, j.expires_at, j.is_active,
                       u.id as employer_id, u.first_name, u.last_name, 
                       u.email, u.avatar_url, u.company_name
                FROM jobs j
                JOIN users u ON j.user_id = u.id
                WHERE j.id = %s
                """,
                (job_id,)
            )
        else:
            cursor.execute(
                """
                SELECT j.id, j.title, j.company, j.location, j.description, 
                       j.requirements, j.salary_range, j.job_type, j.category,
                       j.created_at, j.expires_at, j.is_active,
                       u.id as employer_id, u.first_name, u.last_name, 
                       u.email, u.avatar_url, u.company_name
                FROM jobs j
                JOIN users u ON j.user_id = u.id
                WHERE j.id = ?
                """,
                (job_id,)
            )

        job = cursor.fetchone()
        cursor.close()
        conn.close()

        if not job:
            return jsonify({"success": False, "message": "Job not found"}), 404

        return jsonify({
            "success": True,
            "job": {
                "id": job["id"],
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "description": job["description"],
                "requirements": job["requirements"],
                "salary_range": job["salary_range"],
                "job_type": job["job_type"],
                "category": job["category"],
                "created_at": job["created_at"],
                "expires_at": job["expires_at"],
                "is_active": job["is_active"],
                "employer": {
                    "id": job["employer_id"],
                    "first_name": job["first_name"] or "",
                    "last_name": job["last_name"] or "",
                    "email": job["email"],
                    "avatar_url": job["avatar_url"],
                    "company_name": job["company_name"],
                },
            }
        }), 200

    except Exception as e:
        print(f"Get job error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch job: {str(e)}"}), 500


@app.route("/api/jobs", methods=["POST"])
def create_job():
    """
    Create a new job posting
    """
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "No token provided"}), 401

        parts = auth_header.split(" ")
        if len(parts) != 2:
            return jsonify({"success": False, "message": "Invalid authorization header format"}), 401

        token = parts[1]

        # Decode token to get user_id
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        # Get job data
        data = request.get_json()
        
        required_fields = ["title", "company", "location", "description"]
        for field in required_fields:
            if not data.get(field, "").strip():
                return jsonify({
                    "success": False,
                    "message": f"{field.replace('_', ' ').title()} is required"
                }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify user exists
        if USE_POSTGRESQL:
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "User not found. Please log in again."}), 401

        # Insert job
        now = datetime.now(timezone.utc)
        
        if USE_POSTGRESQL:
            cursor.execute(
                """
                INSERT INTO jobs (user_id, title, company, location, description, 
                                  requirements, salary_range, job_type, category, 
                                  created_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING id
                """,
                (
                    user_id,
                    data["title"].strip(),
                    data["company"].strip(),
                    data["location"].strip(),
                    data["description"].strip(),
                    data.get("requirements", "").strip(),
                    data.get("salary_range", "").strip(),
                    data.get("job_type", "full-time").strip(),
                    data.get("category", "").strip(),
                    now,
                )
            )
            job_id = cursor.fetchone()["id"]
        else:
            cursor.execute(
                """
                INSERT INTO jobs (user_id, title, company, location, description, 
                                  requirements, salary_range, job_type, category, 
                                  created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    user_id,
                    data["title"].strip(),
                    data["company"].strip(),
                    data["location"].strip(),
                    data["description"].strip(),
                    data.get("requirements", "").strip(),
                    data.get("salary_range", "").strip(),
                    data.get("job_type", "full-time").strip(),
                    data.get("category", "").strip(),
                    now,
                )
            )
            job_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Job created successfully",
            "job": {
                "id": job_id,
                "title": data["title"].strip(),
                "company": data["company"].strip(),
                "location": data["location"].strip(),
                "created_at": now.isoformat(),
            }
        }), 201

    except Exception as e:
        print(f"Create job error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to create job: {str(e)}"}), 500


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

# Export application for gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting HireMeBahamas backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
