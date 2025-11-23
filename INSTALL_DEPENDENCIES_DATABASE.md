# Installing All Dependencies to Ensure User Storage

This guide explains how to install **ALL** required system dependencies via `apt-get` to ensure the HireMeBahamas application runs properly and stores user information without data loss.

## 🚨 Critical Issue: Users Being Deleted

**Problem:** Users and posts are deleted after deployment or restart.

**Root Cause:** Missing system dependencies or improper database configuration.

**Solution:** Install all required dependencies and configure proper database storage.

## 🔧 Quick Fix - One Command Installation

Run this command to install **ALL** system dependencies:

```bash
sudo ./install_all_dependencies_complete.sh
```

This will:
- ✅ Install all apt-get system packages
- ✅ Install all Python packages
- ✅ Install all Node.js packages
- ✅ Configure database for user storage
- ✅ Verify all installations

## 📦 Manual Installation Steps

If you prefer to install manually or need to troubleshoot:

### Step 1: Install System Dependencies (apt-get)

```bash
sudo ./install_system_dependencies.sh
```

Or manually install all packages:

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
    sqlite3 \
    libsqlite3-dev \
    redis-server \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    curl \
    wget \
    git
```

### Step 2: Install Python Dependencies

```bash
# Install root Python packages
pip3 install -r requirements.txt

# Install backend Python packages
pip3 install -r backend/requirements.txt
```

**Critical Python packages for database:**
- `python-decouple` - Configuration management (REQUIRED)
- `psycopg2-binary` - PostgreSQL database adapter
- `aiosqlite` - SQLite async support
- `sqlalchemy` - ORM for database operations
- `Flask` or `FastAPI` - Web framework
- `bcrypt` - Password hashing
- `PyJWT` - Authentication tokens

### Step 3: Install Node.js Dependencies

```bash
# Install Node.js if not present
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install frontend packages
cd frontend
npm install
```

### Step 4: Configure Database for User Storage

**For Development (Local):**
```bash
# SQLite will be used automatically
# Database file: hiremebahamas.db
# ⚠️ WARNING: Data is lost on deployment with SQLite
```

**For Production (REQUIRED):**
```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://username:password@hostname:5432/database"

# Or add to .env file:
echo "DATABASE_URL=postgresql://username:password@hostname:5432/database" >> .env
```

## 🗄️ Database Configuration - Preventing Data Loss

### Why Users Get Deleted

1. **SQLite in Production** - Container filesystems are ephemeral
2. **Missing Dependencies** - Database drivers not installed
3. **No DATABASE_URL** - App defaults to temporary storage
4. **Container Restarts** - Data not persisted to external database

### Solution: Use PostgreSQL for Production

**DO NOT use SQLite in production!** It causes data loss because:
- ❌ Container filesystems are destroyed on restart
- ❌ Railway/Render/Docker don't persist local files
- ❌ Every deployment = fresh container = lost data

**ALWAYS use PostgreSQL in production:**
- ✅ Data persists across deployments
- ✅ Survives container restarts
- ✅ Proper concurrent access
- ✅ ACID compliance

### Setting Up PostgreSQL

#### On Railway:
1. Add PostgreSQL plugin in Railway dashboard
2. Copy the DATABASE_URL from plugin
3. Set as environment variable
4. Redeploy

#### On Render:
1. Create PostgreSQL database in Render dashboard
2. Copy Internal Database URL
3. Set as DATABASE_URL environment variable
4. Deploy

#### Local PostgreSQL:
```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Create database
sudo -u postgres createdb hiremebahamas

# Create user
sudo -u postgres createuser -P hiremebahamas_user

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremebahamas_user;"

# Set DATABASE_URL
export DATABASE_URL="postgresql://hiremebahamas_user:password@localhost:5432/hiremebahamas"
```

## ✅ Verification

### Check System Dependencies
```bash
# Verify installations
python3 --version          # Python 3.12+
pip3 --version            # pip 23+
psql --version            # PostgreSQL client
sqlite3 --version         # SQLite
node --version            # Node.js 18+
npm --version             # npm 9+
redis-cli --version       # Redis
```

### Check Python Packages
```bash
# Test critical imports
python3 -c "import flask; print('Flask:', flask.__version__)"
python3 -c "import psycopg2; print('psycopg2:', psycopg2.__version__)"
python3 -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
python3 -c "from decouple import config; print('python-decouple: OK')"
python3 -c "import bcrypt; print('bcrypt: OK')"
python3 -c "import jwt; print('PyJWT: OK')"
```

### Check Database Configuration
```bash
# Run database check
python3 ensure_database_init.py

# Expected output for production:
# ✅ PostgreSQL configured for production
# ✅ Data will persist across deployments
```

## 🚀 Deployment Checklist

Before deploying to production:

- [ ] All system dependencies installed via apt-get
- [ ] All Python packages installed (requirements.txt)
- [ ] All Node.js packages installed (package.json)
- [ ] DATABASE_URL set to PostgreSQL connection string
- [ ] ENVIRONMENT set to "production"
- [ ] SECRET_KEY and JWT_SECRET_KEY configured
- [ ] Database initialized with tables
- [ ] Test deployment with health check

## 🐛 Troubleshooting

### "Users deleted after restart"
**Cause:** Using SQLite in production  
**Fix:** Set DATABASE_URL to PostgreSQL

### "ModuleNotFoundError: No module named 'decouple'"
**Cause:** python-decouple not installed  
**Fix:** `pip3 install python-decouple`

### "ModuleNotFoundError: No module named 'psycopg2'"
**Cause:** psycopg2-binary not installed or missing libpq-dev  
**Fix:** 
```bash
sudo apt-get install libpq-dev
pip3 install psycopg2-binary
```

### "Could not connect to database"
**Cause:** DATABASE_URL not set or incorrect  
**Fix:** Verify DATABASE_URL format:
```
DATABASE_URL=postgresql://user:password@host:5432/database
```

### "Database tables not found"
**Cause:** Database not initialized  
**Fix:** Tables are created automatically on first run. Check logs for initialization errors.

## 📚 Related Documentation

- `SYSTEM_DEPENDENCIES.md` - Complete system package list
- `DATA_PERSISTENCE_GUIDE.md` - Database persistence details
- `POSTGRESQL_SETUP.md` - PostgreSQL configuration
- `README.md` - General setup guide

## 🆘 Support

If you continue to experience issues with user storage:

1. Check logs: `gunicorn` or `railway logs`
2. Verify DATABASE_URL is set correctly
3. Ensure PostgreSQL is accessible
4. Confirm all dependencies are installed
5. Check database initialization in startup logs

## 🎯 Summary

To ensure users and posts are stored properly:

1. **Install all system dependencies** via `sudo apt-get install`
2. **Install all Python packages** including python-decouple
3. **Set DATABASE_URL** to PostgreSQL for production
4. **Never use SQLite** in production environments
5. **Verify configuration** before deployment

Run this to fix everything:
```bash
sudo ./install_all_dependencies_complete.sh
```
