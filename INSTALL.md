# HireMeBahamas - Production Installation Guide

This guide provides comprehensive instructions for installing all system dependencies required to run HireMeBahamas in full production mode.

## Table of Contents
- [Docker Deployment (Recommended)](#docker-deployment-recommended)
- [System Requirements](#system-requirements)
- [Ubuntu/Debian Installation](#ubuntudebian-installation)
- [CentOS/RHEL Installation](#centosrhel-installation)
- [Docker Installation](#docker-installation)
- [Verification](#verification)

---

## Docker Deployment (Recommended)

🚀 **For production deployments, we strongly recommend using Docker with our pre-built base images.**

### Why Docker with Base Images?

- ✅ **5-10x Faster Deployments**: System dependencies are pre-installed
- ✅ **No Build Timeouts**: Eliminates issues with long apt-get/apk operations
- ✅ **Consistent Environment**: Same setup across all deployments
- ✅ **Easy Updates**: Pull latest base images instead of rebuilding dependencies

### Quick Docker Setup

```bash
# 1. Pull and run using Docker Compose
docker-compose up -d

# 2. Or build application images (uses pre-built base images)
docker build -t hiremebahamas-backend ./backend
docker build -t hiremebahamas-frontend ./frontend
```

The Dockerfiles automatically use optimized base images from GitHub Container Registry:
- Backend: `ghcr.io/cliffcho242/hiremebahamas-base-backend:latest`
- Frontend: `ghcr.io/cliffcho242/hiremebahamas-base-frontend:latest`

📖 **For detailed information about Docker base images, see [DOCKER_BASE_IMAGES.md](./DOCKER_BASE_IMAGES.md)**

---

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+, Debian 11+, CentOS 8+, or RHEL 8+
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 20GB free space
- **Network**: Internet connectivity for package installation

### Software Requirements
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Nginx (for production web server)

---

## Ubuntu/Debian Installation

### Step 1: Update System Packages
```bash
# Update package lists and upgrade existing packages
sudo apt-get update -y
sudo apt-get upgrade -y
```

### Step 2: Install Build Tools
Required for compiling Python packages from source (psycopg2, bcrypt, cryptography, etc.)

```bash
sudo apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config
```

### Step 3: Install Python and Dependencies
```bash
# Install Python 3.11+ and development tools
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-setuptools \
    python3-wheel
```

### Step 4: Install PostgreSQL
Required for the database backend (psycopg2-binary package)

```bash
# Install PostgreSQL database server and client
sudo apt-get install -y \
    postgresql \
    postgresql-contrib \
    postgresql-client \
    libpq-dev

# Start and enable PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE hiremebahamas;"
sudo -u postgres psql -c "CREATE USER hiremeuser WITH PASSWORD 'changeme';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremeuser;"
```

### Step 5: Install Redis
Required for caching, session management, and Celery task queue

```bash
# Install Redis server and tools
sudo apt-get install -y \
    redis-server \
    redis-tools

# Start and enable Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping  # Should return "PONG"
```

### Step 6: Install SSL/TLS Libraries
Required for cryptography package and secure connections

```bash
sudo apt-get install -y \
    libssl-dev \
    libffi-dev \
    ca-certificates
```

### Step 7: Install Image Processing Libraries
Required for Pillow package (if handling image uploads)

```bash
sudo apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    zlib1g-dev
```

### Step 8: Install Event Libraries
Required for gevent package (asynchronous I/O)

```bash
sudo apt-get install -y \
    libevent-dev
```

### Step 9: Install XML Processing Libraries
Required for various Python packages that parse XML

```bash
sudo apt-get install -y \
    libxml2-dev \
    libxslt1-dev
```

### Step 10: Install Node.js and npm
Required for the React frontend

```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should be v18.x.x
npm --version   # Should be 9.x.x or higher
```

### Step 11: Install Nginx (Production Web Server)
```bash
# Install Nginx web server
sudo apt-get install -y nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 12: Install Additional Utilities
```bash
# Install useful utilities
sudo apt-get install -y \
    curl \
    wget \
    git \
    htop \
    vim \
    unzip
```

### Complete One-Command Installation (Ubuntu/Debian)
Copy and paste this single command to install everything:

```bash
# Update system
sudo apt-get update -y && sudo apt-get upgrade -y && \

# Install all dependencies
sudo apt-get install -y \
    build-essential gcc g++ make pkg-config \
    python3 python3-pip python3-dev python3-venv python3-setuptools python3-wheel \
    postgresql postgresql-contrib postgresql-client libpq-dev \
    redis-server redis-tools \
    libssl-dev libffi-dev ca-certificates \
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev libopenjp2-7-dev zlib1g-dev \
    libevent-dev \
    libxml2-dev libxslt1-dev \
    nginx \
    curl wget git htop vim unzip && \

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && \
sudo apt-get install -y nodejs && \

# Start services
sudo systemctl start postgresql redis-server nginx && \
sudo systemctl enable postgresql redis-server nginx && \

echo "✅ All dependencies installed successfully!"
```

---

## CentOS/RHEL Installation

### Complete One-Command Installation (CentOS/RHEL)
```bash
# Update system
sudo yum update -y && \

# Install EPEL repository (for Redis)
sudo yum install -y epel-release && \

# Install all dependencies
sudo yum install -y \
    gcc gcc-c++ make pkgconfig \
    python3 python3-pip python3-devel \
    postgresql postgresql-server postgresql-devel \
    redis \
    openssl-devel libffi-devel \
    libjpeg-devel libpng-devel libtiff-devel libwebp-devel zlib-devel \
    libevent-devel \
    libxml2-devel libxslt-devel \
    nginx \
    curl wget git vim && \

# Initialize PostgreSQL (first time only)
sudo postgresql-setup --initdb && \

# Install Node.js 18.x
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - && \
sudo yum install -y nodejs && \

# Start services
sudo systemctl start postgresql redis nginx && \
sudo systemctl enable postgresql redis nginx && \

echo "✅ All dependencies installed successfully!"
```

---

## Docker Installation

If you prefer using Docker, the Dockerfiles already include all necessary system dependencies.

### Build and Run with Docker Compose
```bash
# Install Docker and Docker Compose first
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps
```

### Backend Dockerfile
The backend Dockerfile (`backend/Dockerfile`) includes:
- Build tools: build-essential, gcc, g++, make
- PostgreSQL: postgresql-client, libpq-dev
- SSL/TLS: libssl-dev, libffi-dev
- Image processing: libjpeg-dev, libpng-dev, libtiff-dev, libwebp-dev, libopenjp2-7-dev, zlib1g-dev
- Event library: libevent-dev
- XML processing: libxml2-dev, libxslt1-dev
- Redis tools: redis-tools
- Utilities: curl, wget, git

### Frontend Dockerfile
The frontend Dockerfile (`frontend/Dockerfile`) uses Alpine Linux with apk:
- Build tools: python3, make, g++
- Git: for npm packages from git repositories
- Nginx: for serving static files in production
- Security: ca-certificates, curl for health checks

---

## Verification

### Verify System Dependencies
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check Node.js version
node --version  # Should be 18.x.x

# Check PostgreSQL
psql --version  # Should be 13+
sudo systemctl status postgresql  # Should be active (running)

# Check Redis
redis-cli --version  # Should be 6+
redis-cli ping  # Should return "PONG"

# Check Nginx
nginx -v  # Should show version
sudo systemctl status nginx  # Should be active (running)

# Check build tools
gcc --version
make --version
```

### Install Python Dependencies
```bash
cd /path/to/HireMeBahamas

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Verify critical packages
python3 -c "import psycopg2; print('✅ psycopg2 works')"
python3 -c "import bcrypt; print('✅ bcrypt works')"
python3 -c "import cryptography; print('✅ cryptography works')"
python3 -c "import redis; print('✅ redis works')"
```

### Install Node.js Dependencies
```bash
cd /path/to/HireMeBahamas/frontend

# Install npm packages
npm install

# Build frontend (test)
npm run build

# Should create a dist/ directory
ls -la dist/
```

### Test Database Connection
```bash
# Test PostgreSQL connection
psql -h localhost -U hiremeuser -d hiremebahamas -c "SELECT version();"

# Set environment variable
export DATABASE_URL="postgresql://hiremeuser:changeme@localhost/hiremebahamas"
```

### Test Redis Connection
```bash
# Test Redis connection
redis-cli ping  # Should return "PONG"

# Test Redis write/read
redis-cli SET test "Hello"
redis-cli GET test  # Should return "Hello"
```

### Run Application
```bash
# Start backend (development)
cd /path/to/HireMeBahamas
python3 final_backend_postgresql.py

# Start frontend (development)
cd /path/to/HireMeBahamas/frontend
npm run dev
```

---

## Production Deployment with Gunicorn

### Install Gunicorn
```bash
pip install gunicorn
```

### Run Backend with Gunicorn
```bash
# Basic production start
gunicorn final_backend_postgresql:application --bind 0.0.0.0:8080 --workers 4 --timeout 120 --access-logfile - --error-logfile -

# With systemd service
sudo nano /etc/systemd/system/hiremebahamas.service
```

Example systemd service file:
```ini
[Unit]
Description=HireMeBahamas Backend
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/hiremebahamas
Environment="DATABASE_URL=postgresql://hiremeuser:changeme@localhost/hiremebahamas"
Environment="REDIS_URL=redis://localhost:6379"
ExecStart=/var/www/hiremebahamas/venv/bin/gunicorn \
    final_backend_postgresql:application \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/hiremebahamas/access.log \
    --error-logfile /var/log/hiremebahamas/error.log
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Nginx Configuration for Production

Create `/etc/nginx/sites-available/hiremebahamas`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend static files
    location / {
        root /var/www/hiremebahamas/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/hiremebahamas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## SSL/TLS Setup with Let's Encrypt

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain and install certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured by certbot)
sudo certbot renew --dry-run
```

---

## Troubleshooting

### Common Issues

#### PostgreSQL Connection Failed
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log

# Test connection
psql -h localhost -U hiremeuser -d hiremebahamas
```

#### Redis Connection Failed
```bash
# Check Redis is running
sudo systemctl status redis-server

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log

# Test connection
redis-cli ping
```

#### Python Package Build Failures
```bash
# Ensure all build dependencies are installed
sudo apt-get install -y build-essential python3-dev

# For psycopg2 issues
sudo apt-get install -y libpq-dev

# For cryptography issues
sudo apt-get install -y libssl-dev libffi-dev

# For Pillow issues
sudo apt-get install -y libjpeg-dev libpng-dev
```

#### Node.js Build Failures
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Security Considerations

### Production Checklist
- [ ] Change default PostgreSQL passwords
- [ ] Configure firewall (ufw/firewalld) to allow only necessary ports
- [ ] Enable HTTPS with SSL/TLS certificates
- [ ] Set strong SECRET_KEY and JWT_SECRET_KEY in environment variables
- [ ] Disable debug mode in production
- [ ] Configure rate limiting
- [ ] Set up log rotation
- [ ] Enable PostgreSQL connection encryption
- [ ] Configure Redis authentication
- [ ] Regular security updates: `apt-get update && apt-get upgrade`

### Firewall Configuration
```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## Additional Resources

- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [HireMeBahamas Repository](https://github.com/cliffcho242/HireMeBahamas)

---

## Support

For issues or questions:
1. Check the [README.md](README.md)
2. Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
3. Open an issue on GitHub
4. Contact the development team

---

**Last Updated**: 2025-11-22
