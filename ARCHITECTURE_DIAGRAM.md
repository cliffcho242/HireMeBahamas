# 🏗️ HireMeBahamas Architecture & Connection Diagram

Visual guide to understand how different deployment options connect together.

---

## 🎯 Deployment Options - Visual Overview

### Option 1: Vercel Full Stack (Recommended) ⭐

```
┌─────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                        │
│                   https://your-app.vercel.app                │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTPS
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    VERCEL EDGE NETWORK                       │
│                    (Global CDN - 30+ Locations)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React Frontend (Static Assets)                      │   │
│  │  - HTML, CSS, JS bundles                            │   │
│  │  - Images, fonts                                    │   │
│  │  - Service Worker (PWA)                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Serverless Functions (/api/*)                       │   │
│  │  - Python 3.12                                      │   │
│  │  - Flask/FastAPI backend                            │   │
│  │  - Auto-scaling                                     │   │
│  │  - 10s timeout per function                         │   │
│  └────────────────────────┬─────────────────────────────┘   │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │
                            │ PostgreSQL Protocol
                            │ (with connection pooling)
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              VERCEL POSTGRES (Neon)                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  PostgreSQL 15 (Serverless)                         │    │
│  │  - Automatic scaling                                │    │
│  │  - 0.5 GB storage (Free tier)                       │    │
│  │  - Hibernates after inactivity                      │    │
│  │  - Wakes instantly on query                         │    │
│  │  - Built-in connection pooling                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  Tables:                                                      │
│  - users, posts, jobs, messages, notifications               │
│  - comments, likes, follows, etc.                            │
└───────────────────────────────────────────────────────────────┘

✅ Benefits:
- Single deployment (one vercel.json)
- <200ms response time globally
- Zero cold starts for frontend
- Automatic HTTPS and SSL
- $0/month on free tier
- Scales automatically

📊 Cost: $0 - $5/month
```

---

### Option 2: Vercel Frontend + Railway Backend

```
┌─────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                        │
│                   https://your-app.vercel.app                │
└───────────┬─────────────────────────────────────┬───────────┘
            │                                     │
            │ Frontend Assets                     │ API Calls
            │                                     │
┌───────────▼─────────────────┐    ┌─────────────▼────────────┐
│    VERCEL EDGE NETWORK      │    │  RAILWAY CONTAINER       │
│                             │    │  (US West / US East)     │
│  ┌─────────────────────┐    │    │                          │
│  │ React Frontend      │    │    │  ┌──────────────────┐    │
│  │ - Static Files      │    │    │  │ Docker Container │    │
│  │ - PWA               │    │    │  │                  │    │
│  │ - Service Worker    │    │    │  │ - Python 3.12   │    │
│  └─────────────────────┘    │    │  │ - Flask/FastAPI │    │
│                             │    │  │ - uvicorn       │    │
│  Frontend connects to:      │    │  │ - 4 workers     │    │
│  VITE_API_URL=              │    │  └────────┬─────────┘    │
│  https://your-app.up.       │◄───┼───────────┘              │
│    railway.app              │    │                          │
└─────────────────────────────┘    │  Health: /health         │
                                   │  API: /api/*             │
                                   └────────────┬─────────────┘
                                                │
                                                │ Private Network
                                                │ (No egress fees!)
                                                │
                                   ┌────────────▼─────────────┐
                                   │ RAILWAY POSTGRES         │
                                   │                          │
                                   │  PostgreSQL 15           │
                                   │  - Always-on             │
                                   │  - Private network       │
                                   │  - Automatic backups     │
                                   │  - 1GB storage (free)    │
                                   └──────────────────────────┘

✅ Benefits:
- Dedicated backend container
- Long-running processes support
- WebSocket support
- Background tasks
- Private network (no egress fees)
- Railway free tier: 500 hours/month

📊 Cost: $0 - $5/month
```

---

### Option 3: Vercel Frontend + Render Backend

