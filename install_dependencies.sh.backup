#!/bin/bash
# Install all required and recommended system dependencies for HireMeBahamas

echo "Installing system dependencies for HireMeBahamas..."

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install Python and related dependencies
echo "Installing Python dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential

# Install PostgreSQL client libraries (required for psycopg2)
echo "Installing PostgreSQL dependencies..."
sudo apt-get install -y \
    libpq-dev \
    postgresql-client

# Install Node.js and npm (if not already installed)
echo "Installing Node.js and npm..."
sudo apt-get install -y \
    nodejs \
    npm

# Install image processing libraries (required for Pillow)
echo "Installing image processing libraries..."
sudo apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    zlib1g-dev

# Install additional useful tools
echo "Installing additional tools..."
sudo apt-get install -y \
    git \
    curl \
    wget \
    vim \
    htop

# Install recommended packages
echo "Installing recommended packages..."
sudo apt-get install -y \
    --install-recommends \
    python3-setuptools \
    python3-wheel

# Clean up
echo "Cleaning up..."
sudo apt-get autoremove -y
sudo apt-get clean

echo ""
echo "System dependencies installation complete!"
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: cd backend && pip3 install -r requirements.txt"
echo "2. Install frontend dependencies: cd frontend && npm install"
echo ""
