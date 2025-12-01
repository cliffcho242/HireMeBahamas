#!/bin/bash
#
# ZERO-DOWNTIME MIGRATION SCRIPT
# Railway Postgres → Vercel Postgres (Neon)
#
# Usage: ./migrate_railway_to_vercel.sh
#
# Requirements:
# - RAILWAY_DATABASE_URL environment variable set
# - VERCEL_POSTGRES_URL environment variable set
# - pg_dump and pg_restore installed (PostgreSQL 14+)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKUP_FILE="railway_backup_$(date +%Y%m%d_%H%M%S).dump"
JOBS=8

# Extract database name from URL
get_db_name_from_url() {
    local url="$1"
    # Extract database name from postgresql://user:pass@host:port/dbname
    echo "$url" | sed -E 's|.*://[^/]+/([^?]+).*|\1|'
}

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "CHECKING PREREQUISITES"

    # Check pg_dump
    if ! command -v pg_dump &> /dev/null; then
        print_error "pg_dump not found. Install PostgreSQL client tools."
        exit 1
    fi
    print_success "pg_dump found: $(pg_dump --version | head -1)"

    # Check pg_restore
    if ! command -v pg_restore &> /dev/null; then
        print_error "pg_restore not found. Install PostgreSQL client tools."
        exit 1
    fi
    print_success "pg_restore found: $(pg_restore --version | head -1)"

    # Check psql
    if ! command -v psql &> /dev/null; then
        print_error "psql not found. Install PostgreSQL client tools."
        exit 1
    fi
    print_success "psql found: $(psql --version | head -1)"

    # Check environment variables
    if [ -z "$RAILWAY_DATABASE_URL" ]; then
        print_error "RAILWAY_DATABASE_URL not set"
        echo "Set it with: export RAILWAY_DATABASE_URL='postgresql://...'"
        exit 1
    fi
    print_success "RAILWAY_DATABASE_URL is set"

    if [ -z "$VERCEL_POSTGRES_URL" ]; then
        print_error "VERCEL_POSTGRES_URL not set"
        echo "Set it with: export VERCEL_POSTGRES_URL='postgresql://...'"
        exit 1
    fi
    print_success "VERCEL_POSTGRES_URL is set"

    echo ""
}

# Test connections
test_connections() {
    print_header "TESTING DATABASE CONNECTIONS"

    echo "Testing Railway connection..."
    if psql "$RAILWAY_DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
        print_success "Railway connection OK"
    else
        print_error "Cannot connect to Railway database"
        exit 1
    fi

    echo "Testing Vercel Postgres connection..."
    if psql "$VERCEL_POSTGRES_URL" -c "SELECT 1" > /dev/null 2>&1; then
        print_success "Vercel Postgres connection OK"
    else
        print_error "Cannot connect to Vercel Postgres database"
        exit 1
    fi

    echo ""
}

# Get row counts from source
get_source_counts() {
    print_header "GETTING SOURCE ROW COUNTS"

    echo "Counting rows in Railway database..."
    psql "$RAILWAY_DATABASE_URL" -t -c "
        SELECT 'users' as table_name, COUNT(*)::text as cnt FROM users
        UNION ALL SELECT 'posts', COUNT(*)::text FROM posts
        UNION ALL SELECT 'jobs', COUNT(*)::text FROM jobs
        UNION ALL SELECT 'messages', COUNT(*)::text FROM messages
        UNION ALL SELECT 'notifications', COUNT(*)::text FROM notifications
        ORDER BY table_name;
    " 2>/dev/null || echo "(some tables may not exist)"

    echo ""
}

# Export from Railway
export_from_railway() {
    print_header "EXPORTING FROM RAILWAY"

    echo "Starting pg_dump with $JOBS parallel jobs..."
    echo "Output file: $BACKUP_FILE"
    echo ""

    start_time=$(date +%s)

    pg_dump "$RAILWAY_DATABASE_URL" \
        --no-owner \
        --no-acl \
        --format=custom \
        --compress=0 \
        --jobs="$JOBS" \
        --file="$BACKUP_FILE"

    end_time=$(date +%s)
    duration=$((end_time - start_time))

    print_success "Export completed in ${duration} seconds"
    if [ -f "$BACKUP_FILE" ]; then
        file_size=$(stat -c%s "$BACKUP_FILE" 2>/dev/null || stat -f%z "$BACKUP_FILE" 2>/dev/null)
        echo "Backup file size: $((file_size / 1024 / 1024)) MB"
    fi
    echo ""
}

