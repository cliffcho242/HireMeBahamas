#!/bin/bash
#================================================================
# HireMeBahamas - Quick Secret Generator
#================================================================
# This script generates all required secrets for the application
# in one go, making it easy to set up environment variables.
#
# Usage: ./scripts/generate_secrets.sh
#================================================================

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    echo "Please install Python 3.6 or higher"
    exit 1
fi

echo "================================================"
echo "🔐 HireMeBahamas Secret Generator"
echo "================================================"
echo ""
echo "Generating secrets... (copy these to your .env files)"
echo ""

# Generate JWT_SECRET_KEY
JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
echo "JWT_SECRET_KEY=$JWT_SECRET"

# Generate SECRET_KEY
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(24))')
echo "SECRET_KEY=$SECRET_KEY"

echo ""
echo "================================================"
echo "✅ Secrets generated successfully!"
echo "================================================"
echo ""
echo "Copy these values to your .env files:"
echo "  - Backend: backend/.env"
echo "  - Root: .env"
echo ""
