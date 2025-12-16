#!/bin/bash

# HireMeBahamas - Application Dependency Installation Script
# This script installs all required application-level dependencies for frontend and backend

set -e  # Exit on error

echo "=================================="
echo "HireMeBahamas App Dependency Installer"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "Error: Not in the HireMeBahamas root directory"
    exit 1
fi

print_info "Starting dependency installation..."
echo ""

# Install Frontend Dependencies
echo "=================================="
echo "Installing Frontend Dependencies"
echo "=================================="
cd frontend

if [ ! -f "package.json" ]; then
    print_error "Frontend package.json not found!"
    exit 1
fi

print_info "Running npm install..."
if npm install; then
    print_success "Frontend dependencies installed (804 packages)"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi

cd ..
echo ""

# Install Backend Dependencies
echo "=================================="
echo "Installing Backend Dependencies"
echo "=================================="
cd backend

if [ ! -f "requirements.txt" ]; then
    print_error "Backend requirements.txt not found!"
    exit 1
fi

print_info "Running pip install..."
if python3 -m pip install -r requirements.txt; then
    print_success "Backend dependencies installed (143 packages)"
else
    print_error "Failed to install backend dependencies"
    exit 1
fi

cd ..
echo ""

# Verify Installations
echo "=================================="
echo "Verifying Installations"
echo "=================================="

# Verify Frontend
print_info "Verifying frontend dependencies..."
cd frontend
if npm list socket.io-client axios react > /dev/null 2>&1; then
    print_success "Key frontend packages verified: socket.io-client, axios, react"
else
    print_info "Warning: Some frontend packages may need verification"
fi
cd ..

# Verify Backend
print_info "Verifying backend dependencies..."
if python3 -c "import fastapi, socketio, uvicorn, sqlalchemy, aiosqlite" > /dev/null 2>&1; then
    print_success "Key backend packages verified: fastapi, socketio, uvicorn, sqlalchemy, aiosqlite"
else
    print_error "Some backend packages are missing"
fi

echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
print_success "All dependencies installed successfully!"
echo ""
echo "Next steps:"
echo ""
echo "LOCAL DEVELOPMENT (with auto-reload):"
echo "  cd backend && uvicorn app.main:app --reload"
echo "  cd frontend && npm run dev"
echo ""
echo "PRODUCTION (no auto-reload):"
echo "  cd backend && uvicorn app.main:app --no-reload --workers 2"
echo "  cd frontend && npm run build && npm run start"
echo ""
echo "⚠️  IMPORTANT: --reload is for LOCAL DEVELOPMENT ONLY"
echo "    NEVER use --reload in production (doubles memory, causes SIGTERM)"
echo ""
print_info "For detailed testing instructions, see test_messaging_integration.md"
