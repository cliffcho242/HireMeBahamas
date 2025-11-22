# Docker Base Images

This directory contains Dockerfiles for pre-built base images used by the HireMeBahamas application.

## Purpose

These base images include all system-level dependencies pre-installed, which:
- Eliminates the need to run `apt-get` or `apk` during every build
- Prevents deployment timeouts caused by slow package installations
- Speeds up builds by 5-10x
- Ensures consistent environments across all deployments

## Files

### `Dockerfile.base-backend`
Base image for the backend application.

**Base**: `python:3.11-slim`

**Includes**:
- Build tools (gcc, g++, make)
- PostgreSQL libraries (libpq-dev, postgresql-client)
- Cryptography libraries (libssl-dev, libffi-dev)
- Image processing libraries (libjpeg-dev, libpng-dev, etc.)
- Other dependencies (redis-tools, curl, wget, git)

**Published to**: `ghcr.io/cliffcho242/hiremebahamas-base-backend:latest`

### `Dockerfile.base-frontend`
Base image for the frontend application builder stage.

**Base**: `node:18-alpine`

**Includes**:
- Build tools (python3, make, g++)
- Version control (git)
- HTTP tools (curl)
- SSL/TLS support (ca-certificates)

**Published to**: `ghcr.io/cliffcho242/hiremebahamas-base-frontend:latest`

## Building

### Via GitHub Actions (Recommended)
Base images are automatically built and published when:
1. Changes are pushed to `main` branch affecting files in this directory
2. Workflow is manually triggered via GitHub Actions UI
3. Pull requests are created (builds but doesn't push)

See `.github/workflows/build-base-images.yml` for the workflow configuration.

### Locally
To build and push images manually:

```bash
# From the repository root
./scripts/build-base-images.sh
```

Or build individually:

```bash
# Backend base image
docker build -t ghcr.io/cliffcho242/hiremebahamas-base-backend:latest \
  -f Dockerfile.base-backend .

# Frontend base image
docker build -t ghcr.io/cliffcho242/hiremebahamas-base-frontend:latest \
  -f Dockerfile.base-frontend .
```

## Usage

The application Dockerfiles reference these base images:

**backend/Dockerfile**:
```dockerfile
FROM ghcr.io/cliffcho242/hiremebahamas-base-backend:latest
# ... application-specific steps
```

**frontend/Dockerfile**:
```dockerfile
FROM ghcr.io/cliffcho242/hiremebahamas-base-frontend:latest AS builder
# ... application-specific steps
```

## When to Update

Rebuild base images when:
- Adding or removing system-level dependencies
- Updating base image versions (Python, Node.js)
- Applying security patches
- Optimizing image size

## Making Images Public

For Railway/Render to pull images without authentication:

1. Go to https://github.com/cliffcho242?tab=packages
2. Select the package
3. Go to "Package settings"
4. Under "Danger Zone", click "Change visibility"
5. Select "Public"

## Documentation

For more details, see [DOCKER_BASE_IMAGES.md](../../DOCKER_BASE_IMAGES.md) in the repository root.
