# Automated Dependency Fix for User Profile Error

## Problem
The "Failed to load user profile" error occurs when users try to view profile pages in the frontend. This error is typically caused by missing system dependencies required by the Python backend packages and Node.js frontend build tools.

## Solution
We've created automated scripts that install all necessary system dependencies for **both backend and frontend** using `apt-get`, plus Python dependencies using `pip3` and Node.js dependencies using `npm`.

## Available Scripts

### 1. Shell Script (Linux/Unix) - Installs Backend + Frontend apt-get Dependencies
```bash
sudo bash automated_dependency_fix.sh
```

**Features:**
- Installs all backend system dependencies via apt-get (Python, PostgreSQL, Redis, build tools)
- Installs all frontend system dependencies via apt-get (Node.js 18.x, npm, image libraries)
- Starts PostgreSQL and Redis services
- Enables services to auto-start on boot
- Provides clear step-by-step output with color coding
- Verifies installations

### 2. Python Script (Cross-platform) - Complete Installation
```bash
# Basic installation (system dependencies only for backend + frontend)
sudo python3 automated_dependency_fix.py

# With Python dependencies
sudo python3 automated_dependency_fix.py --install-python-deps

# Without starting services
sudo python3 automated_dependency_fix.py --skip-services
```

**Features:**
- Installs all system dependencies for backend and frontend
- Optionally installs Python dependencies
- Handles version conflicts automatically
- Can skip service startup if needed
- Verifies Python, Node.js, and npm versions

## What Gets Installed

### Backend System Dependencies (via apt-get)
1. **Build Tools:**
   - build-essential, gcc, g++, make, pkg-config

2. **Python Development:**
   - python3, python3-pip, python3-dev, python3-venv
   - python3-setuptools, python3-wheel

3. **Database & Cache:**
   - postgresql, postgresql-contrib, postgresql-client, libpq-dev
   - redis-server, redis-tools

4. **Security Libraries:**
   - libssl-dev, libffi-dev, ca-certificates

5. **Image Processing (Backend):**
   - libjpeg-dev, libpng-dev, libtiff-dev, libwebp-dev
   - libopenjp2-7-dev, zlib1g-dev

6. **Additional Libraries:**
   - libevent-dev (for gevent)
   - libxml2-dev, libxslt1-dev (for XML processing)

### Frontend System Dependencies (via apt-get)
1. **Node.js & npm:**
   - nodejs (18.x LTS)
   - npm (comes with Node.js)

2. **Image Optimization Libraries:**
   - libvips-dev (for sharp image processing)
   - libwebp-dev (WebP support)
   - libheif-dev (HEIF/HEIC support)
   - libavif-dev (AVIF support)

### Utilities (via apt-get)
- curl, wget, git, htop, vim, unzip

### Python Dependencies (if --install-python-deps flag used)
- **Backend:** FastAPI, SQLAlchemy, psycopg2-binary, bcrypt, PyJWT, etc.
- **Root:** Flask, Flask-CORS, redis, celery, gunicorn, etc.

## Usage Instructions

### Quick Start - Complete Installation (Recommended)
```bash
# Clone the repository (if not already done)
cd HireMeBahamas

# Run the automated fix with Python dependencies
sudo python3 automated_dependency_fix.py --install-python-deps

# Install frontend Node.js packages
cd frontend && npm install
```

### Manual Step-by-Step
```bash
# 1. Install all system dependencies (backend + frontend)
sudo bash automated_dependency_fix.sh

# 2. Install Python dependencies manually
pip3 install -r requirements.txt
cd backend && pip3 install -r requirements.txt

# 3. Install frontend Node.js dependencies
cd frontend && npm install

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Start the backend
cd backend && python3 -m app.main

# 6. Start the frontend (in a new terminal)
cd frontend && npm run dev

# 7. Test the fix
python3 test_user_profile_fix.py
```

## Verification

After running the automated fix, verify the installation:

```bash
# Check Python
python3 --version

# Check Node.js and npm
node --version
npm --version

# Check PostgreSQL
psql --version
sudo systemctl status postgresql

# Check Redis
redis-cli ping  # Should return "PONG"

# Check if backend dependencies are installed
python3 -c "import fastapi; import sqlalchemy; print('Backend dependencies OK')"

# Check if frontend dependencies are installed
cd frontend && npm list --depth=0
```

## Troubleshooting

### Permission Errors
If you get permission errors, make sure you're running with sudo:
```bash
sudo python3 automated_dependency_fix.py --install-python-deps
```

### Service Start Issues
If PostgreSQL or Redis don't start automatically:
```bash
# Start manually
sudo systemctl start postgresql
sudo systemctl start redis-server

# Or use service command
sudo service postgresql start
sudo service redis-server start
```

### Python Package Conflicts
If you encounter package version conflicts:
```bash
# Use the --ignore-installed flag
sudo pip3 install --ignore-installed typing_extensions -r requirements.txt
```

### Virtual Environment (Recommended for Development)
For a cleaner installation, use a virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
cd backend && pip install -r requirements.txt
```

## What This Fixes

The automated dependency installation fixes several issues:

1. ✅ **User Profile Loading** - Backend can now return all required fields
2. ✅ **Authentication** - JWT tokens work properly with PyJWT
3. ✅ **Password Hashing** - bcrypt is properly installed
4. ✅ **Database Connections** - psycopg2 works with libpq-dev
5. ✅ **Image Processing** - Pillow works with image libraries
6. ✅ **Async Operations** - gevent works with libevent-dev
7. ✅ **SSL/TLS** - cryptography package works with libssl-dev

## Next Steps After Installation

1. **Configure Database:**
   ```bash
   # Create PostgreSQL database
   sudo -u postgres psql -c "CREATE DATABASE hiremebahamas;"
   sudo -u postgres psql -c "CREATE USER hiremeuser WITH PASSWORD 'yourpassword';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremeuser;"
   ```

2. **Run Migrations:**
   ```bash
   cd backend
   python3 -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

3. **Start Backend:**
   ```bash
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
   ```

4. **Install Frontend Dependencies:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Test the Application:**
   - Backend: http://127.0.0.1:8005
   - Frontend: http://localhost:3000
   - API Docs: http://127.0.0.1:8005/docs

## Support

If you continue to experience issues after running the automated fix:

1. Check the logs for specific error messages
2. Verify all services are running
3. Ensure environment variables are set correctly
4. Review the [INSTALL.md](INSTALL.md) for detailed installation instructions

## Related Documentation

- [INSTALL.md](INSTALL.md) - Comprehensive installation guide
- [DEPENDENCIES_QUICK_REF.md](DEPENDENCIES_QUICK_REF.md) - Quick reference for apt-get commands
- [USER_PROFILE_FIX_SUMMARY.md](USER_PROFILE_FIX_SUMMARY.md) - Original user profile fix details
- [README.md](README.md) - Project overview

---

**Last Updated:** 2025-11-23  
**Tested On:** Ubuntu 20.04, Ubuntu 22.04, Debian 11, GitHub Actions Ubuntu Latest
