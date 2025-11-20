#!/usr/bin/env python3
"""
Environment Configuration Generator for HireMeBahamas
Auto-generates .env file with safe defaults and secure configurations.
"""

import secrets
from pathlib import Path


def generate_secret_key(length=50):
    """Generate a secure random secret key"""
    return secrets.token_urlsafe(length)


def setup_env_file():
    """Create or update .env file with configuration"""
    root_dir = Path(__file__).parent.parent
    env_file = root_dir / ".env"
    
    print("🔧 Setting up environment configuration...")
    print(f"📁 Root directory: {root_dir}")
    
    # Check if .env already exists
    if env_file.exists():
        print(f"⚠️  .env file already exists at {env_file}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("✅ Keeping existing .env file")
            return
    
    # Load existing values if .env exists
    existing_values = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_values[key.strip()] = value.strip()
    
    # Configuration template
    config = {
        "SECRET_KEY": existing_values.get("SECRET_KEY", generate_secret_key()),
        "FLASK_ENV": existing_values.get("FLASK_ENV", "development"),
        "DATABASE_URL": existing_values.get("DATABASE_URL", ""),
        "REDIS_URL": existing_values.get("REDIS_URL", "redis://localhost:6379"),
        "SENTRY_DSN": existing_values.get("SENTRY_DSN", ""),
        "FLASK_APP": "final_backend_postgresql.py",
        "PORT": existing_values.get("PORT", "5000"),
    }
    
    # Additional optional configurations
    optional_config = {
        "FRONTEND_URL": "http://localhost:3000",
        "BACKEND_URL": "http://localhost:5000",
        "MAX_CONTENT_LENGTH": "52428800",  # 50MB
        "UPLOAD_FOLDER": "uploads",
        "SESSION_COOKIE_SECURE": "False",  # Set to True in production
        "SESSION_COOKIE_HTTPONLY": "True",
        "SESSION_COOKIE_SAMESITE": "Lax",
    }
    
    # Merge optional with main config
    for key, value in optional_config.items():
        if key not in config:
            config[key] = existing_values.get(key, value)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write("# HireMeBahamas Environment Configuration\n")
        f.write(f"# Auto-generated: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write("# Edit these values according to your environment\n\n")
        
        f.write("# Flask Configuration\n")
        f.write(f"SECRET_KEY={config['SECRET_KEY']}\n")
        f.write(f"FLASK_ENV={config['FLASK_ENV']}\n")
        f.write(f"FLASK_APP={config['FLASK_APP']}\n")
        f.write(f"PORT={config['PORT']}\n\n")
        
        f.write("# Database Configuration\n")
        if config['DATABASE_URL']:
            f.write(f"DATABASE_URL={config['DATABASE_URL']}\n")
        else:
            f.write("# DATABASE_URL=postgresql://user:password@localhost:5432/hiremebahamas\n")
        f.write("# Leave empty to use SQLite (development mode)\n\n")
        
        f.write("# Redis Configuration (Optional)\n")
        f.write(f"REDIS_URL={config['REDIS_URL']}\n")
        f.write("# Leave empty to use in-memory caching\n\n")
        
        f.write("# Sentry Configuration (Optional)\n")
        if config['SENTRY_DSN']:
            f.write(f"SENTRY_DSN={config['SENTRY_DSN']}\n")
        else:
            f.write("# SENTRY_DSN=https://your-sentry-dsn@sentry.io/project\n")
        f.write("# Leave empty to disable error tracking\n\n")
        
        f.write("# URL Configuration\n")
        f.write(f"FRONTEND_URL={config.get('FRONTEND_URL', 'http://localhost:3000')}\n")
        f.write(f"BACKEND_URL={config.get('BACKEND_URL', 'http://localhost:5000')}\n\n")
        
        f.write("# Upload Configuration\n")
        f.write(f"MAX_CONTENT_LENGTH={config.get('MAX_CONTENT_LENGTH', '52428800')}\n")
        f.write(f"UPLOAD_FOLDER={config.get('UPLOAD_FOLDER', 'uploads')}\n\n")
        
        f.write("# Security Configuration\n")
        f.write(f"SESSION_COOKIE_SECURE={config.get('SESSION_COOKIE_SECURE', 'False')}\n")
        f.write(f"SESSION_COOKIE_HTTPONLY={config.get('SESSION_COOKIE_HTTPONLY', 'True')}\n")
        f.write(f"SESSION_COOKIE_SAMESITE={config.get('SESSION_COOKIE_SAMESITE', 'Lax')}\n\n")
        
        f.write("# Production Settings (uncomment for production)\n")
        f.write("# PRODUCTION=true\n")
        f.write("# SESSION_COOKIE_SECURE=True\n")
        f.write("# FLASK_ENV=production\n")
    
    print(f"✅ Environment file created: {env_file}")
    print("\n📋 Configuration Summary:")
    print(f"   - SECRET_KEY: {'[Generated]' if config['SECRET_KEY'] != existing_values.get('SECRET_KEY') else '[Existing]'}")
    print(f"   - FLASK_ENV: {config['FLASK_ENV']}")
    print(f"   - DATABASE: {'PostgreSQL' if config['DATABASE_URL'] else 'SQLite (default)'}")
    print(f"   - REDIS: {'Configured' if config['REDIS_URL'] else 'Disabled'}")
    print(f"   - SENTRY: {'Configured' if config['SENTRY_DSN'] else 'Disabled'}")
    
    print("\n💡 Tips:")
    print("   - Edit .env file to customize configuration")
    print("   - Never commit .env to version control")
    print("   - Use different .env for production")
    print("   - Set PRODUCTION=true for production deployments")
    
    # Ensure .env is in .gitignore
    gitignore = root_dir / ".gitignore"
    if gitignore.exists():
        with open(gitignore, 'r') as f:
            content = f.read()
        
        if '.env' not in content:
            with open(gitignore, 'a') as f:
                f.write("\n# Environment variables\n")
                f.write(".env\n")
                f.write(".env.local\n")
            print("✅ Added .env to .gitignore")
    
    print("\n✅ Environment setup complete!")


def main():
    """Main entry point"""
    print("=" * 60)
    print("🔧 HireMeBahamas Environment Setup")
    print("=" * 60)
    print()
    
    setup_env_file()
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
