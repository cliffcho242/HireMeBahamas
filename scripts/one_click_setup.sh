#!/bin/bash
# One-Click Setup Script for HireMeBahamas
# Installs and activates all dependencies with zero manual intervention

echo "=================================="
echo "🚀 HireMeBahamas One-Click Setup"
echo "=================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$ROOT_DIR"

echo "📁 Working directory: $ROOT_DIR"
echo ""

# Step 1: Install Python dependencies
echo "=================================="
echo "📦 Step 1: Installing Python Dependencies"
echo "=================================="
echo ""

if command -v python3 &> /dev/null; then
    python3 -m pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Python dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install Python dependencies${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

echo ""

# Step 2: Activate all dependencies
echo "=================================="
echo "⚙️  Step 2: Activating Dependencies"
echo "=================================="
echo ""

python3 scripts/activate_all_dependencies.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Some optional dependencies could not be activated${NC}"
    echo -e "${YELLOW}   The application will still work with reduced functionality${NC}"
fi

echo ""

# Step 3: Install frontend dependencies
echo "=================================="
echo "🎨 Step 3: Installing Frontend Dependencies"
echo "=================================="
echo ""

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    
    if command -v npm &> /dev/null; then
        npm install
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
        else
            echo -e "${YELLOW}⚠️  Frontend installation had issues${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  npm not found. Skipping frontend setup.${NC}"
        echo -e "${YELLOW}   Install Node.js to build the frontend${NC}"
    fi
    
    cd ..
else
    echo -e "${YELLOW}⚠️  Frontend directory not found${NC}"
fi

echo ""

# Step 4: Run startup initialization
echo "=================================="
echo "🔧 Step 4: Running Startup Initialization"
echo "=================================="
echo ""

python3 scripts/startup_init.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Startup checks found some issues${NC}"
fi

echo ""

# Step 5: Verify all dependencies
echo "=================================="
echo "✅ Step 5: Verifying Dependencies"
echo "=================================="
echo ""

python3 scripts/check_dependencies.py
VERIFY_RESULT=$?

echo ""
echo "=================================="

if [ $VERIFY_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ ALL DEPENDENCIES INSTALLED, ACTIVE, AND VERIFIED!${NC}"
    echo ""
    echo "🎉 Setup complete! You can now:"
    echo "   1. Start the backend: python3 final_backend_postgresql.py"
    echo "   2. Start the frontend: cd frontend && npm run dev"
    echo "   3. Check health: curl http://localhost:5000/api/health/dependencies"
else
    echo -e "${YELLOW}⚠️  Setup completed with warnings${NC}"
    echo ""
    echo "💡 The application may work with reduced functionality"
    echo "   Check the dependency report for details"
fi

echo "=================================="
