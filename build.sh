#!/bin/bash
# =============================================================================
# HireMeBahamas Build Script for Render
# =============================================================================
# This script ensures dependencies are installed correctly before starting
# the application. It explicitly uses pip to avoid Poetry auto-detection issues.
#
# Render may auto-detect pyproject.toml and try to use Poetry. This script
# forces pip installation to work around that issue.
# =============================================================================

set -e  # Exit on error

echo "🔧 HireMeBahamas Build Script Starting..."
echo "========================================"

# Upgrade pip, setuptools, and wheel
echo "📦 Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install dependencies from requirements.txt using binary wheels only
# This prevents compilation issues on Render's build environment
echo "📦 Installing dependencies from requirements.txt..."
pip install --only-binary=:all: -r requirements.txt

# Verify gunicorn is installed
echo "✅ Verifying gunicorn installation..."
if ! command -v gunicorn >/dev/null 2>&1; then
    echo "❌ ERROR: gunicorn not found after installation!"
    exit 1
fi

echo "✅ gunicorn found: $(which gunicorn)"
echo "✅ gunicorn version: $(gunicorn --version)"

echo "========================================"
echo "✅ Build completed successfully!"
echo "🚀 Ready to start application with gunicorn"
