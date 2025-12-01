#!/bin/bash
# Deploy Database Schema using Drizzle Kit
# This script generates and pushes the database schema to PostgreSQL
#
# Usage: ./deploy-schema.sh
# Note: Ensure this script is executable: chmod +x deploy-schema.sh

set -e  # Exit on error

echo "🗄️  HireMeBahamas Database Schema Deployment"
echo "==========================================="
echo ""

# Check if POSTGRES_URL is set
if [ -z "$POSTGRES_URL" ]; then
    echo "❌ Error: POSTGRES_URL environment variable is not set"
    echo ""
    echo "Please set your database connection string:"
    echo "  export POSTGRES_URL='postgresql://user:password@host:port/database'"
    echo ""
    echo "Or for Vercel Postgres:"
    echo "  npx vercel env pull .env.local"
    echo "  source .env.local"
    exit 1
fi

echo "✅ Database URL configured"
echo ""

# Step 1: Generate migrations
echo "📝 Step 1: Generating database migrations..."
echo "   Running: npm run db:generate"
npm run db:generate

echo ""
echo "✅ Migration files generated in ./drizzle/"
echo ""

# Step 2: Push schema to database
echo "🚀 Step 2: Pushing schema to database..."
echo "   Running: npm run db:push"
npm run db:push

echo ""
echo "✅ Schema successfully deployed to database!"
echo ""
echo "🎉 Database setup complete!"
echo ""
echo "Next steps:"
echo "  1. Verify tables: Connect to your database and check tables"
echo "  2. Run the application: npm run dev"
echo "  3. Test the API: Access http://localhost:3000/api/health"
