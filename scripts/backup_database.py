#!/usr/bin/env python3
"""
Database Backup Script for HireMeBahamas
Backs up database from Render, Railway, Vercel, or any PostgreSQL database
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
import getpass


# Constants
# Environment variable names for different platforms
ENV_VAR_MAPPING = {
    "render": "RENDER_DATABASE_URL",
    "railway": "RAILWAY_DATABASE_URL",
    "vercel": "VERCEL_DATABASE_URL",
    "custom": "DATABASE_URL"
}

# Database query timeout in seconds
DB_QUERY_TIMEOUT = 10


def get_database_url(source: str) -> str:
    """
    Get database URL from user or environment.
    
    Args:
        source: Platform name (render, railway, vercel, custom)
    
    Returns:
        Database connection URL
    """
    env_var_name = ENV_VAR_MAPPING.get(source, "DATABASE_URL")
    
    # Check environment variable first
    db_url = os.environ.get(env_var_name) or os.environ.get("DATABASE_URL")
    
    if db_url:
        print(f"✅ Using database URL from ${env_var_name or 'DATABASE_URL'}")
        # Mask password in output
        masked_url = mask_password(db_url)
        print(f"   Connection: {masked_url}")
        return db_url
    
    # Prompt user for database URL
    print(f"\n📋 Enter your {source.title()} database URL")
    print("   Format: postgresql://user:password@host:port/database")
    print(f"   Or set environment variable: export {env_var_name}=<url>")
    
    if source == "render":
        print("\n   Get it from: https://dashboard.render.com → Your PostgreSQL → Connections → External Database URL")
    elif source == "railway":
        print("\n   Get it from: https://railway.app → Your PostgreSQL Service → Connect")
    elif source == "vercel":
        print("\n   Get it from: https://vercel.com → Your Project → Storage → Your Database → .env.local")
    
    db_url = getpass.getpass("\n🔑 Database URL: ")
    
    if not db_url or not db_url.startswith("postgresql://"):
        print("❌ Error: Invalid database URL format")
        sys.exit(1)
    
    return db_url


def mask_password(db_url: str) -> str:
    """Mask password in database URL for safe logging."""
    if ":" not in db_url or "@" not in db_url:
        return db_url
    
    try:
        parts = db_url.split("://")
        protocol = parts[0]
        rest = parts[1]
        
        user_pass, host_db = rest.split("@")
        user = user_pass.split(":")[0]
        
        return f"{protocol}://{user}:****@{host_db}"
    except Exception:
        return db_url


def create_backup_dir(output_dir: str) -> Path:
    """Create backup directory if it doesn't exist."""
    backup_path = Path(output_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    return backup_path


def run_pg_dump(db_url: str, output_file: Path) -> bool:
    """
    Run pg_dump to backup database.
    
    Args:
        db_url: PostgreSQL connection URL
        output_file: Path to output SQL file
    
    Returns:
        True if successful, False otherwise
    """
    print(f"\n🔄 Creating database backup...")
    print(f"   Output: {output_file}")
    
    try:
        # Check if pg_dump is installed
        result = subprocess.run(
            ["pg_dump", "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print("❌ Error: pg_dump not found")
            print("\n📦 Install PostgreSQL client:")
            print("   Ubuntu/Debian: sudo apt-get install postgresql-client")
            print("   macOS: brew install postgresql")
            print("   Windows: https://www.postgresql.org/download/windows/")
            return False
        
        # Run pg_dump
        with open(output_file, "w") as f:
            result = subprocess.run(
                ["pg_dump", db_url],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
        
        if result.returncode != 0:
            print(f"❌ Error: pg_dump failed")
            print(f"   {result.stderr}")
            return False
        
        # Check file size
        file_size = output_file.stat().st_size
        if file_size == 0:
            print("❌ Error: Backup file is empty")
            return False
        
        print(f"✅ Backup created successfully!")
        print(f"   Size: {file_size / 1024:.2f} KB")
        
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def verify_backup(db_url: str, output_file: Path) -> bool:
    """
    Verify backup integrity by checking for key tables.
    
    Args:
        db_url: PostgreSQL connection URL
        output_file: Path to backup SQL file
    
    Returns:
        True if backup appears valid, False otherwise
    """
    print("\n🔍 Verifying backup integrity...")
    
    # Check if backup contains SQL commands
    with open(output_file, "r") as f:
        content = f.read(10000)  # Read first 10KB
        
        if "CREATE TABLE" not in content and "INSERT INTO" not in content:
            print("⚠️  Warning: Backup may be incomplete (no CREATE TABLE or INSERT statements found)")
            return False
    
    # Count tables in backup
    table_count = 0
    with open(output_file, "r") as f:
        for line in f:
            if "CREATE TABLE" in line:
                table_count += 1
    
    print(f"✅ Found {table_count} tables in backup")
    
    # Get statistics from source database
    try:
        result = subprocess.run(
            ["psql", db_url, "-t", "-c", "SELECT COUNT(*) FROM users;"],
            capture_output=True,
            text=True,
            check=False,
            timeout=DB_QUERY_TIMEOUT
        )
        
        if result.returncode == 0:
            user_count = result.stdout.strip()
            print(f"   Users in source database: {user_count}")
    except Exception:
        pass
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Backup HireMeBahamas database from any platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Backup from Render
  python backup_database.py --source render --output ./backups/
  
  # Backup from Railway
  python backup_database.py --source railway --output ./backups/
  
  # Backup from custom database
  python backup_database.py --source custom --output ./backups/
  
  # Using environment variable
  export DATABASE_URL="postgresql://user:pass@host:5432/db"
  python backup_database.py --output ./backups/
        """
    )
    
    parser.add_argument(
        "--source",
        choices=["render", "railway", "vercel", "custom"],
        default="custom",
        help="Database platform (default: custom)"
    )
    
    parser.add_argument(
        "--output",
        default="./backups",
        help="Output directory for backup file (default: ./backups)"
    )
    
    parser.add_argument(
        "--name",
        help="Custom backup filename (default: auto-generated with timestamp)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🗄️  HireMeBahamas Database Backup Tool")
    print("=" * 60)
    
    # Get database URL
    db_url = get_database_url(args.source)
    
    # Create backup directory
    backup_dir = create_backup_dir(args.output)
    
    # Generate backup filename
    if args.name:
        backup_filename = args.name
        if not backup_filename.endswith(".sql"):
            backup_filename += ".sql"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"hiremebahamas_{args.source}_backup_{timestamp}.sql"
    
    backup_file = backup_dir / backup_filename
    
    # Create backup
    success = run_pg_dump(db_url, backup_file)
    
    if not success:
        print("\n❌ Backup failed!")
        sys.exit(1)
    
    # Verify backup
    verify_backup(db_url, backup_file)
    
    print("\n" + "=" * 60)
    print("✅ BACKUP COMPLETE!")
    print("=" * 60)
    print(f"\n📁 Backup saved to: {backup_file.absolute()}")
    print(f"📦 Size: {backup_file.stat().st_size / 1024:.2f} KB")
    
    print("\n📋 Next Steps:")
    print("   1. Keep this backup file safe (it contains sensitive data)")
    print("   2. Restore on new platform:")
    print(f"      psql \"$NEW_DATABASE_URL\" < {backup_file}")
    print("   3. Verify restoration:")
    print("      psql \"$NEW_DATABASE_URL\" -c \"SELECT COUNT(*) FROM users;\"")
    
    print("\n⚠️  Security Note:")
    print("   This backup contains user data including hashed passwords.")
    print("   Store securely and delete after successful migration.")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
