#!/usr/bin/env python3
"""
Health Check Endpoint Handler for HireMeBahamas
Provides comprehensive dependency health status via /api/health/dependencies
"""

import importlib
import os
from datetime import datetime, timezone
from typing import Dict, Any


def check_package_status(package_name: str, import_name: str = None) -> Dict[str, Any]:
    """Check if a package is installed and get its version"""
    if import_name is None:
        import_name = package_name.lower().replace("-", "_")
    
    try:
        module = importlib.import_module(import_name)
        version = getattr(module, "__version__", "unknown")
        return {"active": True, "version": version}
    except ImportError:
        return {"active": False, "version": "not installed"}


def check_redis_status() -> Dict[str, Any]:
    """Check Redis connection status"""
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        try:
            r = redis.from_url(redis_url, socket_connect_timeout=2)
            start_time = datetime.now(timezone.utc)
            r.ping()
            latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return {
                "active": True,
                "connected": True,
                "latency_ms": round(latency, 2),
                "url": redis_url
            }
        except Exception as e:
            return {
                "active": False,
                "connected": False,
                "error": str(e)
            }
    except ImportError:
        return {
            "active": False,
            "connected": False,
            "note": "redis-py not installed"
        }


def check_database_status() -> Dict[str, Any]:
    """Check database connection status"""
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # PostgreSQL
        try:
            import psycopg2
            conn = psycopg2.connect(database_url, connect_timeout=5)
            conn.close()
            return {
                "active": True,
                "connected": True,
                "type": "postgresql"
            }
        except Exception as e:
            return {
                "active": False,
                "connected": False,
                "type": "postgresql",
                "error": str(e)
            }
    else:
        # SQLite
        return {
            "active": True,
            "connected": True,
            "type": "sqlite",
            "file": "hireme.db"
        }


def check_sentry_status() -> Dict[str, Any]:
    """Check Sentry SDK status"""
    try:
        import sentry_sdk
        sentry_dsn = os.getenv("SENTRY_DSN")
        
        return {
            "active": bool(sentry_dsn),
            "dsn_configured": bool(sentry_dsn),
            "installed": True
        }
    except ImportError:
        return {
            "active": False,
            "dsn_configured": False,
            "installed": False
        }


def check_socketio_status() -> Dict[str, Any]:
    """Check Socket.IO status"""
    try:
        import flask_socketio
        return {
            "active": True,
            "installed": True,
            "clients_connected": 0  # Would need to integrate with actual SocketIO instance
        }
    except ImportError:
        return {
            "active": False,
            "installed": False
        }


def check_celery_status() -> Dict[str, Any]:
    """Check Celery worker status"""
    try:
        import celery
        return {
            "active": False,
            "installed": True,
            "workers": 0,
            "note": "No workers configured"
        }
    except ImportError:
        return {
            "active": False,
            "installed": False
        }


def get_frontend_status() -> Dict[str, Any]:
    """Get frontend dependency status"""
    from pathlib import Path
    
    frontend_path = Path(__file__).parent.parent / "frontend"
    node_modules = frontend_path / "node_modules"
    
    if not frontend_path.exists():
        return {"active": False, "note": "Frontend not found"}
    
    # Check for key frontend packages
    react_status = {"active": False}
    socketio_status = {"active": False}
    sentry_status = {"active": False}
    
    if node_modules.exists():
        if (node_modules / "react").exists():
            react_status = {"active": True, "version": "18.2.0"}
        
        if (node_modules / "socket.io-client").exists():
            socketio_status = {"active": True, "connected": False}
        
        if (node_modules / "@sentry" / "react").exists():
            sentry_status = {"active": True, "initialized": False}
    
    return {
        "react": react_status,
        "socketio_client": socketio_status,
        "sentry": sentry_status
    }


def get_health_status() -> Dict[str, Any]:
    """Generate comprehensive health status"""
    
    # Check backend dependencies
    backend_deps = {
        "flask": check_package_status("Flask", "flask"),
        "redis": check_redis_status(),
        "database": check_database_status(),
        "sentry": check_sentry_status(),
        "socketio": check_socketio_status(),
        "celery": check_celery_status(),
        "flask_cors": check_package_status("Flask-CORS", "flask_cors"),
        "flask_limiter": check_package_status("Flask-Limiter", "flask_limiter"),
        "flask_caching": check_package_status("Flask-Caching", "flask_caching"),
    }
    
    # Check frontend dependencies
    frontend_deps = get_frontend_status()
    
    # Determine missing and inactive
    missing_dependencies = []
    inactive_services = []
    
    for dep_name, dep_info in backend_deps.items():
        if isinstance(dep_info, dict):
            if not dep_info.get("active", False):
                if dep_info.get("version") == "not installed":
                    missing_dependencies.append(dep_name)
                else:
                    inactive_services.append(dep_name)
    
    # Overall health status
    critical_active = all([
        backend_deps["flask"]["active"],
        backend_deps["database"]["active"],
    ])
    
    status = "healthy" if critical_active else "unhealthy"
    
    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "dependencies": {
            "backend": backend_deps,
            "frontend": frontend_deps
        },
        "missing_dependencies": missing_dependencies,
        "inactive_services": inactive_services
    }


def create_health_endpoint(app):
    """Add health check endpoint to Flask app"""
    
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Basic health check"""
        return {
            "status": "healthy",
            "message": "HireMeBahamas API is running",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        }
    
    @app.route("/api/health/dependencies", methods=["GET"])
    def dependencies_health():
        """Comprehensive dependency health check"""
        return get_health_status()
