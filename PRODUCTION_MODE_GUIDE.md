# Production Mode Setup Guide

This guide explains how to run HireMeBahamas in **full production mode** for local development.

## ⚠️ Prerequisites

Before starting, you need **Docker** and **Docker Compose** installed:

- **Windows/macOS**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow the [Docker Setup Guide](./DOCKER_SETUP.md)

📖 **[Read the complete Docker Setup Guide](./DOCKER_SETUP.md)** for installation instructions.

To verify Docker is installed:
```bash
docker --version
docker compose version
```

## 🎯 What is Production Mode?

Production mode means:
- ✅ **PostgreSQL database** (not SQLite)
- ✅ **Production builds** (optimized, minified)
- ✅ **No hot-reload** (stable, production-like)
- ✅ **Production settings** (caching, security, performance)
- ✅ **No development tools** (no dev overlays, no test buttons)

## 🚀 Quick Start

### Option 1: Automated Script (Recommended)

#### Linux/macOS:
```bash
./start_production.sh
```

#### Windows:
```cmd
start_production.bat
```

This script will:
1. Start PostgreSQL and Redis via Docker
2. Build the frontend for production
3. Start the backend in production mode (no reload)
4. Start the frontend in production mode (optimized build)

### Option 2: Manual Setup

#### 1. Start Database Services
```bash
docker-compose -f docker-compose.local.yml up -d postgres redis
```

#### 2. Configure Environment Variables

**Backend** (`backend/.env`):
```env
DATABASE_URL=postgresql+asyncpg://hiremebahamas_user:hiremebahamas_password@localhost:5432/hiremebahamas
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
DB_ECHO=false
```

**Frontend** (`frontend/.env`):
```env
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
NODE_ENV=production
```

#### 3. Build Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

#### 4. Start Backend (Production Mode)
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-reload --workers 2
```

#### 5. Start Frontend (Production Mode)
```bash
cd frontend
npm run start
```

## 📋 Access Points

Once running, access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8081 (Adminer)

## 🗄️ Database Configuration

### PostgreSQL (Production Mode)

**Connection Details:**
- **Host**: localhost
- **Port**: 5432
- **Database**: hiremebahamas
- **Username**: hiremebahamas_user
- **Password**: hiremebahamas_password

### Accessing Database Admin (Adminer)

1. Open http://localhost:8081
2. Login with:
   - **System**: PostgreSQL
   - **Server**: postgres
   - **Username**: hiremebahamas_user
   - **Password**: hiremebahamas_password
   - **Database**: hiremebahamas

## 🔍 Key Differences from Development Mode

| Feature | Development Mode | Production Mode |
|---------|-----------------|----------------|
| **Database** | SQLite | PostgreSQL |
| **Frontend Build** | Dev server (Vite) | Production build |
| **Hot Reload** | ✅ Enabled | ❌ Disabled |
| **Source Maps** | ✅ Full | ⚠️ Limited |
| **Minification** | ❌ None | ✅ Full |
| **Code Splitting** | Basic | ✅ Optimized |
| **Caching** | Minimal | ✅ Aggressive |
| **Test Features** | ✅ Visible | ❌ Hidden |
| **Debug Logs** | ✅ Verbose | ⚠️ Production |
| **Error Pages** | Developer-friendly | User-friendly |

## 🛠️ Production Mode Features

### Backend (FastAPI + PostgreSQL)

- **No Auto-Reload**: Server stability, no crashes from file changes
- **Multiple Workers**: Better concurrency handling
- **Connection Pooling**: Efficient database connections
- **Production Logging**: Structured, minimal logs
- **Error Handling**: User-friendly error messages
- **Security Headers**: CORS, CSP, HSTS configured

### Frontend (React + Vite Production Build)

- **Code Minification**: Smaller bundle sizes
- **Tree Shaking**: Remove unused code
- **Asset Optimization**: Compressed images, fonts
- **Code Splitting**: Lazy loading for better performance
- **Service Worker**: PWA capabilities, offline support
- **Production Routing**: Optimized React Router
- **No Dev Tools**: Test buttons, debug overlays removed

## 🧪 Testing Production Mode

### 1. Test Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "HireMeBahamas API is running"
}
```

### 2. Test Frontend Build
Check browser console for:
- No development warnings
- Production React build message
- No source maps (or limited)

### 3. Test Database Connection
```bash
# Using psql
psql -h localhost -U hiremebahamas_user -d hiremebahamas

# List tables
\dt
```

### 4. Test API Endpoints
Visit http://localhost:8000/docs to test API endpoints interactively.

## 🔄 Updating Code

In production mode, code changes require:

1. **Frontend Changes**:
   ```bash
   cd frontend
   npm run build
   # Restart: npm run start
   ```

2. **Backend Changes**:
   ```bash
   # Simply restart the backend process
   # No hot-reload, so manual restart required
   ```

## 🛑 Stopping Services

### Stop Application:
- Press `Ctrl+C` in each terminal
- Or close the terminal windows

### Stop Docker Services:
```bash
docker-compose -f docker-compose.local.yml down
```

### Stop Everything (Including Data):
```bash
docker-compose -f docker-compose.local.yml down -v  # WARNING: Deletes database data!
```

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose -f docker-compose.local.yml logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Frontend Build Fails
```bash
# Clear node_modules and rebuild
cd frontend
rm -rf node_modules dist
npm install
npm run build
```

### Database Connection Errors
```bash
# Verify PostgreSQL is accessible
psql -h localhost -U hiremebahamas_user -d hiremebahamas -c "SELECT 1;"

# Check environment variable
echo $DATABASE_URL
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
```

## 📚 Additional Resources

- [Backend API Documentation](http://localhost:8000/docs)
- [PostgreSQL Setup Guide](./POSTGRESQL_SETUP.md)
- [Docker Configuration](./docker-compose.yml)
- [Render Deployment Guide](./RAILWAY_DATABASE_SETUP.md)

## ⚠️ Important Notes

1. **PostgreSQL Required**: Production mode requires PostgreSQL. Use `docker-compose -f docker-compose.local.yml up postgres redis` to start.

2. **No SQLite**: SQLite is NOT used in production mode for data integrity and performance.

3. **Environment Variables**: Always use production-appropriate values for SECRET_KEY and other sensitive config.

4. **Build Step Required**: Frontend changes need `npm run build` to take effect.

5. **Database Migrations**: Run migrations when schema changes:
   ```bash
   cd backend
   alembic upgrade head
   ```

6. **Performance**: Production builds are optimized but take longer to build initially.

## 🔐 Security Considerations

- Change default SECRET_KEY in production deployments
- Use strong database passwords
- Enable SSL for remote PostgreSQL connections
- Keep dependencies updated
- Review CORS settings for production domains

---

**Built with ❤️ for the Bahamas professional community**

*Production Mode: Stable. Tested. Ready.*
