import atexit
import json
import logging
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
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from urllib.parse import urlparse, parse_qs, unquote

import bcrypt
import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, g
from flask_caching import Cache
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Track application startup time for cold start monitoring
# This helps diagnose HTTP 502 errors that occur when container cold starts take too long
_APP_START_TIME = time.time()
_APP_IMPORT_COMPLETE_TIME = None  # Set after all imports complete

# Load environment variables from .env file
load_dotenv()

# Configure logging for database connection management
# Using a named logger allows filtering and configuration at the application level
# NullHandler is the recommended way to configure logging for library code
# It allows the application to configure logging appropriately without this module
# interfering with application-level logging configuration
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


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

# Caching configuration with Redis support (falls back to simple cache if Redis unavailable)
# Redis provides distributed caching for production deployments with multiple workers
# Set REDIS_URL environment variable to enable Redis caching
REDIS_URL = os.getenv("REDIS_URL")
CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))  # 5 minutes default

# Cache timeout configuration for different resource types
CACHE_TIMEOUT_JOBS = int(os.getenv("CACHE_TIMEOUT_JOBS", "60"))  # Jobs list: 1 minute
CACHE_TIMEOUT_POSTS = int(os.getenv("CACHE_TIMEOUT_POSTS", "30"))  # Posts list: 30 seconds (more dynamic)
CACHE_TIMEOUT_USERS = int(os.getenv("CACHE_TIMEOUT_USERS", "120"))  # Users list: 2 minutes
CACHE_TIMEOUT_PROFILE = int(os.getenv("CACHE_TIMEOUT_PROFILE", "60"))  # User profile: 1 minute

# Login user cache timeout in seconds (10 minutes = 600 seconds)
# Caches user data on successful login to skip database query on subsequent logins
# This reduces login time from ~5000ms to <100ms for cached users
CACHE_TIMEOUT_LOGIN_USER = int(os.getenv("CACHE_TIMEOUT_LOGIN_USER", "600"))

# Redis client for cache invalidation (reused across calls)
_redis_client = None
_redis_available = None  # None = not checked, True/False = result


def _get_redis_client():
    """
    Get or create a Redis client for cache operations.
    
    Returns the cached Redis client if available, or creates a new one.
    Returns None if Redis is not configured or unavailable.
    """
    global _redis_client, _redis_available
    
    if not REDIS_URL:
        return None
    
    # If we've already determined Redis is unavailable, don't retry
    if _redis_available is False:
        return None
    
    # Return cached client if available and connected
    if _redis_client is not None:
        try:
            _redis_client.ping()
            return _redis_client
        except Exception:
            # Connection lost, try to reconnect
            _redis_client = None
    
    # Try to create a new connection
    try:
        import redis
        _redis_client = redis.from_url(REDIS_URL, socket_timeout=2)
        _redis_client.ping()
        _redis_available = True
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        _redis_available = False
        _redis_client = None
        return None


def _get_cache_config():
    """
    Get cache configuration with Redis support and fallback to simple cache.
    
    Redis is preferred for production as it provides:
    - Distributed caching across multiple workers/containers
    - Persistence across container restarts
    - Better memory management with eviction policies
    
    Falls back to simple in-memory cache if Redis is unavailable.
    """
    if REDIS_URL:
        # Use the shared Redis client getter to test connection
        client = _get_redis_client()
        if client is not None:
            print("✅ Redis cache connected")
            return {
                "CACHE_TYPE": "redis",
                "CACHE_REDIS_URL": REDIS_URL,
                "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
                "CACHE_KEY_PREFIX": "hiremebahamas:",
            }
        else:
            print("⚠️ Redis unavailable, falling back to simple cache")
    
    print("📦 Using simple in-memory cache")
    return {
        "CACHE_TYPE": "simple",
        "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
    }

cache = Cache(app, config=_get_cache_config())


def invalidate_cache_pattern(pattern: str):
    """
    Invalidate cache entries matching a pattern.
    
    For Redis: Uses SCAN to find and delete matching keys.
    For simple cache: Clears entire cache (simple cache doesn't support pattern deletion).
    
    Args:
        pattern: Cache key pattern (e.g., "jobs:*", "posts:*")
    """
    try:
        cache_type = cache.config.get("CACHE_TYPE", "simple")
        if cache_type == "redis":
            # Use the shared Redis client for cache operations
            client = _get_redis_client()
            if client is not None:
                try:
                    prefix = cache.config.get("CACHE_KEY_PREFIX", "")
                    full_pattern = f"{prefix}{pattern}"
                    cursor = 0
                    deleted_count = 0
                    while True:
                        cursor, keys = client.scan(cursor, match=full_pattern, count=100)
                        if keys:
                            client.delete(*keys)
                            deleted_count += len(keys)
                        if cursor == 0:
                            break
                    if deleted_count > 0:
                        logger.info(f"Invalidated {deleted_count} cache keys matching '{pattern}'")
                except Exception as redis_error:
                    # Fall back to simple cache clear if Redis operation fails
                    logger.warning(f"Redis cache invalidation failed, clearing all cache: {redis_error}")
                    cache.clear()
            else:
                # Redis client unavailable, clear all
                cache.clear()
        else:
            # Simple cache - clear all (no pattern support)
            cache.clear()
            logger.info(f"Cleared simple cache (pattern: {pattern})")
    except Exception as e:
        logger.warning(f"Cache invalidation failed for pattern '{pattern}': {e}")


def make_user_cache_key(identifier: str = None) -> str:
    """
    Generate a cache key for user profile endpoints.
    
    The key includes:
    - The user identifier (ID or username) from the URL
    - Current user ID from the JWT token (for personalized data like is_following)
    
    Args:
        identifier: User ID (as string) or username. Passed by Flask-Caching
                    from the decorated function's arguments.
    
    Returns:
        A unique cache key string, or None if caching should be skipped.
    """
    try:
        # Use passed identifier if provided, otherwise get from URL for backward compatibility
        # Using 'is None' check to handle edge case where empty string is explicitly passed
        if identifier is None:
            identifier = request.view_args.get('identifier', '')
        
        # Get current user from token for personalized data
        auth_header = request.headers.get("Authorization", "")
        current_user_id = 0
        if auth_header.startswith("Bearer "):
            try:
                token = auth_header.split(" ")[1]
                payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
                current_user_id = payload.get("user_id", 0)
            except Exception:
                pass
        
        return f"user_profile:{identifier}:{current_user_id}"
    except Exception:
        return None


def invalidate_user_cache(user_id: int):
    """
    Invalidate cached user profile for a specific user.
    
    Called when user profile is updated to ensure fresh data is returned.
    
    Args:
        user_id: The ID of the user whose cache should be invalidated
    """
    invalidate_cache_pattern(f"user_profile:{user_id}:*")


def _get_login_cache_key(email: str) -> str:
    """
    Generate a cache key for login user lookup.
    
    Uses lowercase email as the key to ensure consistent lookups.
    
    Args:
        email: User's email address (will be lowercased)
        
    Returns:
        Cache key string for Redis lookup
    """
    return f"login_user:{email.lower().strip()}"


def _get_cached_user_for_login(email: str) -> dict | None:
    """
    Get cached user data for login authentication.
    
    Checks Redis cache first for user data to skip database query.
    Returns None if cache miss or Redis unavailable.
    
    Performance impact:
    - Cache hit: Login completes in <100ms (skip 5000ms DB query)
    - Cache miss: Falls back to normal DB query
    
    Args:
        email: User's email address
        
    Returns:
        User dict if found in cache, None otherwise
    """
    redis_client = _get_redis_client()
    if redis_client is None:
        return None
    
    try:
        cache_key = _get_login_cache_key(email)
        cached_data = redis_client.get(cache_key)
        
        if cached_data is None:
            return None
        
        # Parse JSON data
        user_data = json.loads(cached_data)
        logger.debug(f"Login cache hit for email: {email}")
        return user_data
        
    except Exception as e:
        logger.warning(f"Login cache read failed: {e}")
        return None


def _cache_user_for_login(email: str, user_data: dict) -> bool:
    """
    Cache user data after successful login for future fast lookups.
    
    Stores user row data in Redis with 10-minute TTL.
    On subsequent logins within TTL, the database query is skipped entirely.
    
    Security considerations:
    - Only cached on successful password verification
    - TTL ensures data is refreshed periodically
    - Cache invalidated on password change or user deactivation
    
    Args:
        email: User's email address (used as cache key)
        user_data: User dict from database (must include password_hash for verification)
        
    Returns:
        True if cached successfully, False otherwise
    """
    redis_client = _get_redis_client()
    if redis_client is None:
        return False
    
    try:
        cache_key = _get_login_cache_key(email)
        
        # Serialize user data to JSON
        # Only cache essential fields for login verification
        cache_data = {
            "id": user_data["id"],
            "email": user_data["email"],
            "password_hash": user_data["password_hash"],
            "first_name": user_data.get("first_name") or "",
            "last_name": user_data.get("last_name") or "",
            "user_type": user_data.get("user_type") or "user",
            "location": user_data.get("location") or "",
            "phone": user_data.get("phone") or "",
            "bio": user_data.get("bio") or "",
            "avatar_url": user_data.get("avatar_url") or "",
            "is_available_for_hire": bool(user_data.get("is_available_for_hire")),
            "is_active": bool(user_data.get("is_active", True)),
        }
        
        # Store with TTL (10 minutes = 600 seconds)
        redis_client.setex(
            cache_key,
            CACHE_TIMEOUT_LOGIN_USER,
            json.dumps(cache_data)
        )
        
        logger.debug(f"Login cache set for email: {email}, TTL: {CACHE_TIMEOUT_LOGIN_USER}s")
        return True
        
    except Exception as e:
        logger.warning(f"Login cache write failed: {e}")
        return False


def _invalidate_login_cache(email: str) -> bool:
    """
    Invalidate login cache for a user.
    
    Called when:
    - User changes password
    - User account is deactivated
    - User profile is updated
    
    Args:
        email: User's email address
        
    Returns:
        True if invalidated successfully, False otherwise
    """
    redis_client = _get_redis_client()
    if redis_client is None:
        return False
    
    try:
        cache_key = _get_login_cache_key(email)
        redis_client.delete(cache_key)
        logger.debug(f"Login cache invalidated for email: {email}")
        return True
        
    except Exception as e:
        logger.warning(f"Login cache invalidation failed: {e}")
        return False


# Cache timeout for auth profile (in seconds)
# Set to 30 seconds for quick updates while maintaining fast response times
CACHE_TIMEOUT_AUTH_PROFILE = int(os.getenv("CACHE_TIMEOUT_AUTH_PROFILE", "30"))


def _get_auth_profile_cache_key(user_id: int) -> str:
    """Generate cache key for auth profile."""
    return f"auth_profile:{user_id}"


def _get_cached_auth_profile(user_id: int) -> dict | None:
    """
    Get cached auth profile from Redis.
    
    Returns the cached profile dict if found, None otherwise.
    Cache hit reduces /api/auth/profile response from ~200ms to <50ms.
    """
    redis_client = _get_redis_client()
    if redis_client is None:
        return None
    
    try:
        cache_key = _get_auth_profile_cache_key(user_id)
        cached_data = redis_client.get(cache_key)
        
        if cached_data is None:
            return None
        
        profile_data = json.loads(cached_data)
        logger.debug(f"Auth profile cache hit for user_id: {user_id}")
        return profile_data
        
    except Exception as e:
        logger.warning(f"Auth profile cache read failed: {e}")
        return None


def _cache_auth_profile(user_id: int, profile_data: dict) -> bool:
    """
    Cache auth profile in Redis.
    
    Stores the profile response with a 30-second TTL.
    """
    redis_client = _get_redis_client()
    if redis_client is None:
        return False
    
    try:
        cache_key = _get_auth_profile_cache_key(user_id)
        redis_client.setex(
            cache_key,
            CACHE_TIMEOUT_AUTH_PROFILE,
            json.dumps(profile_data)
        )
        logger.debug(f"Auth profile cached for user_id: {user_id}")
        return True
        
    except Exception as e:
        logger.warning(f"Auth profile cache write failed: {e}")
        return False


def _invalidate_auth_profile_cache(user_id: int) -> bool:
    """Invalidate cached auth profile for a user."""
    redis_client = _get_redis_client()
    if redis_client is None:
        return False
    
    try:
        cache_key = _get_auth_profile_cache_key(user_id)
        redis_client.delete(cache_key)
        logger.debug(f"Auth profile cache invalidated for user_id: {user_id}")
        return True
        
    except Exception as e:
        logger.warning(f"Auth profile cache invalidation failed: {e}")
        return False


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

# ==========================================
# SQL COLUMN DEFINITIONS
# ==========================================
# Explicit column lists prevent SELECT * anti-pattern and improve performance
# by reducing network transfer and enabling better query optimization

# Full user columns for profile/registration (all columns from users table)
USER_COLUMNS_FULL = """
    id, email, password_hash, first_name, last_name, user_type,
    location, phone, bio, avatar_url, created_at, last_login,
    is_active, is_available_for_hire, trade, username, occupation,
    company_name, skills, experience, education
"""

# User columns for login (only what's needed for authentication + cache)
USER_COLUMNS_LOGIN = """
    id, email, password_hash, first_name, last_name, user_type,
    location, phone, bio, avatar_url, is_available_for_hire, is_active
"""

# User columns for public profile display (excludes password_hash)
USER_COLUMNS_PUBLIC = """
    id, email, first_name, last_name, user_type, location, phone,
    bio, avatar_url, created_at, is_active, is_available_for_hire,
    trade, username, occupation, company_name, skills, experience, education
"""

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
SLOW_REGISTRATION_THRESHOLD_MS = 1000  # 1 second - trigger warning for slow registrations

# User agent display configuration
USER_AGENT_MAX_DISPLAY_LENGTH = 100  # Maximum characters to display in logs

# Cold start detection configuration
# Requests arriving within this time after app startup are considered cold start requests
COLD_START_THRESHOLD_SECONDS = 5

# Generic mobile client detection patterns (used after specific platform checks)
# These patterns help identify mobile clients that may have shorter timeout settings
# Note: iOS and Android are handled separately for more specific detection
GENERIC_MOBILE_USER_AGENT_PATTERNS = [
    'mobile',      # Generic mobile indicator
    'webos',       # WebOS devices (legacy)
    'blackberry',  # BlackBerry devices (legacy)
    'windows phone',  # Windows Phone devices
    'opera mini',  # Opera Mini browser
    'opera mobi',  # Opera Mobile browser
]

# Query stats configuration constants
# Maximum length of query text to display in query stats responses
# Longer queries are truncated to prevent response payload bloat
QUERY_STATS_MAX_DISPLAY_LENGTH = 500

# Threshold in milliseconds for identifying slow queries in database health checks
# Queries averaging above this threshold trigger slow_query_alert
SLOW_QUERY_THRESHOLD_MS = 500


