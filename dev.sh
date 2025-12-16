#!/bin/bash

# Simple development server startup script
# ⚠️ WARNING: This script is for LOCAL DEVELOPMENT ONLY
# NEVER use --reload in production (Render, Railway, etc.)
# Auto-reload doubles memory usage and causes SIGTERM errors
echo "Starting HireBahamas Development Servers..."

# Function to handle cleanup
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server (with --reload for LOCAL DEVELOPMENT ONLY)
echo "Starting backend server (local development with auto-reload)..."
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Development servers started!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for processes
wait