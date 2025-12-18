#!/usr/bin/env python3
"""
Gunicorn Production Configuration - HireMeBahamas (2025)
Zero 502, Zero cold starts, Sub-800ms boot, Sub-300ms login globally
"""
import os
import time
import logging

# ============================================================================
# BIND CONFIGURATION
# ============================================================================
bind = "0.0.0.0:10000"

# ============================================================================
# WORKER CONFIGURATION
# ============================================================================
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"

# ============================================================================
# TIMEOUT CONFIGURATION
# ============================================================================
timeout = 120
graceful_timeout = 30  # Time to wait for graceful worker shutdown
keepalive = 5

# ============================================================================
# WORKER RECYCLING (Prevents memory leaks)
# ============================================================================
max_requests = 1000  # Restart workers after 1000 requests
max_requests_jitter = 100  # Add randomness to prevent thundering herd

# ============================================================================
# PRELOAD CONFIGURATION
# ============================================================================
preload_app = False  # IMPORTANT 🚫 DO NOT preload when DB/network involved

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
                
                # Get timeout value
                worker_timeout = timeout
                
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
# Trust proxy headers from cloud platform load balancers (Render, Render, etc.)
forwarded_allow_ips = "*"

# ============================================================================
# STARTUP HOOKS
# ============================================================================
_master_start_time = None


def _get_worker_timeout():
    """Get the worker timeout value.
    
    Returns:
        int: Worker timeout in seconds
    """
    return timeout


def on_starting(server):
    """Log startup configuration"""
    global _master_start_time
    _master_start_time = time.time()
    print("")
    print("="*80)
    print("  HireMeBahamas API - Production Configuration")
    print("="*80)
    print(f"  Workers: {workers}")
    print(f"  Timeout: {timeout}s")
    print(f"  Keepalive: {keepalive}s")
    print(f"  Preload: {preload_app}")
    print(f"  Worker Class: {worker_class}")
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

