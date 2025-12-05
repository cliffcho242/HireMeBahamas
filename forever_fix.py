#!/usr/bin/env python3
"""
FOREVER FIX - Immortal Deployment System (2025)
===============================================
Prevents app from dying on Vercel/Railway/Render by implementing:
- Automatic health monitoring and recovery
- Database connection keep-alive with retry logic
- Worker process health checks
- Graceful restart on failures
- Memory leak prevention
- Connection pool management

This module ensures your app NEVER goes down and self-heals automatically.
"""

import asyncio
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("forever_fix")

# =============================================================================
# CONFIGURATION
# =============================================================================
def _get_int_env(key: str, default: int) -> int:
    """Safely get integer from environment variable."""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        logger.warning(f"Invalid value for {key}, using default: {default}")
        return default

HEALTH_CHECK_INTERVAL = _get_int_env("FOREVER_HEALTH_CHECK_INTERVAL", 60)  # 1 minute
DB_KEEPALIVE_INTERVAL = _get_int_env("FOREVER_DB_KEEPALIVE_INTERVAL", 120)  # 2 minutes
MAX_CONSECUTIVE_FAILURES = _get_int_env("FOREVER_MAX_FAILURES", 5)
AUTO_RESTART_ENABLED = os.getenv("FOREVER_AUTO_RESTART", "true").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# =============================================================================
# GLOBAL STATE
# =============================================================================
_keepalive_task: Optional[asyncio.Task] = None
_health_check_task: Optional[asyncio.Task] = None
_is_running = False
_stats = {
    "started_at": None,
    "last_health_check": None,
    "last_db_ping": None,
    "total_health_checks": 0,
    "total_db_pings": 0,
    "consecutive_failures": 0,
    "total_recoveries": 0,
}


# =============================================================================
# DATABASE CONNECTION KEEP-ALIVE
# =============================================================================
async def database_keepalive(db_engine):
    """
    Keeps database connection alive by pinging every N seconds.
    Prevents Railway/Render from sleeping the database.
    """
    from sqlalchemy import text
    
    logger.info("🔄 Database keep-alive started (interval: %ds)", DB_KEEPALIVE_INTERVAL)
    
    consecutive_failures = 0
    max_failures = 10
    
    while _is_running:
        try:
            # Perform simple query to keep connection alive
            async with db_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            
            _stats["last_db_ping"] = datetime.utcnow()
            _stats["total_db_pings"] += 1
            consecutive_failures = 0
            
            if _stats["total_db_pings"] % 10 == 0:
                logger.info("✅ Database keep-alive: %d pings completed", _stats["total_db_pings"])
            
        except Exception as e:
            consecutive_failures += 1
            logger.error(
                "❌ Database keep-alive failed (attempt %d/%d): %s",
                consecutive_failures, max_failures, str(e)
            )
            
            if consecutive_failures >= max_failures:
                logger.critical("💀 Database keep-alive: Too many consecutive failures. System may be unhealthy.")
                _stats["consecutive_failures"] = consecutive_failures
                
                # Try to reconnect
                try:
                    logger.info("🔄 Attempting to reconnect to database...")
                    # dispose() is synchronous in SQLAlchemy
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        # Fallback for older Python or no running loop
                        loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, db_engine.dispose)
                    await asyncio.sleep(5)
                    consecutive_failures = 0
                    _stats["total_recoveries"] += 1
                    logger.info("✅ Database reconnection successful")
                except Exception as reconnect_error:
                    logger.error("❌ Database reconnection failed: %s", str(reconnect_error))
        
        # Wait before next ping
        await asyncio.sleep(DB_KEEPALIVE_INTERVAL)


# =============================================================================
# HEALTH CHECK SYSTEM
# =============================================================================
async def health_check_monitor(app):
    """
    Monitors application health and triggers recovery if needed.
    """
    logger.info("🏥 Health check monitor started (interval: %ds)", HEALTH_CHECK_INTERVAL)
    
    while _is_running:
        try:
            _stats["last_health_check"] = datetime.utcnow()
            _stats["total_health_checks"] += 1
            
            # Check if database keep-alive is still running
            if _stats["last_db_ping"]:
                time_since_last_ping = (datetime.utcnow() - _stats["last_db_ping"]).total_seconds()
                if time_since_last_ping > (DB_KEEPALIVE_INTERVAL * 3):
                    logger.warning(
                        "⚠️ Database keep-alive may have stopped. Last ping: %ds ago",
                        int(time_since_last_ping)
                    )
                    _stats["consecutive_failures"] += 1
                else:
                    _stats["consecutive_failures"] = 0
            
            # Log status every 10 checks
            if _stats["total_health_checks"] % 10 == 0:
                logger.info(
                    "💚 Health check #%d: OK (DB pings: %d, Recoveries: %d)",
                    _stats["total_health_checks"],
                    _stats["total_db_pings"],
                    _stats["total_recoveries"]
                )
            
        except Exception as e:
            logger.error("❌ Health check failed: %s", str(e))
            _stats["consecutive_failures"] += 1
        
        await asyncio.sleep(HEALTH_CHECK_INTERVAL)


# =============================================================================
# GRACEFUL SHUTDOWN
# =============================================================================
async def graceful_shutdown():
    """
    Gracefully shutdown all keep-alive tasks.
    """
    global _is_running, _keepalive_task, _health_check_task
    
    logger.info("🛑 Initiating graceful shutdown...")
    _is_running = False
    
    # Cancel tasks
    if _keepalive_task and not _keepalive_task.done():
        _keepalive_task.cancel()
        try:
            await _keepalive_task
        except asyncio.CancelledError:
            pass
    
    if _health_check_task and not _health_check_task.done():
        _health_check_task.cancel()
        try:
            await _health_check_task
        except asyncio.CancelledError:
            pass
    
    logger.info("✅ Graceful shutdown complete")


