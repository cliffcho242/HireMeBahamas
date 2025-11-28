#!/bin/bash
# Complete dependency installation script for HireMeBahamas
# This script installs all system and application dependencies

set -e  # Exit on error

echo "======================================"
echo "HireMeBahamas Dependency Installation"
echo "======================================"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "Detected OS: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "Detected OS: macOS"
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo ""
echo "Step 1: Installing System Dependencies"
echo "---------------------------------------"

if [ "$OS" = "linux" ]; then
    # Update package list
    echo "Updating package list..."
    sudo apt-get update -y
    
    # Install essential build tools
    echo "Installing build essentials..."
    sudo apt-get install -y build-essential
    
    # Install Python and pip
    echo "Installing Python 3 and pip..."
    sudo apt-get install -y python3 python3-pip python3-dev python3-venv
    
    # Install Node.js and npm
    if ! command_exists node; then
        echo "Installing Node.js and npm..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
    else
        echo "Node.js already installed: $(node --version)"
    fi
    
    # Install PostgreSQL development files
    echo "Installing PostgreSQL development files..."
    sudo apt-get install -y libpq-dev postgresql-client
    
    # Install Redis (for caching and WebSocket support)
    echo "Installing Redis..."
    sudo apt-get install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server || true
    
    # Install other dependencies for Python packages
    echo "Installing additional dependencies..."
    sudo apt-get install -y \
        libssl-dev \
        libffi-dev \
        libjpeg-dev \
        zlib1g-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libopenjp2-7-dev \
        libtiff5-dev \
        libwebp-dev \
        pkg-config
    
elif [ "$OS" = "macos" ]; then
    # Install Homebrew if not present
    if ! command_exists brew; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install Python
    if ! command_exists python3; then
        echo "Installing Python 3..."
        brew install python@3.11
    fi
    
    # Install Node.js
    if ! command_exists node; then
        echo "Installing Node.js..."
        brew install node
    fi
    
    # Install PostgreSQL
    echo "Installing PostgreSQL..."
    brew install postgresql@15
    
    # Install Redis
    echo "Installing Redis..."
    brew install redis
    brew services start redis
    
    # Install other dependencies
    echo "Installing additional dependencies..."
    brew install jpeg libpng freetype libtiff webp pkg-config

    # Install Render CLI for deployment
    echo "Installing Render CLI..."
    brew update
    brew install render
fi

echo ""
echo "Step 2: Verifying Python Installation"
echo "--------------------------------------"
python3 --version
pip3 --version

echo ""
echo "Step 3: Verifying Node.js Installation"
echo "---------------------------------------"
node --version
npm --version

echo ""
echo "Step 4: Installing Python Dependencies"
echo "---------------------------------------"

# Navigate to backend directory
cd "$(dirname "$0")/../backend" || cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install backend dependencies
echo "Installing backend Python packages..."
pip install -r requirements.txt

echo "Backend dependencies installed successfully!"

# Deactivate virtual environment
deactivate

echo ""
echo "Step 5: Installing Frontend Dependencies"
echo "-----------------------------------------"

# Navigate to frontend directory
cd ../frontend || exit

# Install Node.js packages
echo "Installing frontend npm packages..."
npm install

echo "Frontend dependencies installed successfully!"

echo ""
echo "Step 6: Installing Admin Panel Dependencies"
echo "---------------------------------------------"

# Save current directory
FRONTEND_DIR=$(pwd)

# Navigate to admin-panel directory
if cd ../admin-panel 2>/dev/null && [ -f "package.json" ]; then
    # Install Node.js packages
    echo "Installing admin-panel npm packages..."
    if npm install; then
        echo "Admin panel dependencies installed successfully!"
    else
        echo "⚠️  Failed to install admin-panel packages"
    fi
    cd "$FRONTEND_DIR/.." || cd ..
else
    echo "⚠️  Admin panel directory not found or package.json missing, skipping..."
    cd "$FRONTEND_DIR/.." || cd ..
fi

echo ""
echo "Step 7: Installing Root Dependencies"
echo "-------------------------------------"

# Navigate to root directory
cd .. || exit

# Install root Python dependencies (for utility scripts)
echo "Installing root Python packages..."
pip3 install -r requirements.txt

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Configure environment variables (copy .env.example to .env)"
echo "2. Run database migrations if needed"
echo "3. Start the backend server"
echo "4. Start the frontend development server"
echo ""
echo "For more information, see README.md"
echo ""
