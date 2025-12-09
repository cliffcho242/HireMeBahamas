#!/bin/bash
# =============================================================================
# Railway PostgreSQL Quick Check Script
# =============================================================================
# 
# This script helps you quickly verify that Railway is configured correctly
# for PostgreSQL deployment.
#
# Usage: bash railway_quick_check.sh
#
# =============================================================================

set -e

echo "======================================================================"
echo "  Railway PostgreSQL Configuration Quick Check"
echo "======================================================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo "ℹ️  $1"
}

# Check 1: Verify nixpacks.toml doesn't have server packages
echo "Check 1: nixpacks.toml PostgreSQL configuration"
echo "----------------------------------------------------------------------"

if grep -q '"postgresql-client"' nixpacks.toml && ! grep -q '"postgresql"[^-]' nixpacks.toml; then
    print_success "PostgreSQL client libraries configured correctly"
else
    print_error "PostgreSQL server packages might be in nixpacks.toml!"
    print_info "Only postgresql-client, libpq-dev, libpq5 should be present"
    exit 1
fi

echo ""

# Check 2: Verify docker-compose.yml is excluded
echo "Check 2: docker-compose.yml exclusion"
echo "----------------------------------------------------------------------"

if grep -q "docker-compose" .railwayignore; then
    print_success "docker-compose.yml is excluded from Railway deployment"
else
    print_error "docker-compose.yml is NOT excluded!"
    print_info "Add 'docker-compose.yml' to .railwayignore"
    exit 1
fi

echo ""

# Check 3: Verify documentation exists
echo "Check 3: Setup documentation"
echo "----------------------------------------------------------------------"

if [ -f "RAILWAY_SETUP_REQUIRED.md" ]; then
    print_success "RAILWAY_SETUP_REQUIRED.md exists"
else
    print_error "RAILWAY_SETUP_REQUIRED.md not found!"
fi

if [ -f "RAILWAY_POSTGRESQL_SETUP.md" ]; then
    print_success "RAILWAY_POSTGRESQL_SETUP.md exists"
else
    print_warning "RAILWAY_POSTGRESQL_SETUP.md not found"
fi

echo ""

# Check 4: Check if running in Railway
echo "Check 4: Railway environment detection"
echo "----------------------------------------------------------------------"

if [ -n "$RAILWAY_ENVIRONMENT" ]; then
    print_info "Running in Railway environment"
    
    # Check for required environment variables
    missing_vars=()
    
    if [ -z "$DATABASE_URL" ] && [ -z "$DATABASE_PRIVATE_URL" ]; then
        missing_vars+=("DATABASE_URL or DATABASE_PRIVATE_URL")
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        missing_vars+=("SECRET_KEY")
    fi
    
    if [ -z "$JWT_SECRET_KEY" ]; then
        missing_vars+=("JWT_SECRET_KEY")
    fi
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        print_success "All required environment variables are set"
    else
        print_error "Missing environment variables: ${missing_vars[*]}"
        print_info "Configure these in Railway dashboard → Service → Variables"
        exit 1
    fi
else
    print_info "Not running in Railway (this is OK for local development)"
fi

echo ""
echo "======================================================================"
echo "  Summary"
echo "======================================================================"
echo ""

print_success "All checks passed! Your configuration looks good."
echo ""

print_info "To deploy to Railway:"
echo "  1. Ensure you have a MANAGED PostgreSQL database service in Railway"
echo "  2. Do NOT deploy PostgreSQL as a container"
echo "  3. Railway will auto-inject DATABASE_URL into your backend service"
echo "  4. Deploy your backend application"
echo ""

print_info "For detailed setup instructions:"
echo "  📄 Read RAILWAY_SETUP_REQUIRED.md"
echo "  📄 Read RAILWAY_POSTGRESQL_SETUP.md"
echo ""

print_info "Validate with Python script:"
echo "  python3 validate_railway_config.py"
echo ""

exit 0
