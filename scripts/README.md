# HireMeBahamas - Installation Scripts

This directory contains comprehensive automated installation scripts for the HireMeBahamas platform.

## Quick Start

Choose your platform and run the appropriate script:

### Linux/macOS
```bash
./scripts/install_all_dependencies.sh
```

### Windows
```cmd
scripts\install_all_dependencies.bat
```

### Docker
```bash
./scripts/docker_install_all.sh
```

## Scripts Overview

### 🔄 Database Migration Scripts

#### `migrate_railway_to_vercel.sh` (Shell)
Zero-downtime migration from Railway Postgres to Vercel Postgres (Neon).

**Features:**
- Parallel export/import with 8 jobs
- Row count verification
- Connection testing
- Automatic cleanup of target database

**Usage:**
```bash
export RAILWAY_DATABASE_URL='postgresql://...'
export VERCEL_POSTGRES_URL='postgresql://...'
./scripts/migrate_railway_to_vercel.sh
```

#### `migrate_railway_to_vercel.py` (Python)
Python version of the migration script with identical functionality.

**Usage:**
```bash
export RAILWAY_DATABASE_URL='postgresql://...'
export VERCEL_POSTGRES_URL='postgresql://...'
python scripts/migrate_railway_to_vercel.py
```

For complete migration documentation, see [VERCEL_POSTGRES_MIGRATION.md](../VERCEL_POSTGRES_MIGRATION.md).

---

### 🚀 Main Installation Scripts

#### `install_all_dependencies.sh` (Linux/macOS)
Comprehensive installation script for Unix-like systems.

**Features:**
- Automatic OS detection (Ubuntu/Debian, CentOS/RHEL, macOS)
- System package installation via apt-get/yum/Homebrew
- Python package installation from requirements.txt
- Node.js package installation from package.json
- Service configuration (PostgreSQL, Redis)
- Environment file creation
- Installation verification

**Usage:**
```bash
# Standard installation
./scripts/install_all_dependencies.sh

# See all options
./scripts/install_all_dependencies.sh --help

# Dry run (preview without installing)
./scripts/install_all_dependencies.sh --dry-run

# Skip system packages (if already installed)
./scripts/install_all_dependencies.sh --skip-system

# Force reinstall all packages
./scripts/install_all_dependencies.sh --force
```

**Options:**
- `--dry-run` - Show what would be installed without making changes
- `--skip-system` - Skip system package installation
- `--skip-python` - Skip Python package installation
- `--skip-node` - Skip Node.js package installation
- `--skip-services` - Skip service configuration
- `--force` - Force reinstall of all packages
- `--help` - Show help message

---

#### `install_all_dependencies.bat` (Windows)
Windows installation script using Chocolatey.

**Features:**
- Automatic Chocolatey installation
- System package installation (Python, Node.js, PostgreSQL, Redis)
- Visual Studio Build Tools installation
- Python and Node.js package installation
- Service configuration
- Environment file creation

**Usage:**
```cmd
REM Run as Administrator
scripts\install_all_dependencies.bat

REM See help
scripts\install_all_dependencies.bat /help

REM Skip system packages
scripts\install_all_dependencies.bat /skip-system
```

**Options:**
- `/help` - Show help message
- `/skip-system` - Skip system package installation
- `/skip-python` - Skip Python package installation
- `/skip-node` - Skip Node.js package installation

---

#### `docker_install_all.sh` (Docker)
Docker-based installation for all platforms.

**Features:**
- Automatic Dockerfile generation
- Docker Compose configuration
- Multi-service setup (backend, frontend, PostgreSQL, Redis)
- Production-ready configuration
- One-command deployment

**Usage:**
```bash
# Full installation and startup
./scripts/docker_install_all.sh

# Build only (don't start containers)
./scripts/docker_install_all.sh --build-only

# Build without cache
./scripts/docker_install_all.sh --no-cache
```

**Options:**
- `--build-only` - Only build containers, don't start them
- `--no-cache` - Build without using cache
- `--help` - Show help message

---

### ✅ Verification Script

#### `verify_installation.py`
Comprehensive verification script that checks all dependencies and services.

**Features:**
- Checks Python and Node.js versions
- Verifies Python packages from requirements.txt
- Verifies Node.js packages from package.json
- Tests PostgreSQL installation and service
- Tests Redis installation and service
- Validates environment files
- Tests database connections
- Tests Redis connections
- Generates detailed report

**Usage:**
```bash
python scripts/verify_installation.py
```

**Exit Codes:**
- `0` - All checks passed
- `1` - One or more checks failed

---

## Installation Workflow

### Standard Installation (Linux/macOS)

```bash
# 1. Run main installation script
./scripts/install_all_dependencies.sh

# 2. Verify installation
python scripts/verify_installation.py

# 3. Check installation log if needed
cat installation.log
```

