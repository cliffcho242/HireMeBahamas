#!/bin/bash

# Docker Build Optimization Script
# This script builds Docker images with BuildKit enabled for faster builds and better caching

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Docker BuildKit Optimization Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

echo -e "${GREEN}✓ BuildKit enabled${NC}"
echo ""

# Function to build and time
build_image() {
    local name=$1
    local context=$2
    local dockerfile=$3
    
    echo -e "${YELLOW}Building ${name}...${NC}"
    start_time=$(date +%s)
    
    docker build \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        -f "${context}/${dockerfile}" \
        -t "${name}:latest" \
        "${context}"
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    minutes=$((duration / 60))
    seconds=$((duration % 60))
    
    echo -e "${GREEN}✓ ${name} built successfully in ${minutes}m ${seconds}s${NC}"
    echo ""
}

# Build backend
if [ "$1" == "backend" ] || [ "$1" == "all" ] || [ -z "$1" ]; then
    build_image "hiremebahamas-backend" "./backend" "Dockerfile"
fi

# Build frontend
if [ "$1" == "frontend" ] || [ "$1" == "all" ] || [ -z "$1" ]; then
    build_image "hiremebahamas-frontend" "./frontend" "Dockerfile"
fi

# Build with docker-compose
if [ "$1" == "compose" ]; then
    echo -e "${YELLOW}Building with docker-compose...${NC}"
    start_time=$(date +%s)
    
    docker-compose build
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    minutes=$((duration / 60))
    seconds=$((duration % 60))
    
    echo -e "${GREEN}✓ All services built successfully in ${minutes}m ${seconds}s${NC}"
    echo ""
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Build completed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Usage:"
echo -e "  ${YELLOW}./scripts/docker-build-optimized.sh${NC}           # Build all images"
echo -e "  ${YELLOW}./scripts/docker-build-optimized.sh backend${NC}   # Build backend only"
echo -e "  ${YELLOW}./scripts/docker-build-optimized.sh frontend${NC}  # Build frontend only"
echo -e "  ${YELLOW}./scripts/docker-build-optimized.sh compose${NC}   # Build with docker-compose"
echo ""
