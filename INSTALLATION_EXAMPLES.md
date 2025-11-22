# Installation Examples

This document provides real-world examples of installing HireMeBahamas with all dependencies.

## Example 1: Fresh Ubuntu 22.04 Server

```bash
# Start with a fresh Ubuntu 22.04 server
# Connect via SSH: ssh user@your-server

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install all dependencies in one command
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
    curl wget git

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Clone repository
cd /opt
sudo git clone https://github.com/cliffcho242/HireMeBahamas.git
cd HireMeBahamas
sudo chown -R $USER:$USER .

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
npm run build

# Setup PostgreSQL database
sudo -u postgres psql << SQL
CREATE DATABASE hiremebahamas;
CREATE USER hiremeuser WITH PASSWORD 'securepassword123';
GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremeuser;
SQL

# Configure environment
cd ..
cp .env.example .env
# Edit .env with your settings
nano .env

# Start services
sudo systemctl start postgresql redis-server nginx
sudo systemctl enable postgresql redis-server nginx

# Run application
gunicorn final_backend_postgresql:application --bind 0.0.0.0:8080 --workers 4

# Access at http://your-server-ip:8080
```

## Example 2: Docker Deployment

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/cliffcho242/HireMeBahamas.git
cd HireMeBahamas

# Configure environment
cp .env.example .env
nano .env

# Build and start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Access frontend at http://localhost:3000
# Access backend at http://localhost:8000
```

## Example 3: Railway Deployment

```bash
# Railway uses nixpacks.toml automatically
# Just push to Railway-connected repository

# 1. Connect GitHub repo to Railway
# 2. Railway will detect nixpacks.toml
# 3. Railway installs all 20 apt packages automatically:
#    - build-essential, gcc, g++, make
#    - postgresql-client, libpq-dev
#    - libssl-dev, libffi-dev
#    - libjpeg-dev, libpng-dev, libtiff-dev, libwebp-dev, zlib1g-dev
#    - libevent-dev
#    - libxml2-dev, libxslt1-dev
#    - redis-tools
#    - curl, wget, git

# 4. Set environment variables in Railway dashboard:
#    - SECRET_KEY
#    - JWT_SECRET_KEY
#    - DATABASE_URL (provided by Railway PostgreSQL plugin)
#    - REDIS_URL (provided by Railway Redis plugin)

# 5. Deploy!
git push origin main
# Railway automatically builds and deploys
```

## Example 4: DigitalOcean Droplet

```bash
# Create Ubuntu 22.04 droplet on DigitalOcean
# SSH into droplet

# Use the automated installation script
git clone https://github.com/cliffcho242/HireMeBahamas.git
cd HireMeBahamas

# Run automated installer
./scripts/install_all_dependencies.sh

# The script will:
# ✅ Detect OS (Ubuntu)
# ✅ Install all 48 system packages
# ✅ Install Python dependencies
# ✅ Install Node.js dependencies
# ✅ Configure PostgreSQL
# ✅ Configure Redis
# ✅ Start all services

# Setup environment
cp .env.example .env
nano .env

# Deploy with Gunicorn
gunicorn final_backend_postgresql:application \
    --bind 0.0.0.0:8080 \
    --workers 4 \
    --daemon

# Build and serve frontend
cd frontend
npm run build
sudo cp -r dist/* /var/www/html/

# Configure Nginx
sudo nano /etc/nginx/sites-available/hiremebahamas
# See INSTALL.md for nginx configuration

sudo ln -s /etc/nginx/sites-available/hiremebahamas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL with Let's Encrypt
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Example 5: Local Development (Ubuntu)

```bash
# Install only what you need for development
sudo apt-get update -y

# Essential development dependencies
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    postgresql postgresql-client libpq-dev \
    redis-server \
    nodejs npm \
    build-essential libssl-dev libffi-dev \
    git

# Clone and setup
git clone https://github.com/cliffcho242/HireMeBahamas.git
cd HireMeBahamas

# Python backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install

# Start PostgreSQL and Redis
sudo systemctl start postgresql redis-server

# Create dev database
sudo -u postgres psql -c "CREATE DATABASE hiremebahamas_dev;"

# Configure environment
cp .env.example .env
# Edit .env for development

# Run backend
python3 final_backend_postgresql.py

# In another terminal, run frontend
cd frontend
npm run dev
```

## Example 6: Minimal Testing Setup

```bash
# Just want to test if dependencies install correctly?

# Ubuntu/Debian one-liner
sudo apt-get update && sudo apt-get install -y \
    build-essential python3 python3-pip python3-dev \
    libpq-dev libssl-dev libffi-dev redis-tools \
    curl git

# Install Python packages
pip install Flask psycopg2-binary bcrypt cryptography redis

# Test imports
python3 << PYTHON
import flask
import psycopg2
import bcrypt
import cryptography
import redis
print("✅ All critical packages imported successfully!")
PYTHON
```

## Verification After Installation

```bash
# Check all services are running
sudo systemctl status postgresql redis-server nginx

# Check Python
python3 --version
pip list | grep -E "Flask|psycopg2|redis"

# Check Node.js
node --version
npm --version

# Check database
psql -h localhost -U hiremeuser -d hiremebahamas -c "SELECT version();"

# Check Redis
redis-cli ping

# Check build tools
gcc --version
make --version

# Test backend health
curl http://localhost:8080/health

# Test frontend
curl http://localhost:3000
```

## Troubleshooting Examples

### Problem: PostgreSQL won't start
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# View logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log

# Restart PostgreSQL
sudo systemctl restart postgresql

# If still failing, check disk space
df -h
```

### Problem: Python package build fails
```bash
# Install all build dependencies
sudo apt-get install -y build-essential python3-dev

# For psycopg2 issues
sudo apt-get install -y libpq-dev postgresql-client

# For cryptography issues
sudo apt-get install -y libssl-dev libffi-dev

# For Pillow issues
sudo apt-get install -y libjpeg-dev libpng-dev

# Try installing again
pip install -r requirements.txt
```

### Problem: Redis connection failed
```bash
# Start Redis
sudo systemctl start redis-server

# Test connection
redis-cli ping

# Check logs if not working
sudo tail -f /var/log/redis/redis-server.log
```

### Problem: npm install fails
```bash
# Update npm
sudo npm install -g npm@latest

# Clear cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

## Performance Tuning

### PostgreSQL
```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/*/main/postgresql.conf

# Recommended settings for production:
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
max_connections = 100
```

### Redis
```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Recommended settings:
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Nginx
```bash
# Edit Nginx config
sudo nano /etc/nginx/nginx.conf

# Recommended settings:
worker_processes auto;
worker_connections 1024;
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

## See Also

- [INSTALL.md](INSTALL.md) - Comprehensive installation guide
- [DEPENDENCIES_QUICK_REF.md](DEPENDENCIES_QUICK_REF.md) - Quick reference
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
- [README.md](README.md) - Project overview

---

**Note**: These examples assume you have appropriate permissions and network access. Adjust commands based on your specific environment.
