#!/usr/bin/env python3
"""
Gunicorn Production Configuration - HireMeBahamas (2025)
Zero 502, Zero cold starts, Sub-800ms boot, Sub-300ms login globally
"""
import os
import multiprocessing
import time
import logging

# ============================================================================
# BIND CONFIGURATION
# ============================================================================
# ⚠️ CRITICAL: Validate port before binding
_port = os.environ.get('PORT', '10000')
_port_int = int(_port)

# DO NOT USE PORT 5432 - This is a PostgreSQL port, not for HTTP backends
if _port_int == 5432:
    import sys
    print("=" * 80, file=sys.stderr)
    print("❌ CRITICAL ERROR: HTTP service cannot use port 5432", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print("", file=sys.stderr)
    print("Port 5432 is reserved for PostgreSQL database servers.", file=sys.stderr)
    print("Your HTTP backend (gunicorn) should use a different port.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Common HTTP ports:", file=sys.stderr)
    print("  • 8000, 8080, 8888: Common development ports", file=sys.stderr)
    print("  • 10000: Render default", file=sys.stderr)
    print("  • Use $PORT environment variable for cloud deployments", file=sys.stderr)
    print("", file=sys.stderr)
    print("To fix this:", file=sys.stderr)
    print("  1. Check your PORT environment variable: echo $PORT", file=sys.stderr)
    print("  2. Unset PORT if it's 5432: unset PORT", file=sys.stderr)
    print("  3. Use correct port for HTTP: export PORT=8000", file=sys.stderr)
    print("  4. Never set PORT=5432 for web services", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    sys.exit(1)

bind = f"0.0.0.0:{_port}"

# ============================================================================
# WORKER CONFIGURATION (Optimized for Render Small Instances)
# ============================================================================
# Optimized for Render and similar PaaS platforms with small instance sizes
# CRITICAL: Render does NOT like many workers on small instances
# 
# Configuration for Render (AGGRESSIVE FOREVER FIX):
# - workers=1: Single worker is faster + safer on small instances
# - threads=2: Minimal threading for request handling
# - Total capacity: 1 worker with async event loop (handles many concurrent connections)
# 
# Benefits of single worker:
# - Lower memory footprint
# - Faster startup times
# - More predictable behavior on small instances
# - Prevents worker timeout issues on constrained resources
cpu_count = multiprocessing.cpu_count()

# Workers: 1 for optimal performance on Render small instances (CRITICAL)
# Use WEB_CONCURRENCY env var to override (but keep it at 1 for Render)
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))

# Worker class: uvicorn.workers.UvicornWorker for FastAPI async support
# Uvicorn workers provide ASGI support with excellent async/await performance
worker_class = "uvicorn.workers.UvicornWorker"

# Threads: 2 for minimal threading overhead (Render optimization)
# Note: UvicornWorker uses async event loop, not threads for concurrency
# With UvicornWorker:
# - Each worker runs an async event loop
# - Concurrency is handled via async/await, not threads
# - Single worker can handle 100+ concurrent connections efficiently
# - Threads parameter only used if switching to 'gthread' worker class
threads = int(os.environ.get("WEB_THREADS", "2"))

# ============================================================================
# TIMEOUT CONFIGURATION (Optimized for Render)
# ============================================================================
# Worker timeout: 120s - increased for startup and initialization on Render
# This prevents worker SIGTERM during slow startup on small instances
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))

# Graceful timeout: 30s for in-flight requests during shutdown
graceful_timeout = 30

# Keep-alive: 5s (matches most cloud load balancers)
keepalive = 5

# ============================================================================
# MEMORY MANAGEMENT (Prevents OOM on Free Tier)
# ============================================================================
# Restart worker after 1000 requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# ============================================================================
# PRELOAD & PERFORMANCE (DATABASE SAFETY - CRITICAL)
# ============================================================================
# ⚠️ CRITICAL WARNING: Never use --preload with databases!
#
# Preload app setting:
# - True: Load app once before forking (DANGEROUS with databases)
# - False: Each worker loads app independently (SAFE with databases)
#
# Why preload_app = False is critical for database applications:
# 1. Database connection pools cannot be safely shared across fork()
# 2. Each worker needs its own database connections
# 3. Prevents health check failures during initialization
# 4. Allows /health endpoint to respond while workers initialize
# 5. Avoids worker synchronization issues with shared state
#
# ⚠️ NEVER override this with --preload on the command line!
# Command line: poetry run gunicorn final_backend_postgresql:application --config gunicorn.conf.py
# Do NOT add: --preload (this would override the safe setting below)
#
# SAFE COMMAND:   gunicorn final_backend_postgresql:application --config gunicorn.conf.py
# UNSAFE COMMAND: gunicorn final_backend_postgresql:application --config gunicorn.conf.py --preload
preload_app = False

# ============================================================================
# LOGGING (Production-grade)
# ============================================================================
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'


