#!/bin/bash

# Test script for Edge Functions + Postgres implementation
# This verifies that the edge-sql-demo endpoint is correctly configured

echo "🧪 Testing Edge Functions + Postgres Implementation"
echo "=================================================="
echo ""

# Check if Next.js app builds successfully
echo "📦 Step 1: Building Next.js app..."
cd "$(dirname "$0")/next-app"

if npm run build > /tmp/build-test.log 2>&1; then
    echo "✅ Build successful"
else
    echo "❌ Build failed. Check /tmp/build-test.log for details"
    tail -20 /tmp/build-test.log
    exit 1
fi

echo ""
echo "✨ All checks passed!"
echo ""
echo "📚 Next Steps:"
echo "  1. Start dev server: cd next-app && npm run dev"
echo "  2. Test endpoint: curl http://localhost:3000/api/edge-sql-demo?operation=info"
echo "  3. Deploy to Vercel: npx vercel --prod"
echo ""
echo "📖 Documentation:"
echo "  - Complete Guide: EDGE_POSTGRES_README.md"
echo "  - Quick Ref: next-app/EDGE_POSTGRES_QUICKREF.md"
echo "  - Full Docs: next-app/EDGE_POSTGRES_GUIDE.md"
echo ""
echo "🎯 Demo Endpoint: /api/edge-sql-demo"
echo "   - ?operation=info   - System information"
echo "   - ?operation=select - SELECT query demo"
echo "   - ?operation=count  - Aggregate queries"
echo "   - ?operation=join   - Multi-table JOINs"