def _detect_client_type(user_agent: str) -> str:
    """
    Detect the client type from User-Agent string.
    
    Args:
        user_agent: The User-Agent header value from the HTTP request
    
    Returns:
        - 'mobile-ios': iPhone or iPad devices
        - 'mobile-android': Android devices  
        - 'mobile': Other mobile devices (BlackBerry, Windows Phone, etc.)
        - 'desktop': Desktop browsers
        - 'unknown': Empty or missing User-Agent
    """
    if not user_agent:
        return 'unknown'
    
    ua_lower = user_agent.lower()
    
    # iOS detection (iPhone or iPad)
    if 'iphone' in ua_lower or 'ipad' in ua_lower:
        return 'mobile-ios'
    
    # Android detection
    if 'android' in ua_lower:
        return 'mobile-android'
    
    # Generic mobile detection for other mobile platforms
    for pattern in GENERIC_MOBILE_USER_AGENT_PATTERNS:
        if pattern in ua_lower:
            return 'mobile'
    
    return 'desktop'


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
    - Host for correlation with infrastructure logs (e.g., Render)
    - Client type (mobile-ios, mobile-android, mobile, desktop) for timeout analysis
    - Cold start detection for diagnosing slow first requests
    """
    # Generate unique request ID (use longer format for better correlation with external logs)
    g.request_id = str(uuid.uuid4())[:12]
    g.start_time = time.time()
    
    # Get client information
    client_ip = request.remote_addr or 'unknown'
    user_agent = request.headers.get('User-Agent', 'unknown')
    # Get host for correlation with infrastructure logs (e.g., Render's logs)
    host = request.host or 'unknown'
    
    # Detect client type for timeout analysis
    # Mobile clients often have shorter timeout settings than desktop browsers
    g.client_type = _detect_client_type(user_agent)
    
    # Check if this is a cold start request (first request after application startup)
    # Cold start requests are more likely to timeout due to database initialization
    is_cold_start = False
    if _APP_IMPORT_COMPLETE_TIME is not None:
        time_since_startup = g.start_time - _APP_IMPORT_COMPLETE_TIME
        if time_since_startup < COLD_START_THRESHOLD_SECONDS:
            is_cold_start = True
    
    # Log incoming request with context (truncate long user agents)
    user_agent_display = (
        user_agent if len(user_agent) <= USER_AGENT_MAX_DISPLAY_LENGTH 
        else f"{user_agent[:USER_AGENT_MAX_DISPLAY_LENGTH]}..."
    )
    
    # Build log parts and join to avoid extra spaces with optional fields
    log_parts = [
        f"[{g.request_id}] --> {request.method} {host}{request.path}",
        f"clientIP=\"{client_ip}\"",
        f"clientType=\"{g.client_type}\"",
    ]
    if is_cold_start:
        log_parts.append("coldStart=\"true\"")
    log_parts.append(f"userAgent=\"{user_agent_display}\"")
    print(" ".join(log_parts))


@app.after_request
def log_request_end(response):
    """
    Log completed requests with timing and status information.
    
    This middleware logs response status and duration to help identify slow requests
    that may cause timeout issues. For authentication endpoints, it provides additional
    context to help diagnose login failures.
    
    Log format matches Render's infrastructure logs for easier correlation:
    - Host for identifying the target service
    - Request ID for tracing across log entries
    - Response status code
    - Request duration in milliseconds
    - Response size in bytes
    - Client IP and User-Agent for debugging
    - Client type for mobile client timeout analysis
    - Warnings for slow requests (> 3 seconds)
    - Critical warnings for very slow requests (> 10 seconds)
    """
    if not hasattr(g, 'request_id') or not hasattr(g, 'start_time'):
        # Request logging was bypassed (e.g., for static files or middleware chain broken)
        # Log a warning to help identify when middleware chain is interrupted
        if request.path and not request.path.startswith('/static/'):
            print(f"⚠️ Warning: Request logging bypassed for {request.method} {request.path}")
        return response
    
    duration_ms = int((time.time() - g.start_time) * 1000)
    client_ip = request.remote_addr or 'unknown'
    host = request.host or 'unknown'
    user_agent = request.headers.get('User-Agent', 'unknown')
    client_type = getattr(g, 'client_type', 'unknown')
    
    # Truncate long user agents for log readability
    user_agent_display = (
        user_agent if len(user_agent) <= USER_AGENT_MAX_DISPLAY_LENGTH 
        else f"{user_agent[:USER_AGENT_MAX_DISPLAY_LENGTH]}..."
    )
    
    # Determine log level based on status code
    if response.status_code < 400:
        # Success - log at INFO level with full context for correlation
        print(
            f"[{request.method}]{response.status_code} {host}{request.path} "
            f"clientIP=\"{client_ip}\" clientType=\"{client_type}\" "
            f"requestID=\"{g.request_id}\" "
            f"responseTimeMS={duration_ms} responseBytes={response.content_length or 0} "
            f"userAgent=\"{user_agent_display}\""
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
            f"[{request.method}]{response.status_code} {host}{request.path} "
            f"clientIP=\"{client_ip}\" clientType=\"{client_type}\" "
            f"requestID=\"{g.request_id}\" "
            f"responseTimeMS={duration_ms} responseBytes={response.content_length or 0} "
            f"userAgent=\"{user_agent_display}\"{error_detail}"
        )
    
    # Warn about slow requests with appropriate severity level
    # Mobile clients often have shorter timeout settings (typically 30 seconds)
    # so we add extra warnings for mobile clients
    is_slow = duration_ms > SLOW_REQUEST_THRESHOLD_MS
    is_very_slow = duration_ms > VERY_SLOW_REQUEST_THRESHOLD_MS
    is_mobile = client_type.startswith('mobile')
    
    if is_slow:
        severity = "VERY SLOW REQUEST" if is_very_slow else "SLOW REQUEST"
        threshold_note = f">{SLOW_REQUEST_THRESHOLD_MS}ms threshold"
        
        # Add mobile client warning if applicable
        mobile_warning = ""
        if is_mobile:
            mobile_warning = (
                f" Mobile client ({client_type}) detected - "
                "these often have 30s timeout limits which may cause HTTP 499 errors."
            )
        
        print(
            f"[{g.request_id}] ⚠️ {severity}: {request.method} {host}{request.path} "
            f"took {duration_ms}ms ({threshold_note}).{mobile_warning} "
            f"Check database connection pool, bcrypt rounds, and query performance."
        )
    
    return response


# ==========================================
# DATABASE CONNECTION MANAGEMENT
# ==========================================

# Check if running on Railway with PostgreSQL
# Railway Private Network Configuration:
# To avoid egress fees, Railway provides DATABASE_PRIVATE_URL which uses the internal
# private network (RAILWAY_PRIVATE_DOMAIN) instead of the public TCP proxy
# (RAILWAY_TCP_PROXY_DOMAIN used by DATABASE_PUBLIC_URL).
# We prefer DATABASE_PRIVATE_URL > DATABASE_URL to minimize costs.
DATABASE_URL = os.getenv("DATABASE_PRIVATE_URL") or os.getenv("DATABASE_URL")

# Normalize DATABASE_URL for psycopg2 compatibility
# If the URL uses postgresql+asyncpg:// scheme (for SQLAlchemy/asyncpg), convert it
# to postgresql:// for psycopg2 (sync driver) compatibility
if DATABASE_URL and DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
    print("🔄 Normalized DATABASE_URL: converted postgresql+asyncpg:// to postgresql://")

USE_POSTGRESQL = DATABASE_URL is not None

# PostgreSQL extensions to initialize during database setup
# Pre-defined SQL statements prevent SQL injection by avoiding string formatting
# Note: Extensions like pg_stat_statements require server-side configuration
# (shared_preload_libraries) which is not available on managed database services
# like Railway. Only add extensions that don't require server-side configuration.
# 
# For pg_stat_statements setup on Railway PostgreSQL, see:
# RAILWAY_PG_STAT_STATEMENTS_SETUP.md for comprehensive setup instructions.
# 
# The /api/query-stats endpoint provides graceful error handling when 
# pg_stat_statements is not available, with alternative solutions.
POSTGRESQL_EXTENSIONS = {
    # Empty - all previously listed extensions required shared_preload_libraries
    # configuration which is not available on Railway and similar managed services.
    # The pg_stat_statements extension was removed because it causes:
    # "ERROR: pg_stat_statements must be loaded via shared_preload_libraries"
}

# Check if this is a production environment
# Detect Railway environment using Railway-specific variables:
# - RAILWAY_ENVIRONMENT: Set by Railway to indicate the environment (e.g., "production")
# - RAILWAY_PROJECT_ID: Always present in Railway deployments, used as fallback detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
RAILWAY_ENVIRONMENT = os.getenv("RAILWAY_ENVIRONMENT", "").lower()
IS_RAILWAY = os.getenv("RAILWAY_PROJECT_ID") is not None

# Detect Render environment using Render-specific variables:
# - RENDER: Set to "true" by Render in all web services
# - RENDER_SERVICE_ID: Set by Render to identify the service
# See: https://render.com/docs/environment-variables
IS_RENDER = os.getenv("RENDER") == "true" or os.getenv("RENDER_SERVICE_ID") is not None

# Production is determined by:
# 1. Explicit ENVIRONMENT=production setting, OR
# 2. Running on Railway (Railway is inherently a production platform), OR
# 3. Running on Render (Render is inherently a production platform)
# Deployments on these platforms automatically enable production mode to ensure:
# - Database keepalive is active (prevents PostgreSQL from sleeping)
# - Production-level logging and error handling
# - Proper data persistence with PostgreSQL
IS_PRODUCTION = (
    ENVIRONMENT in ["production", "prod"] or 
    IS_RAILWAY or  # Railway deployments are always considered production
    IS_RENDER      # Render deployments are always considered production
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

    # URL decode credentials to handle special characters in username/password
    # For example, if password is "p@ss%word!", it will be encoded as "p%40ss%25word%21"
    # We need to decode it back to the original form for authentication
    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None
    
    DB_CONFIG = {
        "host": parsed.hostname,
        "port": port,
        "database": database,
        "user": username,
        "password": password,
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

# Connection age tracking for pool_recycle functionality
# Maps connection id to creation time for recycling stale connections
_connection_ages = {}
_connection_ages_lock = threading.Lock()

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

# =============================================================================
# TOP 3 TIMEOUT FIXES FOR CLOUD POSTGRESQL (Railway/Render)
# =============================================================================
# These three settings fix 99% of PostgreSQL timeout errors in cloud environments:
#
# 1. DB_CONNECT_TIMEOUT (30s) - Connection establishment timeout
#    Cloud databases often have higher latency due to network hops, SSL handshakes,
#    and cold starts. 30 seconds allows for these delays without failing prematurely.
#
# 2. JIT=off - Disable JIT compilation
#    PostgreSQL's JIT compiler can cause significant delays on first query execution.
#    Disabling JIT prevents unexpected timeouts during query compilation.
#    Set via options="-c jit=off" in connection parameters.
#
# 3. sslmode=require - Proper SSL handling
#    Cloud databases require SSL. Using 'require' ensures encrypted connections
#    without certificate verification issues that can cause connection failures.
# =============================================================================

# Connection timeout in seconds for PostgreSQL
# Set to 45 seconds for cloud databases (Railway/Render) which may have higher latency
# This is FIX #1 of the top 3 timeout fixes - handles Railway cold starts
DB_CONNECT_TIMEOUT = _get_env_int("DB_CONNECT_TIMEOUT", 45, 5, 120)

# Maximum connection pool size
# NUCLEAR FIX: Reduced to 5 for 512MB-1GB instances to prevent OOM
# Configurable via environment variable for different deployment environments
DB_POOL_MAX_CONNECTIONS = _get_env_int("DB_POOL_MAX_CONNECTIONS", 5, 2, 100)

# Minimum connection pool size (pre-warmed connections)
# NUCLEAR FIX: Set to 2 to prevent OOM on 512MB instances while maintaining availability
# Range reduced to 1-10 to align with the nuclear fix's conservative memory approach
DB_POOL_MIN_CONNECTIONS = _get_env_int("DB_POOL_MIN_CONNECTIONS", 2, 1, 10)

# Connection pool recycle time in seconds
# Connections older than this are recycled to prevent stale connection issues
# Set to 180 seconds (3 minutes) for aggressive recycling in cloud environments
# This helps prevent SSL EOF errors from long-idle connections
DB_POOL_RECYCLE_SECONDS = _get_env_int("DB_POOL_RECYCLE_SECONDS", 180, 60, 3600)

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
# Default values optimized for cloud environments (Railway, Render, AWS, etc.):
# - keepalives_idle: 20s (start probing after 20 seconds of idle)
# - keepalives_interval: 5s (probe every 5 seconds)
# - keepalives_count: 3 (mark dead after 3 failed probes)
#
# Total detection time = idle + (interval * count) = 20 + (5 * 3) = 35 seconds
# This is very aggressive to detect stale connections quickly in cloud environments
# where load balancers may drop idle connections after 60 seconds.
#
# tcp_user_timeout: 20s - Abort TCP connection if data isn't acknowledged within 20s
# This helps detect broken connections faster than relying solely on keepalives.
#
# These settings are more aggressive than previous defaults (30/10/3 = 60s total)
# to prevent SSL EOF errors in cloud environments with shorter idle timeouts.
TCP_KEEPALIVE_ENABLED = _get_env_int("TCP_KEEPALIVE_ENABLED", 1, 0, 1)
TCP_KEEPALIVE_IDLE = _get_env_int("TCP_KEEPALIVE_IDLE", 20, 10, 300)
TCP_KEEPALIVE_INTERVAL = _get_env_int("TCP_KEEPALIVE_INTERVAL", 5, 5, 60)
TCP_KEEPALIVE_COUNT = _get_env_int("TCP_KEEPALIVE_COUNT", 3, 1, 10)
# TCP user timeout in milliseconds - abort if data isn't acknowledged within this time
# This provides a hard limit on how long we wait for network acknowledgment
# Works in conjunction with keepalives for faster detection of broken connections
# Set to 20000ms (20 seconds) to match the aggressive keepalive settings
TCP_USER_TIMEOUT_MS = _get_env_int("TCP_USER_TIMEOUT_MS", 20000, 5000, 60000)

# Login request timeout in seconds
# This prevents login requests from blocking indefinitely
# If a login request takes longer than this, it returns a timeout error
# This helps prevent HTTP 499 errors by returning a proper response before
# the client or load balancer times out
# Set to 25 seconds (below typical client/proxy timeouts of 30s)
LOGIN_REQUEST_TIMEOUT_SECONDS = _get_env_int("LOGIN_REQUEST_TIMEOUT_SECONDS", 25, 5, 60)

# Registration request timeout in seconds
# This prevents registration requests from blocking indefinitely
# If a registration request takes longer than this, it returns a timeout error
# This helps prevent HTTP 499 errors by returning a proper response before
# the client or load balancer times out
# Set to 25 seconds (below typical client/proxy timeouts of 30s)
REGISTRATION_REQUEST_TIMEOUT_SECONDS = _get_env_int("REGISTRATION_REQUEST_TIMEOUT_SECONDS", 25, 5, 60)

# API request timeout in seconds for general API endpoints
# This prevents API requests from blocking indefinitely
# If an API request takes longer than this, it returns a timeout error
# This helps prevent HTTP 499 errors by returning a proper response before
# the client or load balancer times out
# Set to 25 seconds (below typical client/proxy timeouts of 30s)
API_REQUEST_TIMEOUT_SECONDS = _get_env_int("API_REQUEST_TIMEOUT_SECONDS", 25, 5, 60)

# Default pagination limit for list endpoints
# Limits the number of results returned to prevent slow queries and large payloads
# This helps prevent HTTP 499 timeout errors by reducing query complexity
DEFAULT_LIST_LIMIT = _get_env_int("DEFAULT_LIST_LIMIT", 100, 10, 500)

# Maximum allowed limit for list endpoints to prevent excessive queries
MAX_LIST_LIMIT = _get_env_int("MAX_LIST_LIMIT", 500, 100, 1000)

# Bcrypt password hashing rounds configuration
# Default of 12 rounds can be slow (~200-300ms per operation) and contribute to HTTP 499 timeouts
# 10 rounds provides good security while being much faster (~60ms per operation)
# See OWASP recommendations: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
# Configurable via environment variable for different deployment environments:
# - 10 rounds: ~60ms per operation, excellent performance, good security (recommended)
# - 11 rounds: ~120ms per operation, very good security
# - 12 rounds: ~240ms per operation, excellent security (original default)
# Note: Existing password hashes continue to work regardless of this setting
BCRYPT_ROUNDS = _get_env_int("BCRYPT_ROUNDS", 10, 4, 14)

# Enable automatic password hash migration for faster future logins
# When a user logs in with an old high-round hash, it will be upgraded
# to the current BCRYPT_ROUNDS setting in the background
# This reduces login latency for users with old hashes over time
PASSWORD_HASH_MIGRATION_ENABLED = os.getenv("PASSWORD_HASH_MIGRATION_ENABLED", "true").lower() == "true"

print(f"🔐 Bcrypt rounds configured: {BCRYPT_ROUNDS}")
if PASSWORD_HASH_MIGRATION_ENABLED:
    print(f"🔄 Password hash migration: enabled (will upgrade old hashes on login)")


def _get_bcrypt_rounds_from_hash(password_hash: str) -> int:
    """
    Extract the bcrypt rounds from a password hash.
    
    Bcrypt hashes have the format: $2b$<rounds>$<salt><hash>
    For example: $2b$12$... means 12 rounds
    
    Args:
        password_hash: The bcrypt password hash string
        
    Returns:
        The number of rounds used, or 0 if unable to parse
    """
    try:
        if password_hash.startswith('$2'):
            # Split by $ to get parts: ['', '2b', '12', 'salt+hash']
            parts = password_hash.split('$')
            if len(parts) >= 3:
                return int(parts[2])
    except (ValueError, IndexError):
        pass
    return 0


def _should_upgrade_password_hash(password_hash: str) -> bool:
    """
    Determine if a password hash should be upgraded to current bcrypt rounds.
    
    Upgrading old high-round hashes (e.g., 12 rounds) to the current setting
    (e.g., 10 rounds) reduces login latency from ~240ms to ~60ms per login.
    
    Args:
        password_hash: The current bcrypt password hash
        
    Returns:
        True if the hash uses more rounds than currently configured
    """
    if not PASSWORD_HASH_MIGRATION_ENABLED:
        return False
    
    current_rounds = _get_bcrypt_rounds_from_hash(password_hash)
    # Only upgrade if current hash uses more rounds than configured
    # This ensures we're reducing latency, not increasing it
    return current_rounds > BCRYPT_ROUNDS


def _upgrade_password_hash_async(user_id: int, password: str, request_id: str):
    """
    Upgrade a user's password hash to current bcrypt rounds in the background.
    
    This function runs asynchronously to avoid blocking the login response.
    It creates a new hash with the current BCRYPT_ROUNDS setting and updates
    the database.
    
    Security note: The password parameter is only used for hashing and is not
    stored. The background thread processes it immediately and the string
    becomes eligible for garbage collection after the thread completes.
    
    Args:
        user_id: The user ID to update
        password: The plain text password (already verified)
        request_id: Request ID for logging correlation
    """
    def _do_upgrade():
        conn = None
        cursor = None
        try:
            # Create new hash with current rounds
            new_hash = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
            ).decode("utf-8")
            
            # Update database
            conn = get_db_connection()
            if conn is None:
                logger.warning("Cannot upgrade password hash: connection unavailable")
                return
            
            cursor = conn.cursor()
            if USE_POSTGRESQL:
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE id = %s",
                    (new_hash, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (new_hash, user_id)
                )
            conn.commit()
            
            print(f"[{request_id}] ✅ Password hash upgraded to {BCRYPT_ROUNDS} rounds for user {user_id}")
        except Exception as e:
            logger.warning("Password hash upgrade failed for user %s: %s", user_id, e)
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass  # Ignore errors closing cursor on failed connection
            if conn:
                return_db_connection(conn)
    
    # Run in background thread
    threading.Thread(target=_do_upgrade, daemon=True).start()

# Transient database error patterns
# These patterns indicate temporary connection issues that may resolve on retry
# Shared across multiple functions to ensure consistent error detection
# Used by _is_transient_connection_error(), get_database_recovery_status(), and api_health_check()
TRANSIENT_ERROR_PATTERNS = [
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
    "decryption failed or bad record mac",  # SSL error from stale/corrupted connection
    "bad record mac",                # Shortened form of SSL MAC error
    "name or service not known",     # DNS resolution failure during container startup
    "no route to host",              # Network not ready during container startup
]

# Container transitioning patterns - more specific than general "container" keyword
# These indicate the database container is starting up or transitioning
CONTAINER_TRANSITIONING_PATTERNS = [
    "container is transitioning",    # Explicit container transitioning message
    "container transitioning",       # Shorter form
    "container is starting",         # Container starting up
    "container starting",            # Shorter form
]

# Combined patterns for detecting container transitioning state
# Used in get_database_recovery_status() and api_health_check()
# Includes transient error patterns and container-specific patterns
ALL_TRANSITIONING_PATTERNS = (
    TRANSIENT_ERROR_PATTERNS +
    CONTAINER_TRANSITIONING_PATTERNS
)


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


def _get_pagination_params(default_limit: int = None, max_limit: int = None):
    """
    Extract and validate pagination parameters from the request.
    
    This helper function standardizes pagination handling across list endpoints
    to prevent slow queries from causing HTTP 499 timeout errors.
    
    Args:
        default_limit: Default number of results if not specified (uses DEFAULT_LIST_LIMIT)
        max_limit: Maximum allowed limit (uses MAX_LIST_LIMIT)
        
    Returns:
        Tuple of (limit, offset) validated pagination parameters
    """
    if default_limit is None:
        default_limit = DEFAULT_LIST_LIMIT
    if max_limit is None:
        max_limit = MAX_LIST_LIMIT
    
    # Get pagination parameters with defaults
    # request.args.get with type=int returns None for invalid values
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)
    
    # Apply defaults for None or invalid values
    if limit is None or limit < 1:
        limit = default_limit
    if limit > max_limit:
        limit = max_limit
    
    if offset is None or offset < 0:
        offset = 0
    
    return limit, offset


def _is_transient_connection_error(error: Exception) -> bool:
    """
    Check if a database connection error is transient and may succeed on retry.
    
    Transient errors occur during:
    - Database recovery after improper shutdown
    - Temporary network issues
    - Connection pool exhaustion
    - Database restarts or failovers
    - Container transitions (Railway/Docker)
    
    Args:
        error: The exception that occurred during connection attempt
        
    Returns:
        True if the error is likely transient and worth retrying
    """
    if not isinstance(error, psycopg2.Error):
        return False
    
    error_msg = str(error).lower()
    
    # Use the shared ALL_TRANSITIONING_PATTERNS constant for consistency
    return any(pattern in error_msg for pattern in ALL_TRANSITIONING_PATTERNS)


def _is_stale_ssl_connection_error(error: Exception) -> bool:
    """
    Check if an error indicates a stale or corrupted SSL connection.
    
    These errors occur when:
    - A TCP connection is silently dropped by network intermediaries but SSL layer doesn't know
    - The SSL session becomes out of sync with the underlying TCP connection
    - Connection pool returns a connection that was idle too long and became stale
    
    When these errors occur, the connection MUST be discarded (not returned to pool)
    and a new connection should be created.
    
    Args:
        error: The exception that occurred during query execution
        
    Returns:
        True if the connection should be discarded due to SSL issues
    """
    # psycopg2.OperationalError is a subclass of psycopg2.Error, so only check parent
    if not isinstance(error, psycopg2.Error):
        return False
    
    error_msg = str(error).lower()
    
    # SSL error patterns that indicate the connection is corrupted and must be discarded
    # Note: patterns are specific to avoid false positives from unrelated SSL errors
    stale_ssl_patterns = [
        "decryption failed or bad record mac",  # SSL MAC verification failed
        "bad record mac",                        # Shortened form
        "ssl error: decryption failed",          # Specific SSL decryption error
        "ssl error: unexpected eof",             # SSL EOF from dropped connection
        "unexpected eof while reading",          # Variant of SSL EOF error
        "ssl connection has been closed unexpectedly",
        "connection reset by peer",              # Connection was forcibly closed
        "connection timed out",                  # Connection became unresponsive
    ]
    
    return any(pattern in error_msg for pattern in stale_ssl_patterns)


def _validate_connection(conn) -> bool:
    """
    Validate that a database connection is still usable.
    
    Performs a lightweight query to check if the connection is alive.
    This helps detect stale connections before they cause SSL errors.
    Also checks connection age for pool_recycle functionality.
    
    Args:
        conn: A psycopg2 connection object
        
    Returns:
        True if the connection is valid, False otherwise
    """
    cursor = None
    try:
        # Check connection age for pool_recycle
        # If connection is older than DB_POOL_RECYCLE_SECONDS, consider it stale
        conn_id = id(conn)
        with _connection_ages_lock:
            conn_created_time = _connection_ages.get(conn_id)
        
        if conn_created_time is not None:
            conn_age = time.time() - conn_created_time
            if conn_age >= DB_POOL_RECYCLE_SECONDS:
                logger.info(f"Connection {conn_id} is {conn_age:.0f}s old (recycle at {DB_POOL_RECYCLE_SECONDS}s), recycling")
                return False
        
        # Use a lightweight query to check connection health
        # This is similar to SQLAlchemy's pool_pre_ping feature
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return True
    except Exception as e:
        logger.warning("Connection validation failed: %s", e)
        return False
    finally:
        # Ensure cursor is always closed
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass  # Ignore errors closing cursor on bad connection


def _track_connection_age(conn):
    """
    Track when a connection was created for pool_recycle functionality.
    
    Called when a new connection is obtained from the pool or created directly.
    
    Args:
        conn: The connection to track
    """
    conn_id = id(conn)
    with _connection_ages_lock:
        if conn_id not in _connection_ages:
            _connection_ages[conn_id] = time.time()


def _clear_connection_age(conn):
    """
    Remove age tracking for a connection that is being discarded.
    
    Called when a connection is discarded to prevent memory leaks.
    
    Args:
        conn: The connection to stop tracking
    """
    conn_id = id(conn)
    with _connection_ages_lock:
        _connection_ages.pop(conn_id, None)


def _discard_connection(conn):
    """
    Discard a bad connection instead of returning it to the pool.
    
    When an SSL error occurs, the connection is corrupted and cannot be reused.
    This function ensures the connection is properly closed and not returned to
    the pool where it could cause errors for subsequent requests.
    
    Args:
        conn: The connection to discard
    """
    if conn is None:
        return
    
    try:
        # Clear age tracking to prevent memory leaks
        _clear_connection_age(conn)
        # Close the connection properly
        conn.close()
    except Exception:
        pass  # Connection may already be in a bad state
    
    logger.info("Discarded bad connection (will not return to pool)")


def _get_connection_pool():
    """
    Get or create the PostgreSQL connection pool.
    Uses ThreadedConnectionPool for thread-safe connection management.
    Pool is created lazily on first request.
    
    Pool configuration optimized for preventing HTTP 499 timeouts:
    - minconn=5 (DB_POOL_MIN_CONNECTIONS) for reduced cold start latency
    - maxconn=30 (DB_POOL_MAX_CONNECTIONS) for better concurrent handling
    - pool_recycle=180s to prevent stale connection issues
    - pool_pre_ping equivalent via connection validation
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
                    # Create a threaded connection pool with optimized settings:
                    # - minconn: Configurable via DB_POOL_MIN_CONNECTIONS (default 5)
                    #   Higher min reduces cold start latency for first requests
                    # - maxconn: Configurable via DB_POOL_MAX_CONNECTIONS (default 30)
                    #   Higher max handles concurrent mobile users during peak traffic
                    #
                    # TOP 3 TIMEOUT FIXES applied here:
                    # 1. connect_timeout=DB_CONNECT_TIMEOUT (30s) for cloud DB latency
                    # 2. jit=off in options to prevent first-query compilation delays
                    # 3. sslmode=require for proper SSL handling
                    #
                    # TCP keepalive parameters prevent "SSL error: unexpected eof while reading"
                    # by detecting and handling stale connections before they cause SSL errors
                    #
                    # tcp_user_timeout: Provides a hard limit on unacknowledged data
                    # This helps detect broken connections faster than keepalives alone
                    _connection_pool = pool.ThreadedConnectionPool(
                        minconn=DB_POOL_MIN_CONNECTIONS,
                        maxconn=DB_POOL_MAX_CONNECTIONS,
                        host=DB_CONFIG["host"],
                        port=DB_CONFIG["port"],
                        database=DB_CONFIG["database"],
                        user=DB_CONFIG["user"],
                        password=DB_CONFIG["password"],
                        sslmode=DB_CONFIG["sslmode"],
                        application_name=DB_CONFIG["application_name"],
                        cursor_factory=RealDictCursor,
                        # FIX #1: Increased to 30s for cloud databases with higher latency
                        connect_timeout=DB_CONNECT_TIMEOUT,
                        # TCP keepalive settings to prevent SSL EOF errors on idle connections
                        # psycopg2 expects integer (1=enabled, 0=disabled)
                        keepalives=1 if TCP_KEEPALIVE_ENABLED else 0,
                        keepalives_idle=TCP_KEEPALIVE_IDLE,
                        keepalives_interval=TCP_KEEPALIVE_INTERVAL,
                        keepalives_count=TCP_KEEPALIVE_COUNT,
                        # tcp_user_timeout: abort if data isn't acknowledged within this time
                        # Works with keepalives for faster detection of broken connections
                        tcp_user_timeout=TCP_USER_TIMEOUT_MS,
                        # FIX #2: jit=off prevents first-query timeout from JIT compilation
                        # Combined with statement_timeout for query execution limits
                        options=f"-c statement_timeout={STATEMENT_TIMEOUT_MS} -c jit=off",
                    )
                    keepalive_status = "enabled" if TCP_KEEPALIVE_ENABLED == 1 else "disabled"
                    user_timeout_sec = TCP_USER_TIMEOUT_MS // 1000
                    print(
                        f"✅ PostgreSQL pool: min={DB_POOL_MIN_CONNECTIONS}, max={DB_POOL_MAX_CONNECTIONS}, "
                        f"timeout={DB_CONNECT_TIMEOUT}s, jit=off, keepalive={keepalive_status}"
                    )
                except psycopg2.OperationalError as e:
                    error_str = str(e)
                    print(f"⚠️ Failed to create connection pool: {e}")
                    
                    # Provide helpful diagnostics for common connection errors
                    if "password authentication failed" in error_str:
                        print("❌ DATABASE CONNECTION ERROR: Password authentication failed")
                        print("   This usually means:")
                        print("   1. The password in DATABASE_URL is incorrect")
                        print("   2. The password contains special characters that need URL encoding")
                        print("   3. The database user doesn't exist or is deactivated")
                        print("")
                        print("   Solution:")
                        print("   - Verify DATABASE_URL has the correct password")
                        print("   - Ensure special characters are URL-encoded (e.g., '@' becomes '%40')")
                        print(f"   - Check database user '{DB_CONFIG['user']}' exists and has correct password")
                        print("   - Verify DATABASE_URL format: postgresql://user:password@host:5432/database")
                    elif "could not connect to server" in error_str:
                        print("❌ DATABASE CONNECTION ERROR: Cannot reach database server")
                        print(f"   Host: {DB_CONFIG['host']}, Port: {DB_CONFIG['port']}")
                        print("   This usually means:")
                        print("   1. Database server is down or not accessible")
                        print("   2. Network/firewall blocking connection")
                        print("   3. Wrong host or port in DATABASE_URL")
                    
                    # Pool creation failed, will fall back to direct connections
                    return None
    
    return _connection_pool


def _warmup_connection_pool():
    """
    Pre-warm the database connection pool to reduce cold-start latency.
    
    This function is called during application startup to establish
    initial database connections before user requests arrive. This
    prevents the first login request from being slow due to connection
    establishment overhead.
    
    Benefits:
    - Reduces first-request latency by ~500-1000ms
    - Validates database connectivity on startup
    - Pre-populates connection pool for immediate availability
    
    Called asynchronously to avoid blocking app startup.
    """
    if not USE_POSTGRESQL:
        return
    
    try:
        # Get connection pool (creates it if not exists)
        conn_pool = _get_connection_pool()
        if not conn_pool:
            logger.warning("Connection pool warmup skipped: pool not available")
            return
        
        # Get and immediately return a few connections to warm up the pool
        # This establishes TCP connections and completes SSL handshakes
        warmup_count = min(3, DB_POOL_MAX_CONNECTIONS)
        warmed_conns = []
        
        warmup_start = time.time()
        for _ in range(warmup_count):
            try:
                conn = conn_pool.getconn()
                if conn:
                    # Run a simple query to fully establish the connection
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()
                    warmed_conns.append(conn)
            except Exception as e:
                logger.warning("Connection warmup failed for one connection: %s", e)
        
        # Return connections to pool
        for conn in warmed_conns:
            try:
                conn_pool.putconn(conn)
            except Exception as e:
                # Log connection return failures - may indicate pool corruption
                logger.debug("Failed to return warmed connection to pool: %s", e)
        
        warmup_ms = int((time.time() - warmup_start) * 1000)
        print(f"✅ Connection pool warmed up: {len(warmed_conns)} connections in {warmup_ms}ms")
        
    except Exception as e:
        logger.warning("Connection pool warmup failed: %s", e)


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
    
    Includes TCP keepalive and tcp_user_timeout settings to prevent 
    "SSL error: unexpected eof while reading" errors that occur when idle 
    connections are silently dropped by network intermediaries.
    
    Applies the TOP 3 TIMEOUT FIXES:
    1. connect_timeout=30s for cloud database latency
    2. jit=off to prevent first-query compilation delays
    3. sslmode=require for proper SSL handling
    
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
        # FIX #1: 30s timeout for cloud databases with higher latency
        connect_timeout=DB_CONNECT_TIMEOUT,
        # TCP keepalive settings to prevent SSL EOF errors on idle connections
        # psycopg2 expects integer (1=enabled, 0=disabled)
        keepalives=1 if TCP_KEEPALIVE_ENABLED else 0,
        keepalives_idle=TCP_KEEPALIVE_IDLE,
        keepalives_interval=TCP_KEEPALIVE_INTERVAL,
        keepalives_count=TCP_KEEPALIVE_COUNT,
        # tcp_user_timeout: abort if data isn't acknowledged within this time
        # Works with keepalives for faster detection of broken connections
        tcp_user_timeout=TCP_USER_TIMEOUT_MS,
        # FIX #2: jit=off prevents first-query timeout from JIT compilation
        options=f"-c statement_timeout={STATEMENT_TIMEOUT_MS} -c jit=off",
    )


