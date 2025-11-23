#!/bin/bash
# HireMeBahamas - Master Installation Script
# This script ensures ALL dependencies are installed (system + Python + Node.js)
# and the database is properly configured to store user information

set -e  # Exit on error

echo "================================================================"
echo "HireMeBahamas - COMPLETE Installation"
echo "This will install ALL dependencies and setup the database"
echo "================================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if running as root for system dependencies
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  System dependencies require sudo privileges."
    echo "This script will use sudo when needed."
    echo ""
fi

# Step 1: Install system dependencies (requires sudo)
echo "================================================================"
echo "Step 1: Installing System Dependencies (apt-get packages)"
echo "================================================================"
echo "This ensures the database can store user information properly."
echo ""

if [ -f "./install_system_dependencies.sh" ]; then
    sudo ./install_system_dependencies.sh
else
    echo "⚠️  System dependency installer not found. Installing manually..."
    
    # Update and install essential packages
    sudo apt-get update -y
    sudo apt-get install -y \
        build-essential \
        gcc \
        g++ \
        make \
        pkg-config \
        python3 \
        python3-pip \
        python3-dev \
        python3-venv \
        postgresql \
        postgresql-client \
        libpq-dev \
        sqlite3 \
        libsqlite3-dev \
        redis-server \
        libssl-dev \
        libffi-dev \
        libjpeg-dev \
        libpng-dev \
        zlib1g-dev \
        curl \
        wget \
        git
    
    echo "✅ System dependencies installed"
fi

echo ""
echo "================================================================"
echo "Step 2: Installing Python Dependencies"
echo "================================================================"
echo ""

# Upgrade pip first
echo "Upgrading pip..."
python3 -m pip install --upgrade pip setuptools wheel

# Install root requirements
if [ -f "requirements.txt" ]; then
    echo "Installing root Python packages..."
    pip3 install -r requirements.txt
    echo "✅ Root Python packages installed"
else
    echo "⚠️  Root requirements.txt not found"
fi

# Install backend requirements
if [ -f "backend/requirements.txt" ]; then
    echo "Installing backend Python packages..."
    pip3 install -r backend/requirements.txt
    echo "✅ Backend Python packages installed"
else
    echo "⚠️  Backend requirements.txt not found"
fi

echo ""
echo "================================================================"
echo "Step 3: Verifying Python Package Installation"
echo "================================================================"
echo ""

# Test critical imports
echo "Testing critical Python packages..."
python3 -c "import flask; print('✅ Flask:', flask.__version__)" 2>/dev/null || echo "⚠️  Flask not installed"
python3 -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" 2>/dev/null || echo "⚠️  FastAPI not installed"
python3 -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)" 2>/dev/null || echo "⚠️  SQLAlchemy not installed"
python3 -c "import psycopg2; print('✅ psycopg2:', psycopg2.__version__)" 2>/dev/null || echo "⚠️  psycopg2 not installed"
python3 -c "import aiosqlite; print('✅ aiosqlite installed')" 2>/dev/null || echo "⚠️  aiosqlite not installed"
python3 -c "from decouple import config; print('✅ python-decouple installed')" 2>/dev/null || echo "⚠️  python-decouple not installed"
python3 -c "import bcrypt; print('✅ bcrypt installed')" 2>/dev/null || echo "⚠️  bcrypt not installed"
python3 -c "import jwt; print('✅ PyJWT installed')" 2>/dev/null || echo "⚠️  PyJWT not installed"

echo ""
echo "================================================================"
echo "Step 4: Installing Node.js Dependencies (Frontend)"
echo "================================================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed. Installing Node.js 18.x..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    echo "✅ Node.js installed"
else
    echo "✅ Node.js already installed: $(node --version)"
fi

# Install frontend dependencies
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    echo "Installing frontend npm packages..."
    cd frontend
    npm install
    echo "✅ Frontend packages installed"
    cd ..
else
    echo "⚠️  Frontend directory not found or package.json missing"
fi

echo ""
echo "================================================================"
echo "Step 5: Database Configuration Check"
echo "================================================================"
echo ""

# Run database initialization check
if [ -f "./ensure_database_init.py" ]; then
    python3 ensure_database_init.py
else
    echo "⚠️  Database initialization check script not found"
    echo "⚠️  Please ensure DATABASE_URL is set for production"
fi

echo ""
echo "================================================================"
echo "Step 6: Creating Environment Configuration"
echo "================================================================"
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Creating .env file from .env.example..."
        cp .env.example .env
        echo "✅ .env file created"
        echo "⚠️  IMPORTANT: Edit .env and set your DATABASE_URL for production!"
    else
        echo "⚠️  .env.example not found"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "================================================================"
echo "✅ INSTALLATION COMPLETE!"
echo "================================================================"
echo ""
echo "All dependencies are installed and configured."
echo "User information and posts will now be stored properly."
echo ""
echo "🔴 CRITICAL FOR PRODUCTION:"
echo "   1. Edit .env file and set DATABASE_URL to PostgreSQL connection:"
echo "      DATABASE_URL=postgresql://user:password@host:5432/database"
echo "   2. PostgreSQL is REQUIRED for production to prevent data loss"
echo "   3. SQLite is ONLY for local development"
echo ""
echo "📖 Next steps:"
echo "   • Start backend: gunicorn final_backend_postgresql:application --bind 0.0.0.0:8080"
echo "   • Start frontend: cd frontend && npm run dev"
echo "   • Access app: http://localhost:5173"
echo ""
echo "📚 Documentation:"
echo "   • SYSTEM_DEPENDENCIES.md - System package details"
echo "   • DATA_PERSISTENCE_GUIDE.md - Database configuration"
echo "   • README.md - Complete setup guide"
echo ""
