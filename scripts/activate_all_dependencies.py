#!/usr/bin/env python3
"""
Automated Dependency Activation Script for HireMeBahamas
Auto-installs missing dependencies, configures services, and activates all features.
"""

import os
import subprocess
import sys
from pathlib import Path


class DependencyActivator:
    """Intelligent activation system for all dependencies"""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.issues = []
        self.successes = []

    def log_success(self, message):
        """Log a successful action"""
        print(f"✅ {message}")
        self.successes.append(message)

    def log_issue(self, message):
        """Log an issue"""
        print(f"❌ {message}")
        self.issues.append(message)

    def log_info(self, message):
        """Log informational message"""
        print(f"ℹ️  {message}")

    def install_python_dependencies(self):
        """Install Python dependencies from requirements.txt"""
        print("\n📦 Installing Python Dependencies...")
        
        requirements_file = self.root_dir / "requirements.txt"
        
        if not requirements_file.exists():
            self.log_issue("requirements.txt not found")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file), "--quiet"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.log_success("Python dependencies installed")
                return True
            else:
                self.log_issue(f"Failed to install Python dependencies: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.log_issue("Installation timeout - dependencies may be too large")
            return False
        except Exception as e:
            self.log_issue(f"Error installing dependencies: {str(e)}")
            return False

    def configure_environment_variables(self):
        """Configure environment variables with safe defaults"""
        print("\n⚙️  Configuring Environment Variables...")
        
        env_file = self.root_dir / ".env"
        
        # Default configuration
        default_env = {
            "SECRET_KEY": "dev-secret-key-change-in-production",
            "FLASK_ENV": "development",
            "DATABASE_URL": "",  # Will use SQLite by default
            "REDIS_URL": "redis://localhost:6379",
            "SENTRY_DSN": "",  # Optional
        }
        
        if env_file.exists():
            self.log_info("Environment file already exists")
            return True
        
        # Create .env from template or defaults
        env_template = self.root_dir / ".env.example"
        
        if env_template.exists():
            import shutil
            shutil.copy(env_template, env_file)
            self.log_success("Created .env from .env.example")
        else:
            with open(env_file, "w") as f:
                f.write("# Auto-generated environment configuration\n")
                f.write(f"# Generated: {__import__('datetime').datetime.now().isoformat()}\n\n")
                
                for key, value in default_env.items():
                    if value:
                        f.write(f"{key}={value}\n")
                    else:
                        f.write(f"# {key}=\n")
            
            self.log_success("Created .env with default configuration")
        
        return True

    def initialize_redis(self):
        """Initialize Redis if available"""
        print("\n🔴 Checking Redis...")
        
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            
            try:
                r = redis.from_url(redis_url, socket_connect_timeout=2)
                r.ping()
                self.log_success("Redis is running and accessible")
                return True
            except Exception:
                self.log_info("Redis not available - will use in-memory caching")
                return True  # Not critical
        except ImportError:
            self.log_info("redis-py not installed - will use in-memory caching")
            return True  # Not critical

    def setup_database(self):
        """Set up database connections and migrations"""
        print("\n🗄️  Setting Up Database...")
        
        database_url = os.getenv("DATABASE_URL")
        
        if database_url:
            # PostgreSQL
            try:
                import psycopg2
                conn = psycopg2.connect(database_url, connect_timeout=5)
                conn.close()
                self.log_success("PostgreSQL database accessible")
                return True
            except ImportError:
                self.log_issue("psycopg2-binary not installed for PostgreSQL")
                return False
            except Exception as e:
                self.log_issue(f"PostgreSQL connection failed: {str(e)}")
                return False
        else:
            # SQLite fallback
            self.log_success("Using SQLite database (development mode)")
            return True

    def configure_flask_extensions(self):
        """Configure Flask extensions"""
        print("\n🔧 Configuring Flask Extensions...")
        
        extensions = ["flask_cors", "flask_limiter", "flask_caching"]
        
        for ext in extensions:
            try:
                __import__(ext)
                self.log_success(f"{ext} available")
            except ImportError:
                self.log_issue(f"{ext} not installed")
        
        return True

    def test_sentry_integration(self):
        """Test Sentry integration"""
        print("\n🔔 Checking Sentry Integration...")
        
        try:
            import sentry_sdk
            sentry_dsn = os.getenv("SENTRY_DSN")
            
            if sentry_dsn:
                self.log_success("Sentry SDK configured")
            else:
                self.log_info("Sentry DSN not configured (optional)")
        except ImportError:
            self.log_info("Sentry SDK not installed (optional)")
        
        return True

    def activate_socketio(self):
        """Activate Socket.IO for real-time features"""
        print("\n🔌 Checking Socket.IO...")
        
        try:
            import flask_socketio
            self.log_success("Flask-SocketIO available")
            return True
        except ImportError:
            self.log_info("Flask-SocketIO not installed (optional)")
            return True

    def check_celery_workers(self):
        """Check Celery workers"""
        print("\n⚙️  Checking Celery Workers...")
        
        try:
            import celery
            self.log_info("Celery installed but workers not configured (optional)")
        except ImportError:
            self.log_info("Celery not installed (optional)")
        
        return True

    def install_frontend_dependencies(self):
        """Install frontend Node.js dependencies"""
        print("\n🎨 Checking Frontend Dependencies...")
        
        frontend_path = self.root_dir / "frontend"
        package_json = frontend_path / "package.json"
        node_modules = frontend_path / "node_modules"
        
        if not package_json.exists():
            self.log_info("Frontend package.json not found - skipping")
            return True
        
        if node_modules.exists():
            self.log_success("Frontend dependencies already installed")
            return True
        
        # Try to install
        try:
            self.log_info("Installing frontend dependencies (this may take a while)...")
            result = subprocess.run(
                ["npm", "install"],
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                self.log_success("Frontend dependencies installed")
                return True
            else:
                self.log_issue(f"Failed to install frontend dependencies: {result.stderr[:200]}")
                return False
        except FileNotFoundError:
            self.log_info("npm not found - please install Node.js manually")
            return True  # Not critical for backend testing
        except subprocess.TimeoutExpired:
            self.log_issue("Frontend installation timeout")
            return False
        except Exception as e:
            self.log_issue(f"Error installing frontend dependencies: {str(e)}")
            return False

    def generate_report(self):
        """Generate activation report"""
        print("\n" + "=" * 60)
        print("📊 ACTIVATION REPORT")
        print("=" * 60)
        
        print(f"\n✅ Successes: {len(self.successes)}")
        for success in self.successes:
            print(f"   - {success}")
        
        if self.issues:
            print(f"\n❌ Issues: {len(self.issues)}")
            for issue in self.issues:
                print(f"   - {issue}")
        
        print("\n" + "=" * 60)
        
        if not self.issues:
            print("\n✅ All dependencies activated successfully!")
            return 0
        else:
            print("\n⚠️  Some dependencies could not be activated")
            print("   The application may still work with degraded functionality")
            return 1

    def activate_all(self):
        """Run all activation steps"""
        print("🚀 Starting Automated Dependency Activation...")
        print(f"📁 Working directory: {self.root_dir}")
        
        # Run activation steps
        self.install_python_dependencies()
        self.configure_environment_variables()
        self.initialize_redis()
        self.setup_database()
        self.configure_flask_extensions()
        self.test_sentry_integration()
        self.activate_socketio()
        self.check_celery_workers()
        self.install_frontend_dependencies()
        
        return self.generate_report()


def main():
    """Main entry point"""
    activator = DependencyActivator()
    exit_code = activator.activate_all()
    
    print("\n💡 Next steps:")
    print("   1. Run: python scripts/check_dependencies.py")
    print("   2. Start the application")
    print("   3. Check /api/health/dependencies endpoint")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
