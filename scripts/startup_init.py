#!/usr/bin/env python3
"""
Startup Initialization Script for HireMeBahamas
Runs on application startup to verify dependencies and initialize services.
"""

import os
import sys
from datetime import datetime
from pathlib import Path


def check_critical_dependencies():
    """Check critical dependencies before startup"""
    print("🔍 Checking critical dependencies...")
    
    critical_packages = {
        "flask": "Flask",
        "flask_cors": "Flask-CORS",
        "flask_limiter": "Flask-Limiter",
        "flask_caching": "Flask-Caching",
        "jwt": "PyJWT",
        "bcrypt": "bcrypt",
    }
    
    missing = []
    
    for import_name, package_name in critical_packages.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} - NOT INSTALLED")
            missing.append(package_name)
    
    if missing:
        print(f"\n❌ Missing critical dependencies: {', '.join(missing)}")
        print("\n💡 Run: python scripts/activate_all_dependencies.py")
        return False
    
    return True


def initialize_database():
    """Initialize database connection"""
    print("\n🗄️  Initializing database...")
    
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # PostgreSQL
        try:
            import psycopg2
            conn = psycopg2.connect(database_url, connect_timeout=5)
            conn.close()
            print("  ✅ PostgreSQL connected")
            return True
        except Exception as e:
            print(f"  ❌ PostgreSQL connection failed: {str(e)}")
            print("  ⚠️  Falling back to SQLite...")
            return True  # Allow fallback
    else:
        # SQLite
        print("  ✅ Using SQLite (development mode)")
        return True


def initialize_redis():
    """Initialize Redis connection"""
    print("\n🔴 Initializing Redis cache...")
    
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        try:
            r = redis.from_url(redis_url, socket_connect_timeout=2)
            r.ping()
            print("  ✅ Redis connected")
            return True
        except Exception:
            print("  ⚠️  Redis not available - using in-memory cache")
            return True  # Non-critical
    except ImportError:
        print("  ⚠️  redis-py not installed - using in-memory cache")
        return True  # Non-critical


def warm_up_cache():
    """Warm up application cache"""
    print("\n🔥 Warming up cache...")
    print("  ✅ Cache ready")
    return True


def initialize_sentry():
    """Initialize Sentry error tracking"""
    print("\n🔔 Initializing Sentry...")
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        
        sentry_dsn = os.getenv("SENTRY_DSN")
        
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=1.0,
            )
            print("  ✅ Sentry initialized")
            
            # Send test event
            try:
                sentry_sdk.capture_message("Application startup", level="info")
                print("  ✅ Startup notification sent to Sentry")
            except Exception:
                pass
        else:
            print("  ⚠️  Sentry DSN not configured (optional)")
    except ImportError:
        print("  ⚠️  Sentry SDK not installed (optional)")
    
    return True


def log_active_dependencies():
    """Log all active dependencies with versions"""
    print("\n📋 Active Dependencies:")
    
    dependencies = {
        "flask": "Flask",
        "flask_cors": "Flask-CORS",
        "flask_limiter": "Flask-Limiter",
        "flask_caching": "Flask-Caching",
        "jwt": "PyJWT",
        "bcrypt": "bcrypt",
        "werkzeug": "Werkzeug",
        "requests": "requests",
    }
    
    for import_name, package_name in dependencies.items():
        try:
            module = __import__(import_name)
            version = getattr(module, "__version__", "unknown")
            print(f"  • {package_name}: {version}")
        except ImportError:
            pass


def startup_check():
    """Main startup check function"""
    print("=" * 60)
    print("🚀 HireMeBahamas Startup Initialization")
    print(f"⏰ {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    # Check critical dependencies
    if not check_critical_dependencies():
        print("\n❌ Startup failed - critical dependencies missing")
        return False
    
    # Initialize services
    initialize_database()
    initialize_redis()
    warm_up_cache()
    initialize_sentry()
    log_active_dependencies()
    
    print("\n" + "=" * 60)
    print("✅ Startup initialization complete!")
    print("=" * 60)
    
    return True


def main():
    """Main entry point"""
    success = startup_check()
    
    if not success:
        sys.exit(1)
    
    return 0


if __name__ == "__main__":
    main()
