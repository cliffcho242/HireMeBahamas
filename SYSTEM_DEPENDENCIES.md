# System Dependencies Installation Guide

This document provides a comprehensive list of all system dependencies for HireMeBahamas, including both **required** and **optional** dependencies.

## Dependency Categories

### ✅ Required (Critical)
These dependencies are essential for the application to function:
- Build tools (gcc, g++, make, etc.)
- Python environment
- PostgreSQL database
- SSL/TLS libraries
- Basic image processing libraries

### ⚠️ Optional (Not Critical)
These dependencies enhance functionality but are not required for basic operation:
- **redis-server** - Provides caching and performance improvements
- **libvips-dev** - Advanced image optimization
- **libheif-dev** - HEIF/HEIC format support
- **libavif-dev** - AVIF format support

## Quick Install (Ubuntu/Debian)

For a quick one-command installation of all core dependencies:

```bash
sudo apt-get update && \
sudo apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    postgresql \
    postgresql-client \
    libpq-dev \
    redis-server \
    redis-tools \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libevent-dev \
    libxml2-dev \
    libxslt1-dev \
    nginx \
    curl \
    wget \
    git
```

## Detailed Dependency Breakdown

### 1. Build Tools

Essential for compiling Python packages and native extensions:

```bash
sudo apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config
```

**Required for:**
- Compiling Python packages like `psycopg2`, `bcrypt`, `cryptography`
- Building native extensions for performance-critical packages

### 2. Python Environment

Python 3.11+ with development headers and virtual environment support:

```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv
```

**Required for:**
- Running the Flask/FastAPI backend
- Installing Python packages with pip
- Creating isolated virtual environments

### 3. Database (PostgreSQL)

PostgreSQL database for production data storage:

```bash
sudo apt-get install -y \
    postgresql \
    postgresql-client \
    libpq-dev
```

**Required for:**
- Storing user accounts, posts, likes, comments
- Production-grade data persistence
- The `psycopg2-binary` Python package

**Configuration:**
```bash
# Start PostgreSQL service
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb hiremebahamas
```

### 4. Redis (Optional - Not Critical)

⚠️ **Optional**: Redis is not required for basic operation but provides enhanced performance features.

Redis for caching, session management, and real-time features:

```bash
sudo apt-get install -y \
    redis-server \
    redis-tools
```

**Used for (when available):**
- Session storage
- Rate limiting
- WebSocket support
- Background job queues (Celery)

**Configuration (if installed):**
```bash
# Start Redis service
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

**Note**: Application will function without Redis, but some features may have reduced performance.

### 5. Cryptography & Security

Libraries for encryption, SSL/TLS, and password hashing:

```bash
sudo apt-get install -y \
    libssl-dev \
    libffi-dev
```

**Required for:**
- JWT token generation (`PyJWT`)
- Password hashing (`bcrypt`)
- Secure connections (`cryptography`)
- HTTPS support

### 6. Image Processing

Libraries for handling user avatars, post images, and stories:

#### Required Image Libraries
```bash
sudo apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev
```

**Required for:**
- Uploading and processing profile pictures
- Handling post images
- Processing story media
- Image optimization and format conversion

#### Optional Image Optimization Libraries

⚠️ **Optional**: These libraries provide enhanced image format support but are not required for basic operation.

```bash
# Optional image optimization and modern format support
sudo apt-get install -y \
    libvips-dev \
    libheif-dev \
    libavif-dev || echo "Optional image libraries not available on this system"
```

**Provides (when available):**
- libvips-dev: Advanced image processing and optimization
- libheif-dev: HEIF/HEIC format support (Apple Photos format)
- libavif-dev: AVIF format support (modern web image format)

### 7. Additional Libraries

Other dependencies for various features:

```bash
sudo apt-get install -y \
    libevent-dev \
    libxml2-dev \
    libxslt1-dev
```

**Required for:**
- WebSocket support (`gevent`)
- XML processing
- Web scraping capabilities

### 8. Web Server (Nginx)

Production web server for serving the application:

```bash
sudo apt-get install -y nginx
```

**Required for:**
- Reverse proxy to the backend API
- Serving static frontend files
- SSL/TLS termination
- Load balancing

### 9. Utilities

Essential development and deployment tools:

```bash
sudo apt-get install -y \
    curl \
    wget \
    git
```

**Required for:**
- Installing Node.js
- Downloading resources
- Version control

### 10. Node.js (for Frontend)

JavaScript runtime for the React frontend:

```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Required for:**
- Building the React frontend
- Running the development server
- Managing frontend dependencies with npm

## Python Package Dependencies

After installing system dependencies, install Python packages:

```bash
pip install -r requirements.txt
```

Key packages include:
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **PyJWT**: JWT token authentication
- **bcrypt**: Password hashing
- **psycopg2-binary**: PostgreSQL adapter
- **redis**: Redis client
- **flask-socketio**: WebSocket support
- **gunicorn**: Production WSGI server
- **sentry-sdk**: Error tracking

## Frontend Dependencies

Install Node.js packages for the React frontend:

```bash
cd frontend
npm install
```

## Verification

After installation, verify all dependencies are working:

```bash
# Check Python
python3 --version

# Check pip
pip3 --version

# Check Node.js
node --version
npm --version

# Check PostgreSQL
psql --version

# Check Redis
redis-cli ping

# Check Git
git --version

# Run dependency test script
python3 test_auth_dependencies.py
```

## Automated Installation Scripts

For convenience, use the provided installation scripts:

### Linux/macOS:
```bash
./install_all_dependencies.sh
```

### Windows:
```cmd
scripts\install_all_dependencies.bat
```

### Docker:
```bash
./scripts/docker_install_all.sh
```

## Troubleshooting

### Build Errors
If you encounter build errors when installing Python packages:
```bash
# Ensure build tools are installed
sudo apt-get install -y build-essential python3-dev

# Update pip
pip3 install --upgrade pip setuptools wheel
```

### PostgreSQL Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Restart if needed
sudo systemctl restart postgresql
```

### Redis Connection Issues
```bash
# Check Redis is running
sudo systemctl status redis-server

# Test connection
redis-cli ping
```

## Platform-Specific Notes

### Render/Render
When deploying to Render or Render, system dependencies are handled automatically through:
- Docker base images (recommended)
- Nixpacks build system
- Platform-provided buildpacks

### Local Development
For local development on SQLite (no PostgreSQL required):
```bash
# Only install Python, Node.js, and Redis
# PostgreSQL can be skipped as SQLite is used by default
```

## Posts Feature Requirements

The following dependencies are **essential** for the posts feature to work correctly:

1. **PostgreSQL/SQLite**: Stores posts, likes, comments
2. **JWT Authentication**: Ensures only authenticated users can create posts
3. **bcrypt**: Secures user passwords
4. **Flask-CORS**: Allows frontend to communicate with backend
5. **Redis**: (Optional) For caching posts and improving performance

## Related Documentation

- [INSTALL.md](./INSTALL.md) - Complete installation guide
- [DEPENDENCIES_QUICK_REF.md](./DEPENDENCIES_QUICK_REF.md) - Quick reference
- [README.md](./README.md) - Main project documentation
- [AUTO_DEPLOY_SETUP.md](./AUTO_DEPLOY_SETUP.md) - Automated deployment guide

---

**Last Updated**: November 2025
