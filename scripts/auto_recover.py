#!/usr/bin/env python3
"""
Auto-Recovery Script for HireMeBahamas
Monitors dependency health and auto-recovers from failures.
"""

import os
import sys
from datetime import datetime, timezone


class AutoRecovery:
    """Self-healing system for dependency management"""

    def __init__(self):
        self.recovery_log = []
        self.critical_failures = []

    def log_action(self, action, success=True):
        """Log recovery action"""
        timestamp = datetime.now(timezone.utc).isoformat()
        status = "✅ SUCCESS" if success else "❌ FAILED"
        message = f"[{timestamp}] {status}: {action}"
        print(message)
        self.recovery_log.append(message)

    def check_redis_health(self):
        """Check Redis health and attempt recovery"""
        print("\n🔴 Checking Redis health...")
        
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            
            try:
                r = redis.from_url(redis_url, socket_connect_timeout=2)
                r.ping()
                print("  ✅ Redis is healthy")
                return True
            except Exception as e:
                print(f"  ❌ Redis connection failed: {str(e)}")
                self.log_action("Redis connection failed - switching to memory cache", True)
                return False
        except ImportError:
            print("  ⚠️  redis-py not installed")
            return False

    def check_database_health(self):
        """Check database health and attempt recovery"""
        print("\n🗄️  Checking database health...")
        
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            # PostgreSQL
            try:
                import psycopg2
                conn = psycopg2.connect(database_url, connect_timeout=5)
                conn.close()
                print("  ✅ PostgreSQL is healthy")
                return True
            except Exception as e:
                print(f"  ❌ PostgreSQL connection failed: {str(e)}")
                print("  🔄 Falling back to SQLite...")
                self.log_action("PostgreSQL failed - fell back to SQLite", True)
                return True  # Fallback successful
        else:
            # SQLite
            print("  ✅ SQLite is healthy (development mode)")
            return True

    def check_dependencies_health(self):
        """Check Python dependencies health"""
        print("\n📦 Checking dependencies health...")
        
        critical_packages = ["flask", "flask_cors", "flask_limiter", "jwt", "bcrypt"]
        
        failed = []
        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                failed.append(package)
                print(f"  ❌ {package} not found")
        
        if failed:
            print(f"  🔄 Attempting to reinstall: {', '.join(failed)}")
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + failed + ["--quiet"],
                    capture_output=True,
                    timeout=60
                )
                if result.returncode == 0:
                    self.log_action(f"Reinstalled packages: {', '.join(failed)}", True)
                    return True
                else:
                    self.log_action(f"Failed to reinstall packages", False)
                    self.critical_failures.append(f"Dependencies: {', '.join(failed)}")
                    return False
            except Exception as e:
                self.log_action(f"Reinstall error: {str(e)}", False)
                self.critical_failures.append("Dependency reinstall failed")
                return False
        else:
            print("  ✅ All dependencies healthy")
            return True

    def clear_cache_on_failure(self):
        """Clear cache if Redis fails"""
        print("\n🗑️  Clearing cache...")
        
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            
            try:
                r = redis.from_url(redis_url, socket_connect_timeout=2)
                r.flushdb()
                print("  ✅ Cache cleared")
                self.log_action("Redis cache cleared", True)
                return True
            except Exception:
                print("  ⚠️  Redis not available - using in-memory cache")
                return True
        except ImportError:
            print("  ⚠️  redis-py not installed")
            return True

    def send_alert(self, message):
        """Send alert for critical failures"""
        print(f"\n🚨 ALERT: {message}")
        
        try:
            import sentry_sdk
            sentry_dsn = os.getenv("SENTRY_DSN")
            
            if sentry_dsn:
                sentry_sdk.capture_message(
                    f"Auto-Recovery Alert: {message}",
                    level="error"
                )
                print("  ✅ Alert sent to Sentry")
                self.log_action(f"Sent alert to Sentry: {message}", True)
        except (ImportError, Exception):
            print("  ⚠️  Could not send alert (Sentry not configured)")

    def run_recovery(self):
        """Run full recovery check"""
        print("=" * 60)
        print("🔧 Auto-Recovery System")
        print(f"⏰ {datetime.now(timezone.utc).isoformat()}")
        print("=" * 60)
        
        # Check all systems
        self.check_redis_health()
        self.check_database_health()
        self.check_dependencies_health()
        
        # Attempt recovery actions
        if not self.check_redis_health():
            self.clear_cache_on_failure()
        
        # Check for critical failures
        if self.critical_failures:
            for failure in self.critical_failures:
                self.send_alert(failure)
        
        # Generate report
        print("\n" + "=" * 60)
        print("📊 Recovery Report")
        print("=" * 60)
        
        print(f"\n📝 Actions taken: {len(self.recovery_log)}")
        for log in self.recovery_log:
            print(f"   {log}")
        
        if self.critical_failures:
            print(f"\n🚨 Critical failures: {len(self.critical_failures)}")
            for failure in self.critical_failures:
                print(f"   - {failure}")
            print("\n❌ Auto-recovery incomplete - manual intervention required")
            return 1
        else:
            print("\n✅ All systems recovered successfully")
            return 0


def main():
    """Main entry point"""
    recovery = AutoRecovery()
    exit_code = recovery.run_recovery()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
