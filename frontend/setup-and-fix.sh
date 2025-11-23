#!/bin/bash

###############################################################################
# HireMeBahamas Frontend - Automated Setup and Fix Script
#
# This script automates the complete setup and fixing of the frontend build,
# including:
# - Checking and installing all dependencies
# - Generating missing PWA assets
# - Fixing vite-plugin-pwa build errors
# - Verifying the build works correctly
#
# Usage: ./setup-and-fix.sh
###############################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Change to frontend directory
cd "$(dirname "$0")" || exit 1
SCRIPT_DIR="$(pwd)"

print_header "HireMeBahamas Frontend - Automated Setup & Fix"

# Step 1: Check Node.js and npm
print_header "Step 1: Checking System Requirements"

if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version $NODE_VERSION is too old. Please install Node.js 18+."
    exit 1
fi

print_success "Node.js $(node -v) detected"
print_success "npm $(npm -v) detected"

# Step 2: Clean install dependencies
print_header "Step 2: Installing Frontend Dependencies"

print_info "Cleaning previous installations..."
rm -rf node_modules package-lock.json 2>/dev/null || true

print_info "Installing dependencies (this may take a few minutes)..."
if npm install; then
    print_success "All frontend dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Step 3: Install sharp for asset generation
print_header "Step 3: Installing Asset Generation Tool (sharp)"

if npm list sharp &> /dev/null; then
    print_info "sharp already installed"
else
    print_info "Installing sharp for PWA asset generation..."
    if npm install --save-dev sharp; then
        print_success "sharp installed successfully"
    else
        print_error "Failed to install sharp"
        exit 1
    fi
fi

# Step 4: Generate PWA assets
print_header "Step 4: Generating PWA Assets"

if [ -f "scripts/generate-pwa-assets.js" ]; then
    print_info "Running PWA asset generator..."
    if node scripts/generate-pwa-assets.js; then
        print_success "PWA assets generated successfully"
    else
        print_error "Failed to generate PWA assets"
        exit 1
    fi
else
    print_error "PWA asset generator script not found at scripts/generate-pwa-assets.js"
    exit 1
fi

# Step 5: Verify generated assets
print_header "Step 5: Verifying Generated Assets"

REQUIRED_ASSETS=(
    "public/pwa-192x192.png"
    "public/pwa-512x512.png"
    "public/apple-touch-icon.png"
    "public/favicon-16x16.png"
    "public/favicon-32x32.png"
    "public/favicon.ico"
    "public/vite.svg"
    "public/splash-screens/iphone5_splash.png"
    "public/splash-screens/iphone6_splash.png"
    "public/splash-screens/iphonex_splash.png"
)

MISSING_ASSETS=0
for asset in "${REQUIRED_ASSETS[@]}"; do
    if [ -f "$asset" ]; then
        print_success "Found: $asset"
    else
        print_error "Missing: $asset"
        MISSING_ASSETS=$((MISSING_ASSETS + 1))
    fi
done

if [ $MISSING_ASSETS -gt 0 ]; then
    print_error "$MISSING_ASSETS required assets are missing"
    exit 1
fi

# Step 6: Build the frontend
print_header "Step 6: Testing Frontend Build"

print_info "Running TypeScript compiler and Vite build..."
if npm run build; then
    print_success "Frontend build completed successfully!"
else
    print_error "Frontend build failed"
    exit 1
fi

# Step 7: Verify build output
print_header "Step 7: Verifying Build Output"

if [ -d "dist" ]; then
    DIST_SIZE=$(du -sh dist | cut -f1)
    print_success "Build output directory created (size: $DIST_SIZE)"
    
    if [ -f "dist/index.html" ]; then
        print_success "index.html generated"
    fi
    
    if [ -f "dist/sw.js" ]; then
        print_success "Service worker (sw.js) generated"
    fi
    
    if [ -f "dist/manifest.webmanifest" ]; then
        print_success "PWA manifest generated"
    fi
else
    print_error "Build output directory not found"
    exit 1
fi

# Step 8: Clean up (optional - remove sharp if not needed)
print_header "Step 8: Cleanup"

print_info "Do you want to remove sharp from dependencies? (It's only needed for asset generation)"
print_info "You can keep it if you plan to regenerate assets later."
read -p "Remove sharp? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npm uninstall sharp
    print_success "sharp removed from dependencies"
else
    print_info "Keeping sharp in devDependencies"
fi

# Final summary
print_header "Setup Complete! 🎉"

print_success "All dependencies installed"
print_success "All PWA assets generated"
print_success "Frontend build verified"
print_success "Ready for deployment"

echo -e "\n${GREEN}Next steps:${NC}"
echo "  1. Start development server: npm run dev"
echo "  2. Preview production build: npm run preview"
echo "  3. Deploy to production"

echo -e "\n${BLUE}Generated assets location:${NC}"
echo "  - PWA icons: frontend/public/*.png"
echo "  - Splash screens: frontend/public/splash-screens/*.png"
echo "  - Build output: frontend/dist/"

print_success "Setup completed successfully!"