### Standard Installation (Windows)

```cmd
REM 1. Run main installation script (as Administrator)
scripts\install_all_dependencies.bat

REM 2. Verify installation
python scripts\verify_installation.py

REM 3. Check installation log if needed
type installation.log
```

### Docker Installation

```bash
# 1. Run Docker installation
./scripts/docker_install_all.sh

# 2. Check container status
docker-compose ps

# 3. View logs
docker-compose logs -f
```

---

## What Gets Installed

### System Dependencies

**Ubuntu/Debian:**
- build-essential, Python 3, Node.js, PostgreSQL, Redis, development libraries

**CentOS/RHEL:**
- GCC, Python 3, Node.js, PostgreSQL, Redis, development libraries

**macOS:**
- Python 3, Node.js, PostgreSQL, Redis (via Homebrew)

**Windows:**
- Python 3.12, Node.js LTS, PostgreSQL 15, Redis, Visual Studio Build Tools

### Python Packages
All packages from `requirements.txt` plus:
- psycopg2-binary, redis, sentry-sdk, gunicorn
- flask-cors, flask-limiter, flask-caching, flask-socketio
- flask-compress, flask-talisman, python-dotenv
- bcrypt, pyjwt

### Node.js Packages
- Global: vite
- Frontend: All packages from frontend/package.json

### Services
- PostgreSQL (port 5432)
- Redis (port 6379)

---

## Environment Files

The installation scripts automatically create:

### `backend/.env`
```env
DATABASE_URL=postgresql://hiremebahamas:hiremebahamas@localhost:5432/hiremebahamas
SECRET_KEY=change-this-to-a-secure-random-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
```

### `frontend/.env`
```env
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

**Important:** Update these files with your actual configuration values!

---

## Troubleshooting

### Installation Fails

1. **Check the log file:**
   ```bash
   cat installation.log
   ```

2. **Run verification:**
   ```bash
   python scripts/verify_installation.py
   ```

3. **Try with specific skips:**
   ```bash
   # If system packages are already installed
   ./scripts/install_all_dependencies.sh --skip-system
   ```

4. **Force reinstall:**
   ```bash
   ./scripts/install_all_dependencies.sh --force
   ```

### Service Issues

**PostgreSQL won't start:**
```bash
# Linux
sudo systemctl status postgresql
sudo systemctl restart postgresql

# macOS
brew services restart postgresql@15
```

**Redis won't start:**
```bash
# Linux
sudo systemctl status redis-server
sudo systemctl restart redis-server

# macOS
brew services restart redis
```

### Permission Issues (Linux/macOS)

```bash
# Make scripts executable
chmod +x scripts/*.sh scripts/*.py

# Run with sudo (script will prompt if needed)
./scripts/install_all_dependencies.sh
```

### Docker Issues

```bash
# Check Docker daemon
docker ps

# Rebuild containers
docker-compose down
docker-compose up -d --build

# View logs
docker-compose logs -f
```

---

## Advanced Usage

### Selective Installation

```bash
# Only Python packages
./scripts/install_all_dependencies.sh --skip-system --skip-node --skip-services

# Only Node.js packages
./scripts/install_all_dependencies.sh --skip-system --skip-python --skip-services

# Everything except services
./scripts/install_all_dependencies.sh --skip-services
```

### Development vs Production

**Development:**
```bash
# Standard installation
./scripts/install_all_dependencies.sh
```

**Production (Docker):**
```bash
# Use Docker for isolated production environment
./scripts/docker_install_all.sh
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Install Dependencies

on: [push, pull_request]

jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: ./scripts/install_all_dependencies.sh --skip-services
      - name: Verify installation
        run: python scripts/verify_installation.py
```

### Railway

Add to `nixpacks.toml`:
```toml
[phases.install]
cmds = ["./scripts/install_all_dependencies.sh --skip-system"]
```

---

## Support

For detailed documentation, see:
- [INSTALLATION_COMPLETE.md](../INSTALLATION_COMPLETE.md) - Full installation guide
- [README.md](../README.md) - Project overview
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Development guide

For issues or questions:
- GitHub Issues: https://github.com/cliffcho242/HireMeBahamas/issues
- GitHub Discussions: https://github.com/cliffcho242/HireMeBahamas/discussions

---

## Script Maintenance

### Adding New Dependencies

1. Update `requirements.txt` or `package.json`
2. Scripts will automatically install them on next run
3. Update `verify_installation.py` if needed

### Testing Scripts

```bash
# Always test in dry-run mode first
./scripts/install_all_dependencies.sh --dry-run

# Then run actual installation
./scripts/install_all_dependencies.sh
```

---

## License

These scripts are part of the HireMeBahamas project and are licensed under the MIT License.

---

**Last Updated:** November 2024  
**Script Version:** 1.0.0
