"""
Performance Monitoring for Facebook/Instagram-Level Response Times

Tracks and logs:
- API response times (target: 50-150ms)
- Database query performance
- Cache hit rates
- Error rates
"""
import time
import logging
import threading
from typing import Optional, Dict, Any
from functools import wraps
from fastapi import Request

logger = logging.getLogger(__name__)

# Performance metrics storage (in-memory for simplicity)
# Thread-safe with lock for concurrent access
_metrics_lock = threading.Lock()
_metrics = {
    "requests": {"total": 0, "by_endpoint": {}},
    "response_times": {"total_ms": 0, "count": 0, "by_endpoint": {}},
    "cache": {"hits": 0, "misses": 0},
    "database": {"queries": 0, "total_time_ms": 0},
    "errors": {"4xx": 0, "5xx": 0},
}


def track_request_time(endpoint: str, duration_ms: float, status_code: int):
    """Track request timing and status (thread-safe).
    
    Args:
        endpoint: API endpoint path
        duration_ms: Request duration in milliseconds
        status_code: HTTP status code
    """
    with _metrics_lock:
        # Update total requests
        _metrics["requests"]["total"] += 1
        if endpoint not in _metrics["requests"]["by_endpoint"]:
            _metrics["requests"]["by_endpoint"][endpoint] = 0
        _metrics["requests"]["by_endpoint"][endpoint] += 1
        
        # Update response times
        _metrics["response_times"]["total_ms"] += duration_ms
        _metrics["response_times"]["count"] += 1
        
        if endpoint not in _metrics["response_times"]["by_endpoint"]:
            _metrics["response_times"]["by_endpoint"][endpoint] = {
                "total_ms": 0,
                "count": 0,
                "min_ms": float('inf'),
                "max_ms": 0,
            }
        
        endpoint_metrics = _metrics["response_times"]["by_endpoint"][endpoint]
        endpoint_metrics["total_ms"] += duration_ms
        endpoint_metrics["count"] += 1
        endpoint_metrics["min_ms"] = min(endpoint_metrics["min_ms"], duration_ms)
        endpoint_metrics["max_ms"] = max(endpoint_metrics["max_ms"], duration_ms)
        
        # Update error counts
        if 400 <= status_code < 500:
            _metrics["errors"]["4xx"] += 1
        elif status_code >= 500:
            _metrics["errors"]["5xx"] += 1
    
    # Log slow requests (>150ms)
    if duration_ms > 150:
        logger.warning(
            f"Slow request: {endpoint} took {duration_ms:.0f}ms (target: <150ms)"
        )
    
    # Log very fast requests for celebration 🎉
    if duration_ms < 50:
        logger.debug(
            f"⚡ Lightning fast: {endpoint} completed in {duration_ms:.0f}ms"
        )


def track_cache_hit():
    """Track a cache hit (thread-safe)."""
    with _metrics_lock:
        _metrics["cache"]["hits"] += 1


def track_cache_miss():
    """Track a cache miss (thread-safe)."""
    with _metrics_lock:
        _metrics["cache"]["misses"] += 1


def track_database_query(duration_ms: float):
    """Track a database query (thread-safe).
    
    Args:
        duration_ms: Query duration in milliseconds
    """
    with _metrics_lock:
        _metrics["database"]["queries"] += 1
        _metrics["database"]["total_time_ms"] += duration_ms


