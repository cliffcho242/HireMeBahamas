#!/bin/bash
#================================================================
# HireMeBahamas - Quick Local Setup Script
#================================================================
# This script sets up your local development environment by:
# 1. Generating secure secrets
# 2. Creating .env files for backend and frontend
# 3. Providing next steps for installation
#
# Usage: ./scripts/quick_local_setup.sh
#================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo -e "${BLUE}🚀 HireMeBahamas Quick Local Setup${NC}"
echo "================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠ Python 3 is required but not found${NC}"
    exit 1
fi

# Generate secrets
echo -e "${BLUE}📝 Generating secure secrets...${NC}"
JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(24))')
echo -e "${GREEN}✓${NC} Secrets generated"
echo ""

# Create backend .env file
echo -e "${BLUE}📝 Creating backend/.env file...${NC}"
cat > backend/.env << EOL
# backend/.env
DATABASE_URL=postgresql://localhost:5432/hiremebahamas_local
JWT_SECRET_KEY=${JWT_SECRET}
SECRET_KEY=${SECRET_KEY}
FLASK_ENV=development
CORS_ORIGINS=http://localhost:5173
EOL
echo -e "${GREEN}✓${NC} Backend .env created"
echo ""

# Create frontend .env file
echo -e "${BLUE}📝 Creating frontend/.env file...${NC}"
cat > frontend/.env << EOL
# frontend/.env
VITE_API_URL=http://localhost:8080
VITE_APP_NAME=HireMeBahamas
EOL
echo -e "${GREEN}✓${NC} Frontend .env created"
echo ""

echo "================================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "================================================"
echo ""
echo -e "${YELLOW}⚠ Security Note: Secrets are displayed below for your convenience.${NC}"
echo -e "${YELLOW}  Keep these safe and never commit them to version control!${NC}"
echo ""
echo "Your generated secrets:"
echo "  JWT_SECRET_KEY=${JWT_SECRET}"
echo "  SECRET_KEY=${SECRET_KEY}"
echo ""
echo "Files created:"
echo "  ✓ backend/.env"
echo "  ✓ frontend/.env"
echo ""
echo "Next steps:"
echo "  1. Install dependencies:"
echo "     pip install -r requirements.txt"
echo "     cd frontend && npm install"
echo ""
echo "  2. Set up PostgreSQL database:"
echo "     createdb hiremebahamas_local"
echo ""
echo "  3. Start the application:"
echo "     python app.py                 # Backend"
echo "     cd frontend && npm run dev    # Frontend"
echo ""
echo "Visit: http://localhost:5173"
echo ""