class SIGTERMContextFilter(logging.Filter):
    """
    Custom logging filter to add context to SIGTERM messages.
    
    When Gunicorn master sends SIGTERM to workers, it logs at ERROR level:
    "[ERROR] Worker (pid:X) was sent SIGTERM!"
    
    This is NORMAL during deployments but looks alarming. This filter adds
    helpful context immediately after the SIGTERM message.
    """
    
    def filter(self, record):
        """Add context message after SIGTERM logs."""
        # Check if this is a SIGTERM message from Gunicorn master
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            if 'was sent SIGTERM' in record.msg or 'was sent SIG' in record.msg:
                # Get the original message
                original_msg = record.msg
                
                # Get timeout value from environment or default
                worker_timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
                
                # Add helpful context
                context = (
                    f"\n{'─'*80}\n"
                    f"ℹ️  SIGTERM CONTEXT: This is NORMAL during:\n"
                    f"   ✓ Deployments and service restarts\n"
                    f"   ✓ Configuration reloads  \n"
                    f"   ✓ Platform maintenance\n"
                    f"   ✓ Scaling operations\n"
                    f"\n"
                    f"⚠️  Only investigate if this happens repeatedly OUTSIDE deployments:\n"
                    f"   • Check for timeout issues (workers exceeding {worker_timeout}s)\n"
                    f"   • Monitor memory usage (potential OOM kills)\n"
                    f"   • Review application errors before SIGTERM\n"
                    f"   • Check for slow database queries or API calls\n"
                    f"{'─'*80}"
                )
                
                # Append context to the message
                record.msg = original_msg + context
        
        return True


# Custom logger class to provide better context for worker signals
logconfig_dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'sigterm_context': {
            '()': SIGTERMContextFilter,
        }
    },
    'formatters': {
        'generic': {
            'format': '%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S %z',
            'class': 'logging.Formatter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic',
            'stream': 'ext://sys.stdout'
        },
        'error_console': {
            'class': 'logging.StreamHandler',
            'formatter': 'generic',
            'filters': ['sigterm_context'],
            'stream': 'ext://sys.stderr'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    },
    'loggers': {
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['error_console'],
            'propagate': False,
            'qualname': 'gunicorn.error'
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
            'qualname': 'gunicorn.access'
        }
    }
}

# ============================================================================
# PROCESS NAMING
# ============================================================================
proc_name = "hiremebahamas"

# ============================================================================
# SECURITY
# ============================================================================
# Trust proxy headers from cloud platform load balancers (Render, etc.)
forwarded_allow_ips = "*"

# ============================================================================
# STARTUP HOOKS
# ============================================================================
_master_start_time = None


def _get_worker_timeout():
    """Get the worker timeout value from environment or config default.
    
    Returns:
        int: Worker timeout in seconds
    """
    import os
    return int(os.environ.get("GUNICORN_TIMEOUT", str(timeout)))


def on_starting(server):
    """Log startup configuration"""
    global _master_start_time
    _master_start_time = time.time()
    print("")
    print("="*80)
    print("  HireMeBahamas API - Production Configuration")
    print("="*80)
    print(f"  Workers: {workers} (single worker = predictable memory)")
    print(f"  Threads: {threads} (async event loop handles concurrency)")
    print(f"  Timeout: {timeout}s (prevents premature SIGTERM)")
    print(f"  Graceful: {graceful_timeout}s (clean shutdown)")
    print(f"  Keepalive: {keepalive}s (connection persistence)")
    print(f"  Preload: {preload_app} (safe for database apps)")
    print(f"  Worker Class: {worker_class} (async)")
    print("")
    print("  This is how production FastAPI apps actually run.")
    print("="*80)
    print("")


def when_ready(server):
    """Log when server is ready to accept connections"""
    if _master_start_time:
        startup_time = time.time() - _master_start_time
        print(f"✅ Gunicorn master ready in {startup_time:.2f}s")
    print(f"   Listening on {bind}")
    print(f"   Health endpoint: GET /health (instant, no DB)")
    print(f"   Ready endpoint: GET /ready (instant, no DB)")
    print(f"   DB Ready: GET /ready/db (with DB check)")
    print("")
    print("🎉 HireMeBahamas API is READY")
    print("")


def on_exit(server):
    """Called on graceful shutdown"""
    print("🛑 Gunicorn shutting down...")


