#!/bin/bash
#
# Automated Fix for "Failed to load user profile" Error
# 
# This script automatically installs all system dependencies (apt-get) needed 
# for HireMeBahamas backend and frontend to run properly, particularly fixing 
# the user profile loading issue.
#
# Installs:
# - Backend dependencies: Python, PostgreSQL, Redis, build tools, libraries
# - Frontend dependencies: Node.js, npm, image optimization libraries
#
# Usage: sudo bash automated_dependency_fix.sh
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}HireMeBahamas - Automated Dependency Fix${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERROR: This script must be run as root or with sudo${NC}"
    echo "Usage: sudo bash automated_dependency_fix.sh"
    exit 1
fi

echo -e "${YELLOW}[1/8] Updating package lists...${NC}"
apt-get update -y || {
    echo -e "${RED}Failed to update package lists${NC}"
    exit 1
}

echo ""
echo -e "${YELLOW}[2/8] Installing build tools and Python development packages...${NC}"
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
    python3-wheel || {
    echo -e "${RED}Failed to install build tools${NC}"
    exit 1
}

echo ""
echo -e "${YELLOW}[3/8] Installing database dependencies and optional caching...${NC}"
apt-get install -y \
    postgresql \
    postgresql-contrib \
    postgresql-client \
    libpq-dev || {
    echo -e "${RED}Failed to install database dependencies${NC}"
    exit 1
}

# Redis is optional
echo "Installing Redis (optional - not critical for basic operation)..."
apt-get install -y \
    redis-server \
    redis-tools || echo "⚠️  Redis not available - continuing without Redis (not critical)"

echo ""
echo -e "${YELLOW}[4/8] Installing cryptography and security libraries...${NC}"
apt-get install -y \
    libssl-dev \
    libffi-dev \
    ca-certificates || {
    echo -e "${RED}Failed to install security libraries${NC}"
    exit 1
}

echo ""
echo -e "${YELLOW}[5/8] Installing image processing and event libraries...${NC}"
apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libevent-dev \
    libxml2-dev \
    libxslt1-dev || {
    echo -e "${RED}Failed to install image processing libraries${NC}"
    exit 1
}

echo ""
echo -e "${YELLOW}[6/8] Installing additional utilities...${NC}"
apt-get install -y \
    curl \
    wget \
    git \
    htop \
    vim \
    unzip || {
    echo -e "${RED}Failed to install utilities${NC}"
    exit 1
}

echo ""
echo -e "${YELLOW}[7/8] Installing Node.js (for frontend)...${NC}"
# Check if Node.js is already installed
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version)
    echo "Node.js is already installed: $NODE_VERSION"
else
    echo "Installing Node.js 18.x LTS..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - || {
        echo -e "${RED}Failed to setup Node.js repository${NC}"
        exit 1
    }
    apt-get install -y nodejs || {
        echo -e "${RED}Failed to install Node.js${NC}"
        exit 1
    }
    echo "Node.js installed successfully: $(node --version)"
fi

echo ""
echo -e "${YELLOW}[8/8] Installing optional frontend image optimization libraries...${NC}"
echo "⚠️  These libraries are optional and provide enhanced image format support"
apt-get install -y \
    libvips-dev \
    libwebp-dev \
    libheif-dev \
    libavif-dev || {
    echo "⚠️  Note: Some optional image optimization libraries are not available on this system"
    echo "The application will function without these libraries"
}

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ System dependencies installed successfully!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Optional Dependencies Status:"
echo "  libvips-dev  - Advanced image optimization (optional)"
echo "  libheif-dev  - HEIF format support (optional)"
echo "  libavif-dev  - AVIF format support (optional)"
echo ""

# Start services
echo -e "${YELLOW}Starting PostgreSQL service...${NC}"
systemctl start postgresql 2>/dev/null || service postgresql start 2>/dev/null || echo "Note: PostgreSQL service may need manual start"

echo -e "${YELLOW}Starting Redis service (if installed)...${NC}"
systemctl start redis-server 2>/dev/null || service redis-server start 2>/dev/null || echo "⚠️  Redis not running (optional - not required for basic operation)"

# Enable services on boot
echo -e "${YELLOW}Enabling services to start on boot...${NC}"
systemctl enable postgresql 2>/dev/null || echo "Note: PostgreSQL auto-start may need manual configuration"
systemctl enable redis-server 2>/dev/null || echo "⚠️  Redis auto-start not configured (optional service)"

echo ""
echo -e "${GREEN}Verifying installations...${NC}"
echo "Python version: $(python3 --version)"
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"

echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Next Steps:${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo "1. Install Python dependencies:"
echo "   pip3 install -r requirements.txt"
echo "   cd backend && pip3 install -r requirements.txt"
echo ""
echo "2. Install frontend Node.js dependencies:"
echo "   cd frontend && npm install"
echo ""
echo "3. Configure environment variables:"
echo "   cp .env.example .env"
echo "   # Edit .env with your settings"
echo ""
echo "4. Start the backend server:"
echo "   cd backend && python3 -m app.main"
echo ""
echo "5. Start the frontend development server:"
echo "   cd frontend && npm run dev"
echo ""
echo "6. Test the user profile endpoint:"
echo "   python3 test_profile_endpoint.py"
echo ""
echo -e "${GREEN}✅ All system dependencies (apt-get) installed for backend and frontend!${NC}"
echo ""
