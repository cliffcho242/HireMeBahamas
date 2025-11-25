#!/bin/bash
# Start HireMeBahamas in Full Production Mode
# Uses PostgreSQL, production builds, no hot-reload

set -e

echo "🚀 Starting HireMeBahamas in Full Production Mode"
echo "=================================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo ""
    echo "Please install Docker first:"
    echo "  • Windows/macOS: https://www.docker.com/products/docker-desktop"
    echo "  • Linux: See DOCKER_SETUP.md"
    echo ""
    exit 1
fi

# Check if docker compose is available (new command)
if ! docker compose version &> /dev/null; then
    echo "❌ docker compose is not available."
    echo ""
    echo "Please install Docker Compose:"
    echo "  • It's included with Docker Desktop (Windows/macOS)"
    echo "  • Linux: See DOCKER_SETUP.md"
    echo ""
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running."
    echo ""
    echo "Please start Docker:"
    echo "  • Windows/macOS: Open Docker Desktop"
    echo "  • Linux: sudo systemctl start docker"
    echo ""
    exit 1
fi

# Start PostgreSQL and Redis
echo "📦 Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if backend .env exists
if [ ! -f backend/.env ]; then
    echo "⚙️  Creating backend/.env from .env.example..."
    cp backend/.env.example backend/.env
    echo "✅ backend/.env created. Please update with your configuration if needed."
fi

# Check if frontend .env exists
if [ ! -f frontend/.env ]; then
    echo "⚙️  Creating frontend/.env from .env.example..."
    cp frontend/.env.example frontend/.env
    echo "✅ frontend/.env created."
fi

# Build frontend for production
echo "🏗️  Building frontend for production..."
cd frontend
npm install
npm run build
cd ..

# Start backend in production mode
echo "🖥️  Starting backend in production mode..."
cd backend
source .env 2>/dev/null || true
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-reload --workers 2 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Start frontend in production mode
echo "🌐 Starting frontend in production mode..."
cd frontend
npm run start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ HireMeBahamas is running in Full Production Mode!"
echo "=================================================="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Database Admin: http://localhost:8081"
echo ""
echo "Database: PostgreSQL (localhost:5432)"
echo "Mode: PRODUCTION"
echo ""
echo "Press Ctrl+C to stop all services..."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    docker-compose stop postgres redis
    echo "✅ Services stopped."
}

trap cleanup EXIT

# Wait for user interrupt
wait
