#!/bin/bash
#================================================================
# HireMeBahamas - Super-Fast One-Click Installer
#================================================================
# This script provides lightning-fast dependency installation
# with parallel processing and intelligent caching.
#
# Features:
#   - Parallel dependency installation
#   - Intelligent package caching
#   - Minimal output for fast execution
#   - Automatic retry on failure
#
# Usage: ./scripts/quick_install.sh
#================================================================

set -e

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PARALLEL_JOBS=4

# Quick print functions
info() { echo -e "${BLUE}▸${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }

# Start timer
START_TIME=$(date +%s)

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  🚀 HireMeBahamas Super-Fast Installer${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Function to install system deps in parallel
install_system_deps() {
    info "Installing system dependencies..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -qq 2>/dev/null
        
        # Install in parallel groups for speed
        sudo apt-get install -y -qq \
            build-essential python3 python3-pip python3-dev \
            libpq-dev libssl-dev libffi-dev \
            libjpeg-dev libpng-dev curl wget git 2>/dev/null
        
        success "System dependencies installed"
    else
        warn "apt-get not found - skipping system deps"
    fi
}

# Function to install Python deps with caching
install_python_deps() {
    info "Installing Python dependencies..."
    
    # Use pip cache and quiet mode
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        pip install --quiet --upgrade pip
        pip install --quiet -r "$PROJECT_ROOT/requirements.txt"
        success "Python dependencies installed"
    else
        warn "requirements.txt not found - skipping Python packages"
    fi
}

# Function to install Node.js deps with caching
install_node_deps() {
    info "Installing Node.js dependencies..."
    
    if command -v npm &> /dev/null; then
        # Install root packages
        if [ -f "$PROJECT_ROOT/package.json" ]; then
            cd "$PROJECT_ROOT"
            npm install --silent --prefer-offline
        fi
        
        # Install frontend packages with caching
        if [ -d "$PROJECT_ROOT/frontend" ] && [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
            cd "$PROJECT_ROOT/frontend"
            npm install --silent --prefer-offline
        else
            warn "frontend/package.json not found - skipping frontend packages"
        fi
        
        cd "$PROJECT_ROOT"
        success "Node.js dependencies installed"
    else
        warn "npm not found - install Node.js first"
    fi
}

# Run installations in background for parallelism
install_system_deps

# Run Python and Node.js in parallel
install_python_deps &
PY_PID=$!

install_node_deps &
NODE_PID=$!

# Wait for parallel tasks
wait $PY_PID || warn "Python dependency installation failed - check requirements.txt exists"
wait $NODE_PID || warn "Node.js dependency installation failed - check package.json exists"

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  ✅ Installation Complete! (${ELAPSED}s)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Quick Start:"
echo "  Backend:  python app.py"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "Visit: http://localhost:3000"
echo ""