def get_db_connection():
    """Get database connection (PostgreSQL on Railway, SQLite locally)
    
    For PostgreSQL, uses connection pool for better performance.
    Falls back to direct connection if pool is unavailable or exhausted.
    
    Includes:
    - Timeout handling to prevent indefinite blocking when pool is exhausted
    - Connection validation to detect stale connections before use
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
                    # Track connection age for pool_recycle
                    _track_connection_age(conn)
                    
                    # Validate the pooled connection before using it
                    # This prevents "SSL error: decryption failed or bad record mac" errors
                    # that occur when using stale connections from the pool
                    # Also enforces pool_recycle by checking connection age
                    if _validate_connection(conn):
                        return conn
                    else:
                        # Connection is stale, discard it and get another
                        logger.warning("Pooled connection is stale, discarding and getting another")
                        _discard_connection(conn)
                        # Try to get another connection from pool
                        conn = _get_pooled_connection_with_timeout(
                            conn_pool, POOL_TIMEOUT_SECONDS
                        )
                        if conn:
                            _track_connection_age(conn)
                            if _validate_connection(conn):
                                return conn
                            else:
                                _discard_connection(conn)
                        # Fall through to direct connection
                        logger.warning("Second pooled connection also stale, creating direct connection")
                # If timeout occurred, fall through to direct connection
                if not conn:
                    logger.warning("Pool timeout, creating direct connection")
            except psycopg2.pool.PoolError as e:
                logger.warning("Pool error: %s, falling back to direct connection", e)
            except Exception as e:
                logger.warning("Pool connection failed, falling back to direct: %s", e)
        
        # Fallback to direct connection with retry logic for transient errors
        # This handles database recovery scenarios after improper shutdown
        last_error = None
        delay_ms = DB_CONNECT_BASE_DELAY_MS
        
        for attempt in range(DB_CONNECT_MAX_RETRIES):
            try:
                conn = _create_direct_postgresql_connection()
                if attempt > 0:
                    logger.info("Connection succeeded on attempt %d", attempt + 1)
                return conn
            except psycopg2.OperationalError as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Handle SSL-related errors by trying with sslmode=prefer
                if "ssl" in error_msg or "certificate" in error_msg:
                    logger.warning("SSL connection failed, attempting with sslmode=prefer...")
                    try:
                        conn = _create_direct_postgresql_connection(sslmode="prefer")
                        return conn
                    except Exception as fallback_error:
                        logger.error("SSL fallback connection also failed: %s", fallback_error)
                        last_error = fallback_error
                
                # Check if this is a transient error worth retrying
                # Use last_error to check the most recent error (may be from SSL fallback)
                if _is_transient_connection_error(last_error) and attempt < DB_CONNECT_MAX_RETRIES - 1:
                    # Calculate delay with exponential backoff and additive jitter
                    # Additive jitter prevents retries from being too aggressive
                    # while still helping prevent thundering herd
                    jitter = random.uniform(0, DB_CONNECT_JITTER_FACTOR * delay_ms)
                    actual_delay_ms = min(delay_ms + jitter, DB_CONNECT_MAX_DELAY_MS)
                    
                    logger.warning(
                        "Transient connection error (attempt %d/%d): %s. Retrying in %.0fms...",
                        attempt + 1, DB_CONNECT_MAX_RETRIES, last_error, actual_delay_ms
                    )
                    
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


def return_db_connection(conn, discard=False):
    """Return a connection to the pool or close it.
    
    Handles both pooled and non-pooled (fallback) connections correctly:
    - For pooled connections: Returns to pool for reuse (unless discard=True)
    - For non-pooled/fallback connections: Closes the connection
    - If discard=True: Always close the connection, never return to pool
    
    IMPORTANT: Before returning to pool, this function calls rollback() to ensure
    no aborted transaction state is carried over. This prevents the PostgreSQL error:
    "current transaction is aborted, commands ignored until end of transaction block"
    
    The discard parameter should be set to True when:
    - An SSL error occurred (e.g., "decryption failed or bad record mac")
    - The connection is detected as stale or corrupted
    - Any error indicates the connection cannot be safely reused
    
    If putconn() fails (e.g., connection wasn't from pool), falls through
    to close the connection, ensuring proper cleanup in all cases.
    
    Args:
        conn: The database connection to return or close
        discard: If True, discard the connection instead of returning to pool
    """
    if conn is None:
        return
    
    if USE_POSTGRESQL:
        # Always rollback before returning to pool to clear any aborted transaction state.
        # This prevents "current transaction is aborted" errors on subsequent queries.
        # Rollback is safe to call even if no transaction is active or if already committed.
        try:
            conn.rollback()
        except Exception:
            # If rollback fails, the connection is likely broken - discard it
            discard = True
        
        conn_pool = _get_connection_pool()
        if conn_pool and not discard:
            try:
                # Try to return to pool - will fail for non-pooled connections
                conn_pool.putconn(conn)
                return
            except Exception:
                # Connection wasn't from pool (fallback connection)
                # Fall through to close it
                pass
        elif discard:
            logger.info("Discarding connection due to error (not returning to pool)")
    
    # Close the connection if not using pool, not PostgreSQL, 
    # pool return failed, or discard was requested
    try:
        conn.close()
    except Exception:
        pass


def _execute_query_internal(query, params, fetch, fetchone, commit, conn):
    """
    Internal query execution helper.
    
    Executes the query using the provided connection and returns the result.
    Handles PostgreSQL placeholder conversion and result fetching.
    
    Args:
        query: SQL query to execute
        params: Query parameters
        fetch: If True, fetch all results
        fetchone: If True, fetch one result
        commit: If True, commit the transaction
        conn: Database connection to use
        
    Returns:
        Query result (dict, list of dicts, or None)
    """
    cursor = conn.cursor()
    
    # Convert SQLite ? placeholders to PostgreSQL %s if using PostgreSQL
    executed_query = query.replace("?", "%s") if USE_POSTGRESQL else query

    if params:
        cursor.execute(executed_query, params)
    else:
        cursor.execute(executed_query)

    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetch:
        result = cursor.fetchall()

    if commit:
        conn.commit()

    cursor.close()
    return result


def execute_query(query, params=None, fetch=False, fetchone=False, commit=False):
    """
    Universal query executor for both PostgreSQL and SQLite.
    
    Handles SSL errors by discarding bad connections and retrying once with
    a fresh connection. This prevents transient SSL errors (like 
    "decryption failed or bad record mac") from causing user-visible failures.
    
    The retry behavior:
    1. First attempt uses a connection from the pool (or creates a new one)
    2. If an SSL error occurs, the bad connection is discarded
    3. A second attempt is made with a fresh connection
    4. If the retry also fails, the error is raised to the caller
    
    Note: Only SSL-related errors trigger retry. Other database errors
    (constraint violations, syntax errors, etc.) are raised immediately.
    """
    max_attempts = 2 if USE_POSTGRESQL else 1
    last_error = None
    
    for attempt in range(max_attempts):
        conn = None
        discard_connection = False
        
        try:
            conn = get_db_connection()
            result = _execute_query_internal(query, params, fetch, fetchone, commit, conn)
            return_db_connection(conn, discard=False)
            return result

        except Exception as e:
            last_error = e
            
            # Check if this is an SSL error that requires discarding the connection
            if USE_POSTGRESQL and _is_stale_ssl_connection_error(e):
                discard_connection = True
                
                if attempt < max_attempts - 1:
                    # Log the retry attempt
                    logger.warning(
                        "SSL connection error on attempt %d/%d, retrying with fresh connection: %s",
                        attempt + 1, max_attempts, e
                    )
                else:
                    # Last attempt failed
                    logger.error(
                        "SSL connection error on final attempt %d/%d: %s",
                        attempt + 1, max_attempts, e
                    )
            else:
                # Non-SSL error - don't retry
                discard_connection = False
            
            # Attempt rollback
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    # Rollback may fail if connection is already broken
                    discard_connection = True
                
                return_db_connection(conn, discard=discard_connection)
            
            # Only retry for SSL errors
            if not (USE_POSTGRESQL and _is_stale_ssl_connection_error(e)):
                raise e
    
    # All retry attempts exhausted
    if last_error:
        raise last_error


# ==========================================
# CONCURRENT QUERY EXECUTION UTILITIES
# ==========================================

# Thread pool executor for concurrent database queries
# This allows multiple independent queries to be executed in parallel,
# reducing total response time for endpoints that need multiple queries.
# Max workers set to 8 to balance parallelism vs resource usage.
_query_executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="db-query")


def _shutdown_query_executor():
    """
    Shutdown the query executor during application exit.
    
    Called via atexit to ensure proper cleanup of executor threads.
    """
    try:
        import sys
        if sys.version_info >= (3, 9):
            _query_executor.shutdown(wait=False, cancel_futures=True)
        else:
            _query_executor.shutdown(wait=False)
    except Exception:
        pass  # Ignore errors during shutdown


# Register query executor shutdown on application exit
atexit.register(_shutdown_query_executor)


def execute_queries_concurrent(queries: list, timeout_seconds: int = 10) -> list:
    """
    Execute multiple independent database queries concurrently.
    
    This function is designed for scenarios where multiple independent queries
    need to be executed (e.g., getting follower count, following count, and
    posts count for a user profile). By executing them concurrently, the total
    time is reduced from sum of individual query times to approximately the
    time of the slowest query.
    
    Performance improvement example:
    - Sequential: 3 queries × 50ms each = 150ms total
    - Concurrent: 3 queries in parallel ≈ 50ms total (3x faster)
    
    Each query is executed with its own connection from the pool to avoid
    connection-level conflicts. Connections are properly returned to the pool
    after each query completes.
    
    Args:
        queries: List of tuples, each containing:
                 (query_sql, params, fetch_mode)
                 where fetch_mode is 'one', 'all', or None (for writes)
        timeout_seconds: Maximum time to wait for all queries to complete
        
    Returns:
        List of results in the same order as the input queries.
        Each result is either the query result or None if the query failed.
        
    Example:
        queries = [
            ("SELECT COUNT(*) as count FROM follows WHERE followed_id = %s", (user_id,), 'one'),
            ("SELECT COUNT(*) as count FROM follows WHERE follower_id = %s", (user_id,), 'one'),
            ("SELECT COUNT(*) as count FROM posts WHERE user_id = %s", (user_id,), 'one'),
        ]
        results = execute_queries_concurrent(queries)
        followers_count = results[0]["count"] if results[0] else 0
        following_count = results[1]["count"] if results[1] else 0
        posts_count = results[2]["count"] if results[2] else 0
    """
    def execute_single_query(query_info):
        """Execute a single query with its own connection."""
        query_sql, params, fetch_mode = query_info
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None
            cursor = conn.cursor()
            
            # Convert SQLite ? placeholders to PostgreSQL %s if using PostgreSQL
            # This allows writing queries with ? placeholders which works for both databases
            executed_query = query_sql.replace("?", "%s") if USE_POSTGRESQL else query_sql
            
            if params:
                cursor.execute(executed_query, params)
            else:
                cursor.execute(executed_query)
            
            result = None
            if fetch_mode == 'one':
                result = cursor.fetchone()
            elif fetch_mode == 'all':
                result = cursor.fetchall()
            
            return result
        except Exception as e:
            logger.warning("Concurrent query failed: %s", e)
            return None
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                return_db_connection(conn)
    
    # Submit all queries to the executor
    futures = []
    for query_info in queries:
        future = _query_executor.submit(execute_single_query, query_info)
        futures.append(future)
    
    # Wait for all futures with a global timeout using concurrent.futures.wait
    # This applies the timeout to all queries collectively rather than per-query
    from concurrent.futures import wait, FIRST_EXCEPTION
    done, not_done = wait(futures, timeout=timeout_seconds, return_when=FIRST_EXCEPTION)
    
    # Collect results in original order
    results = []
    for future in futures:
        if future in done:
            try:
                result = future.result()  # No timeout needed, already done
                results.append(result)
            except Exception as e:
                logger.warning("Concurrent query error: %s", e)
                results.append(None)
        else:
            # Query timed out
            logger.warning("Concurrent query timed out after %ds", timeout_seconds)
            results.append(None)
    
    return results


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


def cleanup_orphaned_extensions(cursor, conn):
    """
    Remove orphaned PostgreSQL extensions that require shared_preload_libraries
    but cannot function without server-side configuration.
    
    This is particularly important for pg_stat_statements which causes errors
    when Railway's monitoring dashboard tries to query it, but the extension
    isn't loaded in shared_preload_libraries.
    
    Also cleans up orphaned tables/views left behind in the public schema
    that may cause errors when monitoring tools try to query them.
    
    Returns True if all cleanup operations succeeded, False if any failed.
    Cleanup failures are non-fatal - the application continues regardless.
    """
    # List of extensions that require shared_preload_libraries and should be removed
    # if they exist but cannot function properly
    orphaned_extensions = ["pg_stat_statements"]
    all_succeeded = True
    
    for ext_name in orphaned_extensions:
        try:
            # Check if the extension is installed
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM pg_extension WHERE extname = %s
                ) as is_installed
                """,
                (ext_name,)
            )
            result = cursor.fetchone()
            is_installed = result["is_installed"] if result else False
            
            if is_installed:
                # Drop the extension to prevent errors from monitoring tools
                # Note: Using CASCADE to remove any dependent objects
                # SQL injection safe: ext_name comes from hardcoded orphaned_extensions list
                # Using psycopg2.sql module for safe identifier handling
                drop_sql = sql.SQL("DROP EXTENSION IF EXISTS {} CASCADE").format(
                    sql.Identifier(ext_name)
                )
                print(f"🧹 Removing orphaned extension '{ext_name}' (requires shared_preload_libraries)")
                cursor.execute(drop_sql)
                conn.commit()
                print(f"✅ Extension '{ext_name}' removed successfully")
            else:
                # Log when extension is not installed (expected state after cleanup)
                print(f"✅ Extension '{ext_name}' not installed (clean state)")
            
        except psycopg2.Error as e:
            # Log the error but don't fail - this is a best-effort cleanup
            error_details = _get_psycopg2_error_details(e)
            print(f"⚠️  Could not remove extension '{ext_name}': {error_details}")
            _safe_rollback(conn)
            all_succeeded = False
        except Exception as e:
            # Log unexpected errors but continue
            print(f"⚠️  Unexpected error cleaning up extension '{ext_name}': {e}")
            _safe_rollback(conn)
            all_succeeded = False
    
    # Also clean up orphaned tables/views in the public schema that may have been
    # left behind by extensions or previous installations. These cause errors when
    # Railway's monitoring dashboard tries to query them (e.g., pg_stat_statements).
    # 
    # If CREATE_DUMMY_PG_STAT_STATEMENTS is enabled, we create a dummy view instead
    # of just dropping the relation. This allows Railway's monitoring queries to
    # succeed with 0 rows instead of failing with an error.
    orphaned_relations = ["pg_stat_statements"]
    
    # Mapping of PostgreSQL relkind codes to human-readable names and DROP statements
    # relkind: 'r' = table, 'v' = view, 'm' = materialized view
    relkind_info = {
        'r': ('TABLE', 'DROP TABLE IF EXISTS public.{} CASCADE'),
        'v': ('VIEW', 'DROP VIEW IF EXISTS public.{} CASCADE'),
        'm': ('MATERIALIZED VIEW', 'DROP MATERIALIZED VIEW IF EXISTS public.{} CASCADE'),
    }
    
    for rel_name in orphaned_relations:
        try:
            # Special handling for pg_stat_statements when dummy view creation is enabled
            if rel_name == "pg_stat_statements" and CREATE_DUMMY_PG_STAT_STATEMENTS:
                # Skip cleanup here - the dummy view will be created after cleanup
                # The create_dummy_pg_stat_statements_view function handles replacing
                # any existing table/view with the dummy view
                print(f"ℹ️  Dummy pg_stat_statements view mode enabled - will create after cleanup")
                continue
            
            # Check if there's a table or view with this name in the public schema
            cursor.execute(
                """
                SELECT relkind FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public' AND c.relname = %s
                """,
                (rel_name,)
            )
            result = cursor.fetchone()
            
            if result:
                relkind = result["relkind"]
                if relkind in relkind_info:
                    kind_name, drop_template = relkind_info[relkind]
                    # Drop the orphaned relation
                    # SQL injection safe: rel_name comes from hardcoded orphaned_relations list
                    drop_sql = sql.SQL(drop_template).format(sql.Identifier(rel_name))
                    print(f"🧹 Removing orphaned {kind_name} 'public.{rel_name}' (causes monitoring errors)")
                    cursor.execute(drop_sql)
                    conn.commit()
                    print(f"✅ Orphaned {kind_name} 'public.{rel_name}' removed successfully")
            else:
                # Log when relation is not found (expected state after cleanup)
                print(f"✅ No orphaned relation 'public.{rel_name}' found (clean state)")

        except psycopg2.Error as e:
            # Log the error but don't fail - this is a best-effort cleanup
            error_details = _get_psycopg2_error_details(e)
            print(f"⚠️  Could not remove orphaned relation 'public.{rel_name}': {error_details}")
            _safe_rollback(conn)
            all_succeeded = False
        except Exception as e:
            # Log unexpected errors but continue
            print(f"⚠️  Unexpected error cleaning up orphaned relation 'public.{rel_name}': {e}")
            _safe_rollback(conn)
            all_succeeded = False
    
    # If dummy pg_stat_statements view creation is enabled, create it now
    if CREATE_DUMMY_PG_STAT_STATEMENTS:
        dummy_view_success = create_dummy_pg_stat_statements_view(cursor, conn)
        if not dummy_view_success:
            all_succeeded = False
    
    return all_succeeded


def create_dummy_pg_stat_statements_view(cursor, conn):
    """
    Create a dummy pg_stat_statements view that returns empty results.
    
    This view satisfies Railway's monitoring queries that periodically run:
    - SET statement_timeout = '30s'; SELECT COUNT(*) FROM public."pg_stat_statements"
    - SET statement_timeout = '30s'; SELECT * FROM public."pg_stat_statements" LIMIT 10
    
    By creating a dummy view that returns no rows, these queries succeed silently
    instead of generating error logs. This reduces log noise while having no impact
    on application functionality.
    
    The view mimics the essential columns from pg_stat_statements that monitoring
    tools typically expect. Since it returns no rows (FALSE WHERE clause), it has
    zero storage overhead.
    
    Returns True if the view was created successfully, False otherwise.
    """
    try:
        # Check if the view or table already exists
        cursor.execute(
            """
            SELECT relkind FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relname = 'pg_stat_statements'
            """
        )
        result = cursor.fetchone()
        
        if result:
            relkind = result["relkind"]
            # Check if it's already a view (relkind = 'v')
            if relkind == 'v':
                # Verify it's our dummy view by checking for the WHERE FALSE clause
                # in the view definition. If it's a real pg_stat_statements view from
                # the extension, it won't have WHERE FALSE.
                cursor.execute(
                    """
                    SELECT pg_get_viewdef('public.pg_stat_statements'::regclass, true) AS definition
                    """
                )
                view_def_result = cursor.fetchone()
                # Check for the specific WHERE FALSE pattern that identifies our dummy view
                # The real pg_stat_statements extension view would not have this pattern
                if view_def_result and "where false" in view_def_result["definition"].lower():
                    print("✅ Dummy pg_stat_statements view already exists (verified by WHERE FALSE)")
                    return True
                else:
                    # It's a view but not our dummy - replace it
                    print("🧹 Replacing existing pg_stat_statements view with dummy view")
                    cursor.execute("DROP VIEW IF EXISTS public.pg_stat_statements CASCADE")
                    conn.commit()
            elif relkind == 'r':
                # It's a table - drop it
                print("🧹 Replacing orphaned TABLE 'public.pg_stat_statements' with dummy view")
                cursor.execute("DROP TABLE IF EXISTS public.pg_stat_statements CASCADE")
                conn.commit()
            elif relkind == 'm':
                # It's a materialized view - drop it
                print("🧹 Replacing orphaned MATERIALIZED VIEW 'public.pg_stat_statements' with dummy view")
                cursor.execute("DROP MATERIALIZED VIEW IF EXISTS public.pg_stat_statements CASCADE")
                conn.commit()
            else:
                # Unknown relkind type - log warning and attempt generic cleanup
                # This handles edge cases like indexes or other PostgreSQL object types
                print(f"⚠️  Unknown relkind '{relkind}' for 'public.pg_stat_statements', attempting cleanup")
                try:
                    # Try DROP VIEW first (most common case), then DROP TABLE as fallback
                    cursor.execute("DROP VIEW IF EXISTS public.pg_stat_statements CASCADE")
                    conn.commit()
                except psycopg2.Error:
                    _safe_rollback(conn)
                    cursor.execute("DROP TABLE IF EXISTS public.pg_stat_statements CASCADE")
                    conn.commit()
        
        # Create the dummy view with essential columns that monitoring tools expect
        # The view returns no rows (WHERE FALSE) so it has zero overhead
        #
        # Column schema is based on pg_stat_statements extension from PostgreSQL 13+
        # Reference: https://www.postgresql.org/docs/current/pgstatstatements.html
        #
        # Compatibility notes:
        # - PostgreSQL 12 and earlier use different column names (e.g., total_time vs total_exec_time)
        # - Railway typically runs PostgreSQL 14+ where this schema is fully compatible
        # - For older PostgreSQL versions, Railway's monitoring may use different queries
        # - This schema covers the core columns used by monitoring tools
        # - If monitoring queries fail due to schema differences, update this definition
        cursor.execute(
            """
            CREATE OR REPLACE VIEW public.pg_stat_statements AS
            SELECT
                0::oid AS userid,
                0::oid AS dbid,
                0::bigint AS queryid,
                ''::text AS query,
                0::bigint AS calls,
                0::double precision AS total_time,
                0::double precision AS min_time,
                0::double precision AS max_time,
                0::double precision AS mean_time,
                0::bigint AS rows,
                0::bigint AS shared_blks_hit,
                0::bigint AS shared_blks_read,
                0::bigint AS shared_blks_dirtied,
                0::bigint AS shared_blks_written,
                0::bigint AS local_blks_hit,
                0::bigint AS local_blks_read,
                0::bigint AS local_blks_dirtied,
                0::bigint AS local_blks_written,
                0::bigint AS temp_blks_read,
                0::bigint AS temp_blks_written,
                0::double precision AS blk_read_time,
                0::double precision AS blk_write_time
            WHERE FALSE
            """
        )
        conn.commit()
        print("✅ Created dummy pg_stat_statements view (Railway monitoring queries will succeed with 0 rows)")
        return True
        
    except psycopg2.Error as e:
        error_details = _get_psycopg2_error_details(e)
        print(f"⚠️  Could not create dummy pg_stat_statements view: {error_details}")
        _safe_rollback(conn)
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error creating dummy pg_stat_statements view: {e}")
        _safe_rollback(conn)
        return False


