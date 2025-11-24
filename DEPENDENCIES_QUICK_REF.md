# Quick Reference: System Dependencies for Production

This document provides a quick reference for all system packages needed to run HireMeBahamas in production.

## Dependency Status

✅ **Required** - Essential for basic operation
⚠️ **Optional** - Enhances functionality but not critical

## One-Command Installation (Ubuntu/Debian)

```bash
# Complete installation command - copy and paste to install everything
sudo apt-get update -y && \
sudo apt-get install -y \
    build-essential gcc g++ make pkg-config \
    python3 python3-pip python3-dev python3-venv python3-setuptools python3-wheel \
    postgresql postgresql-contrib postgresql-client libpq-dev \
    libssl-dev libffi-dev ca-certificates \
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev libopenjp2-7-dev zlib1g-dev \
    libevent-dev \
    libxml2-dev libxslt1-dev \
    nginx \
    curl wget git htop vim unzip

# Optional packages (not critical)
sudo apt-get install -y redis-server redis-tools || echo "Redis not installed (optional)"
```

## Package Categories

### Build Tools (required for Python package compilation)
```bash
sudo apt-get install -y build-essential gcc g++ make pkg-config
```

### Python Runtime & Development
```bash
sudo apt-get install -y \
    python3 python3-pip python3-dev python3-venv \
    python3-setuptools python3-wheel
```

### PostgreSQL Database (for psycopg2-binary)
```bash
sudo apt-get install -y \
    postgresql postgresql-contrib postgresql-client libpq-dev
```

### Redis ⚠️ (Optional - for caching, sessions, Celery)
```bash
sudo apt-get install -y redis-server redis-tools
```

**Note**: Redis is optional and not required for basic operation.

### SSL/TLS Libraries (for cryptography package)
```bash
sudo apt-get install -y libssl-dev libffi-dev ca-certificates
```

### Image Processing Libraries (for Pillow)
```bash
sudo apt-get install -y \
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev \
    libopenjp2-7-dev zlib1g-dev
```

### Event Library (for gevent)
```bash
sudo apt-get install -y libevent-dev
```

### XML Processing Libraries
```bash
sudo apt-get install -y libxml2-dev libxslt1-dev
```

### Nginx Web Server
```bash
sudo apt-get install -y nginx
```

### Node.js & npm (for frontend)
```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Utilities
```bash
sudo apt-get install -y curl wget git htop vim unzip
```

## One-Command Installation (CentOS/RHEL)

```bash
# Complete installation command for RHEL-based systems
sudo yum update -y && \
sudo yum install -y epel-release && \
sudo yum install -y \
    gcc gcc-c++ make pkgconfig \
    python3 python3-pip python3-devel python3-setuptools python3-wheel \
    postgresql postgresql-server postgresql-devel \
    openssl-devel libffi-devel ca-certificates \
    libjpeg-devel libpng-devel libtiff-devel libwebp-devel zlib-devel \
    libevent-devel \
    libxml2-devel libxslt-devel \
    nginx \
    curl wget git htop vim

# Optional packages (not critical)
sudo yum install -y redis || echo "Redis not installed (optional)"
```

## Docker Alternative

If you prefer Docker, all dependencies are pre-configured in:
- `backend/Dockerfile` - Python backend with all system packages
- `frontend/Dockerfile` - Node.js frontend with Alpine Linux packages
- `docker-compose.yml` - Complete multi-container setup

```bash
# Build and run with Docker
docker-compose up -d --build
```

## Verification Commands

```bash
# Check Python
python3 --version

# Check Node.js
node --version

# Check PostgreSQL
psql --version
sudo systemctl status postgresql

# Check Redis (optional)
redis-cli ping || echo "Redis not installed (optional)"

# Check Nginx
nginx -v
sudo systemctl status nginx

# Check build tools
gcc --version
make --version
```

## Python Dependencies Requiring System Packages

| Python Package | System Dependencies | Purpose |
|---------------|-------------------|---------|
| psycopg2-binary | libpq-dev, postgresql-client | PostgreSQL database adapter |
| bcrypt | build-essential, python3-dev | Password hashing |
| cryptography | libssl-dev, libffi-dev | Encryption and SSL/TLS |
| Pillow | libjpeg-dev, libpng-dev, libtiff-dev, libwebp-dev, zlib1g-dev | Image processing |
| gevent | libevent-dev | Asynchronous I/O |
| lxml | libxml2-dev, libxslt1-dev | XML/HTML processing |
| redis ⚠️ | redis-server (optional) | Redis client |
| celery ⚠️ | redis-server (optional) | Task queue (uses Redis) |

## Service Management

```bash
# Start all required services
sudo systemctl start postgresql nginx

# Start optional services
sudo systemctl start redis-server || echo "Redis not installed (optional)"

# Enable services on boot
sudo systemctl enable postgresql nginx
sudo systemctl enable redis-server || echo "Redis not configured (optional)"

# Check service status
sudo systemctl status postgresql
sudo systemctl status redis-server  # Optional
sudo systemctl status nginx
```

## Post-Installation

After installing system dependencies:

```bash
# 1. Install Python dependencies
cd /path/to/HireMeBahamas
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Install Node.js dependencies
cd frontend
npm install

# 3. Setup database
sudo -u postgres psql -c "CREATE DATABASE hiremebahamas;"
sudo -u postgres psql -c "CREATE USER hiremeuser WITH PASSWORD 'yourpassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremeuser;"

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run migrations
python3 manage.py migrate  # Or your migration command

# 6. Start application
# Backend: gunicorn or uvicorn
# Frontend: npm run build && nginx
```

## Troubleshooting

### Package Not Found
```bash
# Update package lists
sudo apt-get update
```

### Build Failures
```bash
# Ensure all build dependencies installed
sudo apt-get install -y build-essential python3-dev
```

### PostgreSQL Connection Issues
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Redis Connection Issues
```bash
# Check if Redis is running
sudo systemctl status redis-server
redis-cli ping  # Should return "PONG"
```

## Minimal Installation (Development Only)

If you only need to run the app in development mode:

```bash
# Minimal dependencies for development
sudo apt-get update -y && \
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    postgresql postgresql-client libpq-dev \
    redis-server redis-tools \
    nodejs npm \
    git curl
```

## See Also

- [INSTALL.md](INSTALL.md) - Comprehensive installation guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment instructions
- [README.md](README.md) - Project overview and quick start
- [DOCKER_SECURITY.md](DOCKER_SECURITY.md) - Docker security best practices

---

**Last Updated**: 2025-11-22  
**Tested On**: Ubuntu 20.04, Ubuntu 22.04, Debian 11, CentOS 8, RHEL 8
