#!/bin/bash
#================================================================
# HireMeBahamas - Docker-based Installation Script
#================================================================
# This script provides a Docker-based installation and deployment
# option for HireMeBahamas using Docker and Docker Compose.
#
# Prerequisites:
#   - Docker
#   - Docker Compose
#
# Usage: ./scripts/docker_install_all.sh [options]
# Options:
#   --build-only    Only build containers, don't start them
#   --no-cache      Build without using cache
#   --help          Show this help message
#================================================================

set -e  # Exit on error

# Colors for output
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# Script variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_ONLY=false
NO_CACHE=""

# Logging functions
print_header() {
    echo -e "\n${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --help)
            head -n 17 "$0" | tail -n 12
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_status "Docker: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    if command -v docker-compose &> /dev/null; then
        print_status "Docker Compose: $(docker-compose --version)"
        COMPOSE_CMD="docker-compose"
    else
        print_status "Docker Compose: $(docker compose version)"
        COMPOSE_CMD="docker compose"
    fi
    
    # Check if Docker daemon is running
    if ! docker ps &> /dev/null; then
        print_error "Docker daemon is not running"
        echo "Please start Docker and try again"
        exit 1
    fi
    print_status "Docker daemon is running"
}

# Create Dockerfiles if they don't exist
create_dockerfiles() {
    print_header "Preparing Docker Configuration"
    
    # Backend Dockerfile
    if [ ! -f "$PROJECT_ROOT/backend/Dockerfile" ]; then
        print_info "Creating backend/Dockerfile..."
        cat > "$PROJECT_ROOT/backend/Dockerfile" << 'EOF'
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]
EOF
        print_status "Created backend/Dockerfile"
    else
        print_info "backend/Dockerfile already exists"
    fi
    
    # Frontend Dockerfile for development
    if [ ! -f "$PROJECT_ROOT/frontend/Dockerfile.dev" ]; then
        print_info "Creating frontend/Dockerfile.dev..."
        cat > "$PROJECT_ROOT/frontend/Dockerfile.dev" << 'EOF'
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
EOF
        print_status "Created frontend/Dockerfile.dev"
    else
        print_info "frontend/Dockerfile.dev already exists"
    fi
    
    # Frontend Dockerfile for production
    if [ ! -f "$PROJECT_ROOT/frontend/Dockerfile" ]; then
        print_info "Creating frontend/Dockerfile..."
        cat > "$PROJECT_ROOT/frontend/Dockerfile" << 'EOF'
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy application code
COPY . .

# Build application
RUN npm run build

# Production image
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF
        print_status "Created frontend/Dockerfile"
    else
        print_info "frontend/Dockerfile already exists"
    fi
    
    # Create nginx config for frontend
    if [ ! -f "$PROJECT_ROOT/frontend/nginx.conf" ]; then
        print_info "Creating frontend/nginx.conf..."
        cat > "$PROJECT_ROOT/frontend/nginx.conf" << 'EOF'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF
        print_status "Created frontend/nginx.conf"
    else
        print_info "frontend/nginx.conf already exists"
    fi
}

# Create environment files
create_env_files() {
    print_header "Creating Environment Files"
    
    if [ ! -f "$PROJECT_ROOT/.env.docker" ]; then
        print_info "Creating .env.docker file..."
        cat > "$PROJECT_ROOT/.env.docker" << 'EOF'
# Database Configuration
POSTGRES_DB=hiremebahamas
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Backend Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/hiremebahamas
SECRET_KEY=docker-secret-key-change-in-production
REDIS_URL=redis://redis:6379
ENVIRONMENT=development

# Frontend Configuration
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
EOF
        print_status "Created .env.docker file"
    else
        print_info ".env.docker already exists"
    fi
}

# Build Docker images
build_images() {
    print_header "Building Docker Images"
    
    cd "$PROJECT_ROOT"
    
    print_info "This may take several minutes..."
    
    if $COMPOSE_CMD build $NO_CACHE; then
        print_status "Docker images built successfully"
    else
        print_error "Failed to build Docker images"
        exit 1
    fi
}

# Start containers
start_containers() {
    if [ "$BUILD_ONLY" = true ]; then
        print_info "Build-only mode: Skipping container startup"
        return
    fi
    
    print_header "Starting Containers"
    
    cd "$PROJECT_ROOT"
    
    print_info "Starting services..."
    
    if $COMPOSE_CMD up -d; then
        print_status "Containers started successfully"
        
        # Wait for services to be healthy
        print_info "Waiting for services to be ready..."
        sleep 10
        
        # Check service status
        echo ""
        print_info "Container status:"
        $COMPOSE_CMD ps
    else
        print_error "Failed to start containers"
        exit 1
    fi
}

# Show service information
show_info() {
    print_header "Installation Complete!"
    
    echo -e "${GREEN}${BOLD}✅ HireMeBahamas is now running in Docker!${NC}\n"
    
    echo -e "${BOLD}Service URLs:${NC}"
    echo -e "  Frontend:  ${CYAN}http://localhost:3000${NC}"
    echo -e "  Backend:   ${CYAN}http://localhost:8000${NC}"
    echo -e "  API Docs:  ${CYAN}http://localhost:8000/docs${NC}"
    echo -e "  PostgreSQL: ${CYAN}localhost:5432${NC}"
    echo -e "  Redis:      ${CYAN}localhost:6379${NC}"
    
    echo -e "\n${BOLD}Docker Commands:${NC}"
    echo -e "  View logs:        ${CYAN}$COMPOSE_CMD logs -f${NC}"
    echo -e "  Stop services:    ${CYAN}$COMPOSE_CMD down${NC}"
    echo -e "  Restart services: ${CYAN}$COMPOSE_CMD restart${NC}"
    echo -e "  Rebuild:          ${CYAN}$COMPOSE_CMD up -d --build${NC}"
    
    echo -e "\n${BOLD}Database Access:${NC}"
    echo -e "  Connect to DB:    ${CYAN}$COMPOSE_CMD exec postgres psql -U postgres -d hiremebahamas${NC}"
    echo -e "  Run migrations:   ${CYAN}$COMPOSE_CMD exec backend python manage.py migrate${NC}"
    
    echo -e "\n${BOLD}Next Steps:${NC}"
    echo -e "  1. Visit ${CYAN}http://localhost:3000${NC} to access the application"
    echo -e "  2. Update environment variables in ${CYAN}.env.docker${NC} if needed"
    echo -e "  3. Check logs: ${CYAN}$COMPOSE_CMD logs -f${NC}"
    
    if [ "$BUILD_ONLY" = true ]; then
        echo -e "\n${YELLOW}Note: Containers were built but not started (--build-only mode)${NC}"
        echo -e "To start containers, run: ${CYAN}$COMPOSE_CMD up -d${NC}"
    fi
}

# Main execution
main() {
    print_header "HireMeBahamas - Docker Installation"
    
    echo -e "${BOLD}Installing HireMeBahamas using Docker${NC}\n"
    
    check_prerequisites
    create_dockerfiles
    create_env_files
    build_images
    start_containers
    show_info
    
    echo -e "\n${GREEN}${BOLD}Docker installation completed successfully!${NC}\n"
}

# Handle script interruption
trap 'echo -e "\n${RED}Installation interrupted${NC}"; exit 130' INT TERM

# Run main function
main
