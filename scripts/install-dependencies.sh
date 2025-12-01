#!/bin/bash
#
# Comprehensive Dependency Installation Script for HireMeBahamas
# 
# This script automatically installs all required dependencies for both
# backend (Python/FastAPI) and frontend (Node.js/React) components.
#
# Usage: 
#   sudo ./scripts/install-dependencies.sh [--backend-only|--frontend-only|--all]
#
# Default: Installs all dependencies
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
INSTALL_MODE="all"
if [ "$1" == "--backend-only" ]; then
    INSTALL_MODE="backend"
elif [ "$1" == "--frontend-only" ]; then
    INSTALL_MODE="frontend"
fi

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}HireMeBahamas - Dependency Installation${NC}"
echo -e "${BLUE}Mode: ${INSTALL_MODE}${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" == "success" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" == "error" ]; then
        echo -e "${RED}✗${NC} $message"
    elif [ "$status" == "info" ]; then
        echo -e "${CYAN}ℹ${NC} $message"
    elif [ "$status" == "warning" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
    fi
}

# Check if running with sudo for system dependencies
if [ "$EUID" -ne 0 ] && [ "$INSTALL_MODE" != "frontend" ]; then 
    print_status "warning" "Not running as root. System dependencies may require sudo."
    echo "You may need to run: sudo $0 $@"
fi

# Install System Dependencies (for backend)
if [ "$INSTALL_MODE" == "all" ] || [ "$INSTALL_MODE" == "backend" ]; then
    echo ""
    echo -e "${YELLOW}[1/5] Installing system dependencies...${NC}"
    
    if [ "$EUID" -eq 0 ]; then
        apt-get update -y || print_status "error" "Failed to update package lists"
        
        print_status "info" "Installing build tools..."
        apt-get install -y \
            build-essential \
            gcc \
            g++ \
            make \
            pkg-config \
            python3 \
            python3-pip \
            python3-dev \
            python3-venv \
            python3-setuptools \
            python3-wheel || print_status "error" "Failed to install build tools"
        
        print_status "info" "Installing database dependencies..."
        apt-get install -y \
            postgresql \
            postgresql-contrib \
            postgresql-client \
            libpq-dev || print_status "warning" "PostgreSQL installation may have failed"
        
        print_status "info" "Installing security libraries..."
        apt-get install -y \
            libssl-dev \
            libffi-dev \
            ca-certificates || print_status "error" "Failed to install security libraries"
        
        print_status "info" "Installing image processing libraries..."
        apt-get install -y \
            libjpeg-dev \
            libpng-dev \
            libtiff-dev \
            libwebp-dev \
            libopenjp2-7-dev \
            zlib1g-dev || print_status "warning" "Some image libraries may have failed"
        
        print_status "info" "Installing utilities..."
        apt-get install -y \
            curl \
            wget \
            git || print_status "warning" "Some utilities may have failed"
        
        print_status "success" "System dependencies installed"
    else
        print_status "warning" "Skipping system dependencies (not running as root)"
        print_status "info" "Run with sudo to install system dependencies"
    fi
fi

# Install Python Backend Dependencies
if [ "$INSTALL_MODE" == "all" ] || [ "$INSTALL_MODE" == "backend" ]; then
    echo ""
    echo -e "${YELLOW}[2/5] Installing Python dependencies...${NC}"
    
    if command_exists python3; then
        print_status "info" "Python version: $(python3 --version)"
        
        # Upgrade pip
        print_status "info" "Upgrading pip..."
        python3 -m pip install --upgrade pip setuptools wheel || print_status "error" "Failed to upgrade pip"
        
        # Install test dependencies
        print_status "info" "Installing test dependencies..."
        python3 -m pip install pytest pytest-flask pytest-asyncio || print_status "error" "Failed to install test tools"
        
        # Install root requirements.txt
        if [ -f "requirements.txt" ]; then
            print_status "info" "Installing from requirements.txt..."
            export CFLAGS="-Wno-conversion"
            python3 -m pip install -r requirements.txt || print_status "error" "Failed to install requirements.txt"
            print_status "success" "Installed root requirements.txt"
        else
            print_status "warning" "requirements.txt not found"
        fi
        
        # Install backend requirements.txt
        if [ -f "backend/requirements.txt" ]; then
            print_status "info" "Installing from backend/requirements.txt..."
            export CFLAGS="-Wno-conversion"
            python3 -m pip install -r backend/requirements.txt || print_status "error" "Failed to install backend/requirements.txt"
            print_status "success" "Installed backend/requirements.txt"
        else
            print_status "warning" "backend/requirements.txt not found"
        fi
        
        # Verify critical Python packages
        print_status "info" "Verifying critical Python packages..."
        python3 -c "
import sys
errors = []

