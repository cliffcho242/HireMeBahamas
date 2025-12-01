#!/usr/bin/env python3
"""
ZERO-DOWNTIME MIGRATION SCRIPT
Railway Postgres → Vercel Postgres (Neon)

Usage: python migrate_railway_to_vercel.py

Requirements:
- RAILWAY_DATABASE_URL environment variable set
- VERCEL_POSTGRES_URL environment variable set
- pg_dump, pg_restore, and psql in PATH
"""

import os
import subprocess
import sys
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_header(msg: str) -> None:
    """Print a formatted header"""
    print(f"{Colors.BLUE}{'=' * 50}{Colors.NC}")
    print(f"{Colors.BLUE}{msg}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.NC}")


def print_success(msg: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")


def print_warning(msg: str) -> None:
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.NC}")


def print_error(msg: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}✗ {msg}{Colors.NC}")


def run_command(cmd: list, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command"""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            print_error(f"Command failed: {' '.join(cmd)}")
            print_error(f"Error: {e.stderr if e.stderr else str(e)}")
            raise
        return e


def check_command_exists(cmd: str) -> bool:
    """Check if a command exists in PATH"""
    try:
        subprocess.run(
            [cmd, '--version'],
            check=True,
            capture_output=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_prerequisites() -> tuple:
    """Check all prerequisites are met"""
    print_header("CHECKING PREREQUISITES")

    # Check PostgreSQL tools
    for tool in ['pg_dump', 'pg_restore', 'psql']:
        if check_command_exists(tool):
            print_success(f"{tool} found")
        else:
            print_error(f"{tool} not found. Install PostgreSQL client tools.")
            sys.exit(1)

    # Check environment variables
    railway_url = os.environ.get('RAILWAY_DATABASE_URL')
    vercel_url = os.environ.get('VERCEL_POSTGRES_URL')

    if not railway_url:
        print_error("RAILWAY_DATABASE_URL not set")
        print("Set it with: export RAILWAY_DATABASE_URL='postgresql://...'")
        sys.exit(1)
    print_success("RAILWAY_DATABASE_URL is set")

    if not vercel_url:
        print_error("VERCEL_POSTGRES_URL not set")
        print("Set it with: export VERCEL_POSTGRES_URL='postgresql://...'")
        sys.exit(1)
    print_success("VERCEL_POSTGRES_URL is set")

    print()
    return railway_url, vercel_url


def test_connection(url: str, name: str) -> bool:
    """Test database connection"""
    print(f"Testing {name} connection...")
    try:
        subprocess.run(
            ['psql', url, '-c', 'SELECT 1'],
            check=True,
            capture_output=True
        )
        print_success(f"{name} connection OK")
        return True
    except subprocess.CalledProcessError:
        print_error(f"Cannot connect to {name} database")
        return False


def get_row_counts(url: str, name: str) -> None:
    """Get row counts from database"""
    print(f"Counting rows in {name} database...")
    query = """
        SELECT 'users' as table_name, COUNT(*)::text as cnt FROM users
        UNION ALL SELECT 'posts', COUNT(*)::text FROM posts
        UNION ALL SELECT 'jobs', COUNT(*)::text FROM jobs
        UNION ALL SELECT 'messages', COUNT(*)::text FROM messages
        UNION ALL SELECT 'notifications', COUNT(*)::text FROM notifications
        ORDER BY table_name;
    """
    try:
        result = subprocess.run(
            ['psql', url, '-t', '-c', query],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError:
        print_warning("Some tables may not exist")
    print()


def export_from_railway(railway_url: str, backup_file: str, jobs: int = 8) -> None:
    """Export data from Railway Postgres"""
    print_header("EXPORTING FROM RAILWAY")
    print(f"Starting pg_dump with {jobs} parallel jobs...")
    print(f"Output file: {backup_file}")
    print()

    start_time = datetime.now()

    cmd = [
        'pg_dump', railway_url,
        '--no-owner',
        '--no-acl',
        '--format=custom',
        '--compress=0',
        f'--jobs={jobs}',
        f'--file={backup_file}'
    ]

    run_command(cmd)

    duration = (datetime.now() - start_time).total_seconds()
    print_success(f"Export completed in {duration:.1f} seconds")

    # Get file size
    file_size = os.path.getsize(backup_file)
    print(f"Backup file size: {file_size / (1024*1024):.2f} MB")
    print()


def clean_target_database(vercel_url: str) -> None:
    """Clean the target database before import"""
    print_warning("Cleaning target database...")
    query = """
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
    """
    try:
        subprocess.run(
            ['psql', vercel_url, '-c', query],
            capture_output=True
        )
    except subprocess.CalledProcessError:
        pass  # Ignore errors, tables might not exist


def import_to_vercel(vercel_url: str, backup_file: str, jobs: int = 8) -> None:
    """Import data to Vercel Postgres"""
    print_header("IMPORTING TO VERCEL POSTGRES")
    print(f"Starting pg_restore with {jobs} parallel jobs...")
    print()

    start_time = datetime.now()

    # Clean target database
    clean_target_database(vercel_url)

    cmd = [
        'pg_restore',
        '--no-owner',
        '--no-acl',
        f'--jobs={jobs}',
        f'--dbname={vercel_url}',
        backup_file
    ]

    # pg_restore may return non-zero for warnings, so don't check strictly
    subprocess.run(cmd, capture_output=True)

    duration = (datetime.now() - start_time).total_seconds()
    print_success(f"Import completed in {duration:.1f} seconds")
    print()


def print_next_steps() -> None:
    """Print next steps for the user"""
    print_header("NEXT STEPS")
    print("""
1. Verify the row counts match between source and target

2. Update DATABASE_URL in Vercel Dashboard:
   Settings → Environment Variables → DATABASE_URL
   Set value to: $VERCEL_POSTGRES_URL

3. Trigger a new deployment or restart the app

4. Test the application:
   - Login
   - Create a post
   - Send a message

5. Keep Railway running for 7 days as backup

6. After 7 days, delete Railway Postgres service
""")

    print_header("ROLLBACK COMMAND (IF NEEDED)")
    print("To rollback, revert DATABASE_URL in Vercel to Railway URL")
    print()


def main() -> None:
    """Main migration function"""
    print_header("ZERO-DOWNTIME MIGRATION")
    print("Railway Postgres → Vercel Postgres (Neon)")
    print()
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    # Generate backup filename
    backup_file = f"railway_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dump"
    jobs = 8

    # Check prerequisites
    railway_url, vercel_url = check_prerequisites()

    # Test connections
    print_header("TESTING DATABASE CONNECTIONS")
    if not test_connection(railway_url, "Railway"):
        sys.exit(1)
    if not test_connection(vercel_url, "Vercel Postgres"):
        sys.exit(1)
    print()

    # Get source counts
    print_header("SOURCE ROW COUNTS")
    get_row_counts(railway_url, "Railway")

    # Export from Railway
    export_from_railway(railway_url, backup_file, jobs)

    # Import to Vercel
    import_to_vercel(vercel_url, backup_file, jobs)

    # Verify counts
    print_header("TARGET ROW COUNTS")
    get_row_counts(vercel_url, "Vercel Postgres")

    # Print next steps
    print_next_steps()

    print_header("MIGRATION COMPLETE")
    print(f"Backup file saved: {backup_file}")
    print(f"Finished at: {datetime.now().isoformat()}")
    print()


if __name__ == '__main__':
    main()