```
┌─────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                        │
│                   https://your-app.vercel.app                │
└───────────┬─────────────────────────────────────┬───────────┘
            │                                     │
            │ Frontend Assets                     │ API Calls
            │                                     │
┌───────────▼─────────────────┐    ┌─────────────▼────────────┐
│    VERCEL EDGE NETWORK      │    │  RENDER WEB SERVICE      │
│                             │    │  (US West / US East)     │
│  ┌─────────────────────┐    │    │                          │
│  │ React Frontend      │    │    │  ┌──────────────────┐    │
│  │ - Static Files      │    │    │  │ Docker Container │    │
│  │ - PWA               │    │    │  │                  │    │
│  │ - Service Worker    │    │    │  │ - Python 3.12   │    │
│  └─────────────────────┘    │    │  │ - Flask/FastAPI │    │
│                             │    │  │ - uvicorn       │    │
│  Frontend connects to:      │    │  │ - 4 workers     │    │
│  VITE_API_URL=              │    │  └────────┬─────────┘    │
│  https://your-app.onrender. │◄───┼───────────┘              │
│    com                      │    │                          │
└─────────────────────────────┘    │  Health: /health         │
                                   │  API: /api/*             │
                                   │                          │
                                   │  ⚠️  Free tier sleeps    │
                                   │     after 15 min         │
                                   └────────────┬─────────────┘
                                                │
                                                │ Internal URL
                                                │ (Same region)
                                                │
                                   ┌────────────▼─────────────┐
                                   │ RENDER POSTGRES          │
                                   │                          │
                                   │  PostgreSQL 15           │
                                   │  - Internal connection   │
                                   │  - Automatic backups     │
                                   │  - 1GB storage (free)    │
                                   │  - 90 day limit          │
                                   └──────────────────────────┘

✅ Benefits:
- Simple deployment
- Internal database connection
- Automatic SSL
- Easy scaling
- Git-based deployment

⚠️ Note: Free tier has cold starts (15 min)
Upgrade to Starter ($7/mo) for always-on

📊 Cost: $0 (with cold starts) or $7+/month
```

---

## 🔗 Connection Flow Details

### HTTP Request Flow (Vercel Full Stack)

```
1. User visits https://your-app.vercel.app
   │
   ▼
2. Vercel Edge serves React frontend
   │
   ▼
3. User clicks "Login"
   │
   ▼
4. Frontend sends POST /api/auth/login
   │
   ▼
5. Vercel Serverless Function processes request
   │   - Validates credentials
   │   - Queries database
   │   - Generates JWT token
   │
   ▼
6. Database query via connection pool
   │   - Uses POSTGRES_URL
   │   - SSL/TLS encryption
   │   - Connection pooling (5 connections)
   │
   ▼
7. Response sent back to frontend
   │   - JWT token
   │   - User data
   │
   ▼
8. Frontend stores token in localStorage
   │
   ▼
9. Subsequent requests include JWT in Authorization header
```

---

## 🗄️ Database Connection Patterns

### Vercel Postgres Connection String

```
Format:
postgresql://default:PASSWORD@ep-xxxxx.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require

Parts:
┌─────────────────────────────────────────────────────────────────────────────┐
│ postgresql://  │  Protocol (must be postgresql:// for SQLAlchemy)            │
├────────────────┼─────────────────────────────────────────────────────────────┤
│ default        │  Username (always "default" for Vercel Postgres)           │
├────────────────┼─────────────────────────────────────────────────────────────┤
│ PASSWORD       │  Your database password (copy from Vercel dashboard)       │
├────────────────┼─────────────────────────────────────────────────────────────┤
│ ep-xxxxx...    │  Hostname (Neon endpoint)                                  │
├────────────────┼─────────────────────────────────────────────────────────────┤
│ 5432           │  Port (standard PostgreSQL port)                           │
├────────────────┼─────────────────────────────────────────────────────────────┤
│ verceldb       │  Database name (always "verceldb")                         │
├────────────────┼─────────────────────────────────────────────────────────────┤
│ sslmode=require│  SSL mode (required for secure connection)                 │
└────────────────┴─────────────────────────────────────────────────────────────┘
```

### Railway Postgres Connection String

```
Private Network (Recommended - No Egress Fees):
postgresql://postgres:PASSWORD@postgres.railway.internal:5432/railway

Public Network (TCP Proxy - Has Egress Fees):
postgresql://postgres:PASSWORD@containers-us-west-1.railway.app:5432/railway

App Priority:
1. DATABASE_PRIVATE_URL (if set) ✅
2. DATABASE_URL (fallback)
```

### Render Postgres Connection String

```
Internal URL (Recommended - Same Region):
postgresql://user:PASSWORD@dpg-xxxxx-a/database

External URL (Public - Any Region):
postgresql://user:PASSWORD@dpg-xxxxx-a.oregon-postgres.render.com:5432/database
```

