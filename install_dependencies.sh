#!/bin/bash
# HireMeBahamas - Complete Dependency Installation Script
# This script installs all required system and application dependencies

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================================"
echo "  HireMeBahamas - Dependency Installation Script"
echo "========================================================"
echo ""

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}===> $1${NC}\n"
}

# Function to print success messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root for apt-get
if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# 1. Update package lists
print_section "Updating package lists"
$SUDO apt-get update -y
print_success "Package lists updated"

# 2. Install System Build Tools
print_section "Installing System Build Tools"
$SUDO apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config
print_success "System build tools installed"

# 3. Install Python and Dependencies
print_section "Installing Python Dependencies"
$SUDO apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv
print_success "Python dependencies installed"

# 4. Install Database Dependencies
print_section "Installing Database Dependencies"
$SUDO apt-get install -y \
    postgresql \
    postgresql-client \
    libpq-dev
print_success "Database dependencies installed"

# 5. Install Redis
print_section "Installing Redis"
$SUDO apt-get install -y \
    redis-server \
    redis-tools
print_success "Redis installed"

# 6. Install SSL/Crypto Libraries
print_section "Installing SSL/Crypto Libraries"
$SUDO apt-get install -y \
    libssl-dev \
    libffi-dev
print_success "SSL/Crypto libraries installed"

# 7. Install Image Processing Libraries
print_section "Installing Image Processing Libraries"
$SUDO apt-get install -y \
    libjpeg-dev \
    libpng-dev
print_success "Image processing libraries installed"

# 8. Install Additional Libraries
print_section "Installing Additional Libraries"
$SUDO apt-get install -y \
    libevent-dev \
    libxml2-dev \
    libxslt1-dev
print_success "Additional libraries installed"

# 9. Install Web Server
print_section "Installing Nginx Web Server"
$SUDO apt-get install -y nginx
print_success "Nginx installed"

# 10. Install Utilities
print_section "Installing Utilities"
$SUDO apt-get install -y \
    curl \
    wget \
    git
print_success "Utilities installed"

# 11. Verify Node.js installation
print_section "Checking Node.js"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js is installed: $NODE_VERSION"
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm is installed: $NPM_VERSION"
    else
        print_error "npm is not installed"
        exit 1
    fi
else
    print_warning "Node.js is not installed"
    print_section "Installing Node.js 18.x LTS"
    curl -fsSL https://deb.nodesource.com/setup_18.x | $SUDO -E bash -
    $SUDO apt-get install -y nodejs
    print_success "Node.js installed"
fi

# 12. Install Python packages
print_section "Installing Python packages from requirements.txt"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Python packages installed"
else
    print_warning "requirements.txt not found, skipping Python package installation"
fi

# 13. Install Frontend dependencies
print_section "Installing Frontend Node.js packages"
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        npm install
        print_success "Frontend dependencies installed"
    else
        print_warning "package.json not found in frontend directory"
    fi
    cd ..
else
    print_warning "frontend directory not found, skipping frontend dependency installation"
fi

# 14. Configure Services
print_section "Configuring Services"

# Start and enable PostgreSQL
$SUDO systemctl start postgresql 2>/dev/null || print_warning "Could not start PostgreSQL (may already be running)"
$SUDO systemctl enable postgresql 2>/dev/null || print_warning "Could not enable PostgreSQL"
print_success "PostgreSQL configured"

# Start and enable Redis
$SUDO systemctl start redis-server 2>/dev/null || print_warning "Could not start Redis (may already be running)"
$SUDO systemctl enable redis-server 2>/dev/null || print_warning "Could not enable Redis"
print_success "Redis configured"

# 15. Summary
echo ""
echo "========================================================"
echo -e "${GREEN}  Installation Complete!${NC}"
echo "========================================================"
echo ""
echo "System Dependencies Installed:"
echo "  ✓ Build tools (gcc, g++, make, pkg-config)"
echo "  ✓ Python 3 and development headers"
echo "  ✓ PostgreSQL database"
echo "  ✓ Redis cache/message broker"
echo "  ✓ SSL/Crypto libraries"
echo "  ✓ Image processing libraries (JPEG, PNG)"
echo "  ✓ Additional libraries (libevent, libxml2, libxslt)"
echo "  ✓ Nginx web server"
echo "  ✓ Utilities (curl, wget, git)"
echo ""
echo "Application Dependencies:"
echo "  ✓ Python packages (Flask, FastAPI, SQLAlchemy, etc.)"
echo "  ✓ Frontend Node.js packages (React, TypeScript, Vite, etc.)"
echo ""
echo "Next Steps:"
echo "  1. Configure environment variables (copy .env.example to .env)"
echo "  2. Set up PostgreSQL database"
echo "  3. Run database migrations"
echo "  4. Start the backend server"
echo "  5. Start the frontend development server"
echo ""
echo "For more information, see README.md"
echo ""
