#!/bin/bash

# PostgreSQL Dependencies Installation Script
# This script installs all required system dependencies for PostgreSQL
# to work properly with the HireMeBahamas application

set -e  # Exit on any error

echo "=========================================="
echo "PostgreSQL Dependencies Installation"
echo "=========================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script requires sudo privileges"
    echo "   Please run: sudo ./install_postgresql_dependencies.sh"
    exit 1
fi

echo "📦 Updating package lists..."
apt-get update -qq

echo ""
echo "📦 Installing PostgreSQL client libraries..."
# These are required for psycopg2-binary to work properly
apt-get install -y \
    libpq-dev \
    libpq5 \
    postgresql-client \
    postgresql-client-common

echo ""
echo "📦 Installing build dependencies..."
# These are needed to compile Python packages that interface with PostgreSQL
apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    make

echo ""
echo "📦 Installing additional system libraries..."
# These may be required by other Python packages
apt-get install -y \
    libssl-dev \
    libffi-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev

echo ""
echo "📦 Installing optional PostgreSQL tools..."
# These are useful for database management and debugging
apt-get install -y \
    postgresql-contrib || echo "⚠️  postgresql-contrib not available, skipping..."

echo ""
echo "🧹 Cleaning up..."
apt-get autoremove -y
apt-get clean

echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "Installed packages:"
echo "  - libpq-dev (PostgreSQL C library headers)"
echo "  - libpq5 (PostgreSQL C client library)"
echo "  - postgresql-client (PostgreSQL client)"
echo "  - build-essential (compilation tools)"
echo "  - python3-dev (Python development headers)"
echo ""
echo "📋 Next steps:"
echo "  1. Install Python dependencies: pip install -r requirements.txt"
echo "  2. Set DATABASE_URL environment variable"
echo "  3. Run the application"
echo ""
echo "For PostgreSQL setup instructions, see: POSTGRESQL_SETUP.md"
echo ""

# Verify installation
echo "🔍 Verifying installations..."
echo ""

if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version | awk '{print $3}')
    echo "✅ PostgreSQL client installed: $PSQL_VERSION"
else
    echo "⚠️  psql command not found"
fi

if pkg-config --exists libpq 2>/dev/null; then
    LIBPQ_VERSION=$(pkg-config --modversion libpq)
    echo "✅ libpq installed: $LIBPQ_VERSION"
else
    echo "⚠️  libpq not found"
fi

if command -v gcc &> /dev/null; then
    GCC_VERSION=$(gcc --version | head -n1 | awk '{print $3}')
    echo "✅ GCC compiler installed: $GCC_VERSION"
else
    echo "⚠️  GCC not found"
fi

if python3 --version &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "✅ Python3 installed: $PYTHON_VERSION"
else
    echo "⚠️  Python3 not found"
fi

echo ""
echo "=========================================="
echo "Installation verification complete!"
echo "=========================================="