def get_performance_metrics() -> Dict[str, Any]:
    """Get current performance metrics (thread-safe).
    
    Returns:
        Dictionary with all performance metrics
    """
    with _metrics_lock:
        # Calculate averages
        avg_response_time = (
            _metrics["response_times"]["total_ms"] / _metrics["response_times"]["count"]
            if _metrics["response_times"]["count"] > 0
            else 0
        )
        
        avg_db_time = (
            _metrics["database"]["total_time_ms"] / _metrics["database"]["queries"]
            if _metrics["database"]["queries"] > 0
            else 0
        )
        
        cache_hit_rate = (
            _metrics["cache"]["hits"]
            / (_metrics["cache"]["hits"] + _metrics["cache"]["misses"])
            if (_metrics["cache"]["hits"] + _metrics["cache"]["misses"]) > 0
            else 0
        )
        
        # Calculate per-endpoint averages
        endpoint_stats = {}
        for endpoint, metrics in _metrics["response_times"]["by_endpoint"].items():
            endpoint_stats[endpoint] = {
                "avg_ms": metrics["total_ms"] / metrics["count"],
                "min_ms": metrics["min_ms"],
                "max_ms": metrics["max_ms"],
                "count": metrics["count"],
            }
        
        return {
            "requests": {
                "total": _metrics["requests"]["total"],
                "avg_response_time_ms": round(avg_response_time, 2),
            },
            "cache": {
                "hit_rate": round(cache_hit_rate * 100, 2),
                "hits": _metrics["cache"]["hits"],
                "misses": _metrics["cache"]["misses"],
            },
            "database": {
                "queries": _metrics["database"]["queries"],
                "avg_query_time_ms": round(avg_db_time, 2),
            },
            "errors": {
                "4xx": _metrics["errors"]["4xx"],
                "5xx": _metrics["errors"]["5xx"],
            },
            "endpoints": endpoint_stats,
            "performance_targets": {
                "api_response_target_ms": "50-150",
                "cache_hit_rate_target": ">80%",
                "page_load_target": "<1s",
            },
        }


def monitor_performance(func):
    """Decorator to monitor function performance.
    
    Usage:
        @monitor_performance
        async def my_endpoint():
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration_ms = (time.time() - start_time) * 1000
            
            # Extract endpoint name
            endpoint = func.__name__
            
            # Log performance
            if duration_ms > 150:
                logger.warning(
                    f"Function {endpoint} took {duration_ms:.0f}ms (target: <150ms)"
                )
    
    return wrapper


async def log_performance_summary():
    """Log a summary of performance metrics.
    
    Should be called periodically (e.g., every hour).
    """
    metrics = get_performance_metrics()
    
    logger.info("=" * 60)
    logger.info("PERFORMANCE SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Requests: {metrics['requests']['total']}")
    logger.info(
        f"Average Response Time: {metrics['requests']['avg_response_time_ms']}ms "
        f"(target: 50-150ms)"
    )
    logger.info(
        f"Cache Hit Rate: {metrics['cache']['hit_rate']}% "
        f"(target: >80%)"
    )
    logger.info(
        f"Database Avg Query Time: {metrics['database']['avg_query_time_ms']}ms"
    )
    logger.info(f"4xx Errors: {metrics['errors']['4xx']}")
    logger.info(f"5xx Errors: {metrics['errors']['5xx']}")
    
    # Log slowest endpoints
    if metrics["endpoints"]:
        logger.info("\nSlowest Endpoints:")
        sorted_endpoints = sorted(
            metrics["endpoints"].items(),
            key=lambda x: x[1]["avg_ms"],
            reverse=True,
        )[:5]
        
        for endpoint, stats in sorted_endpoints:
            logger.info(
                f"  {endpoint}: {stats['avg_ms']:.0f}ms avg "
                f"(min: {stats['min_ms']:.0f}ms, max: {stats['max_ms']:.0f}ms, "
                f"count: {stats['count']})"
            )
    
    logger.info("=" * 60)


def reset_metrics():
    """Reset all performance metrics.
    
    Useful for testing or starting fresh after configuration changes.
    """
    global _metrics
    _metrics = {
        "requests": {"total": 0, "by_endpoint": {}},
        "response_times": {"total_ms": 0, "count": 0, "by_endpoint": {}},
        "cache": {"hits": 0, "misses": 0},
        "database": {"queries": 0, "total_time_ms": 0},
        "errors": {"4xx": 0, "5xx": 0},
    }
    logger.info("Performance metrics reset")
