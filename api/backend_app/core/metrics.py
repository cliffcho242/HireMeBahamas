"""
Prometheus metrics module for HireMeBahamas backend.

Provides standardized metrics for monitoring application health, performance,
and error tracking. Compatible with Prometheus and Grafana dashboards.

Metrics categories:
- HTTP request metrics (count, duration, errors)
- Database connection metrics (pool size, active connections)
- Application health metrics (uptime, version)

Usage:
    from app.core.metrics import (
        request_counter, 
        request_duration, 
        get_metrics_response
    )
    
    # In request handler:
    request_counter.labels(method="GET", endpoint="/api/health", status="200").inc()
"""
import time
from functools import wraps
from typing import Callable

# Try to import prometheus_client, fall back gracefully if not available
try:
    from prometheus_client import (
        Counter,
        Gauge,
        Histogram,
        Info,
        CollectorRegistry,
        generate_latest,
        CONTENT_TYPE_LATEST,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create dummy classes for graceful degradation
    class DummyMetric:
        """Dummy metric class when prometheus_client is not available."""
        def labels(self, **kwargs):
            return self
        def inc(self, amount=1):
            pass
        def dec(self, amount=1):
            pass
        def set(self, value):
            pass
        def observe(self, value):
            pass
        def info(self, value):
            pass
    
    Counter = Gauge = Histogram = Info = lambda *args, **kwargs: DummyMetric()
    CollectorRegistry = None
    CONTENT_TYPE_LATEST = "text/plain"
    
    def generate_latest(registry=None):
        return b"# prometheus_client not installed\n"

# Create a custom registry for the application metrics
# This avoids conflicts with the default registry
if PROMETHEUS_AVAILABLE:
    REGISTRY = CollectorRegistry()
else:
    REGISTRY = None

# Application info metric
app_info = Info(
    "hiremebahamas_app",
    "Application information",
    registry=REGISTRY
) if PROMETHEUS_AVAILABLE else DummyMetric()

# HTTP Request Metrics
request_counter = Counter(
    "hiremebahamas_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=REGISTRY
) if PROMETHEUS_AVAILABLE else DummyMetric()

request_duration = Histogram(
    "hiremebahamas_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
    registry=REGISTRY
) if PROMETHEUS_AVAILABLE else DummyMetric()

# Error metrics
request_errors = Counter(
    "hiremebahamas_http_request_errors_total",
    "Total HTTP request errors (4xx and 5xx)",
    ["method", "endpoint", "status", "error_type"],
    registry=REGISTRY
) if PROMETHEUS_AVAILABLE else DummyMetric()

# Database Metrics
db_connections_active = Gauge(
    "hiremebahamas_db_connections_active",
    "Number of active database connections",
    registry=REGISTRY
) if PROMETHEUS_AVAILABLE else DummyMetric()

db_connections_pool_size = Gauge(
    "hiremebahamas_db_connections_pool_size",
    "Database connection pool size",
    registry=REGISTRY
) if PROMETHEUS_AVAILABLE else DummyMetric()

db_query_duration = Histogram(
    "hiremebahamas_db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=REGISTRY
) if PROMETHEUS_AVAILABLE else DummyMetric()

# Authentication Metrics
auth_attempts = Counter(
    "hiremebahamas_auth_attempts_total",
    "Total authentication attempts",
    ["type", "status"],  # type: login, register; status: success, failure
    registry=REGISTRY
) if PROMETHEUS_AVAILABLE else DummyMetric()

# Application Health
app_uptime = Gauge(
    "hiremebahamas_app_uptime_seconds",
    "Application uptime in seconds",
    registry=REGISTRY
) if PROMETHEUS_AVAILABLE else DummyMetric()

# Start time for uptime calculation
_start_time = time.time()


def update_uptime():
    """Update the uptime metric."""
    app_uptime.set(time.time() - _start_time)


def set_app_info(version: str, environment: str):
    """Set application info metric.
    
    Args:
        version: Application version string
        environment: Environment name (production, development, etc.)
    """
    if PROMETHEUS_AVAILABLE:
        app_info.info({
            "version": version,
            "environment": environment,
        })


def get_metrics_response():
    """Generate Prometheus metrics response.
    
    Returns:
        Tuple of (metrics_data, content_type) for HTTP response
    """
    update_uptime()
    
    if PROMETHEUS_AVAILABLE:
        return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
    else:
        return b"# prometheus_client not installed\n", "text/plain"


def track_request_duration(endpoint: str):
    """Decorator to track request duration.
    
    Args:
        endpoint: The endpoint name for the metric label
        
    Returns:
        Decorated function that tracks duration
        
    Example:
        @track_request_duration("/api/users")
        def get_users():
            # ... handler code ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, method: str = "UNKNOWN", **kwargs):
            """Track request duration.
            
            Args:
                method: HTTP method, passed explicitly or extracted from framework context
                *args: Positional arguments for the wrapped function
                **kwargs: Keyword arguments for the wrapped function
            """
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        return wrapper
    return decorator


def record_request(method: str, endpoint: str, status_code: int):
    """Record an HTTP request for metrics.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: The endpoint path
        status_code: HTTP status code of the response
    """
    request_counter.labels(
        method=method, 
        endpoint=endpoint, 
        status=str(status_code)
    ).inc()
    
    # Track errors separately
    if status_code >= 400:
        error_type = "client_error" if status_code < 500 else "server_error"
        request_errors.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code),
            error_type=error_type
        ).inc()


def record_auth_attempt(auth_type: str, success: bool):
    """Record an authentication attempt.
    
    Args:
        auth_type: Type of authentication (login, register, oauth)
        success: Whether the attempt was successful
    """
    status = "success" if success else "failure"
    auth_attempts.labels(type=auth_type, status=status).inc()


def record_db_query(operation: str, duration: float):
    """Record a database query duration.
    
    Args:
        operation: The type of database operation (select, insert, update, delete)
        duration: Query duration in seconds
    """
    db_query_duration.labels(operation=operation).observe(duration)


def update_db_pool_metrics(active: int, pool_size: int):
    """Update database connection pool metrics.
    
    Args:
        active: Number of currently active connections
        pool_size: Total pool size
    """
    db_connections_active.set(active)
    db_connections_pool_size.set(pool_size)
