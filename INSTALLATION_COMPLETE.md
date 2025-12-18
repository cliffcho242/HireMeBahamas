# HireMeBahamas - Complete Installation Guide

## Overview

This guide provides comprehensive instructions for installing all dependencies for the HireMeBahamas platform with **ZERO manual intervention**. We support multiple installation methods across different platforms.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Linux/macOS Installation](#linuxmacos-installation)
  - [Windows Installation](#windows-installation)
  - [Docker Installation](#docker-installation)
- [What Gets Installed](#what-gets-installed)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Platform-Specific Notes](#platform-specific-notes)
- [Advanced Usage](#advanced-usage)
- [Environment Configuration](#environment-configuration)
- [Next Steps](#next-steps)

---

## Quick Start

Choose your platform and run the appropriate command:

### Linux/macOS (One Command)
```bash
./scripts/install_all_dependencies.sh
```

### Windows (One Command)
```cmd
scripts\install_all_dependencies.bat
```

### Docker (One Command)
```bash
./scripts/docker_install_all.sh
```

That's it! The scripts will:
- ✅ Detect your operating system
- ✅ Install all system dependencies
- ✅ Install all Python packages
- ✅ Install all Node.js packages
- ✅ Configure services (PostgreSQL, Redis)
- ✅ Create environment files
- ✅ Verify the installation

---

## Prerequisites

### All Platforms
- **Internet connection** (for downloading packages)
- **Disk space**: At least 5GB free
- **Time**: 10-30 minutes depending on your internet speed

### Linux/macOS
- **sudo/admin privileges** (for system package installation)
- **Operating System**:
  - Ubuntu 20.04+ / Debian 10+
  - CentOS 8+ / RHEL 8+
  - macOS 11+ (Big Sur or later)

### Windows
- **Administrator privileges**
- **Windows 10 or later**
- **PowerShell 5.1 or later** (pre-installed on Windows 10+)

### Docker
- **Docker** 20.10+
- **Docker Compose** 1.29+ or Docker Compose V2

---

## Installation Methods

### Linux/macOS Installation

#### Step 1: Clone the Repository (if not already done)
```bash
git clone https://github.com/cliffcho242/HireMeBahamas.git
cd HireMeBahamas
```

#### Step 2: Make Scripts Executable
```bash
chmod +x scripts/*.sh scripts/*.py
```

#### Step 3: Run Installation Script
```bash
./scripts/install_all_dependencies.sh
```

The script will automatically:
1. Detect your OS (Ubuntu/Debian, CentOS/RHEL, or macOS)
2. Update package manager (apt-get, yum, or Homebrew)
3. Install system dependencies
4. Install Python dependencies from requirements.txt
5. Install Node.js dependencies from package.json
6. Start and configure PostgreSQL
7. Start and configure Redis
8. Create default .env files
9. Verify the installation

#### Installation Options
```bash
# See all available options
./scripts/install_all_dependencies.sh --help

# Dry run (see what would be installed)
./scripts/install_all_dependencies.sh --dry-run

# Skip system packages (if already installed)
./scripts/install_all_dependencies.sh --skip-system

# Force reinstall all packages
./scripts/install_all_dependencies.sh --force
```

---

### Windows Installation

#### Step 1: Open Command Prompt as Administrator
1. Press `Win + X`
2. Select "Command Prompt (Admin)" or "PowerShell (Admin)"

#### Step 2: Navigate to Project Directory
```cmd
cd path\to\HireMeBahamas
```

#### Step 3: Run Installation Script
```cmd
scripts\install_all_dependencies.bat
```

The script will:
1. Check for/install Chocolatey package manager
2. Install Python 3.12
3. Install Node.js LTS
4. Install PostgreSQL 15
5. Install Redis
6. Install Visual Studio Build Tools
7. Install Python packages
8. Install Node.js packages
9. Configure and start services
10. Create environment files

#### Installation Options
```cmd
REM See help
scripts\install_all_dependencies.bat /help

REM Skip system packages
scripts\install_all_dependencies.bat /skip-system
```

---

### Docker Installation

Docker provides the easiest cross-platform installation method.

#### Step 1: Install Docker
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)
- **macOS**: Install [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Windows**: Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

#### Step 2: Run Docker Installation Script
```bash
./scripts/docker_install_all.sh
```

This will:
1. Check Docker and Docker Compose installation
2. Create Dockerfiles for backend and frontend
3. Build Docker images
4. Start all services in containers
5. Configure networking between services

#### Docker Commands
```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build
```

---

## What Gets Installed

### System Dependencies

#### Ubuntu/Debian
- `build-essential` - Compilation tools
- `python3`, `python3-pip`, `python3-dev`, `python3-venv` - Python environment
- `postgresql`, `postgresql-contrib`, `libpq-dev` - Database
- `redis-server`, `redis-tools` - Caching
- `nodejs`, `npm` - JavaScript runtime
- `libffi-dev`, `libssl-dev`, `pkg-config` - Libraries
- `curl`, `wget`, `git` - Utilities

#### CentOS/RHEL
- `gcc`, `gcc-c++`, `make` - Build tools
- `python3`, `python3-pip`, `python3-devel` - Python
- `postgresql`, `postgresql-server`, `postgresql-devel` - Database
- `redis` - Caching
- `nodejs`, `npm` - JavaScript
- `libffi-devel`, `openssl-devel` - Libraries

#### macOS (via Homebrew)
- `python@3.12` - Python
- `postgresql@15` - Database
- `redis` - Caching
- `node` - JavaScript runtime
- `openssl`, `libffi`, `pkg-config` - Libraries
- `render` - Render CLI for deployment

### Python Packages

All packages from `requirements.txt` plus:
- `psycopg2-binary` - PostgreSQL adapter
- `redis` - Redis client
- `sentry-sdk` - Error tracking
- `gunicorn` - Production WSGI server
- `flask-cors` - CORS support
- `flask-limiter` - Rate limiting
- `flask-caching` - Caching support
- `flask-socketio` - WebSocket support
- `flask-compress` - Response compression
- `flask-talisman` - Security headers
- `python-dotenv` - Environment variables
- `bcrypt` - Password hashing
- `pyjwt` - JWT tokens

### Node.js Packages

**Global:**
- `vite` - Build tool

**Frontend (from package.json):**
- React ecosystem
- TypeScript
- Vite and plugins
- UI libraries (Tailwind, HeadlessUI, etc.)
- State management (Zustand)
- API client (Axios)
- And all other dependencies in frontend/package.json

### Services Configured

1. **PostgreSQL**
   - Database: `hiremebahamas`
   - User: `hiremebahamas` (Linux/macOS) or `postgres` (Windows)
   - Port: `5432`

2. **Redis**
   - Port: `6379`
   - No authentication (development mode)

---

## Verification

After installation, verify everything is working:

### Automated Verification
```bash
python scripts/verify_installation.py
```

This will check:
- ✅ Python version and packages
- ✅ Node.js version and packages
- ✅ PostgreSQL installation and service
- ✅ Redis installation and service
- ✅ Environment files
- ✅ Database connection
- ✅ Redis connection

### Manual Verification

#### Check Python
```bash
python3 --version
pip3 list | grep -i flask
```

#### Check Node.js
```bash
node --version
npm --version
cd frontend && npm list --depth=0
```

#### Check PostgreSQL
```bash
# Linux/macOS
psql -h localhost -U hiremebahamas -d hiremebahamas

# Windows
psql -h localhost -U postgres -d hiremebahamas

# Check if running
pg_isready -h localhost -p 5432
```

#### Check Redis
```bash
redis-cli ping
# Should return: PONG
```

---

## Troubleshooting

### Common Issues

#### 1. Permission Denied Errors (Linux/macOS)
**Problem**: Script fails with permission errors

**Solution**:
```bash
# Make scripts executable
chmod +x scripts/*.sh scripts/*.py

# Run with sudo if needed (script will prompt)
sudo ./scripts/install_all_dependencies.sh
```

#### 2. Chocolatey Installation Fails (Windows)
**Problem**: Chocolatey fails to install

**Solution**:
```powershell
# Install manually
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### 3. PostgreSQL Won't Start (Linux)
**Problem**: PostgreSQL service fails to start

**Solution**:
```bash
# Check status
sudo systemctl status postgresql

# Check logs
sudo journalctl -u postgresql -n 50

# Reinitialize (if needed)
sudo systemctl stop postgresql
sudo rm -rf /var/lib/postgresql/*/main
sudo postgresql-setup --initdb
sudo systemctl start postgresql
```

#### 4. npm Install Fails with Peer Dependency Errors
**Problem**: Frontend dependencies won't install

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

#### 5. Port Already in Use
**Problem**: PostgreSQL or Redis port is already taken

**Solution**:
```bash
# Check what's using the port
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis

# Kill the process or change ports in .env files
```

#### 6. Database Connection Fails
**Problem**: Can't connect to database

**Solution**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list                 # macOS

# Check credentials in backend/.env
# Make sure DATABASE_URL matches your setup

# Create database manually if needed
createdb hiremebahamas
```

#### 7. Python Module Import Errors
**Problem**: Python can't find installed packages

**Solution**:
```bash
# Make sure you're using the right Python
which python3
which pip3

# Reinstall in user space
pip3 install --user -r requirements.txt

# Or use virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Getting Help

1. **Check Installation Log**
   ```bash
   cat installation.log
   ```

2. **Run Verification Script**
   ```bash
   python scripts/verify_installation.py
   ```

3. **Check Service Status**
   ```bash
   # Linux/macOS
   sudo systemctl status postgresql redis-server
   
   # macOS (Homebrew)
   brew services list
   
   # Windows
   Get-Service -Name postgresql*,redis
   ```

4. **Review Error Messages**: The installation script provides detailed error messages with suggestions

---

## Platform-Specific Notes

### Ubuntu/Debian
- ✅ **Recommended**: Most tested platform
- Script uses `apt-get` for package management
- Services managed by `systemctl`
- PostgreSQL user: `postgres`
- Default Python: `python3`

### CentOS/RHEL
- Requires EPEL repository for some packages
- Script uses `yum` for package management
- PostgreSQL may need manual initialization
- SELinux may need configuration

### macOS
- Requires **Homebrew** (installed automatically if missing)
- Services managed by `brew services`
- PostgreSQL installed via Homebrew
- May need Xcode Command Line Tools:
  ```bash
  xcode-select --install
  ```

### Windows
- Requires **Chocolatey** (installed automatically)
- **Administrator privileges** required
- Services managed by Windows Services
- Visual Studio Build Tools installed for native modules
- PostgreSQL password: `postgres` (default)

### Docker
- ✅ **Most portable** solution
- Works identically on all platforms
- Isolated from host system
- Easy to reset and rebuild
- Includes production-ready configuration

---

## Advanced Usage

### Selective Installation

Install only specific components:

```bash
# Skip system packages (already installed)
./scripts/install_all_dependencies.sh --skip-system

# Skip Python packages
./scripts/install_all_dependencies.sh --skip-python

# Skip Node.js packages
./scripts/install_all_dependencies.sh --skip-node

# Skip service configuration
./scripts/install_all_dependencies.sh --skip-services

# Combine options
./scripts/install_all_dependencies.sh --skip-system --skip-services
```

### Force Reinstall

Reinstall all packages even if already installed:

```bash
./scripts/install_all_dependencies.sh --force
```

### Dry Run

See what would be installed without making changes:

```bash
./scripts/install_all_dependencies.sh --dry-run
```

### Custom Installation Path

For Docker, customize volumes and ports:

```bash
# Edit docker-compose.yml
vim docker-compose.yml

# Change ports or volumes as needed
# Then run
./scripts/docker_install_all.sh
```

---

## Environment Configuration

After installation, configure your environment:

### Backend Environment (`backend/.env`)

```env
# Database
DATABASE_URL=postgresql://hiremebahamas:hiremebahamas@localhost:5432/hiremebahamas

# Security
SECRET_KEY=your-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Services
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development

# Cloudinary (for image uploads)
CLOUDINARY_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Sentry (optional, for error tracking)
SENTRY_DSN=your_sentry_dsn
```

### Frontend Environment (`frontend/.env`)

```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000

# Cloudinary
VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name

# Optional: Performance tuning
VITE_ENABLE_RETRY=true
VITE_RETRY_ATTEMPTS=3
VITE_REQUEST_TIMEOUT=30000
```

### Generating a Secure Secret Key

```python
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or
openssl rand -base64 32
```

---

## Next Steps

After successful installation:

### 1. Start Development Servers

#### Backend
```bash
cd backend
python app.py
# or
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm run dev
```

### 2. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 3. Create Admin User (Optional)

```bash
python create_admin.py
```

### 4. Set Up Database Schema

```bash
cd backend
python -c "from app.database import init_db; init_db()"
```

### 5. Production Deployment

For production deployment, see:
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- [Render Deployment](https://render.app)
- [Vercel Frontend](https://vercel.com)
- [Render Backend](https://render.com)

---

## CI/CD Integration

### GitHub Actions

Add to `.github/workflows/dependencies-check.yml`:

```yaml
name: Dependencies Check

on: [push, pull_request]

jobs:
  check-dependencies:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: ./scripts/install_all_dependencies.sh --skip-services
      
      - name: Verify installation
        run: python scripts/verify_installation.py
```

### Render

Use the install script in `nixpacks.toml`:

```toml
[phases.setup]
nixPkgs = ["python310", "nodejs-18_x", "postgresql"]

[phases.install]
cmds = ["./scripts/install_all_dependencies.sh --skip-system"]
```

---

## Support

### Documentation
- **Main README**: [README.md](../README.md)
- **Development Guide**: [DEVELOPMENT.md](../DEVELOPMENT.md)
- **Architecture**: [ARCHITECTURE.md](../ARCHITECTURE.md)

### Community
- **GitHub Issues**: [Report bugs or request features](https://github.com/cliffcho242/HireMeBahamas/issues)
- **Discussions**: [Ask questions](https://github.com/cliffcho242/HireMeBahamas/discussions)

### Logs and Debugging
- Installation log: `installation.log`
- Verification output: `python scripts/verify_installation.py`
- Service logs: `journalctl`, `docker-compose logs`, or Windows Event Viewer

---

## License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

## Changelog

### Version 1.0.0 (2024)
- ✅ Initial release
- ✅ Support for Ubuntu/Debian, CentOS/RHEL, macOS, Windows
- ✅ Docker installation option
- ✅ Comprehensive verification script
- ✅ Detailed troubleshooting guide
- ✅ Zero-intervention installation

---

**🎉 Happy Coding! Welcome to HireMeBahamas!**