---

## 🔐 Environment Variables Flow

### How Environment Variables Work

```
Development (.env file)
    │
    ▼
Git Push
    │
    ▼
Platform Dashboard (Vercel/Railway/Render)
    │
    ├─► Set environment variables
    │   - DATABASE_URL
    │   - SECRET_KEY
    │   - JWT_SECRET_KEY
    │   - ENVIRONMENT=production
    │
    ▼
Deployment Build
    │
    ├─► Backend reads environment variables
    │   - os.getenv('DATABASE_URL')
    │   - os.getenv('SECRET_KEY')
    │
    ▼
Runtime
    │
    └─► Application uses values
        - Connects to database
        - Signs JWT tokens
        - Configures CORS
```

---

## 🚀 Scaling Patterns

### Vercel Full Stack Scaling

```
Light Traffic (0-100 users/day)
    │ Free tier handles easily
    │ Serverless scales automatically
    │ Database hibernates when idle
    │
    ▼ Cost: $0/month

Medium Traffic (100-1,000 users/day)
    │ Serverless scales to demand
    │ Database stays warm
    │ May hit free tier limits
    │
    ▼ Cost: $0-5/month

Heavy Traffic (1,000+ users/day)
    │ Upgrade to Pro plan
    │ Dedicated database resources
    │ Enhanced monitoring
    │
    ▼ Cost: $20-50/month
```

### Railway/Render Scaling

```
Light Traffic (0-100 users/day)
    │ Free tier sufficient
    │ Container runs 24/7
    │ Database always on
    │
    ▼ Cost: $0/month (Railway) or $7/month (Render Starter)

Medium Traffic (100-1,000 users/day)
    │ May need Pro plan
    │ Add horizontal scaling
    │ Load balancing
    │
    ▼ Cost: $5-20/month

Heavy Traffic (1,000+ users/day)
    │ Multiple containers
    │ Read replicas
    │ CDN for assets
    │
    ▼ Cost: $50-200/month
```

---

## 📊 Performance Comparison

```
┌──────────────────┬───────────┬──────────────┬──────────────┐
│ Metric           │ Vercel    │ Railway      │ Render       │
├──────────────────┼───────────┼──────────────┼──────────────┤
│ Cold Start       │ None      │ None         │ 30-60s (Free)│
│ API Response     │ <200ms    │ <300ms       │ <400ms       │
│ Database Latency │ <50ms     │ <10ms        │ <20ms        │
│ Global CDN       │ ✅ Yes    │ ❌ No        │ ❌ No        │
│ Auto-scaling     │ ✅ Yes    │ ⚠️  Manual   │ ⚠️  Manual   │
│ Deployment Time  │ 2-3 min   │ 3-5 min      │ 5-10 min     │
└──────────────────┴───────────┴──────────────┴──────────────┘
```

---

## 🎯 Decision Tree

```
Choose Your Deployment:

START
  │
  ├─► Want simplest setup?
  │   └─► YES → Vercel Full Stack ⭐
  │
  ├─► Need long-running processes?
  │   └─► YES → Railway or Render
  │
  ├─► Budget constraint: $0/month?
  │   └─► YES → Vercel Full Stack
  │
  ├─► Need WebSocket support?
  │   └─► YES → Railway (better WebSocket support)
  │
  ├─► Already using Render?
  │   └─► YES → Vercel + Render
  │
  └─► Not sure? → Vercel Full Stack (recommended)
```

---

## 📚 Additional Resources

- **[DEPLOYMENT_CONNECTION_GUIDE.md](./DEPLOYMENT_CONNECTION_GUIDE.md)** - Complete deployment guide
- **[QUICK_DEPLOYMENT_REFERENCE.md](./QUICK_DEPLOYMENT_REFERENCE.md)** - Quick reference
- **[VERCEL_POSTGRES_SETUP.md](./VERCEL_POSTGRES_SETUP.md)** - Vercel Postgres details
- **[RAILWAY_DATABASE_SETUP.md](./RAILWAY_DATABASE_SETUP.md)** - Railway database setup

---

**Need help?** Check the [Troubleshooting section](./DEPLOYMENT_CONNECTION_GUIDE.md#troubleshooting) in the deployment guide.

*Last Updated: December 2025*
