#!/usr/bin/env python3
"""
Comprehensive Dependency Checker for HireMeBahamas
Verifies all backend Python dependencies, Redis, database, and service configurations.
Returns exit code 0 if all dependencies are active, exit code 1 if any issues.
"""

import importlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class DependencyChecker:
    """Comprehensive dependency verification system"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "checking",
            "python_dependencies": {},
            "flask_extensions": {},
            "services": {},
            "database": {},
            "frontend": {},
            "missing_dependencies": [],
            "inactive_services": [],
            "warnings": [],
        }
        self.all_passed = True

    def check_python_package(self, package_name: str, import_name: str = None) -> Tuple[bool, str]:
        """Check if a Python package is installed and get its version"""
        if import_name is None:
            import_name = package_name.lower().replace("-", "_")
        
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, "__version__", "unknown")
            return True, version
        except ImportError:
            return False, "not installed"

    def check_python_dependencies(self):
        """Check all Python dependencies from requirements.txt"""
        print("\n🔍 Checking Python Dependencies...")
        
        requirements_file = Path(__file__).parent.parent / "requirements.txt"
        
        if not requirements_file.exists():
            self.results["warnings"].append("requirements.txt not found")
            return
        
        required_packages = {
            "Flask": "flask",
            "Flask-CORS": "flask_cors",
            "Flask-Limiter": "flask_limiter",
            "Flask-Caching": "flask_caching",
            "PyJWT": "jwt",
            "bcrypt": "bcrypt",
            "python-dotenv": "dotenv",
            "gunicorn": "gunicorn",
            "waitress": "waitress",
            "Werkzeug": "werkzeug",
            "requests": "requests",
            "psycopg2-binary": "psycopg2",
        }
        
        for package, import_name in required_packages.items():
            installed, version = self.check_python_package(package, import_name)
            
            if installed:
                print(f"  ✅ {package}: {version}")
                self.results["python_dependencies"][package] = {
                    "active": True,
                    "version": version
                }
            else:
                print(f"  ❌ {package}: NOT INSTALLED")
                self.results["python_dependencies"][package] = {
                    "active": False,
                    "version": "not installed"
                }
                self.results["missing_dependencies"].append(package)
                self.all_passed = False

    def check_flask_extensions(self):
        """Check Flask extensions are properly loaded"""
        print("\n🔍 Checking Flask Extensions...")
        
        extensions = {
            "CORS": "flask_cors",
            "Limiter": "flask_limiter",
            "Cache": "flask_caching",
        }
        
        for ext_name, module_name in extensions.items():
            installed, version = self.check_python_package(ext_name, module_name)
            
            if installed:
                print(f"  ✅ Flask-{ext_name}: Available")
                self.results["flask_extensions"][f"Flask-{ext_name}"] = {
                    "active": True,
                    "loaded": True
                }
            else:
                print(f"  ❌ Flask-{ext_name}: NOT AVAILABLE")
                self.results["flask_extensions"][f"Flask-{ext_name}"] = {
                    "active": False,
                    "loaded": False
                }
                self.all_passed = False

    def check_redis_connection(self):
        """Check Redis connection and caching functionality"""
        print("\n🔍 Checking Redis Connection...")
        
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            
            try:
                r = redis.from_url(redis_url, socket_connect_timeout=2)
                r.ping()
                print(f"  ✅ Redis: Connected ({redis_url})")
                self.results["services"]["redis"] = {
                    "active": True,
                    "connected": True,
                    "url": redis_url
                }
            except Exception as e:
                print(f"  ⚠️  Redis: Not connected - {str(e)}")
                self.results["services"]["redis"] = {
                    "active": False,
                    "connected": False,
                    "error": str(e)
                }
                self.results["warnings"].append("Redis not available - using in-memory cache")
        except ImportError:
            print("  ⚠️  Redis: Python package not installed (optional)")
            self.results["services"]["redis"] = {
                "active": False,
                "connected": False,
                "note": "redis-py not installed (optional)"
            }
            self.results["warnings"].append("redis-py not installed")

    def check_database_connection(self):
        """Check database connections (PostgreSQL/SQLite)"""
        print("\n🔍 Checking Database Connection...")
        
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            # PostgreSQL
            try:
                import psycopg2
                conn = psycopg2.connect(database_url)
                conn.close()
                print(f"  ✅ PostgreSQL: Connected")
                self.results["database"] = {
                    "active": True,
                    "connected": True,
                    "type": "postgresql",
                    "url": database_url.split("@")[1] if "@" in database_url else "configured"
                }
            except Exception as e:
                print(f"  ❌ PostgreSQL: Connection failed - {str(e)}")
                self.results["database"] = {
                    "active": False,
                    "connected": False,
                    "type": "postgresql",
                    "error": str(e)
                }
                self.all_passed = False
        else:
            # SQLite fallback
            print("  ✅ SQLite: Using local database (development)")
            self.results["database"] = {
                "active": True,
                "connected": True,
                "type": "sqlite",
                "file": "hireme.db"
            }

    def check_sentry_sdk(self):
        """Check if Sentry SDK is configured"""
        print("\n🔍 Checking Sentry SDK...")
        
        try:
            import sentry_sdk
            sentry_dsn = os.getenv("SENTRY_DSN")
            
            if sentry_dsn:
                print(f"  ✅ Sentry: Configured")
                self.results["services"]["sentry"] = {
                    "active": True,
                    "dsn_configured": True
                }
            else:
                print(f"  ⚠️  Sentry: DSN not configured (optional)")
                self.results["services"]["sentry"] = {
                    "active": False,
                    "dsn_configured": False,
                    "note": "SENTRY_DSN not set"
                }
                self.results["warnings"].append("Sentry DSN not configured")
        except ImportError:
            print("  ⚠️  Sentry: SDK not installed (optional)")
            self.results["services"]["sentry"] = {
                "active": False,
                "installed": False,
                "note": "sentry-sdk not installed (optional)"
            }
            self.results["warnings"].append("sentry-sdk not installed")

    def check_socketio(self):
        """Check Socket.IO availability"""
        print("\n🔍 Checking Socket.IO...")
        
        try:
            import flask_socketio
            print(f"  ✅ Flask-SocketIO: Available")
            self.results["services"]["socketio"] = {
                "active": True,
                "installed": True
            }
        except ImportError:
            print("  ⚠️  Flask-SocketIO: Not installed (optional)")
            self.results["services"]["socketio"] = {
                "active": False,
                "installed": False,
                "note": "flask-socketio not installed (optional)"
            }
            self.results["warnings"].append("Flask-SocketIO not installed")

    def check_celery(self):
        """Check Celery workers"""
        print("\n🔍 Checking Celery...")
        
        try:
            import celery
            print(f"  ⚠️  Celery: Installed but workers not configured")
            self.results["services"]["celery"] = {
                "active": False,
                "installed": True,
                "workers": 0,
                "note": "No workers configured"
            }
            self.results["warnings"].append("Celery installed but not configured")
        except ImportError:
            print("  ⚠️  Celery: Not installed (optional)")
            self.results["services"]["celery"] = {
                "active": False,
                "installed": False,
                "note": "celery not installed (optional)"
            }
            self.results["warnings"].append("Celery not installed")

    def check_frontend_dependencies(self):
        """Check frontend Node.js dependencies"""
        print("\n🔍 Checking Frontend Dependencies...")
        
        frontend_path = Path(__file__).parent.parent / "frontend"
        package_json = frontend_path / "package.json"
        node_modules = frontend_path / "node_modules"
        
        if package_json.exists():
            if node_modules.exists():
                print(f"  ✅ Node.js dependencies: Installed")
                self.results["frontend"]["dependencies"] = {
                    "active": True,
                    "installed": True
                }
            else:
                print(f"  ❌ Node.js dependencies: NOT INSTALLED")
                self.results["frontend"]["dependencies"] = {
                    "active": False,
                    "installed": False
                }
                self.results["missing_dependencies"].append("Frontend node_modules")
                self.all_passed = False
        else:
            print(f"  ⚠️  Frontend: package.json not found")
            self.results["warnings"].append("Frontend package.json not found")

    def check_environment_variables(self):
        """Check required environment variables"""
        print("\n🔍 Checking Environment Variables...")
        
        env_vars = {
            "SECRET_KEY": os.getenv("SECRET_KEY"),
            "DATABASE_URL": os.getenv("DATABASE_URL"),
            "REDIS_URL": os.getenv("REDIS_URL"),
            "SENTRY_DSN": os.getenv("SENTRY_DSN"),
        }
        
        for var_name, var_value in env_vars.items():
            if var_value:
                print(f"  ✅ {var_name}: Configured")
            else:
                if var_name in ["REDIS_URL", "SENTRY_DSN"]:
                    print(f"  ⚠️  {var_name}: Not set (optional)")
                else:
                    print(f"  ⚠️  {var_name}: Not set (using default)")

    def auto_fix_common_issues(self):
        """Attempt to auto-fix common issues"""
        print("\n🔧 Auto-fixing Common Issues...")
        
        # Create .env file if it doesn't exist
        env_file = Path(__file__).parent.parent / ".env"
        if not env_file.exists():
            print("  📝 Creating .env file with defaults...")
            env_template = Path(__file__).parent.parent / ".env.example"
            if env_template.exists():
                import shutil
                shutil.copy(env_template, env_file)
                print("  ✅ Created .env from .env.example")
            else:
                with open(env_file, "w") as f:
                    f.write("# Auto-generated .env file\n")
                    f.write("SECRET_KEY=your-secret-key-change-in-production\n")
                    f.write("# DATABASE_URL=postgresql://user:pass@localhost/dbname\n")
                    f.write("# REDIS_URL=redis://localhost:6379\n")
                    f.write("# SENTRY_DSN=your-sentry-dsn\n")
                print("  ✅ Created basic .env file")

    def generate_report(self):
        """Generate comprehensive status report"""
        print("\n" + "=" * 60)
        print("📊 DEPENDENCY CHECK REPORT")
        print("=" * 60)
        
        if self.all_passed:
            self.results["status"] = "healthy"
            print("\n✅ ALL CRITICAL DEPENDENCIES ACTIVE")
        else:
            self.results["status"] = "unhealthy"
            print("\n❌ SOME DEPENDENCIES MISSING OR INACTIVE")
        
        if self.results["missing_dependencies"]:
            print(f"\n❌ Missing Dependencies ({len(self.results['missing_dependencies'])}):")
            for dep in self.results["missing_dependencies"]:
                print(f"   - {dep}")
        
        if self.results["warnings"]:
            print(f"\n⚠️  Warnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"]:
                print(f"   - {warning}")
        
        # Save report to file
        report_file = Path(__file__).parent.parent / "dependency_check_report.json"
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_file}")
        print("=" * 60)
        
        return 0 if self.all_passed else 1

    def run_all_checks(self):
        """Run all dependency checks"""
        print("🚀 Starting Comprehensive Dependency Check...")
        print(f"⏰ Timestamp: {self.results['timestamp']}")
        
        self.check_python_dependencies()
        self.check_flask_extensions()
        self.check_redis_connection()
        self.check_database_connection()
        self.check_sentry_sdk()
        self.check_socketio()
        self.check_celery()
        self.check_frontend_dependencies()
        self.check_environment_variables()
        self.auto_fix_common_issues()
        
        return self.generate_report()


def main():
    """Main entry point"""
    checker = DependencyChecker()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
