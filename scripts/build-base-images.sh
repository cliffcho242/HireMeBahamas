#!/bin/bash

# Build and push Docker base images for HireMeBahamas
# This script builds the base images locally and pushes them to GitHub Container Registry
# Usage: ./scripts/build-base-images.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}HireMeBahamas Base Image Builder${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if user is logged into GitHub Container Registry
echo -e "${YELLOW}Checking Docker login status...${NC}"
if ! docker system info 2>&1 | grep -q "Username"; then
    echo -e "${RED}Warning: You may not be logged into Docker${NC}"
    echo "To log in to GitHub Container Registry:"
    echo "  docker login ghcr.io -u YOUR_GITHUB_USERNAME"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Configuration
REGISTRY="ghcr.io"
REPO_OWNER="cliffcho242"
BACKEND_IMAGE="${REGISTRY}/${REPO_OWNER}/hiremebahamas-base-backend"
FRONTEND_IMAGE="${REGISTRY}/${REPO_OWNER}/hiremebahamas-base-frontend"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="${PROJECT_ROOT}/docker/base-images"

# Check if Dockerfiles exist
if [ ! -f "${DOCKER_DIR}/Dockerfile.base-backend" ]; then
    echo -e "${RED}Error: Backend Dockerfile not found at ${DOCKER_DIR}/Dockerfile.base-backend${NC}"
    exit 1
fi

if [ ! -f "${DOCKER_DIR}/Dockerfile.base-frontend" ]; then
    echo -e "${RED}Error: Frontend Dockerfile not found at ${DOCKER_DIR}/Dockerfile.base-frontend${NC}"
    exit 1
fi

# Function to build and push an image
build_and_push() {
    local dockerfile=$1
    local image_name=$2
    local description=$3

    echo ""
    echo -e "${YELLOW}Building ${description}...${NC}"
    echo "Dockerfile: ${dockerfile}"
    echo "Image: ${image_name}:latest"
    echo ""

    # Build the image
    if docker build -t "${image_name}:latest" -f "${dockerfile}" "${DOCKER_DIR}"; then
        echo -e "${GREEN}✓ Successfully built ${description}${NC}"
    else
        echo -e "${RED}✗ Failed to build ${description}${NC}"
        return 1
    fi

    # Push the image
    echo ""
    echo -e "${YELLOW}Pushing ${description} to registry...${NC}"
    if docker push "${image_name}:latest"; then
        echo -e "${GREEN}✓ Successfully pushed ${description}${NC}"
    else
        echo -e "${RED}✗ Failed to push ${description}${NC}"
        return 1
    fi
}

# Build and push backend base image
build_and_push \
    "${DOCKER_DIR}/Dockerfile.base-backend" \
    "${BACKEND_IMAGE}" \
    "Backend Base Image"

# Build and push frontend base image
build_and_push \
    "${DOCKER_DIR}/Dockerfile.base-frontend" \
    "${FRONTEND_IMAGE}" \
    "Frontend Base Image"

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Base images are now available at:"
echo "  - ${BACKEND_IMAGE}:latest"
echo "  - ${FRONTEND_IMAGE}:latest"
echo ""
echo "These images can now be used in:"
echo "  - backend/Dockerfile"
echo "  - frontend/Dockerfile"
echo ""
echo "To make images public (if needed):"
echo "  1. Go to https://github.com/${REPO_OWNER}?tab=packages"
echo "  2. Find the package"
echo "  3. Click 'Package settings'"
echo "  4. Scroll to 'Danger Zone'"
echo "  5. Click 'Change visibility' → 'Public'"
echo ""
