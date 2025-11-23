# Quick Reference: Preventing User Deletion

## 🚨 Problem
Users and posts are deleted after deployment or restart.

## ✅ Solution Summary

### 1. Install ALL Dependencies
```bash
sudo ./install_all_dependencies_complete.sh
```

### 2. For Production - Use PostgreSQL
```bash
export DATABASE_URL="postgresql://user:pass@host:5432/db"
```

### 3. Verify Installation
```bash
python3 test_dependencies.py
python3 ensure_database_init.py
```

## 📦 Required System Packages (apt-get)

**Database:**
- `postgresql`, `postgresql-client`, `libpq-dev` - PostgreSQL support
- `sqlite3`, `libsqlite3-dev` - SQLite support

**Build Tools:**
- `build-essential`, `gcc`, `g++`, `make`, `pkg-config`

**Python:**
- `python3`, `python3-pip`, `python3-dev`, `python3-venv`

**Security:**
- `libssl-dev`, `libffi-dev`, `ca-certificates`

**Media:**
- `libjpeg-dev`, `libpng-dev`, `zlib1g-dev`

## 🐍 Required Python Packages

**Critical for Database:**
```
python-decouple==3.8        # Configuration (REQUIRED!)
psycopg2-binary==2.9.11     # PostgreSQL
aiosqlite==0.21.0           # SQLite async
sqlalchemy                  # ORM
Flask or FastAPI            # Web framework
bcrypt==5.0.0               # Password hashing
PyJWT==2.10.1              # Authentication
python-dotenv==1.2.1        # Environment variables
```

## 🗄️ Database Configuration

### Development (Local)
```bash
# Uses SQLite automatically
# File: hiremebahamas.db
# ⚠️ Data lost on deployment
```

### Production (Required)
```bash
# Set in .env or environment variables:
DATABASE_URL=postgresql://username:password@hostname:5432/database
ENVIRONMENT=production
```

## 🚀 Deployment Checklist

Before deploying:
- [ ] Run `sudo ./install_all_dependencies_complete.sh`
- [ ] Set `DATABASE_URL` to PostgreSQL
- [ ] Set `ENVIRONMENT=production`
- [ ] Verify: `python3 test_dependencies.py`
- [ ] Verify: `python3 ensure_database_init.py`

## 🔧 Quick Fixes

### "ModuleNotFoundError: No module named 'decouple'"
```bash
pip3 install python-decouple
```

### "Users deleted after restart"
```bash
# Set DATABASE_URL to PostgreSQL!
export DATABASE_URL="postgresql://user:pass@host:5432/db"
```

### "psycopg2 installation failed"
```bash
sudo apt-get install libpq-dev python3-dev
pip3 install psycopg2-binary
```

## 📚 Documentation

- `INSTALL_DEPENDENCIES_DATABASE.md` - Complete guide
- `SYSTEM_DEPENDENCIES.md` - All system packages
- `DATA_PERSISTENCE_GUIDE.md` - Database details

## 🎯 One-Line Fix

```bash
sudo ./install_all_dependencies_complete.sh && export DATABASE_URL="postgresql://user:pass@host:5432/db"
```