def init_postgresql_extensions(cursor, conn):
    """
    Initialize PostgreSQL extensions that don't require server-side configuration.
    
    Note: Extensions like pg_stat_statements have been removed because they require
    shared_preload_libraries configuration on the PostgreSQL server, which is not
    available on managed database services like Railway.
    
    Currently, no extensions are configured because all previously listed extensions
    required server-side configuration that is unavailable on Railway.
    
    Returns True if all extensions initialized successfully, False otherwise.
    Extension failures are non-fatal - the application continues regardless.
    """
    success = True
    
    # First, clean up any orphaned extensions that require shared_preload_libraries
    # This prevents errors from Railway's monitoring dashboard trying to query
    # extensions like pg_stat_statements that can't function without server-side config
    cleanup_success = cleanup_orphaned_extensions(cursor, conn)
    if not cleanup_success:
        print("⚠️  Some orphaned extensions could not be cleaned up, but this is non-fatal")
    
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
                        company_name VARCHAR(200),
                        skills TEXT,
                        experience TEXT,
                        education TEXT
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

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS friendships (
                        id SERIAL PRIMARY KEY,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(sender_id, receiver_id),
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        participant_1_id INTEGER NOT NULL,
                        participant_2_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(participant_1_id, participant_2_id),
                        FOREIGN KEY (participant_1_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (participant_2_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        conversation_id INTEGER NOT NULL,
                        sender_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
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
                        company_name TEXT,
                        skills TEXT,
                        experience TEXT,
                        education TEXT
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

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS friendships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(sender_id, receiver_id),
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        participant_1_id INTEGER NOT NULL,
                        participant_2_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(participant_1_id, participant_2_id),
                        FOREIGN KEY (participant_1_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (participant_2_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id INTEGER NOT NULL,
                        sender_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        is_read INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
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
            
            # Run migrations to create missing tables
            migrate_missing_tables(cursor, conn)
            
            # Ensure indexes exist (idempotent)
            create_database_indexes(cursor, conn)

        cursor.close()
        return_db_connection(conn)

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
            return_db_connection(conn, discard=True)
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
            return_db_connection(conn, discard=True)
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
            # Speeds up username lookups (user profile by username)
            ("users_username_idx", "CREATE INDEX IF NOT EXISTS users_username_idx ON users (username) WHERE username IS NOT NULL"),
            # Speeds up user's posts queries
            ("posts_user_id_idx", "CREATE INDEX IF NOT EXISTS posts_user_id_idx ON posts (user_id)"),
            # Speeds up posts ordering by date
            ("posts_created_at_idx", "CREATE INDEX IF NOT EXISTS posts_created_at_idx ON posts (created_at DESC)"),
            # Composite index for posts feed (user_id + created_at for efficient pagination)
            ("posts_user_created_idx", "CREATE INDEX IF NOT EXISTS posts_user_created_idx ON posts (user_id, created_at DESC)"),
            # Speeds up job searches
            ("jobs_is_active_idx", "CREATE INDEX IF NOT EXISTS jobs_is_active_idx ON jobs (is_active) WHERE is_active = TRUE"),
            ("jobs_created_at_idx", "CREATE INDEX IF NOT EXISTS jobs_created_at_idx ON jobs (created_at DESC)"),
            # Composite index for job filtering by category
            ("jobs_category_active_idx", "CREATE INDEX IF NOT EXISTS jobs_category_active_idx ON jobs (category, is_active) WHERE is_active = TRUE"),
            # Composite index for job filtering by location
            ("jobs_location_active_idx", "CREATE INDEX IF NOT EXISTS jobs_location_active_idx ON jobs (location, is_active) WHERE is_active = TRUE"),
            # Speeds up followers list queries - prevents HTTP 499 timeouts from slow queries
            ("follows_follower_id_idx", "CREATE INDEX IF NOT EXISTS follows_follower_id_idx ON follows (follower_id)"),
            # Speeds up following list queries - prevents HTTP 499 timeouts from slow queries
            ("follows_followed_id_idx", "CREATE INDEX IF NOT EXISTS follows_followed_id_idx ON follows (followed_id)"),
            # Composite index for friendship checks (both directions)
            ("friendships_sender_receiver_idx", "CREATE INDEX IF NOT EXISTS friendships_sender_receiver_idx ON friendships (sender_id, receiver_id)"),
            # Speeds up conversation lookups
            ("conversations_participants_idx", "CREATE INDEX IF NOT EXISTS conversations_participants_idx ON conversations (participant_1_id, participant_2_id)"),
            # Speeds up message retrieval for conversations
            ("messages_conversation_idx", "CREATE INDEX IF NOT EXISTS messages_conversation_idx ON messages (conversation_id, created_at)"),
            # Speeds up unread message count queries
            ("messages_unread_idx", "CREATE INDEX IF NOT EXISTS messages_unread_idx ON messages (is_read, sender_id) WHERE is_read = FALSE"),
            # Speeds up likes count queries
            ("likes_post_id_idx", "CREATE INDEX IF NOT EXISTS likes_post_id_idx ON likes (post_id)"),
            # Speeds up comments count queries
            ("comments_post_id_idx", "CREATE INDEX IF NOT EXISTS comments_post_id_idx ON comments (post_id)"),
            # Composite index for user profile queries (created_at for sorting new users)
            ("users_created_at_idx", "CREATE INDEX IF NOT EXISTS users_created_at_idx ON users (created_at DESC) WHERE is_active = TRUE"),
            # Full-text search index for job title and description (GIN index for text search)
            # Uses COALESCE to handle null values in title or description
            ("jobs_search_idx", "CREATE INDEX IF NOT EXISTS jobs_search_idx ON jobs USING GIN (to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''))) WHERE is_active = TRUE"),
            # Index for stories expiration (speeds up cleanup queries)
            ("stories_expires_at_idx", "CREATE INDEX IF NOT EXISTS stories_expires_at_idx ON stories (expires_at) WHERE expires_at > NOW()"),
            # Composite index for friendship status lookups (both directions)
            ("friendships_receiver_sender_idx", "CREATE INDEX IF NOT EXISTS friendships_receiver_sender_idx ON friendships (receiver_id, sender_id)"),
            # Index for pending friendship requests (partial index for efficiency)
            ("friendships_pending_idx", "CREATE INDEX IF NOT EXISTS friendships_pending_idx ON friendships (receiver_id, status) WHERE status = 'pending'"),
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
            cursor.execute("CREATE INDEX IF NOT EXISTS posts_user_created_idx ON posts (user_id, created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS jobs_is_active_idx ON jobs (is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS jobs_created_at_idx ON jobs (created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS jobs_category_idx ON jobs (category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS jobs_location_idx ON jobs (location)")
            # Indexes for follows table to speed up followers/following list queries
            cursor.execute("CREATE INDEX IF NOT EXISTS follows_follower_id_idx ON follows (follower_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS follows_followed_id_idx ON follows (followed_id)")
            # Indexes for messaging system
            cursor.execute("CREATE INDEX IF NOT EXISTS messages_conversation_idx ON messages (conversation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS likes_post_id_idx ON likes (post_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS comments_post_id_idx ON comments (post_id)")
            # Additional indexes matching PostgreSQL for consistency
            cursor.execute("CREATE INDEX IF NOT EXISTS users_created_at_idx ON users (created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS friendships_sender_receiver_idx ON friendships (sender_id, receiver_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS friendships_receiver_sender_idx ON friendships (receiver_id, sender_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS friendships_pending_idx ON friendships (receiver_id, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS stories_expires_at_idx ON stories (expires_at)")
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
            ("skills", "TEXT"),
            ("experience", "TEXT"),
            ("education", "TEXT"),
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


def migrate_missing_tables(cursor, conn):
    """Create missing tables if they don't exist (for database migrations)"""
    try:
        if USE_POSTGRESQL:
            # Check and create follows table
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'follows'
                ) as table_exists
            """
            )
            if not cursor.fetchone()["table_exists"]:
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
                conn.commit()
                print("✅ Created missing 'follows' table")

            # Check and create friendships table
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'friendships'
                ) as table_exists
            """
            )
            if not cursor.fetchone()["table_exists"]:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS friendships (
                        id SERIAL PRIMARY KEY,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(sender_id, receiver_id),
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )
                conn.commit()
                print("✅ Created missing 'friendships' table")

            # Check and create stories table
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'stories'
                ) as table_exists
            """
            )
            if not cursor.fetchone()["table_exists"]:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS stories (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        media_url TEXT NOT NULL,
                        media_type VARCHAR(50) NOT NULL,
                        caption TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL,
                        views INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )
                conn.commit()
                print("✅ Created missing 'stories' table")

            # Check and create comments table
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'comments'
                ) as table_exists
            """
            )
            if not cursor.fetchone()["table_exists"]:
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
                conn.commit()
                print("✅ Created missing 'comments' table")

            # Check and create likes table
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'likes'
                ) as table_exists
            """
            )
            if not cursor.fetchone()["table_exists"]:
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
                conn.commit()
                print("✅ Created missing 'likes' table")

            # Check and create conversations table
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'conversations'
                ) as table_exists
            """
            )
            if not cursor.fetchone()["table_exists"]:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        participant_1_id INTEGER NOT NULL,
                        participant_2_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(participant_1_id, participant_2_id),
                        FOREIGN KEY (participant_1_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (participant_2_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )
                conn.commit()
                print("✅ Created missing 'conversations' table")

            # Check and create messages table
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'messages'
                ) as table_exists
            """
            )
            if not cursor.fetchone()["table_exists"]:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        conversation_id INTEGER NOT NULL,
                        sender_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )
                conn.commit()
                print("✅ Created missing 'messages' table")

        else:
            # SQLite version
            # Check and create follows table
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='follows'
            """
            )
            if cursor.fetchone() is None:
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
                print("✅ Created missing 'follows' table")

            # Check and create friendships table
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='friendships'
            """
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS friendships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender_id INTEGER NOT NULL,
                        receiver_id INTEGER NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(sender_id, receiver_id),
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )
                conn.commit()
                print("✅ Created missing 'friendships' table")

            # Check and create stories table
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='stories'
            """
            )
            if cursor.fetchone() is None:
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
                conn.commit()
                print("✅ Created missing 'stories' table")

            # Check and create comments table
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='comments'
            """
            )
            if cursor.fetchone() is None:
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
                conn.commit()
                print("✅ Created missing 'comments' table")

            # Check and create likes table
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='likes'
            """
            )
            if cursor.fetchone() is None:
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
                conn.commit()
                print("✅ Created missing 'likes' table")

            # Check and create conversations table
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='conversations'
            """
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        participant_1_id INTEGER NOT NULL,
                        participant_2_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(participant_1_id, participant_2_id),
                        FOREIGN KEY (participant_1_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (participant_2_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )
                conn.commit()
                print("✅ Created missing 'conversations' table")

            # Check and create messages table
            cursor.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='messages'
            """
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id INTEGER NOT NULL,
                        sender_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        is_read INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE,
                        FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """
                )
                conn.commit()
                print("✅ Created missing 'messages' table")

    except Exception as e:
        print(f"⚠️ Table migration warning: {e}")


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
        
        # Check if error indicates database is in recovery mode (explicit PostgreSQL startup/recovery)
        # These patterns indicate PostgreSQL is actively recovering from improper shutdown
        recovery_patterns = ["the database system is starting up", "the database system is in recovery"]
        is_recovery = any(pattern in error_msg for pattern in recovery_patterns)
        
        if is_recovery:
            return {
                "type": "postgresql",
                "in_recovery": True,
                "status": "startup_or_recovery",
                "message": "Database is starting up or recovering. Connections may be temporarily unavailable."
            }
        
        # Check if error indicates container transitioning or not yet available
        # Use the shared ALL_TRANSITIONING_PATTERNS constant for consistency
        if any(pattern in error_msg for pattern in ALL_TRANSITIONING_PATTERNS):
            return {
                "type": "postgresql",
                "in_recovery": None,
                "status": "container_transitioning",
                "message": (
                    "The database container is starting up or transitioning. "
                    "Please wait a moment and try again. This typically resolves within 30-60 seconds."
                )
            }
        
        return {
            "type": "postgresql",
            "in_recovery": None,
            "status": "connection_error",
            "error": str(e)[:200],
            "message": "Database connection error. Please try again in a moment."
        }
        
    except Exception as e:
        return {
            "type": "postgresql",
            "in_recovery": None,
            "status": "error",
            "error": str(e)[:200],
            "message": "An unexpected error occurred while checking database status."
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
            # Warm up the connection pool to reduce first-request latency
            # This is especially important for mobile clients with short timeouts
            _warmup_connection_pool()
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

print("🏥 IMMORTAL HEALTH ENDPOINTS LOADED — /health (GET+HEAD), /ready, /ping — RENDER CANNOT STOP ME")


# ==========================================
# DATABASE KEEPALIVE
# ==========================================

# Database keepalive configuration
# Keeps database connections alive to prevent connection pool timeout issues
# when web services restart from sleep (Railway/Render free tier sleep after 15 min)
#
# Enabled when:
# - Running on Railway (IS_RAILWAY=True, detected via RAILWAY_PROJECT_ID), OR
# - Running on Render (IS_RENDER=True, detected via RENDER env var), OR
# - Running in production environment (IS_PRODUCTION=True)
# AND PostgreSQL is configured (USE_POSTGRESQL=True)
#
# This ensures the keepalive runs on production platforms to maintain
# fresh database connections after any cold start or restart event.
#
# Note: For Render free tier, the web service itself also sleeps after 15 minutes.
# Use an external pinger (UptimeRobot, Healthchecks.io) or upgrade to paid plan.
# See docs/RENDER_502_FIX_GUIDE.md for complete instructions.
DB_KEEPALIVE_ENABLED = (IS_PRODUCTION or IS_RAILWAY or IS_RENDER) and USE_POSTGRESQL
# Ping database every 2 minutes (120s) to keep connections fresh
# This provides a safety margin for maintaining connection pool health
DB_KEEPALIVE_INTERVAL_SECONDS = int(os.getenv("DB_KEEPALIVE_INTERVAL_SECONDS", "120"))  # 2 minutes
DB_KEEPALIVE_FAILURE_THRESHOLD = 3  # Number of consecutive failures before warning
DB_KEEPALIVE_ERROR_RETRY_DELAY_SECONDS = 60  # Delay before retrying after unexpected error
DB_KEEPALIVE_SHUTDOWN_TIMEOUT_SECONDS = 5  # Max time to wait for graceful shutdown

# Aggressive keepalive for the first period after startup
# This helps ensure the database stays awake right after deployment
# Extended to 4 hours (14400s) to provide longer protection during
# initial usage patterns when database sleep is most likely to cause issues.
DB_KEEPALIVE_AGGRESSIVE_PERIOD_SECONDS = int(os.getenv("DB_KEEPALIVE_AGGRESSIVE_PERIOD_SECONDS", "14400"))  # 4 hours
DB_KEEPALIVE_AGGRESSIVE_INTERVAL_SECONDS = int(os.getenv("DB_KEEPALIVE_AGGRESSIVE_INTERVAL_SECONDS", "60"))  # 1 minute

# Initial warm-up ping configuration
# Perform multiple pings on startup to ensure database is fully awake
DB_KEEPALIVE_WARMUP_PING_COUNT = 5  # Increased from 3 for more thorough warm-up
DB_KEEPALIVE_WARMUP_PING_DELAY_SECONDS = 2  # Delay between warm-up pings
DB_KEEPALIVE_WARMUP_RETRY_DELAY_MULTIPLIER = 2  # Multiply delay for retry on failure

# Thread health monitoring - restart keepalive if thread dies
DB_KEEPALIVE_HEALTH_CHECK_INTERVAL_SECONDS = 60  # Check thread health every minute
DB_KEEPALIVE_MAX_PING_AGE_SECONDS = 300  # Consider thread dead if no ping for 5 minutes

# Periodic cleanup of pg_stat_statements extension
# This prevents Railway's monitoring dashboard from getting errors when it tries
# to query pg_stat_statements (which requires shared_preload_libraries configuration)
# Cleanup runs every hour (3600 seconds) to catch any newly created extensions
DB_EXTENSION_CLEANUP_INTERVAL_SECONDS = int(os.getenv("DB_EXTENSION_CLEANUP_INTERVAL_SECONDS", "3600"))

# Disable periodic extension cleanup entirely
# Set to "true" to prevent the periodic extension cleanup from running.
# The initial cleanup at startup will still run to set up the dummy view.
# This is useful if you want to eliminate the "Periodic extension cleanup failed" warnings
# that occur when the database connection times out.
# Default: "false" (cleanup enabled)
DISABLE_EXTENSION_CLEANUP = os.getenv("DISABLE_EXTENSION_CLEANUP", "false").lower() == "true"

# Create a dummy pg_stat_statements view to satisfy Railway's monitoring queries
# When enabled, instead of dropping the pg_stat_statements table/view, we create a
# dummy empty view that returns no rows. This allows Railway's monitoring queries
# (SELECT COUNT(*) FROM public."pg_stat_statements") to succeed with 0 rows instead
# of failing with an error. This reduces log noise from Railway's monitoring.
# Set to "true" to enable this behavior.
CREATE_DUMMY_PG_STAT_STATEMENTS = os.getenv("CREATE_DUMMY_PG_STAT_STATEMENTS", "true").lower() == "true"

# Suppress extension cleanup failure logs for transient connection errors
# Set to "true" to hide warnings when periodic extension cleanup fails due to
# database connection timeouts. Since the cleanup is non-critical (only cosmetic),
# these warnings can be safely suppressed.
# Default: "true" (suppress transient error warnings)
SUPPRESS_EXTENSION_CLEANUP_WARNINGS = os.getenv("SUPPRESS_EXTENSION_CLEANUP_WARNINGS", "true").lower() == "true"

# Track keepalive thread and status
_keepalive_thread = None
_keepalive_running = False
_keepalive_last_ping = None
_keepalive_consecutive_failures = 0
_keepalive_start_time = None  # Track when keepalive started for aggressive mode
_keepalive_total_pings = 0  # Track total successful pings for monitoring
_last_extension_cleanup = None  # Track when we last cleaned up orphaned extensions

# Connection error indicators for detecting transient database issues
# These patterns indicate network/connection problems that are typically transient
# Using specific phrases to avoid false positives with generic terms
CONNECTION_ERROR_PATTERNS = frozenset([
    "connection timed out", "connection refused", "connection reset",
    "connect timeout", "network unreachable", "no route to host",
    "broken pipe", "connection closed unexpectedly", "server closed the connection",
    "ssl connection has been closed", "could not connect", "failed to connect",
    "unable to connect", "lost connection", "connection lost"
])


def _is_connection_error(error_message: str) -> bool:
    """
    Check if an error message indicates a transient connection error.
    
    This function checks for common patterns in error messages that indicate
    network or connection issues (timeouts, refused connections, etc.).
    These errors are typically transient and the operation can be retried later.
    
    Args:
        error_message: The error message to check
        
    Returns:
        True if the error appears to be a connection-related issue
    """
    if not error_message:
        return False
    error_lower = error_message.lower()
    return any(pattern in error_lower for pattern in CONNECTION_ERROR_PATTERNS)


def _log_cleanup_warning(message: str, is_connection_error: bool = False) -> None:
    """
    Log a cleanup warning message, respecting suppression settings.
    
    If SUPPRESS_EXTENSION_CLEANUP_WARNINGS is True and the error is a
    connection-related issue, the warning will be suppressed.
    
    Args:
        message: The warning message to log
        is_connection_error: Whether this is a connection-related error
    """
    if SUPPRESS_EXTENSION_CLEANUP_WARNINGS and is_connection_error:
        return
    print(message)


def should_run_extension_cleanup():
    """
    Determine if extension cleanup should run based on elapsed time.
    
    This function checks the global `_last_extension_cleanup` variable to decide
    whether to run the cleanup:
    - Returns False if DISABLE_EXTENSION_CLEANUP is True
    - Returns True on the first call (when `_last_extension_cleanup` is None)
    - Returns True if `DB_EXTENSION_CLEANUP_INTERVAL_SECONDS` has passed since last cleanup
    - Returns False otherwise
    
    Returns:
        True if cleanup should run, False otherwise
    """
    global _last_extension_cleanup
    
    # If cleanup is disabled via environment variable, skip it
    if DISABLE_EXTENSION_CLEANUP:
        return False
    
    if _last_extension_cleanup is None:
        # First cleanup after startup
        return True
    
    seconds_since_cleanup = (datetime.now(timezone.utc) - _last_extension_cleanup).total_seconds()
    return seconds_since_cleanup >= DB_EXTENSION_CLEANUP_INTERVAL_SECONDS


def periodic_extension_cleanup():
    """
    Perform periodic cleanup of orphaned PostgreSQL extensions.
    
    This function is called periodically by the keepalive worker to remove
    orphaned extensions that require shared_preload_libraries configuration
    (which is not available on Railway's managed PostgreSQL).
    
    Currently cleans up:
    - pg_stat_statements extension and any related orphaned tables/views
    
    The cleanup prevents errors from Railway's monitoring dashboard which tries
    to query pg_stat_statements. Without this cleanup, queries fail with:
    "ERROR: pg_stat_statements must be loaded via shared_preload_libraries"
    
    The cleanup is non-blocking and failures are logged but don't affect other operations.
    Updates `_last_extension_cleanup` timestamp after each cleanup attempt.
    
    Connection timeout errors are suppressed by default (controlled by
    SUPPRESS_EXTENSION_CLEANUP_WARNINGS) since they are transient and the
    cleanup is non-critical.
    
    Returns:
        True if cleanup was successful or not needed, False if cleanup failed
    """
    global _last_extension_cleanup
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        if conn is None:
            # Connection failed - treat as transient since cleanup is non-critical
            # When the connection pool can't provide a connection, it's typically
            # due to pool exhaustion, database unreachable, or network issues
            _log_cleanup_warning(
                "⚠️ Periodic extension cleanup skipped: could not get database connection",
                is_connection_error=True  # Treat as connection error for suppression
            )
            # Update timestamp even on failure to prevent retry storms when DB is down
            # Since cleanup is non-critical, waiting for next interval is acceptable
            _last_extension_cleanup = datetime.now(timezone.utc)
            return False
        
        cursor = conn.cursor()
        
        # Call the existing cleanup function
        success = cleanup_orphaned_extensions(cursor, conn)
        
        _last_extension_cleanup = datetime.now(timezone.utc)
        
        if success:
            print(f"✅ Periodic extension cleanup completed at {_last_extension_cleanup.isoformat()}")
        else:
            _log_cleanup_warning(
                f"⚠️ Periodic extension cleanup had some issues at {_last_extension_cleanup.isoformat()}",
                is_connection_error=False
            )
        
        return success
        
    except Exception as e:
        error_msg = str(e)[:100]
        is_conn_error = _is_connection_error(error_msg)
        _log_cleanup_warning(
            f"⚠️ Periodic extension cleanup failed: {error_msg}",
            is_connection_error=is_conn_error
        )
        _last_extension_cleanup = datetime.now(timezone.utc)  # Update time even on failure
        return False
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


def database_keepalive_worker():
    """
    Background worker that periodically pings the database to prevent it from sleeping.
    
    Railway databases on free/hobby tiers sleep after 15 minutes of inactivity.
    This worker uses an adaptive interval strategy:
    - Aggressive mode (first 4 hours): Ping every 1 minute to ensure database stays awake
    - Normal mode (after 4 hours): Ping every 2 minutes for maintenance
    
    The keepalive uses a simple SELECT 1 query that:
    - Wakes up sleeping connections
    - Verifies connection pool health
    - Minimal resource overhead
    - Non-intrusive to production operations
    
    Additionally, the worker periodically cleans up orphaned PostgreSQL extensions
    (like pg_stat_statements) that cause errors in Railway's monitoring dashboard.
    """
    global _keepalive_running, _keepalive_last_ping, _keepalive_consecutive_failures
    global _keepalive_start_time, _keepalive_total_pings, _last_extension_cleanup
    
    _keepalive_running = True
    _keepalive_start_time = datetime.now(timezone.utc)
    _keepalive_total_pings = 0
    
    print(f"🔄 Database keepalive started (AGGRESSIVE MODE)")
    print(f"   Aggressive mode: {DB_KEEPALIVE_AGGRESSIVE_INTERVAL_SECONDS}s interval for first {DB_KEEPALIVE_AGGRESSIVE_PERIOD_SECONDS}s ({DB_KEEPALIVE_AGGRESSIVE_PERIOD_SECONDS // 3600}h)")
    print(f"   Normal mode: {DB_KEEPALIVE_INTERVAL_SECONDS}s interval after")
    
    # Perform aggressive initial pings to ensure database is fully awake
    # Railway databases may take multiple queries to fully wake up after sleeping
    for i in range(DB_KEEPALIVE_WARMUP_PING_COUNT):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return_db_connection(conn)
            _keepalive_last_ping = datetime.now(timezone.utc)
            _keepalive_total_pings += 1
            
            if i == 0:
                print(f"✅ Initial database keepalive ping {i + 1}/{DB_KEEPALIVE_WARMUP_PING_COUNT} successful")
            else:
                print(f"✅ Database warm-up ping {i + 1}/{DB_KEEPALIVE_WARMUP_PING_COUNT} successful")
            
            # Short delay between warm-up pings
            if i < DB_KEEPALIVE_WARMUP_PING_COUNT - 1:
                time.sleep(DB_KEEPALIVE_WARMUP_PING_DELAY_SECONDS)
                
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            # Provide more detailed diagnostics for common errors
            if "password authentication failed" in error_msg:
                print(f"⚠️ Initial database keepalive ping {i + 1}/{DB_KEEPALIVE_WARMUP_PING_COUNT} failed: PASSWORD AUTHENTICATION ERROR")
                print("   The database password appears to be incorrect or the user doesn't exist.")
                print("   Please verify DATABASE_URL environment variable has correct credentials.")
            elif "could not connect to server" in error_msg:
                print(f"⚠️ Initial database keepalive ping {i + 1}/{DB_KEEPALIVE_WARMUP_PING_COUNT} failed: CONNECTION ERROR")
                print("   Cannot reach database server. Check network/firewall settings.")
            else:
                print(f"⚠️ Initial database keepalive ping {i + 1}/{DB_KEEPALIVE_WARMUP_PING_COUNT} failed: {error_msg[:100]}")
            
            _keepalive_consecutive_failures += 1
            # Wait a bit longer before retry on failure
            if i < DB_KEEPALIVE_WARMUP_PING_COUNT - 1:
                time.sleep(DB_KEEPALIVE_WARMUP_PING_DELAY_SECONDS * DB_KEEPALIVE_WARMUP_RETRY_DELAY_MULTIPLIER)
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"⚠️ Initial database keepalive ping {i + 1}/{DB_KEEPALIVE_WARMUP_PING_COUNT} failed: {error_msg}")
            _keepalive_consecutive_failures += 1
            # Wait a bit longer before retry on failure
            if i < DB_KEEPALIVE_WARMUP_PING_COUNT - 1:
                time.sleep(DB_KEEPALIVE_WARMUP_PING_DELAY_SECONDS * DB_KEEPALIVE_WARMUP_RETRY_DELAY_MULTIPLIER)
    
    print(f"🔥 Database warm-up complete, entering aggressive mode (ping every {DB_KEEPALIVE_AGGRESSIVE_INTERVAL_SECONDS}s)")
    
    # Perform initial extension cleanup immediately after warm-up
    # This ensures pg_stat_statements is removed as soon as the keepalive starts
    print("🧹 Performing initial extension cleanup...")
    periodic_extension_cleanup()
    
    # Flag to track if we've transitioned to normal mode
    transitioned_to_normal = False
    
    while _keepalive_running:
        try:
            # Determine current interval based on how long keepalive has been running
            elapsed_seconds = (datetime.now(timezone.utc) - _keepalive_start_time).total_seconds()
            
            if elapsed_seconds < DB_KEEPALIVE_AGGRESSIVE_PERIOD_SECONDS:
                # Aggressive mode - more frequent pings right after deployment
                current_interval = DB_KEEPALIVE_AGGRESSIVE_INTERVAL_SECONDS
                mode = "aggressive"
            else:
                # Normal mode - standard interval (still aggressive at 2 min)
                current_interval = DB_KEEPALIVE_INTERVAL_SECONDS
                mode = "normal"
                
                # Log transition to normal mode once
                if not transitioned_to_normal:
                    transitioned_to_normal = True
                    print(f"📊 Transitioning to normal keepalive mode (ping every {DB_KEEPALIVE_INTERVAL_SECONDS}s)")
            
            # Wait for the interval before next ping
            time.sleep(current_interval)
            
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
                _keepalive_total_pings += 1
                
                # Log every ping to ensure visibility
                elapsed_hours = elapsed_seconds / 3600
                print(f"✅ Database keepalive ping #{_keepalive_total_pings} [{mode}] at {_keepalive_last_ping.isoformat()} (uptime: {elapsed_hours:.1f}h)")
                
                # Perform periodic extension cleanup to remove pg_stat_statements
                # This prevents errors in Railway's monitoring dashboard
                if should_run_extension_cleanup():
                    periodic_extension_cleanup()
                
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


def ensure_keepalive_running():
    """
    Check if the keepalive thread is running and restart if necessary.
    
    This function provides automatic recovery if the keepalive thread crashes.
    Called from the health check endpoint to ensure continuous operation.
    
    Returns:
        dict: Status of the keepalive thread with recovery information
    """
    global _keepalive_thread, _keepalive_running, _keepalive_last_ping
    
    if not DB_KEEPALIVE_ENABLED:
        return {"status": "disabled", "reason": "Not in production or Railway environment"}
    
    thread_alive = _keepalive_thread is not None and _keepalive_thread.is_alive()
    
    # Check if thread is alive
    if thread_alive:
        # Check if last ping is too old (thread might be stuck)
        if _keepalive_last_ping:
            seconds_since_ping = (datetime.now(timezone.utc) - _keepalive_last_ping).total_seconds()
            if seconds_since_ping > DB_KEEPALIVE_MAX_PING_AGE_SECONDS:
                print(f"⚠️ Keepalive thread appears stuck (no ping for {seconds_since_ping:.0f}s), restarting...")
                _keepalive_running = False
                _keepalive_thread.join(timeout=2)
                thread_alive = False
        
        if thread_alive:
            return {
                "status": "running",
                "thread_alive": True,
                "total_pings": _keepalive_total_pings,
            }
    
    # Thread is not alive, try to restart
    print("⚠️ Keepalive thread not running, attempting restart...")
    _keepalive_running = False  # Reset flag
    
    try:
        _keepalive_thread = threading.Thread(
            target=database_keepalive_worker,
            daemon=True,
            name="db-keepalive"
        )
        _keepalive_thread.start()
        print("✅ Database keepalive thread restarted successfully")
        return {
            "status": "restarted",
            "thread_alive": True,
            "message": "Keepalive thread was dead and has been restarted"
        }
    except Exception as e:
        print(f"❌ Failed to restart keepalive thread: {e}")
        return {
            "status": "failed",
            "thread_alive": False,
            "error": str(e)[:100]
        }


def perform_database_ping():
    """
    Perform a direct database ping to keep the connection alive.
    
    This function can be called from external sources (like GitHub Actions)
    to ensure the database stays awake, even if the keepalive thread
    is having issues.
    
    Returns:
        dict: Result of the ping attempt with timing information
    """
    ping_start = time.time()
    conn = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as ping, NOW() as server_time")
        result = cursor.fetchone()
        cursor.close()
        return_db_connection(conn)
        
        ping_ms = int((time.time() - ping_start) * 1000)
        
        # Extract server_time from result (RealDictCursor returns dict-like objects)
        # Use safe access pattern to handle both dict and non-dict results
        server_time = None
        if result:
            try:
                # Try dict-style access first (for RealDictCursor)
                server_time = str(result["server_time"])
            except (KeyError, TypeError):
                # Fallback to index access if needed
                try:
                    server_time = str(result[1]) if len(result) > 1 else None
                except (IndexError, TypeError):
                    pass
        
        # Note: We intentionally don't update _keepalive_last_ping here to avoid
        # interfering with the keepalive worker thread's state tracking.
        # The keepalive thread maintains its own timing for interval calculations.
        
        return {
            "success": True,
            "ping_ms": ping_ms,
            "server_time": server_time,
            "message": "Database is awake and responding"
        }
    except Exception as e:
        ping_ms = int((time.time() - ping_start) * 1000)
        error_msg = str(e)[:200]
        
        if conn:
            try:
                return_db_connection(conn, discard=True)
            except Exception:
                pass
        
        return {
            "success": False,
            "ping_ms": ping_ms,
            "error": error_msg,
            "message": "Database ping failed"
        }


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
                    "ping": "/ping",
                    "health": "/health",
                    "health_detailed": "/api/health",
                    "database_wakeup": "/api/database/wakeup",
                    "database_ping": "/api/database/ping",
                    "database_recovery": "/api/database/recovery-status",
                },
            }
        ),
        200,
    )


@app.route("/health", methods=["GET", "HEAD"])
@limiter.exempt
def health_check():
    """
    Lightning-fast health check endpoint for Render/Railway.
    
    Returns 200 OK with {"status":"healthy"} in <10ms.
    No database access, no logging overhead - just a quick response.
    Supports both GET and HEAD methods for maximum compatibility.
    Exempt from rate limiting to allow monitoring services to check frequently.
    """
    return jsonify({"status": "healthy"}), 200


@app.route("/live", methods=["GET", "HEAD"])
@limiter.exempt
def liveness_probe():
    """
    Kubernetes-style liveness probe for container orchestrators.
    
    Returns 200 OK immediately without any external dependency checks.
    Use this endpoint for:
    - Kubernetes livenessProbe configuration
    - Container orchestrator health checks
    - Basic process liveness verification
    
    This endpoint confirms the Python process is running and Flask is responsive.
    It does NOT check database connectivity - use /ready for that.
    
    Supports both GET and HEAD methods for maximum compatibility.
    Exempt from rate limiting to allow monitoring services to check frequently.
    """
    return jsonify({"status": "alive"}), 200


@app.route("/ready", methods=["GET"])
@limiter.exempt
def readiness_probe():
    """
    Database readiness probe for Render/Railway cold start handling.
    
    Returns 200 ONLY when PostgreSQL is fully connected and responsive.
    Returns 503 if database is down or not ready.
    
    Use this as Render Health Check Path: /ready
    Render will wait up to 180s for this to return 200 before routing traffic.
    """
    conn = None
    cursor = None
    try:
        # 5 second timeout for database check
        start_time = time.time()
        
        conn = get_db_connection()
        if conn is None:
            print("🔴 /ready: Database connection unavailable")
            return jsonify({"status": "not_ready", "database": "unavailable"}), 503
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Check if we exceeded 5 second timeout
        if elapsed_ms > 5000:
            print(f"🔴 /ready: Database check timed out ({elapsed_ms}ms)")
            return jsonify({"status": "not_ready", "database": "timeout"}), 503
        
        print(f"🟢 /ready: DATABASE READY! Query completed in {elapsed_ms}ms")
        return jsonify({"status": "ready", "database": "ok", "latency_ms": elapsed_ms}), 200
        
    except Exception as e:
        error_msg = str(e)[:200]
        print(f"🔴 /ready: Database error - {error_msg}")
        return jsonify({"status": "not_ready", "database": "error", "error": error_msg}), 503
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/ping", methods=["GET", "HEAD"])
@limiter.exempt
def ping():
    """
    Simple ping endpoint for scheduled keepalive services.
    
    This lightweight endpoint is optimized for external schedulers (cron jobs,
    uptime monitors, etc.) that need to periodically ping the app to keep it
    active and prevent it from sleeping on free-tier hosting platforms.
    
    Features:
    - Minimal response payload (returns 200 OK with "pong")
    - Supports both GET and HEAD methods
    - Exempt from rate limiting for monitoring services
    - No database access required (app-level health only)
    
    Use this endpoint for:
    - External cron job pings (every 5-10 minutes)
    - Uptime monitoring services (Pingdom, UptimeRobot, etc.)
    - Platform health check configuration
    
    For detailed health status including database connectivity,
    use /api/health instead.
    """
    return "pong", 200


@app.route("/health/ping", methods=["GET", "HEAD"])
@limiter.exempt
def health_ping():
    """
    Simple health ping endpoint for keep-alive workers.
    
    This lightweight endpoint is specifically designed for background workers
    that need to ping the service to prevent it from sleeping. It returns
    a minimal response with a 200 status code.
    
    Features:
    - Minimal response payload (returns 200 OK with "pong")
    - Supports both GET and HEAD methods
    - Exempt from rate limiting for monitoring services
    - No database access required (app-level health only)
    """
    return "pong", 200


@app.route("/api/auth/ping", methods=["GET", "HEAD"])
@limiter.exempt
def auth_ping():
    """
    Simple auth ping endpoint for keep-alive workers.
    
    This lightweight endpoint is specifically designed for background workers
    that need to ping the service to prevent it from sleeping. It returns
    a minimal JSON response with a 200 status code.
    
    Features:
    - Returns {"status": "ok"} for JSON compatibility
    - Supports both GET and HEAD methods
    - Exempt from rate limiting for monitoring services
    - No database access required (app-level health only)
    - Located under /api/auth/ for consistency with other auth endpoints
    """
    return jsonify({"status": "ok"}), 200


@app.route("/api/health", methods=["GET"])
@limiter.exempt
def api_health_check():
    """
    Detailed health check endpoint with database status
    This can be used for monitoring but won't block Railway/Render healthcheck
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
        "is_render": IS_RENDER,
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
            # Determine current mode based on elapsed time
            if _keepalive_start_time:
                elapsed_seconds = (datetime.now(timezone.utc) - _keepalive_start_time).total_seconds()
                is_aggressive_mode = elapsed_seconds < DB_KEEPALIVE_AGGRESSIVE_PERIOD_SECONDS
                current_interval = DB_KEEPALIVE_AGGRESSIVE_INTERVAL_SECONDS if is_aggressive_mode else DB_KEEPALIVE_INTERVAL_SECONDS
                mode = "aggressive" if is_aggressive_mode else "normal"
                time_until_normal = max(0, DB_KEEPALIVE_AGGRESSIVE_PERIOD_SECONDS - elapsed_seconds)
            else:
                current_interval = DB_KEEPALIVE_INTERVAL_SECONDS
                mode = "initializing"
                time_until_normal = None
            
            # Check if keepalive thread is actually running
            thread_alive = _keepalive_thread is not None and _keepalive_thread.is_alive()
            
            keepalive_status = {
                "enabled": True,
                "running": _keepalive_running,
                "thread_alive": thread_alive,
                "mode": mode,
                "current_interval_seconds": current_interval,
                "normal_interval_seconds": DB_KEEPALIVE_INTERVAL_SECONDS,
                "aggressive_interval_seconds": DB_KEEPALIVE_AGGRESSIVE_INTERVAL_SECONDS,
                "consecutive_failures": _keepalive_consecutive_failures,
                "total_pings": _keepalive_total_pings,
            }
            
            if time_until_normal is not None and time_until_normal > 0:
                keepalive_status["seconds_until_normal_mode"] = int(time_until_normal)
            
            if _keepalive_last_ping:
                keepalive_status["last_ping"] = _keepalive_last_ping.isoformat()
                keepalive_status["seconds_since_last_ping"] = (
                    datetime.now(timezone.utc) - _keepalive_last_ping
                ).total_seconds()
            
            if _keepalive_start_time:
                keepalive_status["uptime_hours"] = round(elapsed_seconds / 3600, 2)
            
            response["keepalive"] = keepalive_status
            
            # If thread is not alive, try to restart it
            if not thread_alive and _keepalive_running:
                print("⚠️ Health check detected dead keepalive thread, attempting restart...")
                ensure_keepalive_running()
            
    except Exception as e:
        response["database"] = "error"
        response["status"] = "unhealthy"
        http_status = 503  # Service Unavailable - actual database connection failure
        
        # Keep meaningful error information up to MAX_ERROR_MESSAGE_LENGTH
        error_msg = str(e)
        error_msg_lower = error_msg.lower()
        
        # Check for container transitioning or startup errors
        # Use shared ALL_TRANSITIONING_PATTERNS constant for consistency
        is_transitioning = any(pattern in error_msg_lower for pattern in ALL_TRANSITIONING_PATTERNS)
        
        if is_transitioning:
            response["database_status"] = "transitioning"
            response["user_message"] = (
                "The database container is starting up or transitioning. "
                "Please wait a moment and try again. This typically resolves within 30-60 seconds."
            )
        else:
            response["database_status"] = "connection_error"
            response["user_message"] = (
                "Database connection error. Please try again in a moment."
            )
        
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
    status = recovery_status.get("status")
    if status == "error" or status == "connection_error":
        http_status = 503  # Service unavailable
    elif status == "container_transitioning":
        http_status = 503  # Service unavailable (container transitioning)
    elif recovery_status.get("in_recovery"):
        http_status = 200  # OK, but degraded - service is still functional
    else:
        http_status = 200  # Normal operation
    
    return jsonify({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "recovery": recovery_status,
    }), http_status


@app.route("/api/database/ping", methods=["GET", "POST"])
@limiter.exempt
def database_ping_endpoint():
    """
    Dedicated database ping endpoint to keep PostgreSQL awake.
    
    This endpoint is specifically designed for external services (like GitHub Actions)
    to call periodically to ensure the Railway PostgreSQL database does not go to sleep.
    
    The endpoint:
    - Performs a direct database ping (SELECT 1)
    - Checks and restarts the keepalive thread if necessary
    - Returns detailed status about the database and keepalive health
    
    This acts as a backup mechanism in case the internal keepalive thread
    stops working for any reason.
    
    Returns:
        JSON with:
        - ping_result: Result of the database ping
        - keepalive_status: Status of the background keepalive thread
        - timestamp: Current server time
    
    Exempt from rate limiting to allow monitoring services to call frequently.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Perform database ping
    ping_result = perform_database_ping()
    
    # Check and potentially restart keepalive thread
    keepalive_status = ensure_keepalive_running()
    
    # Add keepalive thread stats
    if DB_KEEPALIVE_ENABLED:
        keepalive_status["total_pings"] = _keepalive_total_pings
        keepalive_status["consecutive_failures"] = _keepalive_consecutive_failures
        if _keepalive_last_ping:
            keepalive_status["last_ping"] = _keepalive_last_ping.isoformat()
            keepalive_status["seconds_since_last_ping"] = (
                datetime.now(timezone.utc) - _keepalive_last_ping
            ).total_seconds()
        if _keepalive_start_time:
            uptime_seconds = (datetime.now(timezone.utc) - _keepalive_start_time).total_seconds()
            keepalive_status["uptime_seconds"] = uptime_seconds
            keepalive_status["uptime_hours"] = round(uptime_seconds / 3600, 2)
    
    # Determine HTTP status
    http_status = 200 if ping_result["success"] else 503
    
    response = {
        "timestamp": timestamp,
        "database": {
            "type": "PostgreSQL" if USE_POSTGRESQL else "SQLite",
            "ping": ping_result,
        },
        "keepalive": keepalive_status,
        "config": {
            "aggressive_interval_seconds": DB_KEEPALIVE_AGGRESSIVE_INTERVAL_SECONDS,
            "normal_interval_seconds": DB_KEEPALIVE_INTERVAL_SECONDS,
            "aggressive_period_seconds": DB_KEEPALIVE_AGGRESSIVE_PERIOD_SECONDS,
        }
    }
    
    # Log the ping for visibility
    if ping_result["success"]:
        print(f"🏓 External database ping successful (ping_ms={ping_result['ping_ms']})")
    else:
        print(f"⚠️ External database ping failed: {ping_result.get('error', 'unknown error')}")
    
    return jsonify(response), http_status


@app.route("/metrics", methods=["GET"])
@limiter.exempt
def prometheus_metrics():
    """
    Prometheus metrics endpoint for monitoring.
    
    Returns metrics in Prometheus text format for scraping by Prometheus server.
    Metrics include:
    - HTTP request counts and durations
    - Database connection pool stats
    - Authentication attempt counts
    - Application uptime
    
    This endpoint is exempt from rate limiting to allow monitoring services
    to scrape metrics frequently (typically every 15-30 seconds).
    
    Integration with Grafana:
    - Add Prometheus as a data source in Grafana
    - Use the provided metrics for dashboards and alerts
    
    Example Prometheus configuration:
        scrape_configs:
          - job_name: 'hiremebahamas'
            metrics_path: '/metrics'
            scrape_interval: 30s
            static_configs:
              - targets: ['your-backend-url:8080']
    """
    from flask import Response
    
    # Try to import metrics module
    try:
        from backend.app.core.metrics import get_metrics_response, set_app_info
        
        # Set app info on each request (idempotent)
        set_app_info(version="1.0.0", environment=ENVIRONMENT)
        
        metrics_data, content_type = get_metrics_response()
        return Response(metrics_data, mimetype=content_type)
    except ImportError:
        # Fallback if prometheus_client is not available
        return Response(
            b"# prometheus_client not installed\n",
            mimetype="text/plain"
        )


# Database wakeup retry configuration
# Base delay for linear backoff (in seconds)
# Each retry waits (WAKEUP_RETRY_BASE_DELAY * attempt_number) seconds
# Using linear backoff (0.5s, 1.0s, 1.5s) rather than exponential since
# database wakeup typically needs only a short wait between attempts
WAKEUP_RETRY_BASE_DELAY = 0.5


@app.route("/api/database/wakeup", methods=["GET", "POST"])
@limiter.exempt
def database_wakeup():
    """
    Wake up the database and verify connectivity.
    
    This endpoint is specifically designed to help users who encounter
    "Database not connecting" errors in Railway's Data tab. It:
    - Performs multiple connection attempts with retries
    - Wakes up sleeping databases
    - Returns detailed connection status
    
    Usage:
    - Call this endpoint before accessing Railway's Data tab
    - Wait for successful response, then refresh Railway dashboard
    
    Returns:
        JSON with:
        - success: Whether database is now accessible
        - attempts: Number of connection attempts made
        - message: Human-readable status message
        - details: Detailed connection information
    
    Exempt from rate limiting to allow multiple wake-up attempts.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    max_attempts = 3
    attempt_results = []
    should_retry = True
    success_response = None
    
    # Try multiple connection attempts to wake up the database
    for attempt in range(1, max_attempts + 1):
        if not should_retry:
            break
            
        ping_start = time.time()
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Execute a simple query to ensure connection is active
            cursor.execute("SELECT 1 as test, NOW() as server_time")
            result = cursor.fetchone()
            
            ping_ms = int((time.time() - ping_start) * 1000)
            
            # Get server time for verification
            server_time = None
            if result:
                server_time = _get_cursor_value(result, "server_time", None)
                if server_time:
                    server_time = str(server_time)
            
            attempt_results.append({
                "attempt": attempt,
                "success": True,
                "ping_ms": ping_ms,
                "server_time": server_time
            })
            
            # Mark success and prepare response (will be returned after cleanup)
            should_retry = False
            success_response = jsonify({
                "success": True,
                "timestamp": timestamp,
                "message": "Database is awake and accepting connections. You can now access Railway's Data tab.",
                "database_type": "PostgreSQL" if USE_POSTGRESQL else "SQLite",
                "attempts": attempt,
                "attempt_details": attempt_results,
                "next_steps": [
                    "Refresh the Railway Dashboard",
                    "Navigate to your PostgreSQL service",
                    "Click on the 'Data' tab",
                    "The database connection should now work"
                ]
            }), 200
            
        except Exception as e:
            ping_ms = int((time.time() - ping_start) * 1000)
            error_msg = str(e)
            
            # Truncate error message using the existing constant and pattern (with ellipsis)
            if len(error_msg) > MAX_ERROR_MESSAGE_LENGTH:
                truncated_error = error_msg[:(MAX_ERROR_MESSAGE_LENGTH - 3)] + "..."
            else:
                truncated_error = error_msg
            
            attempt_results.append({
                "attempt": attempt,
                "success": False,
                "ping_ms": ping_ms,
                "error": truncated_error
            })
        finally:
            # Ensure cursor and connection are always properly cleaned up
            if cursor:
                try:
                    cursor.close()
                except Exception as cleanup_error:
                    # Log cleanup errors for debugging but continue with connection cleanup
                    logger.debug("Cursor close failed during wakeup cleanup: %s", cleanup_error)
            if conn:
                try:
                    return_db_connection(conn)
                except Exception as conn_cleanup_error:
                    # Log connection cleanup errors but don't mask original error
                    logger.debug("Connection cleanup failed during wakeup: %s", conn_cleanup_error)
        
        # Wait briefly before retry (linear backoff) - outside finally block
        if should_retry and attempt < max_attempts:
            time.sleep(WAKEUP_RETRY_BASE_DELAY * attempt)
    
    # Return success response if connection succeeded
    if success_response:
        return success_response
    
    # All attempts failed
    return jsonify({
        "success": False,
        "timestamp": timestamp,
        "message": "Unable to connect to database after multiple attempts. The database may be starting up.",
        "database_type": "PostgreSQL" if USE_POSTGRESQL else "SQLite",
        "attempts": max_attempts,
        "attempt_details": attempt_results,
        "troubleshooting": [
            "Wait 30-60 seconds and try again",
            "Check if PostgreSQL service shows 'Active' in Railway",
            "If PostgreSQL is 'Sleeping', make any API request to wake it",
            "Check Railway status page for any incidents: https://status.railway.app"
        ]
    }), 503


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
    - Request-level timeout check to return proper response before client disconnects
    - Early timeout check before CPU-intensive password hashing
    - Detailed timing logs for performance monitoring and debugging
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    request_id = getattr(g, 'request_id', 'unknown')
    client_type = getattr(g, 'client_type', 'unknown')
    
    # Use the actual request arrival time from middleware for accurate timeout detection
    # g.start_time is set by log_request_start() before_request middleware
    # This catches requests that were queued or delayed before reaching the endpoint
    request_arrival_time = getattr(g, 'start_time', None) or time.time()
    registration_start = time.time()

    try:
        # Early timeout check - useful when request arrives during cold start
        # Uses request_arrival_time to detect requests that have been waiting in queue
        # This is more accurate than using registration_start which is set just now
        if _check_request_timeout(request_arrival_time, REGISTRATION_REQUEST_TIMEOUT_SECONDS, "registration (early check)"):
            return (
                jsonify({
                    "success": False,
                    "message": "Registration request timed out. Please try again."
                }),
                504,  # Gateway Timeout
            )

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
        # bcrypt hashing is CPU-intensive, track timing for performance monitoring
        # Uses BCRYPT_ROUNDS configuration for optimal performance vs security balance
        password_hash_start = time.time()
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        ).decode("utf-8")
        password_hash_ms = int((time.time() - password_hash_start) * 1000)
        
        print(
            f"[{request_id}] Password hashing completed in {password_hash_ms}ms "
            f"(bcrypt rounds: {BCRYPT_ROUNDS}) for registration: {email}"
        )

        # Check for request timeout after password hashing
        if _check_request_timeout(registration_start, REGISTRATION_REQUEST_TIMEOUT_SECONDS, "registration (after password hash)"):
            return (
                jsonify({
                    "success": False,
                    "message": "Registration request timed out. Please try again."
                }),
                504,  # Gateway Timeout
            )

        # Get database connection - use single connection for all operations
        db_start = time.time()
        conn = get_db_connection()
        
        if conn is None:
            # Connection pool exhausted - return 503 to indicate temporary unavailability
            # Note: Email is not logged to avoid exposing sensitive information
            print(
                f"[{request_id}] ⚠️ Connection pool exhausted for registration attempt"
            )
            return (
                jsonify({
                    "success": False,
                    "message": "Service temporarily unavailable. Please try again in a moment."
                }),
                503,
            )
        
        cursor = conn.cursor()

        # Check if user already exists
        if USE_POSTGRESQL:
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = %s", (email,))
        else:
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,))

        db_check_ms = int((time.time() - db_start) * 1000)
        print(
            f"[{request_id}] Database query (email check) completed in {db_check_ms}ms for {email}"
        )

        if cursor.fetchone():
            print(
                f"[{request_id}] Registration failed - User already exists: {email}"
            )
            return (
                jsonify(
                    {"success": False, "message": "User with this email already exists"}
                ),
                409,
            )

        # Check for request timeout after email check
        if _check_request_timeout(registration_start, REGISTRATION_REQUEST_TIMEOUT_SECONDS, "registration (after email check)"):
            return (
                jsonify({
                    "success": False,
                    "message": "Registration request timed out. Please try again."
                }),
                504,  # Gateway Timeout
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

        insert_start = time.time()
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
            cursor.execute(f"SELECT {USER_COLUMNS_FULL} FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()

        insert_ms = int((time.time() - insert_start) * 1000)
        print(
            f"[{request_id}] Database insert completed in {insert_ms}ms for user_id: {user_id}"
        )

        commit_start = time.time()
        conn.commit()
        commit_ms = int((time.time() - commit_start) * 1000)
        
        print(
            f"[{request_id}] Database commit completed in {commit_ms}ms"
        )

        # Note: No timeout check after commit since user is already created in database
        # Returning a timeout error here would leave the user confused - they're registered
        # but receive an error. Better to proceed and complete the registration response.

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

        # Calculate total registration time using registration_start for consistency
        # with timeout checks (which also use registration_start)
        total_registration_ms = int((time.time() - registration_start) * 1000)
        
        print(
            f"[{request_id}] Registration successful - user: {user['email']}, user_id: {user['id']}, "
            f"user_type: {user['user_type']}, client_type: {client_type}, total_time: {total_registration_ms}ms "
            f"(password_hash: {password_hash_ms}ms, db_check: {db_check_ms}ms, "
            f"db_insert: {insert_ms}ms, db_commit: {commit_ms}ms, token_create: {token_create_ms}ms)"
        )
        
        # Warn about slow registration operations
        # Mobile clients are more sensitive to slow responses due to shorter timeout limits
        if total_registration_ms > SLOW_REGISTRATION_THRESHOLD_MS:
            # Build warning message parts
            warning_parts = [
                f"[{request_id}] ⚠️ SLOW REGISTRATION: Total time {total_registration_ms}ms -",
                f"Breakdown: PasswordHash={password_hash_ms}ms, DBCheck={db_check_ms}ms,",
                f"DBInsert={insert_ms}ms, DBCommit={commit_ms}ms, Token={token_create_ms}ms.",
            ]
            if client_type.startswith('mobile'):
                warning_parts.append(f"⚠️ Mobile client ({client_type}) - may cause timeout issues.")
            warning_parts.append("Consider checking connection pool, database performance, or bcrypt configuration.")
            print(" ".join(warning_parts))

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
        print(f"[{request_id}] Registration error: {type(e).__name__}: {str(e)}")
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
    - Redis cache: Checks cache first, skips DB if user found (reduces login to <100ms)
    - Rate limited to 10 requests per minute per IP to prevent pool exhaustion
    - Uses connection pool with 5-second timeout to fail fast
    - Pool expanded to 30 max connections for high concurrency
    - Statement timeout of 30 seconds prevents long-running queries
    - Proper connection cleanup with try/finally pattern
    - Returns connections to pool instead of closing to improve reuse
    - All database operations have timeout protection
    - Email lookup uses LOWER(email) index for fast queries
    - Detailed timing logs for performance monitoring
    - Request-level timeout check to return proper response before client disconnects
    - User data cached for 10 minutes after successful login
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    request_id = getattr(g, 'request_id', 'unknown')
    login_start = time.time()
    cache_hit = False
    db_query_ms = 0
    
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

        # Check for request timeout before cache/database operation
        if _check_request_timeout(login_start, LOGIN_REQUEST_TIMEOUT_SECONDS, "login (before lookup)"):
            return (
                jsonify({
                    "success": False,
                    "message": "Login request timed out. Please try again."
                }),
                504,  # Gateway Timeout
            )

        # Try Redis cache first for fast login (<100ms)
        # This skips the database query entirely if user is cached
        cache_start = time.time()
        user = _get_cached_user_for_login(email)
        cache_lookup_ms = int((time.time() - cache_start) * 1000)
        
        if user is not None:
            cache_hit = True
            print(
                f"[{request_id}] 🚀 Cache HIT for login: {email} (lookup: {cache_lookup_ms}ms)"
            )
            
            # Check if user is active
            if not user.get("is_active", True):
                print(f"[{request_id}] Login failed - User account deactivated: {email}")
                return (
                    jsonify({"success": False, "message": "Account has been deactivated"}),
                    401,
                )
        else:
            # Cache miss - query database
            print(
                f"[{request_id}] Cache MISS for login: {email}, querying database"
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
                cursor.execute(f"SELECT {USER_COLUMNS_LOGIN} FROM users WHERE LOWER(email) = %s", (email,))
            else:
                cursor.execute(f"SELECT {USER_COLUMNS_LOGIN} FROM users WHERE LOWER(email) = ?", (email,))

            user = cursor.fetchone()
            db_query_ms = int((time.time() - db_start) * 1000)
            
            print(
                f"[{request_id}] Database query (email lookup) completed in {db_query_ms}ms for {email}"
            )
            
            # Convert Row to dict for consistent handling
            if user is not None:
                user = dict(user)

        # Check for request timeout after lookup
        if _check_request_timeout(login_start, LOGIN_REQUEST_TIMEOUT_SECONDS, "login (after lookup)"):
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
        if not user.get("password_hash"):
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

        # Check if password hash should be upgraded to current bcrypt rounds
        # This improves future login performance for users with old high-round hashes
        if _should_upgrade_password_hash(user["password_hash"]):
            old_rounds = _get_bcrypt_rounds_from_hash(user["password_hash"])
            print(
                f"[{request_id}] Password hash upgrade needed: {old_rounds} -> {BCRYPT_ROUNDS} rounds for user {user['id']}"
            )
            _upgrade_password_hash_async(user["id"], password, request_id)

        # Update last login (only if we have a DB connection or need to create one)
        now = datetime.now(timezone.utc)
        if cursor is None:
            # We got user from cache, need to update last_login in background
            # to avoid slowing down the login response
            # Capture values as parameters to avoid race conditions
            user_id_for_update = user["id"]
            login_time = now
            
            def _update_last_login_async(uid, ltime):
                """Update last_login in background thread with proper error handling."""
                update_conn = None
                update_cursor = None
                try:
                    update_conn = get_db_connection()
                    if update_conn:
                        update_cursor = update_conn.cursor()
                        if USE_POSTGRESQL:
                            update_cursor.execute(
                                "UPDATE users SET last_login = %s WHERE id = %s", (ltime, uid)
                            )
                        else:
                            update_cursor.execute(
                                "UPDATE users SET last_login = ? WHERE id = ?", (ltime, uid)
                            )
                        update_conn.commit()
                except Exception as e:
                    logger.warning(f"Failed to update last_login for user {uid}: {e}")
                finally:
                    if update_cursor:
                        try:
                            update_cursor.close()
                        except Exception:
                            pass
                    if update_conn:
                        return_db_connection(update_conn)
            
            # Run in background thread with captured parameters
            thread = threading.Thread(
                target=_update_last_login_async, 
                args=(user_id_for_update, login_time),
                daemon=True
            )
            thread.start()
        else:
            # Update directly if we already have a connection
            if USE_POSTGRESQL:
                cursor.execute(
                    "UPDATE users SET last_login = %s WHERE id = %s", (now, user["id"])
                )
            else:
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?", (now, user["id"])
                )
            conn.commit()

        # Cache user data for future logins (10 minute TTL)
        # Only cache on successful password verification
        if not cache_hit:
            cache_success = _cache_user_for_login(email, user)
            if cache_success:
                print(f"[{request_id}] 📦 Cached user for future logins: {email}")

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
            
            cache_status = "cache_hit" if cache_hit else f"db:{db_query_ms}ms"
            print(
                f"[{request_id}] Login successful - user: {user['email']}, user_id: {user['id']}, "
                f"user_type: {user.get('user_type', 'user')}, total_time: {total_login_ms}ms "
                f"({cache_status}, password_verify: {password_verify_ms}ms, "
                f"token_create: {token_create_ms}ms)"
            )
            
            # Warn about slow login operations (only if not cache hit)
            if total_login_ms > 1000 and not cache_hit:  # Over 1 second
                print(
                    f"[{request_id}] ⚠️ SLOW LOGIN: Total time {total_login_ms}ms - "
                    f"Breakdown: DB={db_query_ms}ms, Password={password_verify_ms}ms, "
                    f"Token={token_create_ms}ms. Consider checking connection pool, "
                    f"database performance, or bcrypt configuration (current rounds: {BCRYPT_ROUNDS})."
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
                        "first_name": user.get("first_name") or "",
                        "last_name": user.get("last_name") or "",
                        "user_type": user.get("user_type") or "user",
                        "location": user.get("location") or "",
                        "phone": user.get("phone") or "",
                        "bio": user.get("bio") or "",
                        "avatar_url": user.get("avatar_url") or "",
                        "is_available_for_hire": bool(user.get("is_available_for_hire")),
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
            cursor.execute(f"SELECT {USER_COLUMNS_PUBLIC} FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute(f"SELECT {USER_COLUMNS_PUBLIC} FROM users WHERE id = ?", (user_id,))

        user = cursor.fetchone()
        cursor.close()
        return_db_connection(conn)

        if not user:
            # User ID from token doesn't exist in database anymore
            # This can happen if the database was reset or user was deleted
            # Return 401 to force the client to clear the invalid token and re-login
            return (
                jsonify({
                    "success": False, 
                    "message": "Your account was not found. Please log in again.",
                    "error_code": "USER_NOT_FOUND",
                    "action": "logout"
                }),
                401,
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
            return_db_connection(conn)

            if not user:
                # User ID from token doesn't exist in database anymore
                # This can happen if the database was reset or user was deleted
                # Return 401 to force the client to clear the invalid token and re-login
                return (
                    jsonify({
                        "success": False, 
                        "valid": False,
                        "message": "Your account was not found. Please log in again.",
                        "error_code": "USER_NOT_FOUND",
                        "action": "logout"
                    }),
                    401,
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


@app.route("/api/auth/profile", methods=["GET", "PUT", "OPTIONS"])
def profile():
    """
    Get or update user profile.
    
    GET: Returns cached profile if available (Redis), otherwise queries database.
    PUT: Updates profile and invalidates cache.
    
    Performance: GET requests with Redis cache return in <50ms.
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

        # For GET requests, try Redis cache first
        if request.method == "GET":
            cached_profile = _get_cached_auth_profile(user_id)
            if cached_profile is not None:
                return jsonify(cached_profile), 200

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Handle PUT request (update profile)
            if request.method == "PUT":
                data = request.get_json()
                if not data:
                    cursor.close()
                    return_db_connection(conn)
                    return (
                        jsonify({"success": False, "message": "No data provided"}),
                        400,
                    )

                # Define allowed fields for update (prevents SQL injection and unauthorized field updates)
                allowed_fields = [
                    "first_name", "last_name", "username", "phone", "location",
                    "bio", "occupation", "company_name", "skills", "experience", "education"
                ]

                # Build update query dynamically based on provided fields
                update_fields = []
                update_values = []
                for field in allowed_fields:
                    if field in data:
                        update_fields.append(field)
                        update_values.append(data[field])

                if update_fields:
                    # Build SET clause with parameterized queries
                    if USE_POSTGRESQL:
                        set_clause = ", ".join([f"{field} = %s" for field in update_fields])
                        update_values.append(user_id)
                        cursor.execute(
                            f"UPDATE users SET {set_clause} WHERE id = %s",
                            tuple(update_values)
                        )
                    else:
                        set_clause = ", ".join([f"{field} = ?" for field in update_fields])
                        update_values.append(user_id)
                        cursor.execute(
                            f"UPDATE users SET {set_clause} WHERE id = ?",
                            tuple(update_values)
                        )
                    conn.commit()
                    
                    # Invalidate user profile cache after update
                    invalidate_user_cache(user_id)
                    
                    # Invalidate auth profile cache
                    _invalidate_auth_profile_cache(user_id)
                    
                    # Also invalidate login cache (need to get email first)
                    # This is done after fetching the user below

            # Get user from database (for both GET and after PUT update)
            if USE_POSTGRESQL:
                cursor.execute(f"SELECT {USER_COLUMNS_PUBLIC} FROM users WHERE id = %s", (user_id,))
            else:
                cursor.execute(f"SELECT {USER_COLUMNS_PUBLIC} FROM users WHERE id = ?", (user_id,))

            user = cursor.fetchone()
            
            # Invalidate login cache if profile was updated
            if request.method == "PUT" and user:
                _invalidate_login_cache(user["email"])
            
            cursor.close()
            return_db_connection(conn)

            if not user:
                # User ID from token doesn't exist in database anymore
                # This can happen if the database was reset or user was deleted
                # Return 401 to force the client to clear the invalid token and re-login
                return (
                    jsonify({
                        "success": False, 
                        "message": "Your account was not found. Please log in again.",
                        "error_code": "USER_NOT_FOUND",
                        "action": "logout"
                    }),
                    401,
                )

            # Build profile response
            profile_data = {
                "id": user["id"],
                "email": user["email"],
                "first_name": user["first_name"] or "",
                "last_name": user["last_name"] or "",
                "username": user.get("username") or "",
                "role": user["user_type"] or "user",
                "user_type": user["user_type"] or "user",
                "location": user["location"] or "",
                "phone": user["phone"] or "",
                "bio": user["bio"] or "",
                "occupation": user.get("occupation") or "",
                "company_name": user.get("company_name") or "",
                "skills": user.get("skills") or "",
                "experience": user.get("experience") or "",
                "education": user.get("education") or "",
                "avatar_url": user["avatar_url"] or "",
                "is_available_for_hire": bool(user["is_available_for_hire"]),
                "is_active": bool(user.get("is_active", True)),
                "created_at": str(user["created_at"]) if user.get("created_at") else "",
                "updated_at": str(user.get("last_login")) if user.get("last_login") else "",
            }
            
            # Cache profile for GET requests
            if request.method == "GET":
                _cache_auth_profile(user_id, profile_data)

            return jsonify(profile_data), 200

        except Exception as db_error:
            # Ensure database resources are properly cleaned up
            try:
                cursor.close()
                return_db_connection(conn)
            except Exception:
                pass
            raise db_error

    except Exception as e:
        import traceback
        print(f"Profile error: {str(e)}")
        traceback.print_exc()
        return (
            jsonify({"success": False, "message": f"Profile operation failed: {str(e)}"}),
            500,
        )


# ==========================================
# POSTS ENDPOINTS
# ==========================================


@app.route("/api/posts", methods=["GET", "OPTIONS"])
@cache.cached(timeout=CACHE_TIMEOUT_POSTS, key_prefix="posts_list", query_string=True)
def get_posts():
    """
    Get posts with user information.
    
    Posts are PERMANENTLY stored - never automatically deleted.
    Supports pagination for handling millions of posts efficiently.
    
    Cached for performance optimization (default: 30 seconds).
    Cache is keyed by pagination parameters.
    
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
        return_db_connection(conn)

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
            return_db_connection(conn)
            return (
                jsonify({
                    "success": False, 
                    "message": "Your account was not found. Please log in again.",
                    "error_code": "USER_NOT_FOUND",
                    "action": "logout"
                }),
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
        return_db_connection(conn)

        # Invalidate posts cache after creating a new post
        invalidate_cache_pattern("posts_*")

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
        return_db_connection(conn)

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
            return_db_connection(conn)
            return (
                jsonify({"success": False, "message": "Post not found"}),
                404,
            )

        if post["user_id"] != user_id:
            cursor.close()
            return_db_connection(conn)
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
        return_db_connection(conn)

        # Invalidate posts cache after deleting a post
        invalidate_cache_pattern("posts_*")

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

@app.route("/api/users/<identifier>", methods=["GET", "OPTIONS"])
@cache.cached(timeout=CACHE_TIMEOUT_PROFILE, key_prefix="user_profile", make_cache_key=make_user_cache_key)
def get_user(identifier):
    """
    Get a specific user's profile by ID or username.
    
    Performance optimizations to prevent HTTP 499/502 timeouts:
    - Cached for 60 seconds to reduce database load
    - Request timeout detection returns error before client disconnects
    - Concurrent queries for independent data (followers, following, posts counts)
    - Indexed queries on primary keys
    - Cache for user stats (followers, following, posts counts)
    
    Cache is personalized per viewer (includes current user ID in key)
    to ensure is_following status is accurate for each user.
    
    Args:
        identifier: Can be either a numeric user ID (integer) or a username string.
                   The endpoint handles both formats automatically:
                   - /api/users/1 -> looks up user with ID 1
                   - /api/users/johndoe -> looks up user with username "johndoe"
                   - /api/users/123abc -> tries ID first, falls back to username
    """
    if request.method == "OPTIONS":
        return "", 200

    # Track request timing for timeout detection
    request_start = time.time()
    request_id = getattr(g, 'request_id', 'unknown')

    conn = None
    cursor = None
    try:
        # Input validation - strip whitespace and validate
        if not identifier:
            logger.warning("[%s] User lookup failed: empty identifier", request_id)
            return jsonify({
                "success": False,
                "message": "User identifier is required",
                "error_code": "INVALID_INPUT"
            }), 400
        
        identifier = str(identifier).strip()
        if not identifier:
            logger.warning("[%s] User lookup failed: whitespace-only identifier", request_id)
            return jsonify({
                "success": False,
                "message": "User identifier cannot be empty",
                "error_code": "INVALID_INPUT"
            }), 400
        
        # Log the lookup attempt for debugging
        # In production, mask the identifier to avoid logging sensitive data
        masked_identifier = identifier if not IS_PRODUCTION else (
            f"{identifier[:2]}***" if len(identifier) > 2 else "***"
        )
        logger.info("[%s] User profile lookup: identifier='%s', type=%s", 
                   request_id, masked_identifier, 'numeric' if identifier.isdigit() else 'username')

        # Verify authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("[%s] User lookup failed: missing auth token", request_id)
            return jsonify({"success": False, "message": "Authentication required"}), 401

        token = auth_header.split(" ")[1]
        
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user_id = payload["user_id"]
            # Log authenticated user lookup (IDs only, not sensitive in this context)
            logger.info("[%s] Authenticated user ID: %s looking up user: '%s'", 
                       request_id, current_user_id, masked_identifier)
        except jwt.InvalidTokenError as e:
            logger.warning("[%s] User lookup failed: invalid token - %s", request_id, str(e))
            return jsonify({"success": False, "message": "Invalid token"}), 401

        # Check for timeout before database query
        if _check_request_timeout(request_start, API_REQUEST_TIMEOUT_SECONDS, "get user (before db)"):
            return jsonify({
                "success": False, 
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }), 504

        conn = get_db_connection()
        if conn is None:
            logger.error("[%s] User lookup failed: database connection unavailable", request_id)
            return jsonify({
                "success": False,
                "message": "Database temporarily unavailable. Please try again.",
                "error_code": "DB_UNAVAILABLE"
            }), 503
        cursor = conn.cursor()

        # Determine if identifier is a numeric ID or username
        # Design note: If the identifier can be parsed as a number, try ID lookup first.
        # If no user is found by ID (or identifier is not numeric), fall back to username
        # lookup. This approach handles purely numeric usernames and maintains backward
        # compatibility with existing ID-based lookups.
        user = None
        
        try:
            user_id = int(identifier)
            # It's a numeric ID - query by ID first
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
        except ValueError:
            # Identifier is not numeric, will fall through to username lookup
            pass
        
        # If no user found by ID (or identifier isn't numeric), try username
        if user is None:
            cursor.execute(
                """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, company_name, location, phone, user_type, 
                       is_available_for_hire, created_at
                FROM users
                WHERE username = %s AND is_active = TRUE
                """ if USE_POSTGRESQL else """
                SELECT id, email, first_name, last_name, username, avatar_url, bio,
                       occupation, company_name, location, phone, user_type, 
                       is_available_for_hire, created_at
                FROM users
                WHERE username = ? AND is_active = 1
                """,
                (identifier,)
            )
            user = cursor.fetchone()
        
        if not user:
            # Log detailed info for debugging "user not found" issues
            # We always try ID first if numeric, then fall back to username
            is_numeric_id = str(identifier).isdigit()
            logger.warning(
                "[%s] User not found: identifier='%s', lookup_type='%s', "
                "searched_by_id=%s, searched_by_username=%s",
                request_id, masked_identifier, 
                'numeric' if is_numeric_id else 'username',
                is_numeric_id, True  # Always try username as fallback
            )
            cursor.close()
            return_db_connection(conn)
            return jsonify({
                "success": False, 
                "message": f"User not found. The user '{identifier}' may have been deleted or does not exist.",
                "error_code": "USER_NOT_FOUND",
                "identifier_received": identifier,
                "identifier_type": "numeric" if is_numeric_id else "username"
            }), 404

        # Get the user's ID for follow queries (in case we looked up by username)
        found_user_id = user["id"]
        
        # Close the initial connection before concurrent queries
        cursor.close()
        return_db_connection(conn)
        conn = None
        cursor = None

        # Execute stats queries concurrently for better performance
        # This reduces total query time from ~150ms (sequential) to ~50ms (parallel)
        concurrent_queries = [
            # Query 1: Check if current user follows this user
            (
                "SELECT id FROM follows WHERE follower_id = ? AND followed_id = ?",
                (current_user_id, found_user_id),
                'one'
            ),
            # Query 2: Get follower count
            (
                "SELECT COUNT(*) as count FROM follows WHERE followed_id = ?",
                (found_user_id,),
                'one'
            ),
            # Query 3: Get following count
            (
                "SELECT COUNT(*) as count FROM follows WHERE follower_id = ?",
                (found_user_id,),
                'one'
            ),
            # Query 4: Get posts count
            (
                "SELECT COUNT(*) as count FROM posts WHERE user_id = ?",
                (found_user_id,),
                'one'
            ),
        ]
        
        results = execute_queries_concurrent(concurrent_queries, timeout_seconds=10)
        
        # Extract results with safe defaults
        is_following = results[0] is not None
        followers_count = results[1]["count"] if results[1] else 0
        following_count = results[2]["count"] if results[2] else 0
        posts_count = results[3]["count"] if results[3] else 0

        # Check for timeout after database queries
        if _check_request_timeout(request_start, API_REQUEST_TIMEOUT_SECONDS, "get user (after db)"):
            return jsonify({
                "success": False, 
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }), 504

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
    finally:
        # Always clean up database resources to prevent connection leaks
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


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
        return_db_connection(conn)

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

        # Check if user exists and is active
        cursor.execute(
            """
            SELECT id, is_active FROM users WHERE id = %s
            """ if USE_POSTGRESQL else """
            SELECT id, is_active FROM users WHERE id = ?
            """,
            (user_id,)
        )
        target_user = cursor.fetchone()
        if not target_user:
            cursor.close()
            return_db_connection(conn)
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Check if user is active
        if not target_user["is_active"]:
            cursor.close()
            return_db_connection(conn)
            return jsonify({"success": False, "message": "User account is not active"}), 404

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
            return_db_connection(conn)
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
        return_db_connection(conn)

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
            return_db_connection(conn)
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
        return_db_connection(conn)

        return jsonify({"success": True, "message": "User unfollowed successfully"}), 200

    except Exception as e:
        print(f"Unfollow user error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to unfollow user: {str(e)}"}), 500


@app.route("/api/users/following/list", methods=["GET", "OPTIONS"])
def get_following_list():
    """
    Get list of users that current user is following.
    
    Performance optimizations to prevent HTTP 499 timeouts:
    - Query uses LIMIT to prevent returning too many results
    - Database index on follows.follower_id speeds up the join
    - Request timeout detection returns error before client disconnects
    
    Query Parameters:
    - limit: Maximum number of following to return (default: DEFAULT_LIST_LIMIT)
    - offset: Number of following to skip for pagination (default: 0)
    """
    if request.method == "OPTIONS":
        return "", 200

    # Track request timing for timeout detection
    request_start = time.time()

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

        # Check for timeout before database query
        if _check_request_timeout(request_start, API_REQUEST_TIMEOUT_SECONDS, "following list (before db)"):
            return jsonify({
                "success": False, 
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }), 504

        # Get and validate pagination parameters
        limit, offset = _get_pagination_params()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get users that current user is following with pagination
        # Query uses index on follows.follower_id for performance
        cursor.execute(
            """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.followed_id
            WHERE f.follower_id = %s
            LIMIT %s OFFSET %s
            """ if USE_POSTGRESQL else """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.followed_id
            WHERE f.follower_id = ?
            LIMIT ? OFFSET ?
            """,
            (current_user_id, limit, offset)
        )

        following_users = cursor.fetchall()

        # Check for timeout after database query
        if _check_request_timeout(request_start, API_REQUEST_TIMEOUT_SECONDS, "following list (after db)"):
            cursor.close()
            return_db_connection(conn)
            return jsonify({
                "success": False, 
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }), 504
        
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
        return_db_connection(conn)

        return jsonify({"success": True, "following": following_data}), 200

    except Exception as e:
        print(f"Get following list error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch following list: {str(e)}"}), 500


@app.route("/api/users/followers/list", methods=["GET", "OPTIONS"])
def get_followers_list():
    """
    Get list of users that follow current user.
    
    Performance optimizations to prevent HTTP 499 timeouts:
    - Query uses LIMIT to prevent returning too many results
    - Database index on follows.followed_id speeds up the join
    - Request timeout detection returns error before client disconnects
    
    Query Parameters:
    - limit: Maximum number of followers to return (default: DEFAULT_LIST_LIMIT)
    - offset: Number of followers to skip for pagination (default: 0)
    """
    if request.method == "OPTIONS":
        return "", 200

    # Track request timing for timeout detection
    request_start = time.time()

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

        # Check for timeout before database query
        if _check_request_timeout(request_start, API_REQUEST_TIMEOUT_SECONDS, "followers list (before db)"):
            return jsonify({
                "success": False, 
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }), 504

        # Get and validate pagination parameters
        limit, offset = _get_pagination_params()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get users that follow current user with pagination
        # Query uses index on follows.followed_id for performance
        cursor.execute(
            """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.follower_id
            WHERE f.followed_id = %s
            LIMIT %s OFFSET %s
            """ if USE_POSTGRESQL else """
            SELECT u.id, u.email, u.first_name, u.last_name, u.username, 
                   u.avatar_url, u.bio, u.occupation, u.location
            FROM users u
            INNER JOIN follows f ON u.id = f.follower_id
            WHERE f.followed_id = ?
            LIMIT ? OFFSET ?
            """,
            (current_user_id, limit, offset)
        )

        followers = cursor.fetchall()

        # Check for timeout after database query
        if _check_request_timeout(request_start, API_REQUEST_TIMEOUT_SECONDS, "followers list (after db)"):
            cursor.close()
            return_db_connection(conn)
            return jsonify({
                "success": False, 
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }), 504
        
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
        return_db_connection(conn)

        return jsonify({"success": True, "followers": followers_data}), 200

    except Exception as e:
        print(f"Get followers list error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to fetch followers list: {str(e)}"}), 500


# ==========================================
# JOBS ENDPOINTS
# ==========================================


@app.route("/api/jobs", methods=["GET", "OPTIONS"])
@cache.cached(timeout=CACHE_TIMEOUT_JOBS, key_prefix="jobs_list", query_string=True)
def get_jobs():
    """
    Get all active jobs with optional filtering.
    
    Cached for performance optimization (default: 60 seconds).
    Cache is keyed by query parameters (search, category, location).
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
        return_db_connection(conn)

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
@cache.cached(timeout=CACHE_TIMEOUT_JOBS * 2, key_prefix="jobs_stats")
def get_job_stats():
    """
    Get job statistics overview.
    Returns counts of active jobs, companies hiring, and new jobs this week.
    
    Cached for 2x the jobs timeout (aggregate data changes less frequently).
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
        return_db_connection(conn)

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
        return_db_connection(conn)

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

        # Verify user exists and is active
        if USE_POSTGRESQL:
            cursor.execute("SELECT id, is_active FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT id, is_active FROM users WHERE id = ?", (user_id,))
        
        current_user = cursor.fetchone()
        if not current_user:
            cursor.close()
            return_db_connection(conn)
            return jsonify({
                "success": False, 
                "message": "Your account was not found. Please log in again.",
                "error_code": "USER_NOT_FOUND",
                "action": "logout"
            }), 401
        
        if not current_user["is_active"]:
            cursor.close()
            return_db_connection(conn)
            return jsonify({
                "success": False, 
                "message": "Your account is not active. Please contact support.",
                "error_code": "USER_INACTIVE",
                "action": "logout"
            }), 403

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

        # Also create a post for the news feed so the job appears on the home page
        # Reuse the already-stripped values from the job data used above
        job_title = data["title"].strip()
        job_company = data["company"].strip()
        job_location = data["location"].strip()
        job_type_formatted = data.get("job_type", "full-time").strip().replace('-', ' ').title()
        job_description = data["description"].strip()
        
        # Truncate description for the post (max 500 chars)
        truncated_description = job_description[:500]
        if len(job_description) > 500:
            truncated_description += '...'
        
        # Create a formatted post content for the job
        post_content = (
            f"📢 New Job Posting!\n\n"
            f"🏢 {job_title} at {job_company}\n"
            f"📍 {job_location}\n"
            f"⏰ {job_type_formatted}\n\n"
            f"{truncated_description}"
        )
        
        if USE_POSTGRESQL:
            cursor.execute(
                """
                INSERT INTO posts (user_id, content, created_at)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (user_id, post_content, now)
            )
            cursor.fetchone()  # Consume the result but don't need to store it
        else:
            cursor.execute(
                """
                INSERT INTO posts (user_id, content, created_at)
                VALUES (?, ?, ?)
                """,
                (user_id, post_content, now)
            )

        conn.commit()
        cursor.close()
        return_db_connection(conn)

        # Invalidate jobs cache after creating a new job
        invalidate_cache_pattern("jobs_*")

        return jsonify({
            "success": True,
            "message": "Job created successfully",
            "job": {
                "id": job_id,
                "title": job_title,
                "company": job_company,
                "location": job_location,
                "created_at": now.isoformat(),
            }
        }), 201

    except Exception as e:
        print(f"Create job error: {str(e)}")
        return jsonify({"success": False, "message": f"Failed to create job: {str(e)}"}), 500


# ==========================================
# FRIENDS ENDPOINTS
# ==========================================


@app.route("/api/friends/send-request/<int:user_id>", methods=["POST", "OPTIONS"])
def send_friend_request(user_id):
    """Send a friend request to another user"""
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            sender_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        if sender_id == user_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Cannot send friend request to yourself",
                    }
                ),
                400,
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if users exist and are active
        if USE_POSTGRESQL:
            cursor.execute("SELECT id, is_active FROM users WHERE id IN (%s, %s)", (sender_id, user_id))
        else:
            cursor.execute("SELECT id, is_active FROM users WHERE id IN (?, ?)", (sender_id, user_id))
        found_users = cursor.fetchall()
        if len(found_users) != 2:
            cursor.close()
            return_db_connection(conn)
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Check if both users are active
        for found_user in found_users:
            if not found_user["is_active"]:
                cursor.close()
                return_db_connection(conn)
                return jsonify({"success": False, "message": "User account is not active"}), 404

        # Check if friendship already exists
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT status FROM friendships
                WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
            """,
                (sender_id, user_id, user_id, sender_id),
            )
        else:
            cursor.execute(
                """
                SELECT status FROM friendships
                WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
            """,
                (sender_id, user_id, user_id, sender_id),
            )

        existing = cursor.fetchone()
        if existing:
            status = existing["status"]
            if status == "accepted":
                return jsonify({"success": False, "message": "Already friends"}), 400
            elif status == "pending":
                return (
                    jsonify(
                        {"success": False, "message": "Friend request already sent"}
                    ),
                    400,
                )

        # Create friend request
        if USE_POSTGRESQL:
            cursor.execute(
                """
                INSERT INTO friendships (sender_id, receiver_id, status, created_at, updated_at)
                VALUES (%s, %s, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (sender_id, receiver_id) DO UPDATE SET status = 'pending', updated_at = CURRENT_TIMESTAMP
            """,
                (sender_id, user_id),
            )
        else:
            # For SQLite, use INSERT OR IGNORE followed by UPDATE to preserve created_at
            cursor.execute(
                """
                INSERT OR IGNORE INTO friendships (sender_id, receiver_id, status, created_at, updated_at)
                VALUES (?, ?, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
                (sender_id, user_id),
            )
            cursor.execute(
                """
                UPDATE friendships SET status = 'pending', updated_at = CURRENT_TIMESTAMP
                WHERE sender_id = ? AND receiver_id = ?
            """,
                (sender_id, user_id),
            )

        conn.commit()

        return (
            jsonify({"success": True, "message": "Friend request sent successfully"}),
            201,
        )

    except Exception as e:
        logger.error(f"Error sending friend request: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": "Failed to send friend request"}),
            500,
        )
    finally:
        # Always clean up database resources to prevent connection leaks
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/friends/requests", methods=["GET", "OPTIONS"])
def get_friend_requests():
    """Get friend requests for current user"""
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get incoming friend requests
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT f.id, f.sender_id, f.created_at,
                       u.first_name, u.last_name, u.email, u.avatar_url
                FROM friendships f
                JOIN users u ON f.sender_id = u.id
                WHERE f.receiver_id = %s AND f.status = 'pending'
                ORDER BY f.created_at DESC
            """,
                (user_id,),
            )
        else:
            cursor.execute(
                """
                SELECT f.id, f.sender_id, f.created_at,
                       u.first_name, u.last_name, u.email, u.avatar_url
                FROM friendships f
                JOIN users u ON f.sender_id = u.id
                WHERE f.receiver_id = ? AND f.status = 'pending'
                ORDER BY f.created_at DESC
            """,
                (user_id,),
            )

        rows = cursor.fetchall()
        requests_list = []
        for row in rows:
            requests_list.append(
                {
                    "id": row["id"],
                    "sender_id": row["sender_id"],
                    "created_at": row["created_at"],
                    "sender": {
                        "id": row["sender_id"],
                        "first_name": row["first_name"] or "",
                        "last_name": row["last_name"] or "",
                        "email": row["email"],
                        "avatar_url": row["avatar_url"] or "",
                    },
                }
            )

        return jsonify({"success": True, "requests": requests_list}), 200

    except Exception as e:
        logger.error(f"Error getting friend requests: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": "Failed to get friend requests"}),
            500,
        )
    finally:
        # Always clean up database resources to prevent connection leaks
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/friends/respond/<int:request_id>", methods=["POST", "OPTIONS"])
def respond_to_friend_request(request_id):
    """Accept or decline a friend request"""
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        data = request.get_json()
        action = data.get("action")  # 'accept' or 'decline'

        if action not in ["accept", "decline"]:
            return jsonify({"success": False, "message": "Invalid action"}), 400

        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if request exists and belongs to user
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT sender_id FROM friendships
                WHERE id = %s AND receiver_id = %s AND status = 'pending'
            """,
                (request_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT sender_id FROM friendships
                WHERE id = ? AND receiver_id = ? AND status = 'pending'
            """,
                (request_id, user_id),
            )

        result = cursor.fetchone()
        if not result:
            return (
                jsonify({"success": False, "message": "Friend request not found"}),
                404,
            )

        if action == "accept":
            # Update friendship status to accepted
            if USE_POSTGRESQL:
                cursor.execute(
                    """
                    UPDATE friendships SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """,
                    (request_id,),
                )
            else:
                cursor.execute(
                    """
                    UPDATE friendships SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (request_id,),
                )
        else:
            # Delete the friend request
            if USE_POSTGRESQL:
                cursor.execute("DELETE FROM friendships WHERE id = %s", (request_id,))
            else:
                cursor.execute("DELETE FROM friendships WHERE id = ?", (request_id,))

        conn.commit()

        return (
            jsonify(
                {"success": True, "message": f"Friend request {action}ed successfully"}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error responding to friend request: {str(e)}", exc_info=True)
        return (
            jsonify(
                {"success": False, "message": "Failed to respond to friend request"}
            ),
            500,
        )
    finally:
        # Always clean up database resources to prevent connection leaks
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/friends/list", methods=["GET", "OPTIONS"])
def get_friends_list():
    """Get list of accepted friends"""
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get accepted friends (both directions)
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT DISTINCT u.id, u.first_name, u.last_name, u.email, u.avatar_url, u.is_available_for_hire
                FROM friendships f
                JOIN users u ON (
                    (f.sender_id = %s AND f.receiver_id = u.id) OR
                    (f.receiver_id = %s AND f.sender_id = u.id)
                )
                WHERE (f.sender_id = %s OR f.receiver_id = %s) AND f.status = 'accepted'
                ORDER BY u.first_name, u.last_name
            """,
                (user_id, user_id, user_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT DISTINCT u.id, u.first_name, u.last_name, u.email, u.avatar_url, u.is_available_for_hire
                FROM friendships f
                JOIN users u ON (
                    (f.sender_id = ? AND f.receiver_id = u.id) OR
                    (f.receiver_id = ? AND f.sender_id = u.id)
                )
                WHERE (f.sender_id = ? OR f.receiver_id = ?) AND f.status = 'accepted'
                ORDER BY u.first_name, u.last_name
            """,
                (user_id, user_id, user_id, user_id),
            )

        friends = []
        for row in cursor.fetchall():
            friends.append(
                {
                    "id": row["id"],
                    "first_name": row["first_name"] or "",
                    "last_name": row["last_name"] or "",
                    "email": row["email"],
                    "avatar_url": row["avatar_url"] or "",
                    "is_available_for_hire": bool(row["is_available_for_hire"]),
                }
            )

        return (
            jsonify({"success": True, "friends": friends, "count": len(friends)}),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting friends list: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "Failed to get friends list"}), 500
    finally:
        # Always clean up database resources to prevent connection leaks
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/friends/suggestions", methods=["GET", "OPTIONS"])
def get_friend_suggestions():
    """
    Get friend suggestions (users not already friends or requested).
    
    Performance optimizations to prevent HTTP 499/502 timeouts:
    - Request timeout detection returns error before client disconnects
    - Limited to 10 results to prevent slow queries
    - Indexed queries on user IDs
    """
    if request.method == "OPTIONS":
        return "", 200

    # Track request timing for timeout detection
    request_start = time.time()

    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        # Check for timeout before database query
        if _check_request_timeout(request_start, API_REQUEST_TIMEOUT_SECONDS, "friend suggestions (before db)"):
            return jsonify({
                "success": False, 
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }), 504

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get users who are not already friends or have pending requests
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT u.id, u.first_name, u.last_name, u.email, u.avatar_url, u.bio, u.location
                FROM users u
                WHERE u.id != %s AND u.is_active = TRUE
                AND u.id NOT IN (
                    SELECT CASE
                        WHEN f.sender_id = %s THEN f.receiver_id
                        ELSE f.sender_id
                    END
                    FROM friendships f
                    WHERE (f.sender_id = %s OR f.receiver_id = %s) AND f.status IN ('pending', 'accepted')
                )
                ORDER BY u.created_at DESC
                LIMIT 10
            """,
                (user_id, user_id, user_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT u.id, u.first_name, u.last_name, u.email, u.avatar_url, u.bio, u.location
                FROM users u
                WHERE u.id != ? AND u.is_active = 1
                AND u.id NOT IN (
                    SELECT CASE
                        WHEN f.sender_id = ? THEN f.receiver_id
                        ELSE f.sender_id
                    END
                    FROM friendships f
                    WHERE (f.sender_id = ? OR f.receiver_id = ?) AND f.status IN ('pending', 'accepted')
                )
                ORDER BY u.created_at DESC
                LIMIT 10
            """,
                (user_id, user_id, user_id, user_id),
            )

        suggestions = []
        for row in cursor.fetchall():
            suggestions.append(
                {
                    "id": row["id"],
                    "first_name": row["first_name"] or "",
                    "last_name": row["last_name"] or "",
                    "email": row["email"],
                    "avatar_url": row["avatar_url"] or "",
                    "bio": row["bio"] or "",
                    "location": row["location"] or "",
                }
            )

        # Check for timeout after database query
        if _check_request_timeout(request_start, API_REQUEST_TIMEOUT_SECONDS, "friend suggestions (after db)"):
            return jsonify({
                "success": False, 
                "message": "Request timed out. Please try again.",
                "error_code": "TIMEOUT"
            }), 504

        return jsonify({"success": True, "suggestions": suggestions}), 200

    except Exception as e:
        logger.error(f"Error getting friend suggestions: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": "Failed to get friend suggestions"}),
            500,
        )
    finally:
        # Always clean up database resources to prevent connection leaks
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


# ==========================================
# MESSAGES ENDPOINTS
# ==========================================


@app.route("/api/messages/conversations", methods=["GET", "OPTIONS"])
def get_conversations():
    """
    Get all conversations for the current user.
    Returns conversations with participant info and messages.
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all conversations where user is a participant
        # OPTIMIZATION: Fetch conversations and messages in 2 queries instead of N+1
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT c.id, c.participant_1_id, c.participant_2_id, 
                       c.created_at, c.updated_at,
                       u1.first_name as p1_first_name, u1.last_name as p1_last_name,
                       u1.avatar_url as p1_avatar_url,
                       u2.first_name as p2_first_name, u2.last_name as p2_last_name,
                       u2.avatar_url as p2_avatar_url
                FROM conversations c
                JOIN users u1 ON c.participant_1_id = u1.id
                JOIN users u2 ON c.participant_2_id = u2.id
                WHERE c.participant_1_id = %s OR c.participant_2_id = %s
                ORDER BY c.updated_at DESC
                """,
                (user_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT c.id, c.participant_1_id, c.participant_2_id, 
                       c.created_at, c.updated_at,
                       u1.first_name as p1_first_name, u1.last_name as p1_last_name,
                       u1.avatar_url as p1_avatar_url,
                       u2.first_name as p2_first_name, u2.last_name as p2_last_name,
                       u2.avatar_url as p2_avatar_url
                FROM conversations c
                JOIN users u1 ON c.participant_1_id = u1.id
                JOIN users u2 ON c.participant_2_id = u2.id
                WHERE c.participant_1_id = ? OR c.participant_2_id = ?
                ORDER BY c.updated_at DESC
                """,
                (user_id, user_id),
            )

        conversations_data = cursor.fetchall()
        
        # Collect all conversation IDs for batch message fetch
        conversation_ids = [conv["id"] for conv in conversations_data]
        
        # OPTIMIZATION: Fetch all messages for all conversations in a single query
        # This eliminates N+1 queries (was 1 query per conversation)
        messages_by_conversation = {}
        if conversation_ids:
            if USE_POSTGRESQL:
                # Use ANY for efficient IN clause with array
                cursor.execute(
                    """
                    SELECT m.id, m.conversation_id, m.sender_id, m.content, 
                           m.is_read, m.created_at,
                           u.first_name, u.last_name
                    FROM messages m
                    JOIN users u ON m.sender_id = u.id
                    WHERE m.conversation_id = ANY(%s)
                    ORDER BY m.conversation_id, m.created_at ASC
                    """,
                    (conversation_ids,),
                )
            else:
                # SQLite doesn't support ANY, use IN with placeholders
                # SECURITY: placeholders contains only "?" characters, not user data
                # The actual values are passed as parameterized query arguments
                placeholders = ",".join("?" * len(conversation_ids))
                cursor.execute(
                    f"""
                    SELECT m.id, m.conversation_id, m.sender_id, m.content, 
                           m.is_read, m.created_at,
                           u.first_name, u.last_name
                    FROM messages m
                    JOIN users u ON m.sender_id = u.id
                    WHERE m.conversation_id IN ({placeholders})
                    ORDER BY m.conversation_id, m.created_at ASC
                    """,
                    tuple(conversation_ids),
                )
            
            # Group messages by conversation_id
            for msg in cursor.fetchall():
                conv_id = msg["conversation_id"]
                if conv_id not in messages_by_conversation:
                    messages_by_conversation[conv_id] = []
                messages_by_conversation[conv_id].append({
                    "id": msg["id"],
                    "conversation_id": msg["conversation_id"],
                    "sender_id": msg["sender_id"],
                    "content": msg["content"],
                    "is_read": bool(msg["is_read"]),
                    "created_at": msg["created_at"].isoformat() if hasattr(msg["created_at"], 'isoformat') else str(msg["created_at"]),
                    "sender": {
                        "first_name": msg["first_name"] or "",
                        "last_name": msg["last_name"] or "",
                    },
                })

        # Build response using pre-fetched messages
        conversations = []
        for conv in conversations_data:
            conversations.append({
                "id": conv["id"],
                "participant_1_id": conv["participant_1_id"],
                "participant_2_id": conv["participant_2_id"],
                "created_at": conv["created_at"].isoformat() if hasattr(conv["created_at"], 'isoformat') else str(conv["created_at"]),
                "updated_at": conv["updated_at"].isoformat() if hasattr(conv["updated_at"], 'isoformat') and conv["updated_at"] else str(conv["updated_at"]) if conv["updated_at"] else None,
                "participant_1": {
                    "first_name": conv["p1_first_name"] or "",
                    "last_name": conv["p1_last_name"] or "",
                    "avatar_url": conv["p1_avatar_url"] or "",
                },
                "participant_2": {
                    "first_name": conv["p2_first_name"] or "",
                    "last_name": conv["p2_last_name"] or "",
                    "avatar_url": conv["p2_avatar_url"] or "",
                },
                "messages": messages_by_conversation.get(conv["id"], []),
            })

        return jsonify(conversations), 200

    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": "Failed to get conversations"}),
            500,
        )
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/messages/conversations", methods=["POST"])
def create_conversation():
    """
    Create a new conversation or return existing one between two users.
    """
    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        data = request.get_json()
        participant_id = data.get("participant_id")
        
        if not participant_id:
            return jsonify({"success": False, "message": "participant_id is required"}), 400

        # Convert to int if string
        try:
            participant_id = int(participant_id)
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "Invalid participant_id"}), 400

        if participant_id == user_id:
            return jsonify({"success": False, "message": "Cannot create conversation with yourself"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if participant exists and is active
        if USE_POSTGRESQL:
            cursor.execute("SELECT id, is_active FROM users WHERE id = %s", (participant_id,))
        else:
            cursor.execute("SELECT id, is_active FROM users WHERE id = ?", (participant_id,))
        
        participant = cursor.fetchone()
        if not participant:
            cursor.close()
            return_db_connection(conn)
            return jsonify({"success": False, "message": "User not found"}), 404
        
        if not participant["is_active"]:
            cursor.close()
            return_db_connection(conn)
            return jsonify({"success": False, "message": "User account is not active"}), 404

        # Check if conversation already exists (check both orderings)
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT c.id, c.participant_1_id, c.participant_2_id, 
                       c.created_at, c.updated_at,
                       u1.first_name as p1_first_name, u1.last_name as p1_last_name,
                       u1.avatar_url as p1_avatar_url,
                       u2.first_name as p2_first_name, u2.last_name as p2_last_name,
                       u2.avatar_url as p2_avatar_url
                FROM conversations c
                JOIN users u1 ON c.participant_1_id = u1.id
                JOIN users u2 ON c.participant_2_id = u2.id
                WHERE (c.participant_1_id = %s AND c.participant_2_id = %s)
                   OR (c.participant_1_id = %s AND c.participant_2_id = %s)
                """,
                (user_id, participant_id, participant_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT c.id, c.participant_1_id, c.participant_2_id, 
                       c.created_at, c.updated_at,
                       u1.first_name as p1_first_name, u1.last_name as p1_last_name,
                       u1.avatar_url as p1_avatar_url,
                       u2.first_name as p2_first_name, u2.last_name as p2_last_name,
                       u2.avatar_url as p2_avatar_url
                FROM conversations c
                JOIN users u1 ON c.participant_1_id = u1.id
                JOIN users u2 ON c.participant_2_id = u2.id
                WHERE (c.participant_1_id = ? AND c.participant_2_id = ?)
                   OR (c.participant_1_id = ? AND c.participant_2_id = ?)
                """,
                (user_id, participant_id, participant_id, user_id),
            )

        existing = cursor.fetchone()
        
        if existing:
            # Return existing conversation with messages
            conversation_id = existing["id"]
            
            # Get messages for this conversation
            if USE_POSTGRESQL:
                cursor.execute(
                    """
                    SELECT m.id, m.conversation_id, m.sender_id, m.content, 
                           m.is_read, m.created_at,
                           u.first_name, u.last_name
                    FROM messages m
                    JOIN users u ON m.sender_id = u.id
                    WHERE m.conversation_id = %s
                    ORDER BY m.created_at ASC
                    """,
                    (conversation_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT m.id, m.conversation_id, m.sender_id, m.content, 
                           m.is_read, m.created_at,
                           u.first_name, u.last_name
                    FROM messages m
                    JOIN users u ON m.sender_id = u.id
                    WHERE m.conversation_id = ?
                    ORDER BY m.created_at ASC
                    """,
                    (conversation_id,),
                )

            messages_data = cursor.fetchall()
            messages = [
                {
                    "id": msg["id"],
                    "conversation_id": msg["conversation_id"],
                    "sender_id": msg["sender_id"],
                    "content": msg["content"],
                    "is_read": bool(msg["is_read"]),
                    "created_at": msg["created_at"].isoformat() if hasattr(msg["created_at"], 'isoformat') else str(msg["created_at"]),
                    "sender": {
                        "first_name": msg["first_name"] or "",
                        "last_name": msg["last_name"] or "",
                    },
                }
                for msg in messages_data
            ]

            return jsonify({
                "id": existing["id"],
                "participant_1_id": existing["participant_1_id"],
                "participant_2_id": existing["participant_2_id"],
                "created_at": existing["created_at"].isoformat() if hasattr(existing["created_at"], 'isoformat') else str(existing["created_at"]),
                "updated_at": existing["updated_at"].isoformat() if hasattr(existing["updated_at"], 'isoformat') and existing["updated_at"] else str(existing["updated_at"]) if existing["updated_at"] else None,
                "participant_1": {
                    "first_name": existing["p1_first_name"] or "",
                    "last_name": existing["p1_last_name"] or "",
                    "avatar_url": existing["p1_avatar_url"] or "",
                },
                "participant_2": {
                    "first_name": existing["p2_first_name"] or "",
                    "last_name": existing["p2_last_name"] or "",
                    "avatar_url": existing["p2_avatar_url"] or "",
                },
                "messages": messages,
            }), 200

        # Create new conversation with canonical participant ordering
        # Always store with participant_1_id < participant_2_id to prevent duplicates
        p1_id = min(user_id, participant_id)
        p2_id = max(user_id, participant_id)
        
        now = datetime.now(timezone.utc)
        if USE_POSTGRESQL:
            cursor.execute(
                """
                INSERT INTO conversations (participant_1_id, participant_2_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (p1_id, p2_id, now, now),
            )
            conversation_id = cursor.fetchone()["id"]
        else:
            cursor.execute(
                """
                INSERT INTO conversations (participant_1_id, participant_2_id, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (p1_id, p2_id, now, now),
            )
            conversation_id = cursor.lastrowid

        conn.commit()

        # Get participant info for response
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT first_name, last_name, avatar_url FROM users WHERE id = %s
                """,
                (p1_id,),
            )
        else:
            cursor.execute(
                """
                SELECT first_name, last_name, avatar_url FROM users WHERE id = ?
                """,
                (p1_id,),
            )
        p1 = cursor.fetchone()

        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT first_name, last_name, avatar_url FROM users WHERE id = %s
                """,
                (p2_id,),
            )
        else:
            cursor.execute(
                """
                SELECT first_name, last_name, avatar_url FROM users WHERE id = ?
                """,
                (p2_id,),
            )
        p2 = cursor.fetchone()

        return jsonify({
            "id": conversation_id,
            "participant_1_id": p1_id,
            "participant_2_id": p2_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "participant_1": {
                "first_name": p1["first_name"] or "" if p1 else "",
                "last_name": p1["last_name"] or "" if p1 else "",
                "avatar_url": p1["avatar_url"] or "" if p1 else "",
            },
            "participant_2": {
                "first_name": p2["first_name"] or "" if p2 else "",
                "last_name": p2["last_name"] or "" if p2 else "",
                "avatar_url": p2["avatar_url"] or "" if p2 else "",
            },
            "messages": [],
        }), 201

    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": "Failed to create conversation"}),
            500,
        )
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/messages/conversations/<int:conversation_id>/messages", methods=["GET", "OPTIONS"])
def get_conversation_messages(conversation_id):
    """
    Get all messages in a conversation.
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify user is part of the conversation
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT id FROM conversations 
                WHERE id = %s AND (participant_1_id = %s OR participant_2_id = %s)
                """,
                (conversation_id, user_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT id FROM conversations 
                WHERE id = ? AND (participant_1_id = ? OR participant_2_id = ?)
                """,
                (conversation_id, user_id, user_id),
            )

        if not cursor.fetchone():
            return jsonify({"success": False, "message": "Conversation not found or access denied"}), 404

        # Get messages
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT m.id, m.conversation_id, m.sender_id, m.content, 
                       m.is_read, m.created_at,
                       u.first_name, u.last_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.conversation_id = %s
                ORDER BY m.created_at ASC
                """,
                (conversation_id,),
            )
        else:
            cursor.execute(
                """
                SELECT m.id, m.conversation_id, m.sender_id, m.content, 
                       m.is_read, m.created_at,
                       u.first_name, u.last_name
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.conversation_id = ?
                ORDER BY m.created_at ASC
                """,
                (conversation_id,),
            )

        messages_data = cursor.fetchall()
        messages = [
            {
                "id": msg["id"],
                "conversation_id": msg["conversation_id"],
                "sender_id": msg["sender_id"],
                "content": msg["content"],
                "is_read": bool(msg["is_read"]),
                "created_at": msg["created_at"].isoformat() if hasattr(msg["created_at"], 'isoformat') else str(msg["created_at"]),
                "sender": {
                    "first_name": msg["first_name"] or "",
                    "last_name": msg["last_name"] or "",
                },
            }
            for msg in messages_data
        ]

        return jsonify(messages), 200

    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": "Failed to get messages"}),
            500,
        )
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/messages/conversations/<int:conversation_id>/messages", methods=["POST"])
def send_message(conversation_id):
    """
    Send a message in a conversation.
    """
    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        data = request.get_json()
        content = data.get("content", "").strip()
        
        if not content:
            return jsonify({"success": False, "message": "Message content is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify user is part of the conversation
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT id FROM conversations 
                WHERE id = %s AND (participant_1_id = %s OR participant_2_id = %s)
                """,
                (conversation_id, user_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT id FROM conversations 
                WHERE id = ? AND (participant_1_id = ? OR participant_2_id = ?)
                """,
                (conversation_id, user_id, user_id),
            )

        if not cursor.fetchone():
            return jsonify({"success": False, "message": "Conversation not found or access denied"}), 404

        # Create message
        now = datetime.now(timezone.utc)
        if USE_POSTGRESQL:
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, sender_id, content, is_read, created_at)
                VALUES (%s, %s, %s, FALSE, %s)
                RETURNING id
                """,
                (conversation_id, user_id, content, now),
            )
            message_id = cursor.fetchone()["id"]
        else:
            cursor.execute(
                """
                INSERT INTO messages (conversation_id, sender_id, content, is_read, created_at)
                VALUES (?, ?, ?, 0, ?)
                """,
                (conversation_id, user_id, content, now),
            )
            message_id = cursor.lastrowid

        # Update conversation updated_at
        if USE_POSTGRESQL:
            cursor.execute(
                "UPDATE conversations SET updated_at = %s WHERE id = %s",
                (now, conversation_id),
            )
        else:
            cursor.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conversation_id),
            )

        conn.commit()

        # Get sender info for response
        if USE_POSTGRESQL:
            cursor.execute(
                "SELECT first_name, last_name FROM users WHERE id = %s",
                (user_id,),
            )
        else:
            cursor.execute(
                "SELECT first_name, last_name FROM users WHERE id = ?",
                (user_id,),
            )
        sender = cursor.fetchone()

        return jsonify({
            "id": message_id,
            "conversation_id": conversation_id,
            "sender_id": user_id,
            "content": content,
            "is_read": False,
            "created_at": now.isoformat(),
            "sender": {
                "first_name": sender["first_name"] or "" if sender else "",
                "last_name": sender["last_name"] or "" if sender else "",
            },
        }), 201

    except Exception as e:
        logger.error(f"Error sending message: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": "Failed to send message"}),
            500,
        )
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/messages/messages/<int:message_id>/read", methods=["PUT", "OPTIONS"])
def mark_message_read(message_id):
    """
    Mark a message as read.
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get message and verify user is recipient (not sender)
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT m.id, m.sender_id, c.participant_1_id, c.participant_2_id
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE m.id = %s
                """,
                (message_id,),
            )
        else:
            cursor.execute(
                """
                SELECT m.id, m.sender_id, c.participant_1_id, c.participant_2_id
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE m.id = ?
                """,
                (message_id,),
            )

        message = cursor.fetchone()
        if not message:
            return jsonify({"success": False, "message": "Message not found"}), 404

        # Verify user is part of the conversation but not the sender
        is_participant = user_id in (message["participant_1_id"], message["participant_2_id"])
        is_sender = user_id == message["sender_id"]
        
        if not is_participant:
            return jsonify({"success": False, "message": "Access denied"}), 403
        
        if is_sender:
            return jsonify({"success": False, "message": "Cannot mark your own message as read"}), 400

        # Mark as read
        if USE_POSTGRESQL:
            cursor.execute(
                "UPDATE messages SET is_read = TRUE WHERE id = %s",
                (message_id,),
            )
        else:
            cursor.execute(
                "UPDATE messages SET is_read = 1 WHERE id = ?",
                (message_id,),
            )

        conn.commit()

        return jsonify({"success": True, "message": "Message marked as read"}), 200

    except Exception as e:
        logger.error(f"Error marking message as read: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": "Failed to mark message as read"}),
            500,
        )
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/messages/unread-count", methods=["GET", "OPTIONS"])
def get_unread_message_count():
    """
    Get count of unread messages for current user.
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({"success": False, "message": "Authorization token required"}),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Count unread messages where user is recipient (not sender)
        if USE_POSTGRESQL:
            cursor.execute(
                """
                SELECT COUNT(*) as unread_count
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE m.is_read = FALSE 
                AND m.sender_id != %s
                AND (c.participant_1_id = %s OR c.participant_2_id = %s)
                """,
                (user_id, user_id, user_id),
            )
        else:
            cursor.execute(
                """
                SELECT COUNT(*) as unread_count
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE m.is_read = 0 
                AND m.sender_id != ?
                AND (c.participant_1_id = ? OR c.participant_2_id = ?)
                """,
                (user_id, user_id, user_id),
            )

        result = cursor.fetchone()
        unread_count = result["unread_count"] if result else 0

        return jsonify({"unread_count": unread_count}), 200

    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}", exc_info=True)
        return (
            jsonify({"success": False, "message": "Failed to get unread count"}),
            500,
        )
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


# ==========================================
# DATABASE PERFORMANCE MONITORING ENDPOINTS
# ==========================================


@app.route("/api/query-stats", methods=["GET", "OPTIONS"])
def get_query_stats():
    """
    Get PostgreSQL query performance statistics from pg_stat_statements.
    
    This endpoint provides insights into slow queries for performance monitoring.
    Requires pg_stat_statements extension to be enabled on the PostgreSQL server.
    
    Query Parameters:
        - limit: Maximum number of queries to return (default: 20, max: 100)
        - min_avg_time_ms: Filter queries with average time >= this value (default: 0)
        - order_by: Sort field - 'total_time', 'avg_time', 'calls' (default: 'total_time')
    
    Returns:
        - success: Boolean indicating if the request was successful
        - query_stats: List of query statistics
        - extension_available: Boolean indicating if pg_stat_statements is available
        - message: Status message or error details
        
    Note: If pg_stat_statements is not available, returns a helpful error with
    extension_available: false and instructions for enabling it.
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        # Get token from Authorization header (required for security)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return (
                jsonify({
                    "success": False,
                    "message": "Authorization token required. This endpoint requires authentication.",
                    "extension_available": None
                }),
                401,
            )

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Token expired",
                "extension_available": None
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid token",
                "extension_available": None
            }), 401

        # Only PostgreSQL supports pg_stat_statements
        if not USE_POSTGRESQL:
            return jsonify({
                "success": False,
                "message": "Query statistics are only available with PostgreSQL. SQLite does not support pg_stat_statements.",
                "extension_available": False,
                "query_stats": []
            }), 200

        # Parse query parameters
        limit = request.args.get('limit', type=int, default=20)
        min_avg_time_ms = request.args.get('min_avg_time_ms', type=float, default=0)
        order_by = request.args.get('order_by', default='total_time')
        
        # Validate parameters
        if limit < 1:
            limit = 1
        elif limit > 100:
            limit = 100
        
        # Map order_by to SQL column
        order_by_map = {
            'total_time': 'total_exec_time',
            'avg_time': 'mean_exec_time',
            'calls': 'calls'
        }
        order_column = order_by_map.get(order_by, 'total_exec_time')

        conn = get_db_connection()
        if conn is None:
            return jsonify({
                "success": False,
                "message": "Database connection unavailable",
                "extension_available": None,
                "query_stats": []
            }), 503
            
        cursor = conn.cursor()

        # First, check if pg_stat_statements extension is available
        try:
            cursor.execute("""
                SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
            """)
            extension_exists = cursor.fetchone() is not None
        except Exception as ext_check_error:
            # Error checking extension - likely permission issue
            return jsonify({
                "success": False,
                "message": f"Error checking pg_stat_statements extension: {str(ext_check_error)}",
                "extension_available": False,
                "query_stats": [],
                "setup_guide": "See RAILWAY_PG_STAT_STATEMENTS_SETUP.md for setup instructions"
            }), 200

        if not extension_exists:
            return jsonify({
                "success": False,
                "message": "pg_stat_statements extension is not installed. See setup guide for instructions.",
                "extension_available": False,
                "query_stats": [],
                "setup_guide": "See RAILWAY_PG_STAT_STATEMENTS_SETUP.md for setup instructions",
                "alternative": "Use PgHero (https://railway.app/template/pghero) for query monitoring"
            }), 200

        # Query pg_stat_statements for performance data
        # SECURITY: order_column is validated through whitelist (order_by_map) above
        # and cannot contain user input - only 'total_exec_time', 'mean_exec_time', or 'calls'
        # User-supplied values (min_avg_time_ms, limit) use parameterized queries
        try:
            # Build query with whitelisted column name
            # The ORDER BY clause uses a validated column from order_by_map
            query = f"""
                SELECT 
                    LEFT(query, {QUERY_STATS_MAX_DISPLAY_LENGTH}) as query,
                    calls,
                    total_exec_time as total_time_ms,
                    mean_exec_time as avg_time_ms,
                    rows,
                    CASE 
                        WHEN (shared_blks_hit + shared_blks_read) = 0 THEN 0
                        ELSE 100.0 * shared_blks_hit / (shared_blks_hit + shared_blks_read)
                    END as hit_percent
                FROM pg_stat_statements
                WHERE mean_exec_time >= %s
                ORDER BY {order_column} DESC
                LIMIT %s
            """
            cursor.execute(query, (min_avg_time_ms, limit))
            
            rows = cursor.fetchall()
            query_stats = []
            for row in rows:
                query_stats.append({
                    "query": row["query"],
                    "calls": row["calls"],
                    "total_time_ms": round(row["total_time_ms"], 2) if row["total_time_ms"] else 0,
                    "avg_time_ms": round(row["avg_time_ms"], 2) if row["avg_time_ms"] else 0,
                    "rows": row["rows"],
                    "hit_percent": round(row["hit_percent"], 2) if row["hit_percent"] else 0
                })

            return jsonify({
                "success": True,
                "query_stats": query_stats,
                "extension_available": True,
                "message": f"Retrieved {len(query_stats)} query statistics",
                "parameters": {
                    "limit": limit,
                    "min_avg_time_ms": min_avg_time_ms,
                    "order_by": order_by
                }
            }), 200

        except Exception as query_error:
            error_msg = str(query_error).lower()
            
            # Check if the error is about shared_preload_libraries
            if "shared_preload_libraries" in error_msg:
                return jsonify({
                    "success": False,
                    "message": "pg_stat_statements must be loaded via shared_preload_libraries. The extension is installed but not loaded at server startup.",
                    "error": str(query_error),
                    "extension_available": False,
                    "query_stats": [],
                    "setup_guide": "See RAILWAY_PG_STAT_STATEMENTS_SETUP.md for setup instructions",
                    "solutions": [
                        "Use a custom PostgreSQL image with shared_preload_libraries configured",
                        "Use Neon or Supabase which have pg_stat_statements enabled by default",
                        "Deploy PgHero (https://railway.app/template/pghero) for query monitoring"
                    ]
                }), 200
            
            # Other query errors
            return jsonify({
                "success": False,
                "message": f"Error querying pg_stat_statements: {str(query_error)}",
                "extension_available": True,
                "query_stats": []
            }), 500

    except Exception as e:
        logger.error(f"Error getting query stats: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Failed to get query statistics: {str(e)}",
            "extension_available": None,
            "query_stats": []
        }), 500
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)


