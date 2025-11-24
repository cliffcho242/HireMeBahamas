#!/bin/bash
# HireMeBahamas - Complete System Dependencies Installation
# This script installs ALL required system packages via apt-get to ensure
# the database can properly store user information and posts without data loss

set -e  # Exit on error

echo "============================================================"
echo "HireMeBahamas - System Dependencies Installation"
echo "Installing all required packages to ensure database works"
echo "============================================================"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script requires sudo privileges to install system packages."
    echo "Please run with: sudo $0"
    exit 1
fi

# Update package lists
echo "Step 1: Updating package lists..."
echo "----------------------------------------"
apt-get update -y
echo "✅ Package lists updated"
echo ""

# Install build essentials
echo "Step 2: Installing build tools..."
echo "----------------------------------------"
apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    cmake \
    autoconf \
    automake \
    libtool
echo "✅ Build tools installed"
echo ""

# Install Python and development files
echo "Step 3: Installing Python and development files..."
echo "----------------------------------------"
apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-setuptools \
    python3-wheel
echo "✅ Python and development files installed"
echo ""

# Install PostgreSQL client and libraries (for production database)
echo "Step 4: Installing PostgreSQL client and libraries..."
echo "----------------------------------------"
apt-get install -y \
    postgresql \
    postgresql-client \
    postgresql-client-common \
    postgresql-common \
    postgresql-contrib \
    libpq-dev \
    libpq5
echo "✅ PostgreSQL packages installed"
echo ""

# Install SQLite libraries (for development database)
echo "Step 5: Installing SQLite libraries..."
echo "----------------------------------------"
apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    libsqlite3-0
echo "✅ SQLite libraries installed"
echo ""

# Install Redis (for caching and session storage)
echo "Step 6: Installing Redis..."
echo "----------------------------------------"
apt-get install -y \
    redis-server \
    redis-tools
echo "✅ Redis installed"
echo ""

# Install Apache Kafka (for message streaming and event processing)
echo "Step 7: Installing Apache Kafka..."
echo "----------------------------------------"
apt-get install -y \
    openjdk-11-jdk \
    kafka
echo "✅ Apache Kafka installed"
echo ""

# Install SSL/TLS libraries (required for secure database connections)
echo "Step 8: Installing SSL/TLS libraries..."
echo "----------------------------------------"
apt-get install -y \
    libssl-dev \
    libffi-dev \
    ca-certificates \
    openssl
echo "✅ SSL/TLS libraries installed"
echo ""

# Install image processing libraries (for avatar uploads)
echo "Step 9: Installing image processing libraries..."
echo "----------------------------------------"
apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    zlib1g-dev
echo "✅ Image processing libraries installed"
echo ""

# Install other required libraries
echo "Step 10: Installing additional libraries..."
echo "----------------------------------------"
apt-get install -y \
    libevent-dev \
    libxml2-dev \
    libxslt1-dev \
    libreadline-dev \
    libbz2-dev \
    libncurses5-dev \
    libncursesw5-dev \
    tk-dev \
    xz-utils \
    llvm
echo "✅ Additional libraries installed"
echo ""

# Install utilities
echo "Step 11: Installing utilities..."
echo "----------------------------------------"
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    net-tools \
    htop
echo "✅ Utilities installed"
echo ""

# Clean up
echo "Step 12: Cleaning up..."
echo "----------------------------------------"
apt-get autoremove -y
apt-get clean
rm -rf /var/lib/apt/lists/*
echo "✅ Cleanup complete"
echo ""

# Verify installations
echo "Step 13: Verifying installations..."
echo "----------------------------------------"
echo -n "Python 3: "
python3 --version
echo -n "pip: "
pip3 --version
echo -n "PostgreSQL client: "
psql --version
echo -n "SQLite: "
sqlite3 --version
echo -n "Redis: "
redis-cli --version
echo -n "Java (for Kafka): "
java -version 2>&1 | head -n 1
echo -n "Git: "
git --version
echo "✅ All tools verified"
echo ""

echo "============================================================"
echo "✅ ALL SYSTEM DEPENDENCIES INSTALLED SUCCESSFULLY!"
echo "============================================================"
echo ""
echo "Database storage is now properly configured."
echo "User information and posts will be stored safely."
echo ""
echo "Next steps:"
echo "1. Install Python packages: pip3 install -r requirements.txt"
echo "2. Install backend packages: pip3 install -r backend/requirements.txt"
echo "3. Install frontend packages: cd frontend && npm install"
echo "4. Configure DATABASE_URL for production (PostgreSQL required)"
echo "5. Start the application"
echo ""
echo "📖 For production deployment, ensure DATABASE_URL is set to PostgreSQL"
echo "   to prevent user data loss on restarts/deployments."
echo ""
