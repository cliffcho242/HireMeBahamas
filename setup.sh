#!/bin/bash

# HireBahamas Setup Script

# Export CFLAGS to suppress compiler warnings during C extension builds
export CFLAGS="-Wno-conversion"

echo "🇧🇸 Setting up HireBahamas - The Ultimate Bahaman Job Platform!"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are installed"

# Create environment files
print_info "Creating environment files..."

# Backend environment
cat > backend/.env << EOL
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/hirebahamas
SECRET_KEY=your-super-secret-key-change-this-in-production-$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
CLOUDINARY_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
EOL

# Frontend environment
cat > frontend/.env << EOL
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name
EOL

print_status "Environment files created"

# Install frontend dependencies
print_info "Installing frontend dependencies..."
cd frontend
npm install
if [ $? -eq 0 ]; then
    print_status "Frontend dependencies installed"
else
    print_error "Failed to install frontend dependencies"
    exit 1
fi
cd ..

# Install backend dependencies
print_info "Installing backend dependencies..."
cd backend
python -m pip install -r requirements.txt
if [ $? -eq 0 ]; then
    print_status "Backend dependencies installed"
else
    print_error "Failed to install backend dependencies"
    exit 1
fi
cd ..

# Build and start services with Docker Compose
print_info "Building and starting services with Docker Compose..."
docker-compose up -d --build

if [ $? -eq 0 ]; then
    print_status "Services started successfully!"
    
    echo ""
    echo "🎉 HireBahamas is now running!"
    echo "================================"
    echo ""
    echo "Frontend (React): http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "PostgreSQL: localhost:5432"
    echo "Redis: localhost:6379"
    echo ""
    echo "📝 To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "🛑 To stop services:"
    echo "  docker-compose down"
    echo ""
    echo "🔄 To restart services:"
    echo "  docker-compose restart"
    echo ""
    print_warning "Remember to update your environment variables with real values!"
    print_warning "Especially DATABASE_URL, SECRET_KEY, and Cloudinary settings for production."
    
else
    print_error "Failed to start services"
    echo "Check the logs with: docker-compose logs"
    exit 1
fi