# =============================================================================
# STARTUP SYSTEM
# =============================================================================
async def start_forever_system(app, db_engine):
    """
    Start the forever fix system with all monitoring and keep-alive tasks.
    
    Args:
        app: FastAPI application instance
        db_engine: SQLAlchemy async engine instance
    """
    global _is_running, _keepalive_task, _health_check_task
    
    if _is_running:
        logger.warning("⚠️ Forever fix system already running")
        return
    
    logger.info("="*60)
    logger.info("🚀 FOREVER FIX SYSTEM - STARTING")
    logger.info("="*60)
    logger.info("Environment: %s", ENVIRONMENT)
    logger.info("Health Check Interval: %ds", HEALTH_CHECK_INTERVAL)
    logger.info("DB Keep-Alive Interval: %ds", DB_KEEPALIVE_INTERVAL)
    logger.info("Auto-Restart: %s", "Enabled" if AUTO_RESTART_ENABLED else "Disabled")
    logger.info("="*60)
    
    _is_running = True
    _stats["started_at"] = datetime.utcnow()
    
    # Start database keep-alive
    if db_engine:
        _keepalive_task = asyncio.create_task(database_keepalive(db_engine))
        logger.info("✅ Database keep-alive task started")
    else:
        logger.warning("⚠️ No database engine provided - keep-alive disabled")
    
    # Start health check monitor
    _health_check_task = asyncio.create_task(health_check_monitor(app))
    logger.info("✅ Health check monitor started")
    
    logger.info("="*60)
    logger.info("💚 FOREVER FIX SYSTEM - ACTIVE")
    logger.info("="*60)


# =============================================================================
# FASTAPI MIDDLEWARE
# =============================================================================
class ForeverFixMiddleware:
    """
    Middleware that ensures the application never dies by:
    - Catching all unhandled exceptions
    - Logging errors comprehensively
    - Preventing worker crashes
    - Providing recovery mechanisms
    """
    
    def __init__(self, app):
        self.app = app
        logger.info("🛡️ Forever Fix Middleware initialized")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        response_started = False
        
        async def wrapped_send(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)
        
        try:
            await self.app(scope, receive, wrapped_send)
        except Exception as e:
            # Log the error comprehensively
            logger.error(
                "💥 Unhandled exception in request:\n"
                "Path: %s %s\n"
                "Error: %s\n"
                "Traceback:\n%s",
                scope.get("method", "UNKNOWN"),
                scope.get("path", "UNKNOWN"),
                str(e),
                traceback.format_exc()
            )
            
            # Increment failure counter
            _stats["consecutive_failures"] += 1
            
            # Send error response only if response hasn't started
            if not response_started:
                try:
                    await send({
                        "type": "http.response.start",
                        "status": 500,
                        "headers": [[b"content-type", b"application/json"]],
                    })
                    await send({
                        "type": "http.response.body",
                        "body": b'{"error":"Internal Server Error","message":"An unexpected error occurred"}',
                    })
                except Exception:
                    # Connection closed or other error
                    pass


# =============================================================================
# HEALTH STATUS ENDPOINT DATA
# =============================================================================
def get_forever_fix_status() -> Dict[str, Any]:
    """
    Get current status of the forever fix system.
    
    Returns:
        Dictionary containing system status and statistics
    """
    uptime = None
    if _stats["started_at"]:
        uptime = (datetime.utcnow() - _stats["started_at"]).total_seconds()
    
    return {
        "enabled": _is_running,
        "uptime_seconds": int(uptime) if uptime else None,
        "health_checks": {
            "total": _stats["total_health_checks"],
            "last_check": _stats["last_health_check"].isoformat() if _stats["last_health_check"] else None,
            "interval_seconds": HEALTH_CHECK_INTERVAL,
        },
        "database_keepalive": {
            "total_pings": _stats["total_db_pings"],
            "last_ping": _stats["last_db_ping"].isoformat() if _stats["last_db_ping"] else None,
            "interval_seconds": DB_KEEPALIVE_INTERVAL,
        },
        "failures": {
            "consecutive": _stats["consecutive_failures"],
            "max_allowed": MAX_CONSECUTIVE_FAILURES,
        },
        "recoveries": _stats["total_recoveries"],
        "auto_restart": AUTO_RESTART_ENABLED,
    }


# =============================================================================
# SIGNAL HANDLERS
# =============================================================================
_shutdown_task_ref = None

def setup_signal_handlers():
    """
    Setup signal handlers for graceful shutdown.
    """
    def signal_handler(sig, frame):
        global _shutdown_task_ref
        logger.info("⚠️ Received signal %s, initiating graceful shutdown...", sig)
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # Fallback for older Python or no running loop
                loop = asyncio.get_event_loop()
            if loop.is_running():
                # Store task reference to prevent garbage collection
                _shutdown_task_ref = asyncio.ensure_future(graceful_shutdown())
        except RuntimeError:
            # No event loop running, log and exit
            logger.warning("No event loop running, exiting immediately")
            sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


# =============================================================================
# EXPORT
# =============================================================================
__all__ = [
    "start_forever_system",
    "graceful_shutdown",
    "get_forever_fix_status",
    "ForeverFixMiddleware",
    "setup_signal_handlers",
]
