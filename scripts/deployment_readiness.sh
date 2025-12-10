#!/bin/bash
# ============================================================================
# Deployment Readiness Check
# ============================================================================
# Shell script wrapper for quick local checks
# Runs Python script + additional system checks
# Provides actionable error messages
#
# Usage:
#   ./scripts/deployment_readiness.sh
#   ./scripts/deployment_readiness.sh --verbose
#   ./scripts/deployment_readiness.sh --quick
#
# Exit codes:
#   0 - Ready to deploy
#   1 - Issues found, fix before deploying
#   2 - Critical failures, do NOT deploy
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
VERBOSE=0
QUICK=0

# Parse arguments
for arg in "$@"; do
    case $arg in
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        --quick|-q)
            QUICK=1
            shift
            ;;
        --help|-h)
            echo "Deployment Readiness Check"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --verbose, -v    Enable verbose output"
            echo "  --quick, -q      Run quick checks only (skip database test)"
            echo "  --help, -h       Show this help message"
            echo ""
            exit 0
            ;;
    esac
done

# Print header
echo -e "${BLUE}${BOLD}============================================================${NC}"
echo -e "${BLUE}${BOLD}           Deployment Readiness Check v1.0.0               ${NC}"
echo -e "${BLUE}${BOLD}============================================================${NC}"
echo ""

# Check if running in repository root
if [ ! -f "package.json" ] && [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Must run from repository root${NC}"
    exit 1
fi

# System checks
echo -e "${CYAN}🔍 Running system checks...${NC}"
echo ""

# 1. Check Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo -e "${YELLOW}   Install Python 3.11 or higher${NC}"
    exit 2
else
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
fi

# 2. Check Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found${NC}"
    echo -e "${YELLOW}   Install Node.js 18 or higher for frontend${NC}"
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js $NODE_VERSION${NC}"
fi

# 3. Check Git is installed
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠️  Git not found${NC}"
else
    GIT_VERSION=$(git --version)
    echo -e "${GREEN}✅ $GIT_VERSION${NC}"
fi

echo ""

# Check .env file
if [ -f ".env" ]; then
    echo -e "${CYAN}🔍 Loading environment from .env file...${NC}"
    set -a
    source .env
    set +a
    echo -e "${GREEN}✅ Environment loaded${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo -e "${YELLOW}   Using existing environment variables${NC}"
    echo ""
fi

# Check required Python packages
echo -e "${CYAN}🔍 Checking Python dependencies...${NC}"
echo ""

REQUIRED_PACKAGES=("flask" "psycopg2" "asyncpg")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        [ $VERBOSE -eq 1 ] && echo -e "${GREEN}✅ $package${NC}"
    else
        echo -e "${YELLOW}⚠️  $package not installed${NC}"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    echo -e "${CYAN}Install with: pip install -r requirements.txt${NC}"
    echo ""
fi

# Run Python health check script
echo -e "${CYAN}🔍 Running comprehensive health checks...${NC}"
echo ""

PYTHON_ARGS=""
[ $VERBOSE -eq 1 ] && PYTHON_ARGS="--verbose"
[ $QUICK -eq 1 ] && PYTHON_ARGS="$PYTHON_ARGS --check environment --check security --check imports"

if [ -f "scripts/pre_deployment_check.py" ]; then
    if python3 scripts/pre_deployment_check.py $PYTHON_ARGS; then
        HEALTH_EXIT=$?
    else
        HEALTH_EXIT=$?
    fi
else
    echo -e "${RED}❌ Health check script not found: scripts/pre_deployment_check.py${NC}"
    HEALTH_EXIT=1
fi

# Additional file checks
echo ""
echo -e "${CYAN}🔍 Checking critical files...${NC}"
echo ""

CRITICAL_FILES=(
    "api/index.py"
    "frontend/package.json"
    "requirements.txt"
    ".gitignore"
)

MISSING_FILES=()
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        [ $VERBOSE -eq 1 ] && echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${YELLOW}⚠️  $file not found${NC}"
        MISSING_FILES+=("$file")
    fi
done

# Check .gitignore for critical patterns
if [ -f ".gitignore" ]; then
    if grep -q "\.env" .gitignore && grep -q "node_modules" .gitignore; then
        [ $VERBOSE -eq 1 ] && echo -e "${GREEN}✅ .gitignore properly configured${NC}"
    else
        echo -e "${YELLOW}⚠️  .gitignore may be missing critical patterns${NC}"
    fi
fi

# Git status check
echo ""
echo -e "${CYAN}🔍 Checking git status...${NC}"
echo ""

if [ -d ".git" ]; then
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}⚠️  Uncommitted changes detected${NC}"
        [ $VERBOSE -eq 1 ] && git status --short
        echo -e "${YELLOW}   Commit changes before deploying${NC}"
    else
        echo -e "${GREEN}✅ Working directory clean${NC}"
    fi
    
    # Check current branch
    CURRENT_BRANCH=$(git branch --show-current)
    echo -e "${CYAN}   Current branch: ${CURRENT_BRANCH}${NC}"
    
    # Warn if not on main
    if [ "$CURRENT_BRANCH" != "main" ]; then
        echo -e "${YELLOW}⚠️  Not on main branch${NC}"
        echo -e "${YELLOW}   Deployments typically happen from main${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Not a git repository${NC}"
fi

# Final summary
echo ""
echo -e "${BLUE}${BOLD}============================================================${NC}"
echo -e "${BLUE}${BOLD}                    Summary                                 ${NC}"
echo -e "${BLUE}${BOLD}============================================================${NC}"
echo ""

if [ $HEALTH_EXIT -eq 0 ]; then
    if [ ${#MISSING_FILES[@]} -eq 0 ]; then
        echo -e "${GREEN}${BOLD}✅ READY TO DEPLOY${NC}"
        echo ""
        echo -e "${CYAN}Next steps:${NC}"
        echo -e "${CYAN}  1. Commit any pending changes${NC}"
        echo -e "${CYAN}  2. Push to GitHub${NC}"
        echo -e "${CYAN}  3. Monitor deployment workflows${NC}"
        echo ""
        exit 0
    else
        echo -e "${YELLOW}${BOLD}⚠️  WARNINGS DETECTED${NC}"
        echo ""
        echo -e "${YELLOW}Missing files: ${MISSING_FILES[*]}${NC}"
        echo -e "${YELLOW}Review warnings before deploying${NC}"
        echo ""
        exit 1
    fi
elif [ $HEALTH_EXIT -eq 2 ]; then
    echo -e "${RED}${BOLD}❌ CRITICAL FAILURES - DO NOT DEPLOY${NC}"
    echo ""
    echo -e "${RED}Fix critical issues before attempting deployment${NC}"
    echo ""
    exit 2
else
    echo -e "${YELLOW}${BOLD}⚠️  ISSUES DETECTED${NC}"
    echo ""
    echo -e "${YELLOW}Fix issues before deploying${NC}"
    echo ""
    echo -e "${CYAN}Run with --verbose for more details:${NC}"
    echo -e "${CYAN}  ./scripts/deployment_readiness.sh --verbose${NC}"
    echo ""
    exit 1
fi
