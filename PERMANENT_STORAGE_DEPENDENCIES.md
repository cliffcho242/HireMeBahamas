# Complete System Dependencies for Permanent Data Storage

This document provides **all required and recommended dependencies** to ensure users are stored permanently when they register and the application runs reliably in production.

## Critical Dependencies for Permanent Storage

### 1. Database System (REQUIRED)

**For Production - PostgreSQL (Recommended):**
```bash
sudo apt-get install -y postgresql postgresql-client libpq-dev
```

**Configuration:**
```bash
# Start and enable PostgreSQL
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Create production database
sudo -u postgres createdb hiremebahamas
sudo -u postgres psql -c "CREATE USER hiremebahamas WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremebahamas;"
```

**For Development - SQLite (Built-in):**
- No additional installation needed
- Included with Python
- Data stored in `hiremebahamas.db` file

### 2. Python Development Tools (REQUIRED)

Essential for building database drivers and ensuring permanent storage:
```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential
```

## Complete Installation - All Dependencies

### Quick Install Command (Ubuntu/Debian)

Install **all required and recommended** dependencies in one command:

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
    python3-setuptools \
    python3-wheel \
    postgresql \
    postgresql-client \
    postgresql-contrib \
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
    git \
    sqlite3 \
    libsqlite3-dev
```

### Required Dependencies Breakdown

#### 1. Build Tools (REQUIRED)
```bash
sudo apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config
```
**Why:** Compile Python packages (psycopg2, bcrypt, cryptography) that ensure secure user storage.

#### 2. Python Environment (REQUIRED)
```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-setuptools \
    python3-wheel
```
**Why:** Run the backend application and install packages for user management.

#### 3. PostgreSQL Database (REQUIRED for Production)
```bash
sudo apt-get install -y \
    postgresql \
    postgresql-client \
    postgresql-contrib \
    libpq-dev
```
**Why:** Permanent, reliable, production-grade data storage for users, posts, and all application data.

#### 4. SQLite (REQUIRED for Development)
```bash
sudo apt-get install -y \
    sqlite3 \
    libsqlite3-dev
```
**Why:** Development database, data stored in file (`hiremebahamas.db`) - persists across restarts.

#### 5. Redis (RECOMMENDED)
```bash
sudo apt-get install -y \
    redis-server \
    redis-tools
```
**Why:** 
- Session management (keeps users logged in)
- Caching (improves performance)
- Rate limiting (prevents abuse)
- Background jobs

**Configuration:**
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### 6. Security Libraries (REQUIRED)
```bash
sudo apt-get install -y \
    libssl-dev \
    libffi-dev
```
**Why:**
- Password hashing (bcrypt) - secure user passwords
- JWT tokens (cryptography) - authentication
- HTTPS support

#### 7. Image Processing (RECOMMENDED)
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
**Why:** Handle user avatars, post images, story media.

#### 8. WebSocket Support (RECOMMENDED)
```bash
sudo apt-get install -y \
    libevent-dev \
    libxml2-dev \
    libxslt1-dev
```
**Why:** Real-time messaging and notifications.

#### 9. Web Server (REQUIRED for Production)
```bash
sudo apt-get install -y nginx
```
**Why:** Production web server, reverse proxy, SSL/TLS termination.

#### 10. Utilities (RECOMMENDED)
```bash
sudo apt-get install -y \
    curl \
    wget \
    git
```
**Why:** Download resources, version control, deployment.

#### 11. Node.js (REQUIRED for Frontend)
```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```
**Why:** Build and run React frontend.

## Python Package Dependencies

After installing system dependencies, install Python packages:

```bash
# Install all Python dependencies
pip3 install -r requirements.txt
```

**Key packages for permanent storage:**
- `psycopg2-binary==2.9.11` - PostgreSQL database driver
- `aiosqlite==0.21.0` - SQLite async support
- `Flask-SQLAlchemy==3.1.1` - ORM for database operations
- `Flask-Migrate==4.1.0` - Database migrations
- `bcrypt==5.0.0` - Password hashing
- `PyJWT==2.10.1` - Authentication tokens

## Verification

### 1. Verify System Dependencies
```bash
# Python
python3 --version  # Should be 3.11+

