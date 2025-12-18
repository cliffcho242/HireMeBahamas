#!/bin/bash
# Automated Deployment Script for HireMeBahamas

echo "=========================================="
echo "  HireMeBahamas Automated Deployment"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - HireMeBahamas"
fi

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git add .
git commit -m "Deploy: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "Next steps:"
echo "1. Deploy backend to Render: https://render.app"
echo "2. Deploy frontend to Vercel: https://vercel.com"
echo "3. Update environment variables with production URLs"
echo ""
echo "=========================================="