def worker_exit(server, worker):
    """Called when a worker exits.
    
    This hook ensures proper cleanup of async resources when a worker is restarted.
    CRITICAL for preventing "Task was destroyed but it is pending!" warnings.
    """
    import sys
    import asyncio
    
    print(f"👷 Worker {worker.pid} exiting - cleaning up async resources...")
    
    # Try to clean up any pending async tasks in the worker's event loop
    try:
        # Get the event loop if it exists
        try:
            loop = asyncio.get_event_loop()
            if loop and not loop.is_closed():
                # Cancel all pending tasks
                pending_tasks = [
                    task for task in asyncio.all_tasks(loop)
                    if not task.done()
                ]
                
                if pending_tasks:
                    print(f"   Cancelling {len(pending_tasks)} pending tasks in worker {worker.pid}...", file=sys.stderr)
                    for task in pending_tasks:
                        # Double-check task is still pending before cancelling (prevents race condition)
                        if not task.done():
                            task.cancel()
                    
                    # Give tasks a moment to cancel
                    # Note: Can't use asyncio.wait here since we're in a sync context
                    # Tasks will be cleaned up when the loop is closed
                
                # Close the event loop
                if not loop.is_closed():
                    loop.close()
                    print(f"   Event loop closed for worker {worker.pid}", file=sys.stderr)
        except RuntimeError:
            # No event loop in current thread - this is fine
            pass
    except Exception as e:
        print(f"   Warning: Error during worker cleanup: {e}", file=sys.stderr)
    
    print(f"✅ Worker {worker.pid} cleanup complete")


def worker_int(worker):
    """Called when a worker receives SIGINT or SIGQUIT signal.
    
    This hook is triggered when Gunicorn sends SIGTERM/SIGINT/SIGQUIT to a worker:
    - During graceful shutdown (deployment, restart)
    - When worker needs to be terminated cleanly
    - Before escalating to SIGABRT for unresponsive workers
    
    IMPORTANT: Gunicorn master process will also log "Worker (pid:X) was sent SIGTERM!"
    at ERROR level. This is normal behavior and doesn't indicate a problem.
    
    Args:
        worker: The worker instance being interrupted
    """
    import sys
    # Get timeout from helper function
    worker_timeout = _get_worker_timeout()
    
    # Use stderr to ensure this appears near Gunicorn's ERROR log
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"ℹ️  WORKER INTERRUPT SIGNAL RECEIVED - PID {worker.pid}", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"Signal: SIGTERM/SIGINT/SIGQUIT (graceful shutdown)", file=sys.stderr)
    print(f"Worker: {worker.pid}", file=sys.stderr)
    print(f"Status: This is NORMAL during:", file=sys.stderr)
    print(f"  ✓ Deployments and service restarts", file=sys.stderr)
    print(f"  ✓ Configuration reloads", file=sys.stderr)
    print(f"  ✓ Manual service restarts", file=sys.stderr)
    print(f"  ✓ Platform maintenance windows", file=sys.stderr)
    print(f"\n⚠️  Only investigate if this happens frequently OUTSIDE of deployments:", file=sys.stderr)
    print(f"  • Check if workers are timing out during requests (>{worker_timeout}s)", file=sys.stderr)
    print(f"  • Review application logs for errors before SIGTERM", file=sys.stderr)
    print(f"  • Monitor memory usage (workers may be OOM killed)", file=sys.stderr)
    print(f"  • Check for slow database queries or API calls", file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)


def worker_abort(worker):
    """Called when a worker is forcibly terminated (SIGABRT).
    
    This hook is triggered when Gunicorn sends SIGABRT to a worker because:
    - Worker exceeded the timeout (didn't respond within timeout seconds)
    - Worker became unresponsive or hung
    - Master process needs to forcibly terminate the worker
    
    ⚠️  THIS IS A CRITICAL ERROR - Unlike SIGTERM, SIGABRT indicates a real problem.
    
    Args:
        worker: The worker instance being aborted
    """
    import sys
    # Get timeout from helper function
    worker_timeout = _get_worker_timeout()
    
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"❌ CRITICAL: WORKER ABORTED - PID {worker.pid}", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    print(f"Signal: SIGABRT (forceful termination)", file=sys.stderr)
    print(f"Worker: {worker.pid}", file=sys.stderr)
    print(f"Timeout: {worker_timeout}s (exceeded)", file=sys.stderr)
    print(f"\n⚠️  This worker was forcibly killed because it exceeded the timeout.", file=sys.stderr)
    print(f"This indicates a serious problem that MUST be investigated:\n", file=sys.stderr)
    print(f"Common causes:", file=sys.stderr)
    print(f"  1. Blocking database operations (long queries, connection issues)", file=sys.stderr)
    print(f"  2. Slow external API calls without timeout", file=sys.stderr)
    print(f"  3. Deadlocks or infinite loops in application code", file=sys.stderr)
    print(f"  4. Database connection pool exhaustion", file=sys.stderr)
    print(f"  5. CPU-intensive operations blocking the event loop", file=sys.stderr)
    print(f"\nNext steps:", file=sys.stderr)
    print(f"  • Check application logs immediately before this abort", file=sys.stderr)
    print(f"  • Review recent endpoint requests and their duration", file=sys.stderr)
    print(f"  • Monitor database connection pool status", file=sys.stderr)
    print(f"  • Use APM tools to identify slow operations", file=sys.stderr)
    print(f"  • Consider increasing timeout only if operations legitimately need more time", file=sys.stderr)
    print(f"{'='*80}\n", file=sys.stderr)


def post_fork(server, worker):
    """Called after worker fork"""
    print(f"👶 Booting worker with pid {worker.pid}")