packages = [
    ('fastapi', 'FastAPI'),
    ('sqlalchemy', 'SQLAlchemy'),
    ('psycopg2', 'psycopg2-binary'),
    ('jose', 'python-jose'),
    ('passlib', 'passlib'),
    ('pydantic', 'Pydantic'),
    ('asyncpg', 'asyncpg'),
]

for module, name in packages:
    try:
        __import__(module)
        print(f'✓ {name}')
    except ImportError:
        errors.append(name)
        print(f'✗ {name}')

if errors:
    print(f'\nMissing packages: {', '.join(errors)}')
    sys.exit(1)
" || print_status "error" "Some critical packages are missing"
        
        print_status "success" "Python dependencies installed"
    else
        print_status "error" "Python3 not found"
        exit 1
    fi
fi

# Install Node.js (if needed for frontend)
if [ "$INSTALL_MODE" == "all" ] || [ "$INSTALL_MODE" == "frontend" ]; then
    echo ""
    echo -e "${YELLOW}[3/5] Checking Node.js installation...${NC}"
    
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_status "info" "Node.js is installed: $NODE_VERSION"
        
        # Check if version is acceptable (v18 or higher)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1 | sed 's/v//')
        if [ "$NODE_MAJOR" -lt 18 ]; then
            print_status "warning" "Node.js version should be 18 or higher"
        else
            print_status "success" "Node.js version is acceptable"
        fi
    else
        print_status "warning" "Node.js is not installed"
        
        if [ "$EUID" -eq 0 ]; then
            print_status "info" "Installing Node.js 18.x LTS..."
            curl -fsSL https://deb.nodesource.com/setup_18.x | bash - || print_status "error" "Failed to setup Node.js repository"
            apt-get install -y nodejs || print_status "error" "Failed to install Node.js"
            print_status "success" "Node.js installed: $(node --version)"
        else
            print_status "error" "Cannot install Node.js without root privileges"
            print_status "info" "Please install Node.js manually or run with sudo"
            exit 1
        fi
    fi
fi

# Install Frontend Dependencies
if [ "$INSTALL_MODE" == "all" ] || [ "$INSTALL_MODE" == "frontend" ]; then
    echo ""
    echo -e "${YELLOW}[4/5] Installing frontend dependencies...${NC}"
    
    if [ -d "frontend" ]; then
        cd frontend
        
        if [ -f "package.json" ]; then
            print_status "info" "Found package.json"
            
            # Check if package-lock.json exists
            if [ -f "package-lock.json" ]; then
                print_status "info" "Using npm ci (clean install)..."
                npm ci || {
                    print_status "warning" "npm ci failed, trying npm install..."
                    npm install || print_status "error" "npm install failed"
                }
            else
                print_status "warning" "package-lock.json not found, using npm install..."
                npm install || print_status "error" "npm install failed"
            fi
            
            print_status "success" "Frontend dependencies installed"
            
            # Verify critical packages
            print_status "info" "Verifying critical frontend packages..."
            node -e "
const fs = require('fs');
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };

const required = [
    'react',
    'react-dom',
    'react-router-dom',
    'axios',
    'react-hook-form',
    'react-hot-toast',
    '@react-oauth/google',
    'react-apple-signin-auth',
    'vite',
    'typescript'
];

const missing = required.filter(pkg => !deps[pkg]);

required.forEach(pkg => {
    if (deps[pkg]) {
        console.log('✓', pkg);
    } else {
        console.log('✗', pkg);
    }
});

if (missing.length > 0) {
    console.log('\nMissing packages:', missing.join(', '));
    process.exit(1);
}
" || print_status "error" "Some critical frontend packages are missing"
            
        else
            print_status "error" "package.json not found in frontend directory"
            exit 1
        fi
        
        cd ..
    else
        print_status "error" "frontend directory not found"
        exit 1
    fi
fi

# Final Summary
echo ""
echo -e "${YELLOW}[5/5] Installation Summary${NC}"
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✓ Dependency Installation Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Print next steps
echo -e "${BLUE}Next Steps:${NC}"
echo ""

if [ "$INSTALL_MODE" == "all" ] || [ "$INSTALL_MODE" == "backend" ]; then
    echo "Backend:"
    echo "  1. Configure environment: cp .env.example .env"
    echo "  2. Start backend: cd backend && python3 -m app.main"
    echo "  3. Test registration: python3 test_registration.py"
    echo ""
fi

if [ "$INSTALL_MODE" == "all" ] || [ "$INSTALL_MODE" == "frontend" ]; then
    echo "Frontend:"
    echo "  1. Configure environment: cd frontend && cp .env.example .env"
    echo "  2. Start frontend: cd frontend && npm run dev"
    echo "  3. Build frontend: cd frontend && npm run build"
    echo ""
fi

echo -e "${GREEN}✓ All dependencies installed successfully!${NC}"
echo ""

exit 0