@app.route("/api/database-health", methods=["GET", "OPTIONS"])
def get_database_health():
    """
    Get comprehensive database health metrics including connection pool status,
    slow query detection, and extension availability.
    
    This endpoint provides a quick overview of database health for monitoring.
    
    Returns:
        - status: 'healthy', 'degraded', or 'unhealthy'
        - connection_pool: Pool statistics
        - extensions: Available PostgreSQL extensions
        - slow_query_alert: True if there are queries averaging >500ms
    """
    if request.method == "OPTIONS":
        return "", 200

    conn = None
    cursor = None
    try:
        if not USE_POSTGRESQL:
            return jsonify({
                "status": "healthy",
                "database_type": "sqlite",
                "message": "SQLite database is in use (development mode)",
                "connection_pool": None,
                "extensions": [],
                "slow_query_alert": False
            }), 200

        conn = get_db_connection()
        if conn is None:
            return jsonify({
                "status": "unhealthy",
                "database_type": "postgresql",
                "message": "Unable to connect to database",
                "connection_pool": None,
                "extensions": [],
                "slow_query_alert": False
            }), 503
            
        cursor = conn.cursor()

        # Check database connectivity with a simple query
        cursor.execute("SELECT 1")
        
        # Get available extensions
        cursor.execute("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname IN ('pg_stat_statements', 'pg_trgm', 'uuid-ossp')
        """)
        extensions = [{"name": row["extname"], "version": row["extversion"]} for row in cursor.fetchall()]

        # Check for slow queries if pg_stat_statements is available
        slow_query_alert = False
        slow_query_count = 0
        pg_stat_available = any(ext["name"] == "pg_stat_statements" for ext in extensions)
        
        if pg_stat_available:
            try:
                # Use parameterized query for the threshold value
                cursor.execute("""
                    SELECT COUNT(*) as slow_count
                    FROM pg_stat_statements
                    WHERE mean_exec_time > %s
                """, (SLOW_QUERY_THRESHOLD_MS,))
                result = cursor.fetchone()
                slow_query_count = result["slow_count"] if result else 0
                slow_query_alert = slow_query_count > 0
            except Exception:
                # pg_stat_statements might be installed but not loaded
                pg_stat_available = False

        # Get connection pool stats (if available)
        pool_stats = None
        if _connection_pool is not None:
            try:
                pool_stats = {
                    "min_connections": 2,
                    "max_connections": DB_POOL_MAX_CONNECTIONS,
                    "status": "active"
                }
            except Exception:
                pass

        status = "healthy"
        if slow_query_alert:
            status = "degraded"

        return jsonify({
            "status": status,
            "database_type": "postgresql",
            "message": "Database is operational",
            "connection_pool": pool_stats,
            "extensions": extensions,
            "pg_stat_statements_available": pg_stat_available,
            "slow_query_alert": slow_query_alert,
            "slow_query_count": slow_query_count,
            "monitoring_tips": {
                "pghero": "Deploy PgHero for comprehensive query monitoring: https://railway.app/template/pghero",
                "api_endpoint": "/api/query-stats - Query performance statistics (requires auth)"
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting database health: {str(e)}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "database_type": "postgresql" if USE_POSTGRESQL else "sqlite",
            "message": f"Error checking database health: {str(e)}",
            "connection_pool": None,
            "extensions": [],
            "slow_query_alert": False
        }), 500
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            return_db_connection(conn)



# ==========================================
# GLOBAL API FALLBACK HANDLER
# ==========================================
# This route MUST be defined last to ensure all explicit API routes
# are registered first. Flask routes by specificity, so explicit routes
# like /api/users/<identifier> will match before /api/<path:path>.


@app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
@limiter.exempt
def api_fallback(path):
    """
    Global fallback handler for unknown /api/* routes.
    
    Returns 200 OK with {"error":"not_implemented"} instead of 404/502.
    This prevents mobile clients from seeing blank screens when hitting
    routes that haven't been implemented yet.
    
    For OPTIONS requests (CORS preflight), return 200 with empty body.
    
    Note: This route must be defined after all other API routes to ensure
    it only catches requests that don't match any explicit route.
    """
    if request.method == "OPTIONS":
        return "", 200
    
    return jsonify({
        "error": "not_implemented",
        "path": f"/api/{path}",
        "method": request.method,
        "message": "This endpoint is not yet implemented"
    }), 200


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

# Mark application import as complete and log startup time
_APP_IMPORT_COMPLETE_TIME = time.time()
_startup_time_ms = int((_APP_IMPORT_COMPLETE_TIME - _APP_START_TIME) * 1000)
print(f"✅ Application ready to serve requests (startup time: {_startup_time_ms}ms)")

# Export application for gunicorn
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting HireMeBahamas backend on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
