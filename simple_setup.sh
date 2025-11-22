#!/bin/bash
# Simple setup script for HireMeBahamas (without Docker)
# This script ensures all dependencies are installed and environment is configured

set -e

echo "🚀 HireMeBahamas Simple Setup"
echo "=============================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    
    if [ ! -f .env.example ]; then
        echo "❌ .env.example not found!"
        exit 1
    fi
    
    cp .env.example .env
    
    # Generate secure secret keys
    echo ""
    echo "🔐 Generating secure SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env file with generated keys
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-generate-a-random-one/$SECRET_KEY/" .env
        sed -i '' "s/your-jwt-secret-key-here-generate-a-random-one/$JWT_SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here-generate-a-random-one/$SECRET_KEY/" .env
        sed -i "s/your-jwt-secret-key-here-generate-a-random-one/$JWT_SECRET_KEY/" .env
    fi
    
    echo "✅ .env file created with secure keys"
    echo "⚠️  IMPORTANT: Never commit the .env file to git!"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -q -r requirements.txt
    echo "✅ Python dependencies installed"
else
    echo "❌ pip3 not found. Please install Python 3.8+ first."
    exit 1
fi

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
if command -v npm &> /dev/null; then
    cd frontend
    npm install --silent
    cd ..
    echo "✅ Frontend dependencies installed"
else
    echo "⚠️  npm not found. Skipping frontend installation."
    echo "   Please install Node.js 18+ to run the frontend."
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python3 -c "
from final_backend_postgresql import init_database
try:
    init_database()
    print('✅ Database initialized successfully')
except Exception as e:
    print(f'⚠️  Database initialization: {e}')
    print('   Database will be initialized on first run')
"

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "  1. Review the .env file and update if needed"
echo "  2. Start backend: python3 final_backend_postgresql.py"
echo "  3. Start frontend: cd frontend && npm run dev"
echo "  4. Visit http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "  - DATA_PERSISTENCE_GUIDE.md - Data persistence and session management"
echo "  - README.md - General project documentation"
echo ""
