# System Dependencies and Installation Guide

## Overview

This document lists all system and application dependencies required for HireMeBahamas platform, including the chat/messaging feature.

## System Dependencies (APT packages for Ubuntu/Debian)

### Essential Build Tools
```bash
sudo apt-get update
sudo apt-get install -y build-essential
```

### Python Dependencies
```bash
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv
```

### Node.js and npm
```bash
# Install Node.js 18.x or later
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### PostgreSQL (Database)
```bash
sudo apt-get install -y \
    libpq-dev \
    postgresql-client \
    postgresql \
    postgresql-contrib
```

### Redis (Caching and Real-time Features)
```bash
sudo apt-get install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### Image Processing Libraries (for Pillow/image uploads)
```bash
sudo apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev
```

### SSL/Security Libraries
```bash
sudo apt-get install -y \
    libssl-dev \
    libffi-dev
```

### Other Essential Tools
```bash
sudo apt-get install -y \
    pkg-config \
    git \
    curl \
    wget
```

## Complete One-Command Installation

For convenience, install all dependencies with:

```bash
./install_all_dependencies.sh
```

Or manually:

```bash
# All system dependencies in one command
sudo apt-get update && sudo apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    libpq-dev \
    postgresql-client \
    redis-server \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    libssl-dev \
    libffi-dev \
    pkg-config \
    git \
    curl \
    wget
```

## Python Application Dependencies

### Backend (FastAPI)

All Python dependencies are listed in `backend/requirements.txt`:

**Key dependencies for chat/messaging:**
- `fastapi==0.109.0` - Modern web framework
- `uvicorn[standard]==0.27.0` - ASGI server
- `python-socketio==5.11.0` - WebSocket support for real-time chat
- `redis==5.0.1` - Caching and WebSocket message broker
- `websockets==12.0` - WebSocket protocol implementation
- `sqlalchemy==2.0.25` - Database ORM
- `asyncpg==0.29.0` - PostgreSQL async driver
- `psycopg2-binary==2.9.9` - PostgreSQL driver

Install backend dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Root Dependencies (Flask utilities)

Listed in root `requirements.txt`:

**Key dependencies:**
- `Flask==3.0.1` - Alternative backend framework
- `flask-socketio==5.3.6` - Flask WebSocket support
- `python-socketio==5.11.0` - WebSocket library
- `python-engineio==4.9.0` - Engine.IO implementation
- `gunicorn==21.2.0` - Production WSGI server
- `gevent==23.9.1` - Async support for Flask

Install root dependencies:
```bash
pip3 install -r requirements.txt
```

## Frontend (React/TypeScript) Dependencies

All Node.js dependencies are listed in `frontend/package.json`:

**Key dependencies for chat/messaging:**
- `socket.io-client@^4.8.1` - WebSocket client for real-time chat
- `axios@^1.6.5` - HTTP client for API calls
- `react-hot-toast@^2.6.0` - Toast notifications
- `framer-motion@^12.23.24` - Animations for chat UI
- `@heroicons/react@^2.2.0` - Icons

Install frontend dependencies:
```bash
cd frontend
npm install
```

## Database Setup

### PostgreSQL Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb hiremebahamas

# Create user (optional)
sudo -u postgres createuser -P hiremebahamas_user

# Grant permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hiremebahamas TO hiremebahamas_user;"
```

### SQLite (Development)

No setup required - SQLite database file will be created automatically on first run.

## Redis Setup

```bash
# Start Redis
sudo systemctl start redis-server

# Enable Redis to start on boot
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
# Should return: PONG
```

## Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/hiremebahamas
# Or for SQLite:
# DATABASE_URL=sqlite:///./hiremebahamas.db

# Redis
REDIS_URL=redis://localhost:6379/0

# Backend
PORT=8000
SECRET_KEY=your-secret-key-here

# Frontend
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

## Running the Application

### Backend

```bash
cd backend
source venv/bin/activate

# Run database migrations (if needed)
python migrate_messages_sqlite.py  # For SQLite
# OR
python migrate_messages_table.py   # For PostgreSQL

# Start backend server
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Troubleshooting

### "Failed to load chat" error

This usually indicates:
1. Backend server is not running
2. WebSocket connection failed
3. Missing dependencies

**Solution:**
1. Ensure Redis is running: `sudo systemctl status redis-server`
2. Check backend logs for errors
3. Verify all dependencies are installed: `pip list` and `npm list`

### WebSocket connection errors

**Solution:**
1. Check CORS configuration in `backend/app/main.py`
2. Ensure `python-socketio` is installed: `pip show python-socketio`
3. Verify Redis is accessible: `redis-cli ping`

### Database migration errors

**Solution:**
1. Backup your database
2. Run migration script: `python backend/migrate_messages_sqlite.py`
3. Check database schema: `sqlite3 hiremebahamas.db ".schema messages"`

## Verification

Run the verification script to check all dependencies:

```bash
python scripts/verify_installation.py
```

## Production Deployment

For production, ensure:
1. All dependencies are installed on the server
2. PostgreSQL and Redis are properly configured
3. Environment variables are set correctly
4. Firewall rules allow WebSocket connections
5. SSL/TLS is configured for secure WebSocket (WSS)

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Socket.IO Documentation](https://socket.io/docs/v4/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
