#!/bin/bash
# Check if system is ready for HireMeBahamas Production Mode

echo "🔍 HireMeBahamas Environment Check"
echo "===================================="
echo ""

ERRORS=0

# Check Docker
echo -n "Checking Docker installation... "
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f 3 | cut -d ',' -f 1)
    echo "✅ Installed (v$DOCKER_VERSION)"
else
    echo "❌ Not installed"
    echo "   → Install Docker Desktop: https://www.docker.com/products/docker-desktop"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker Compose
echo -n "Checking docker compose... "
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "installed")
    echo "✅ Available (v$COMPOSE_VERSION)"
else
    echo "❌ Not available"
    echo "   → Update Docker Desktop or see DOCKER_SETUP.md"
    ERRORS=$((ERRORS + 1))
fi

# Check Docker daemon
echo -n "Checking Docker daemon... "
if docker info &> /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not running"
    echo "   → Start Docker Desktop"
    ERRORS=$((ERRORS + 1))
fi

# Check Node.js
echo -n "Checking Node.js... "
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Installed ($NODE_VERSION)"
else
    echo "⚠️  Not installed (required for frontend)"
    echo "   → Install from: https://nodejs.org/"
    ERRORS=$((ERRORS + 1))
fi

# Check npm
echo -n "Checking npm... "
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ Installed (v$NPM_VERSION)"
else
    echo "⚠️  Not installed (included with Node.js)"
    ERRORS=$((ERRORS + 1))
fi

# Check Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    echo "✅ Installed (v$PYTHON_VERSION)"
else
    echo "⚠️  Not installed (required for backend)"
    echo "   → Install from: https://www.python.org/"
    ERRORS=$((ERRORS + 1))
fi

# Check pip
echo -n "Checking pip... "
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    echo "✅ Installed"
else
    echo "⚠️  Not installed (included with Python)"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "===================================="

if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! You're ready to run production mode."
    echo ""
    echo "Next steps:"
    echo "  1. ./start_production.sh"
    echo "  2. Open http://localhost:3000"
    exit 0
else
    echo "❌ Found $ERRORS issue(s). Please fix them before continuing."
    echo ""
    echo "For help:"
    echo "  • Docker: See DOCKER_SETUP.md"
    echo "  • Full guide: See PRODUCTION_MODE_GUIDE.md"
    exit 1
fi