# PostgreSQL
psql --version  # Should be 13+

# Redis
redis-cli ping  # Should return "PONG"

# Node.js
node --version  # Should be 18+
```

### 2. Test Database Connection
```bash
# PostgreSQL
sudo -u postgres psql -c "SELECT version();"

# SQLite
sqlite3 hiremebahamas.db ".tables"
```

### 3. Test User Registration & Persistence
```bash
# Run the persistence test
python3 register_cliff_users.py
```

This will:
- Register test users
- Verify they're stored in database
- Restart the server
- Verify users still exist (persistence check)
- Test login after restart

## Data Persistence Guarantees

### SQLite (Development)
- ✅ Data stored in file: `hiremebahamas.db`
- ✅ Persists across server restarts
- ✅ Persists across system reboots
- ✅ Can be backed up by copying the file
- ⚠️ Single-user access, not recommended for production

### PostgreSQL (Production)
- ✅ Enterprise-grade persistence
- ✅ ACID compliance (data integrity)
- ✅ Multi-user concurrent access
- ✅ Automatic crash recovery
- ✅ Backup and replication support
- ✅ Recommended for production use

## Automated Installation Scripts

### Linux/macOS
```bash
# Install all dependencies automatically
sudo ./install_all_dependencies.sh
```

### Windows
```cmd
# Run as Administrator
scripts\install_all_dependencies.bat
```

### Docker (Includes all dependencies)
```bash
# Docker has all dependencies pre-installed
docker-compose up -d
```

## Testing Permanent Storage

After installation, verify permanent storage works:

```bash
# 1. Register users
python3 register_cliff_users.py

# 2. Check database directly
sqlite3 hiremebahamas.db "SELECT email, first_name, last_name FROM users;"

# 3. Test posts API
python3 test_posts_api.py

# 4. Restart server and verify data persists
python3 final_backend_postgresql.py
# (Stop with Ctrl+C, then start again)
# Users should still exist
```

## Production Deployment Checklist

For production deployment with permanent storage:

- [ ] Install PostgreSQL (not SQLite)
- [ ] Set `DATABASE_URL` environment variable
- [ ] Configure automated database backups
- [ ] Install Redis for session management
- [ ] Set up Nginx with SSL/TLS
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Test backup and restore procedures

## Environment Variables for Production

```bash
# .env file
DATABASE_URL=postgresql://user:password@localhost:5432/hiremebahamas
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_secret_key_here  # Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your_jwt_secret_here
ENVIRONMENT=production
```

## Troubleshooting

### Users Not Persisting
1. Check database file exists: `ls -la hiremebahamas.db`
2. Check database has users table: `sqlite3 hiremebahamas.db ".tables"`
3. Check database permissions: `ls -l hiremebahamas.db`
4. Run database initialization: `python3 final_backend_postgresql.py` (it auto-creates tables)

### PostgreSQL Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep hiremebahamas

# Test connection
psql -U hiremebahamas -d hiremebahamas -h localhost
```

### Dependency Installation Fails
```bash
# Update package lists
sudo apt-get update

# Fix broken dependencies
sudo apt-get install -f

# Reinstall specific package
sudo apt-get install --reinstall <package-name>
```

## Related Documentation

- [SYSTEM_DEPENDENCIES.md](./SYSTEM_DEPENDENCIES.md) - Detailed dependency guide
- [INSTALL.md](./INSTALL.md) - Complete installation guide
- [DATA_PERSISTENCE_GUIDE.md](./DATA_PERSISTENCE_GUIDE.md) - Data persistence technical details
- [README.md](./README.md) - Main project documentation

---

**Last Updated**: November 2025

**Verified For:**
- Ubuntu 20.04, 22.04, 24.04
- Debian 11, 12
- Compatible with Render, Render, AWS, Azure, GCP