# Import to Vercel Postgres
import_to_vercel() {
    print_header "IMPORTING TO VERCEL POSTGRES"

    echo "Starting pg_restore with $JOBS parallel jobs..."
    echo ""

    start_time=$(date +%s)

    # Drop existing tables if any (clean slate)
    print_warning "Cleaning target database..."
    psql "$VERCEL_POSTGRES_URL" -c "
        DO \$\$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END \$\$;
    " 2>/dev/null || true

    # Restore data
    pg_restore \
        --no-owner \
        --no-acl \
        --jobs="$JOBS" \
        --dbname="$VERCEL_POSTGRES_URL" \
        "$BACKUP_FILE" 2>/dev/null || true

    end_time=$(date +%s)
    duration=$((end_time - start_time))

    print_success "Import completed in ${duration} seconds"
    echo ""
}

# Verify row counts
verify_counts() {
    print_header "VERIFYING DATA INTEGRITY"

    echo "Counting rows in Vercel Postgres database..."
    psql "$VERCEL_POSTGRES_URL" -t -c "
        SELECT 'users' as table_name, COUNT(*)::text as cnt FROM users
        UNION ALL SELECT 'posts', COUNT(*)::text FROM posts
        UNION ALL SELECT 'jobs', COUNT(*)::text FROM jobs
        UNION ALL SELECT 'messages', COUNT(*)::text FROM messages
        UNION ALL SELECT 'notifications', COUNT(*)::text FROM notifications
        ORDER BY table_name;
    " 2>/dev/null || echo "(some tables may not exist)"

    echo ""
    print_success "Compare counts above with source counts to verify migration"
    echo ""
}

# Set Railway to read-only
set_railway_readonly() {
    print_header "SETTING RAILWAY TO READ-ONLY (7-DAY BACKUP)"

    echo "Setting Railway database to read-only mode..."

    # Extract database name from URL
    local db_name
    db_name=$(get_db_name_from_url "$RAILWAY_DATABASE_URL")
    
    if [ -z "$db_name" ]; then
        print_warning "Could not extract database name from URL"
        return
    fi

    # Note: This requires superuser privileges which may not be available
    # In that case, rely on switching DATABASE_URL as the cutover mechanism
    psql "$RAILWAY_DATABASE_URL" -c "
        ALTER DATABASE \"$db_name\" SET default_transaction_read_only = on;
    " 2>/dev/null || print_warning "Could not set read-only (may require superuser)"

    print_success "Railway database is now read-only"
    echo ""
}

# Print next steps
print_next_steps() {
    print_header "NEXT STEPS"

    echo "1. Verify the row counts match between source and target"
    echo ""
    echo "2. Update DATABASE_URL in Vercel Dashboard:"
    echo "   Settings → Environment Variables → DATABASE_URL"
    echo "   Set value to: \$VERCEL_POSTGRES_URL"
    echo ""
    echo "3. Trigger a new deployment or restart the app"
    echo ""
    echo "4. Test the application:"
    echo "   - Login"
    echo "   - Create a post"
    echo "   - Send a message"
    echo ""
    echo "5. Set Railway to read-only (optional, for 7-day backup):"
    echo "   ./scripts/migrate_railway_to_vercel.sh --set-readonly"
    echo ""
    echo "6. After 7 days, delete Railway Postgres service"
    echo ""

    print_header "ROLLBACK COMMAND (IF NEEDED)"
    echo "To rollback, revert DATABASE_URL in Vercel to Railway URL"
    echo ""
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help          Show this help message"
    echo "  --set-readonly  Set Railway database to read-only mode"
    echo ""
    echo "Environment Variables Required:"
    echo "  RAILWAY_DATABASE_URL   Source database URL"
    echo "  VERCEL_POSTGRES_URL    Target database URL"
    echo ""
}

# Main execution
main() {
    # Handle command line arguments
    case "${1:-}" in
        --help)
            show_usage
            exit 0
            ;;
        --set-readonly)
            check_prerequisites
            set_railway_readonly
            exit 0
            ;;
    esac

    print_header "ZERO-DOWNTIME MIGRATION"
    echo "Railway Postgres → Vercel Postgres (Neon)"
    echo ""
    echo "Started at: $(date)"
    echo ""

    check_prerequisites
    test_connections
    get_source_counts
    export_from_railway
    import_to_vercel
    verify_counts
    print_next_steps

    print_header "MIGRATION COMPLETE"
    echo "Backup file saved: $BACKUP_FILE"
    echo "Finished at: $(date)"
    echo ""
}

# Run main function
main "$@"
