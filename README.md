# HireMeBahamas - Facebook-Style Professional Social Network 🇧🇸

![Deploy Status](https://github.com/cliffcho242/HireMeBahamas/actions/workflows/ci.yml/badge.svg)

A modern, Facebook-inspired social platform designed specifically for professionals in the Bahamas to connect, share career opportunities, and build meaningful professional relationships.

---

## 🚨 **IMPORTANT: Users Can't Sign In? Fix Deployment Issues**

**If users cannot sign in**, your deployment configuration is likely incomplete.

### 🔧 Quick Fix (5 minutes):

📖 **[COMPLETE FIX GUIDE: Sign-In & Deployment Issues](./FIX_SIGN_IN_DEPLOYMENT_GUIDE.md)**

This guide covers:
- ✅ Configuring GitHub Secrets for automated deployments
- ✅ Setting up Vercel environment variables
- ✅ Connecting PostgreSQL database (Railway/Render)
- ✅ Troubleshooting common deployment issues
- ✅ Verifying sign-in functionality

### 🔥 **Getting 404: DEPLOYMENT_NOT_FOUND Error?**

📖 **[TROUBLESHOOTING: Deployment Not Found](./TROUBLESHOOTING_DEPLOYMENT_NOT_FOUND.md)** - Complete troubleshooting guide
📖 **[FIX: Vercel 404 Deployment Error](./VERCEL_DEPLOYMENT_404_FIX.md)** - Detailed fix documentation

These comprehensive guides cover:
- ✅ Step-by-step troubleshooting process
- ✅ Common causes and solutions
- ✅ Fixing Vercel configuration conflicts
- ✅ Resolving mixed API version issues
- ✅ Proper serverless function setup
- ✅ Complete verification steps

**Verify your configuration:**
```bash
python3 scripts/verify-vercel-deployment.py
```

**Common issues:**
- Missing `VERCEL_TOKEN`, `VERCEL_ORG_ID`, or `VERCEL_PROJECT_ID` secrets in GitHub
- `DATABASE_URL`, `SECRET_KEY`, or `JWT_SECRET_KEY` not set in Vercel
- Database not connected or not accessible
- Conflicting `vercel.json` configuration files
- Build failures or missing output directory

---

## 🚀 **NEW: Complete Deployment & Connection Guides**

**📖 [START HERE: Deployment Guide](./START_HERE_DEPLOYMENT.md)** - Your starting point for deployment

**🔗 [DIRECT LINKS: Where to Configure Everything](./DIRECT_LINKS_WHERE_TO_CONFIGURE.md)** - Exact dashboard links for Vercel, Railway, and Render

**🎯 [WHERE TO PUT DATABASE URL](./WHERE_TO_PUT_DATABASE_URL.md)** - Exact instructions showing where to paste your database URL

Choose your deployment guide:
- 🌟 **[Complete Deployment & Connection Guide](./DEPLOYMENT_CONNECTION_GUIDE.md)** - Step-by-step for all platforms
- ⚡ **[Quick Deployment Reference](./QUICK_DEPLOYMENT_REFERENCE.md)** - One-page quick reference
- 🏗️ **[Architecture Diagram](./ARCHITECTURE_DIAGRAM.md)** - Visual connection flows

---

## 🚀 **RECOMMENDED: Complete Vercel Deployment**

**Deploy frontend + backend together on Vercel in 10 minutes!**

✅ **$0/month** - Free tier covers most apps  
✅ **<200ms response** - Global edge network  
✅ **Zero cold starts** - Always fast  
✅ **One deployment** - Frontend + backend together  
✅ **Auto HTTPS** - SSL included  
✅ **61 API endpoints** - Full backend integrated  

### 📖 Complete Deployment & Database Connection Guides

Choose your deployment platform and follow the step-by-step guide:

- 🌟 **[DEPLOYMENT_CONNECTION_GUIDE.md](./DEPLOYMENT_CONNECTION_GUIDE.md)** - Complete guide with direct links and instructions for Vercel, Railway, and Render
- ⚡ **[QUICK_DEPLOYMENT_REFERENCE.md](./QUICK_DEPLOYMENT_REFERENCE.md)** - One-page quick reference with all commands and URLs
- 📚 **[VERCEL_POSTGRES_SETUP.md](./VERCEL_POSTGRES_SETUP.md)** - Detailed Vercel Postgres setup
- 🚂 **[RAILWAY_DATABASE_SETUP.md](./RAILWAY_DATABASE_SETUP.md)** - Railway database configuration

### Quick Deploy to Vercel

1. **Push to GitHub** (if not already done)
2. **Import to Vercel**: [vercel.com/new](https://vercel.com/new)
3. **Add Environment Variables**:
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   SECRET_KEY=your-secret-key-32-chars
   JWT_SECRET_KEY=your-jwt-secret-32-chars
   ENVIRONMENT=production
   ```
4. **Deploy!** ✅

📚 **[Complete Deployment & Connection Guide](./DEPLOYMENT_CONNECTION_GUIDE.md)** - Everything you need to connect your database and deploy to Vercel, Railway, or Render

---

## 🚀 Production Mode (Recommended for Local Development)

**NEW**: Run HireMeBahamas in full production mode with PostgreSQL!

### Prerequisites
- **Docker & Docker Compose** - [Install Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Windows/macOS: Docker Desktop includes everything
  - Linux: See [DOCKER_SETUP.md](./DOCKER_SETUP.md)

### Quick Start
```bash
# Linux/macOS
./start_production.sh

# Windows
start_production.bat
```

This runs the app with:
- ✅ **PostgreSQL** (production-ready database)
- ✅ **Production builds** (optimized, minified)
- ✅ **No hot-reload** (stable, production-like)
- ✅ **Production settings** (security, performance)

📖 **[Read the Production Mode Guide](./PRODUCTION_MODE_GUIDE.md)** for detailed setup instructions.
📖 **[Read the Docker Setup Guide](./DOCKER_SETUP.md)** for Docker installation help.

---

## ✅ Recent Updates: Data Persistence & Session Management

**What's Fixed:**
- ✅ User sessions now persist across page reloads
- ✅ Posts and user data are permanently saved
- ✅ Token refresh system prevents unexpected logouts
- ✅ Fixed SECRET_KEY configuration for consistent authentication
- ✅ All authentication endpoints working correctly

📚 **[Read the Data Persistence Guide](./DATA_PERSISTENCE_GUIDE.md)** for technical details.

**Quick Setup (New Users):**
```bash
# Run the simple setup script
./simple_setup.sh

# Or manually:
cp .env.example .env  # Then edit with your settings
pip install -r requirements.txt
cd frontend && npm install
```

## 🚀 Auto-Deploy Enabled

This repository is configured with **automated deployments** via GitHub Actions:
- 🌐 **Frontend**: Auto-deploys to Vercel on every push to `main`
- ⚡ **Backend**: Auto-deploys to Railway/Render on every push to `main`
- ✅ **CI/CD**: Automatic testing and linting on pull requests

👉 **[View Auto-Deploy Setup Guide](./AUTO_DEPLOY_SETUP.md)** for configuration instructions.

### ⚡ Deployment Speed Improvements

**New**: Docker deployments now use **pre-built base images** for significantly faster builds:
- 🚀 **5-10x faster deployments** (no apt-get/apk install during builds)
- ✅ **No more build timeouts** on Railway/Render
- 🔄 **Consistent environment** across all deployments
- 📦 **Base images automatically updated** via GitHub Actions

Base images include all system dependencies pre-installed:
- Backend: `ghcr.io/cliffcho242/hiremebahamas-base-backend:latest`
- Frontend: `ghcr.io/cliffcho242/hiremebahamas-base-frontend:latest`

📖 **[Read Docker Base Images Documentation](./DOCKER_BASE_IMAGES.md)** for technical details.

### 🗄️ Database Setup

**🔗 NEW: [Complete Database Connection Guide with Direct Links](./DATABASE_CONNECTION_GUIDE.md)** 

This comprehensive guide provides:
- ✅ **Direct clickable links** to find database URLs on Vercel, Railway, and Render
- ✅ **Step-by-step instructions** with exact navigation paths
- ✅ **Copy-paste commands** to connect your database
- ✅ **Troubleshooting** for common connection issues
- ✅ **Platform comparison** to help you choose

---

#### Vercel Postgres (⭐ Recommended - Best Performance & Integration)

**NEW**: Full Vercel Postgres support with automated migration tools!

Vercel Postgres offers the best integration for this application:
- ✅ **Zero Cold Starts**: Database stays warm on Vercel's infrastructure
- ✅ **<50ms Latency**: Direct connection from Vercel Edge & Serverless
- ✅ **Free Tier**: 0.5GB storage, perfect for development and small apps
- ✅ **Auto-Scaling**: Serverless architecture scales with your app
- ✅ **Built-in Pooling**: Connection pooling handled automatically
- ✅ **Cost Effective**: $0-5/month vs $7-20/month on Railway/Render

**Quick Setup:**
1. 🔗 **[Database Connection Guide](./DATABASE_CONNECTION_GUIDE.md)** - Direct links and complete walkthrough
2. 📖 **[Complete Setup Guide](./VERCEL_POSTGRES_SETUP.md)** - Detailed step-by-step instructions
3. 📖 **[Migration from Railway/Render](./VERCEL_POSTGRES_MIGRATION_GUIDE.md)** - Zero-downtime migration guide
4. 📖 **[Quick Start](./docs/VERCEL_POSTGRES_QUICK_START.md)** - 5-minute setup

**Automated Migration:**
```bash
# Set environment variables
export RAILWAY_DATABASE_URL="postgresql://user:pass@railway.app:5432/railway"
export VERCEL_POSTGRES_URL="postgresql://user:pass@ep-xxxxx.neon.tech:5432/verceldb"

# Run migration (includes verification)
python scripts/migrate_railway_to_vercel.py

# Verify migration success
python scripts/verify_vercel_postgres_migration.py
```

#### Railway Postgres (Alternative)

Vercel Postgres (powered by Neon) provides serverless PostgreSQL optimized for Vercel:

- ✅ **Free Tier**: 0.5 GB storage (Hobby plan)
- ✅ **Serverless**: Automatic scaling and hibernation
- ✅ **Edge Network**: Low latency worldwide
- ✅ **Simple Setup**: 5-minute configuration

📖 **[Complete Vercel Postgres Setup Guide](./VERCEL_POSTGRES_SETUP.md)** - Step-by-step instructions with connection string configuration, migration guide, and troubleshooting.

#### Railway Postgres (Alternative Option)

For production deployments on Railway, you need to configure PostgreSQL for persistent data storage:

1. **Add PostgreSQL** to your Railway project via the "+ New" button
2. **DATABASE_URL** is automatically configured
3. **Add required environment variables** (SECRET_KEY, JWT_SECRET_KEY, ENVIRONMENT)

🔗 **[Database Connection Guide - Railway Section](./DATABASE_CONNECTION_GUIDE.md#railway-setup)** - Direct links and step-by-step instructions  
📖 **[Complete Railway DATABASE_URL Setup Guide](./RAILWAY_DATABASE_SETUP.md)** - Detailed guide with screenshots and troubleshooting

### 🗄️ Database Admin Interface

For local development, access the built-in database management interface (Adminer):

1. **Start services**: `docker-compose up -d`
2. **Access Adminer**: http://localhost:8081
3. **Login credentials**:
   - Server: `postgres`
   - Username: `hiremebahamas_user`
   - Password: `hiremebahamas_password`
   - Database: `hiremebahamas`

📖 **[Database Admin Interface Guide](./DATABASE_ADMIN_INTERFACE.md)** - Complete guide for using Adminer to inspect and manage your database.

## 🌟 Features

### Core Social Features (Facebook-Style)
- **Stories**: Share temporary updates and highlights
- **Posts & Interactions**: Create posts, like, comment, and share
- **Real-time Messaging**: Chat with connections
- **Notifications**: Stay updated on activities
- **Friends System**: Connect with other professionals

### Professional Focus
- **Job Postings**: Employers can post opportunities
- **Career Networking**: Connect with industry peers
- **Professional Groups**: Join interest-based communities
- **Resume Sharing**: Showcase your professional profile

### Bahamas-Specific Features
- **Local Job Market**: Focus on Bahamas employment
- **Island Networking**: Connect across different islands
- **Cultural Integration**: Embrace Bahamian professional culture

## 🚀 Quick Start

### 🎯 Automated Installation (Recommended)

**NEW: Automated dependency fix for "Failed to load user profile" error:**

```bash
# Install all system dependencies (apt-get) for backend + frontend
sudo python3 automated_dependency_fix.py --install-python-deps

# Then install Node.js packages
cd frontend && npm install
```

📖 **See [AUTOMATED_DEPENDENCY_FIX_README.md](AUTOMATED_DEPENDENCY_FIX_README.md)** for complete instructions.

**Alternative: One-command installation for all dependencies:**

#### Linux/macOS
```bash
./scripts/install_all_dependencies.sh
```

#### Windows
```cmd
scripts\install_all_dependencies.bat
```

#### Docker
```bash
./scripts/docker_install_all.sh
```

These scripts will automatically:
- ✅ Install all system dependencies (Python, Node.js, PostgreSQL, Redis)
- ✅ Install all Python packages from requirements.txt
- ✅ Install all Node.js packages from package.json
- ✅ Configure services (PostgreSQL, Redis)
- ✅ Create environment files
- ✅ Verify installation

📖 **For detailed installation instructions, see [INSTALLATION_COMPLETE.md](INSTALLATION_COMPLETE.md)**

---

### Manual Installation

📦 **For complete system dependency installation instructions, see:**
- **[AUTOMATED_DEPENDENCY_FIX_README.md](AUTOMATED_DEPENDENCY_FIX_README.md)** - NEW: Automated apt-get fix for backend + frontend
- **[INSTALL.md](INSTALL.md)** - Comprehensive production installation guide
- **[DEPENDENCIES_QUICK_REF.md](DEPENDENCIES_QUICK_REF.md)** - Quick reference for apt-get commands

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 13+ (recommended for production) or SQLite3 (development)
- Redis 6+ (required for caching, sessions, and Celery)
- Nginx (for production deployment)
- System build tools (see INSTALL.md for details)

### Installation Steps

1. **Install System Dependencies (Ubuntu/Debian)**
```bash
# One-command installation of all system packages
sudo apt-get update -y && \
sudo apt-get install -y \
    build-essential gcc g++ make pkg-config \
    python3 python3-pip python3-dev python3-venv \
    postgresql postgresql-client libpq-dev \
    redis-server redis-tools \
    libssl-dev libffi-dev libjpeg-dev libpng-dev \
    libevent-dev libxml2-dev libxslt1-dev \
    nginx curl wget git

# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

2. **Clone and Setup**
```bash
cd HireMeBahamas
pip install -r requirements.txt
cd frontend && npm install
```

2. **Verify Installation**
   
   To ensure all authentication dependencies are installed correctly:
   ```bash
   # Test authentication dependencies
   python test_auth_dependencies.py
   
   # Test complete authentication flow (requires backend running)
   python test_authentication_flow.py
   ```
   
   You should see:
   - ✓ All dependencies are installed and working!
   - ✓ Users can sign in and sign out successfully.

3. **Database Setup**

   **For Development (with sample data):**
   ```bash
   python seed_data.py --dev
   ```

   **For Production (no sample data):**
   ```bash
   # Just create tables, no sample data
   python create_posts_table.py
   
   # Set production environment
   export PRODUCTION=true
   ```
   
   **To clean existing sample data:**
   ```bash
   python remove_fake_posts.py
   ```
   
   See [CLEAN_DATABASE.md](CLEAN_DATABASE.md) for detailed cleanup instructions.

4. **Launch Application**
```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\launch_app.ps1 -Force
```

4. **Access Platform**
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8008

## � Default Accounts

| Email | Password | Role | Description |
|-------|----------|------|-------------|
| `admin@hiremebahamas.com` | `admin123` | Admin | Platform administrator |
| `john@hiremebahamas.com` | `password123` | Job Seeker | Regular user |
| `sarah@hiremebahamas.com` | `password123` | Employer | Can post jobs |
| `mike@hiremebahamas.com` | `password123` | Job Seeker | Regular user |
| `emma@hiremebahamas.com` | `password123` | Employer | Can post jobs |

## 🎨 Facebook-Inspired UI

### Layout Structure
```
┌─────────────────────────────────────────────────┐
│ Header: Logo | Search | Navigation | User Menu  │
├─────────────────┬───────────────────────────────┤
│ Left Sidebar    │ Main Feed                      │
│ • Navigation    │ • Stories                      │
│ • Friends       │ • Create Post                  │
│ • Groups        │ • Posts Feed                   │
│                 │   - Like/Comment/Share         │
├─────────────────┼───────────────────────────────┤
│                 │ Right Sidebar                  │
│                 │ • Online Friends               │
│                 │ • Suggested Connections        │
│                 │ • Sponsored Content            │
└─────────────────┴───────────────────────────────┘
```

### Key Components

#### Stories (`Stories.tsx`)
- Horizontal scrollable story cards
- Create story option
- Viewed/unviewed indicators

#### Post Feed (`PostFeed.tsx`)
- Facebook-style post cards
- Like, comment, share actions
- User avatars and timestamps
- Image support

#### Create Post Modal (`CreatePostModal.tsx`)
- Rich text posting
- Image upload (supports local storage, Cloudinary, or Google Cloud Storage)
- Privacy settings
- Character counter

#### Messages (`Messages.tsx`)
- Real-time chat interface
- Conversation list
- Message threads

#### Notifications (`Notifications.tsx`)
- Activity feed
- Mark as read functionality
- Different notification types

## 🛠 Technical Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Router** for navigation
- **React Hot Toast** for notifications
- **Axios** for API calls

### Backend
- **Flask** (Python)
- **SQLite** database
- **JWT** authentication
- **CORS** enabled

### Key Libraries
- **Heroicons** - Icon library
- **React Icons** - Additional icons
- **Date-fns** - Date formatting
- **Socket.io** - Real-time features

## 📱 Responsive Design

The platform is fully responsive with:
- **Mobile-first** approach
- **Adaptive layouts** for all screen sizes
- **Touch-friendly** interactions
- **Optimized performance** on mobile devices

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/profile` - Get user profile

### Posts
- `GET /api/posts` - Get all posts
- `POST /api/posts` - Create new post
- `POST /api/posts/{id}/like` - Like/unlike post
- `POST /api/posts/{id}/comment` - Add comment

### Users
- `GET /api/users` - Get users list
- `GET /api/users/{id}` - Get user details
- `POST /api/users/{id}/friend` - Send friend request

### Health Check
- `GET /health` - Simple health check endpoint (used by Railway/Render for monitoring)
- `GET /api/health` - Detailed health check with database status and connection pool info

## 🎯 User Roles

### Job Seekers
- Create posts and stories
- Apply for jobs
- Network with professionals
- Join groups

### Employers
- Post job opportunities
- View candidate profiles
- Manage company page
- Access premium features

### Administrators
- Manage platform content
- Moderate user activities
- Access analytics
- System configuration

## 🧪 Testing

### Data Persistence Testing

**New: Comprehensive data persistence test suite**

```bash
# Test data persistence and session management
python test_data_persistence.py
```

This test suite verifies:
- ✓ Health check endpoints working
- ✓ User registration and login
- ✓ Token refresh functionality
- ✓ Session verification
- ✓ Profile fetching
- ✓ Database persistence across restarts

### Authentication Testing

Verify that all dependencies are installed correctly for sign in/sign out functionality:

```bash
# Test authentication dependencies (backend libraries)
python test_auth_dependencies.py

# Test complete authentication flow (end-to-end)
# Note: Backend must be running on http://127.0.0.1:8080
python test_authentication_flow.py
```

**What these tests verify:**
- ✓ Flask and Flask-CORS are installed
- ✓ PyJWT (JSON Web Tokens) is working
- ✓ bcrypt password hashing is functional
- ✓ Login endpoint accepts credentials and returns tokens
- ✓ JWT tokens are properly generated and can be validated
- ✓ Users can successfully sign in and sign out

## 🚀 Deployment

### 🎯 Vercel Full-Stack Deployment (Recommended)

**NEW**: Deploy both frontend and backend to Vercel in 10 minutes with $0 cost!

**Benefits:**
- ✅ **$0/month** - Free tier covers most apps
- ✅ **<200ms response** - Global edge network
- ✅ **Zero cold starts** - Always fast
- ✅ **One deployment** - Frontend + backend together
- ✅ **Auto HTTPS** - SSL included
- ✅ **Preview URLs** - Every PR gets a preview

**Quick Start:**
```bash
# 1. Push to GitHub
git push origin main

# 2. Import to Vercel (one-time)
# Go to https://vercel.com → Import Git Repository

# 3. Add environment variables
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret

# 4. Deploy! ✅
```

📚 **[10-Minute Deployment Guide](./VERCEL_QUICK_DEPLOY.md)** - Get started now!  
📖 **[Complete Migration Guide](./VERCEL_MIGRATION_GUIDE.md)** - Full details and troubleshooting

**After Vercel is working:**
- Delete Render services → $0 bill
- Test login on phone - should be <200ms
- Check Vercel logs to see requests

---

### Automated Deployment (Legacy - Railway/Render) ⚡

The repository includes GitHub Actions workflows for automatic deployment:

**Prerequisites:**
1. Set up accounts: Vercel (frontend) and Railway/Render (backend)
2. Configure GitHub Secrets (see [AUTO_DEPLOY_SETUP.md](./AUTO_DEPLOY_SETUP.md))

**Deploy with a single push:**
```bash
git add .
git commit -m "Your changes"
git push origin main
```

GitHub Actions will automatically:
- ✅ Run tests and linting
- ✅ Build and deploy frontend to Vercel
- ✅ Deploy backend to Railway/Render

📚 **Complete Guide**: [AUTO_DEPLOY_SETUP.md](./AUTO_DEPLOY_SETUP.md)  
⚡ **Quick Reference**: [AUTO_DEPLOY_QUICK_REF.md](./AUTO_DEPLOY_QUICK_REF.md)

### High Availability & Scaling

For production deployments requiring high availability:

- **Load Balancing**: Automatic via Railway/Render/Vercel managed platforms
- **Auto-Scaling**: Configure in `render.yaml` or platform dashboard
- **Health Checks**: Built-in `/health` endpoint for load balancer integration
- **Zero-Downtime Deploys**: Rolling updates with graceful shutdown

📚 **Complete Guide**: [docs/HIGH_AVAILABILITY.md](./docs/HIGH_AVAILABILITY.md)

### 🔧 Fixing 502 Bad Gateway on Render

If you're experiencing 502 errors after periods of inactivity on Render, this is because Render free tier services sleep after 15 minutes. **Solution: Migrate to Vercel (see above)** for always-on, free deployment.

Alternative solutions for Render:
1. **Upgrade to Paid Plan** ($7/month) - Service stays always on
2. **External Pinger** (Free) - Use UptimeRobot to ping `/ping` every 5 minutes

📚 **Complete Guide**: [docs/RENDER_502_FIX_GUIDE.md](./docs/RENDER_502_FIX_GUIDE.md)

### Manual Deployment

#### Development
```bash
# Backend
python app.py

# Frontend
cd frontend && npm run dev
```

#### Production
```bash
# Build frontend
cd frontend && npm run build

# Serve static files
# Configure your web server (nginx/apache) to serve the built files
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Troubleshooting
- **Port conflicts**: Check if ports 3000 and 8008 are available
- **Database issues**: Run `python seed_data.py` to reset data
- **Build errors**: Clear node_modules and reinstall

### Common Issues
- **Chrome CORS**: Use the diagnostic page at `/diagnostic.html`
- **Login issues**: Check browser console for errors
- **API errors**: Verify backend is running on port 8008

## 📚 Examples

Check out the [examples directory](./examples/) for additional sample applications:

- **[Prisma Postgres App](./examples/my-prisma-postgres-app/)** - Complete Next.js application using Prisma with Prisma Postgres (Accelerate)
  - Learn how to set up Prisma with Next.js 15
  - Type-safe database access with Prisma Client
  - Database migrations and seeding
  - Perfect starting point for modern database-driven apps

See the [examples README](./examples/README.md) for a complete list of available examples.

## 🎉 What's Next

### Planned Features
- [ ] Video calling integration
- [ ] Advanced search and filters
- [ ] Professional groups and communities
- [ ] Job application tracking
- [ ] Resume builder
- [ ] Event management
- [ ] Mobile app (React Native)

### Enhancements
- [ ] Dark mode support
- [ ] Push notifications
- [ ] Advanced analytics
- [ ] AI-powered job matching
- [ ] Multi-language support

---

**Built with ❤️ for the Bahamas professional community**

*Connect. Grow. Succeed.*
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables

⚠️ **Security Notice**: Never commit secrets to git. See [DOCKER_SECURITY.md](DOCKER_SECURITY.md) for best practices.

### Backend (.env)
```bash
# Copy .env.example to .env and update with your values
cp .env.example .env

# Required variables:
SECRET_KEY=your_secret_key  # Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=postgresql://user:password@localhost/hiremebahamas
REDIS_URL=redis://localhost:6379

# Optional integrations:
CLOUDINARY_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Google Cloud Storage (optional):
GCS_BUCKET_NAME=your_bucket_name
GCS_PROJECT_ID=your_project_id
GCS_CREDENTIALS_PATH=/path/to/credentials.json
GCS_MAKE_PUBLIC=False  # Set to True for public files, False for signed URLs
```

📖 **[Google Cloud Storage Setup Guide](./docs/GOOGLE_CLOUD_STORAGE.md)** - Learn how to configure GCS for file uploads.

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

### Docker Security

This project follows [Docker security best practices](DOCKER_SECURITY.md):
- Secrets are loaded from `.env` files (local) or platform environment (production)
- No secrets in Dockerfiles (no ARG/ENV for sensitive data)
- `.dockerignore` prevents sensitive files from being copied into images
- See [DOCKER_SECURITY.md](DOCKER_SECURITY.md) for detailed information

## Troubleshooting

### GitHub Copilot Model Endpoint Error

If you encounter this error while using GitHub Copilot Workspace:

```
HTTP error 400: bad request: no endpoints available for this model under your current plan and policies
```

**This is not a code issue** - it's related to your GitHub subscription plan's AI model access.

📖 **[Read the complete troubleshooting guide](GITHUB_COPILOT_MODEL_ERROR.md)** for solutions.

**Quick Summary:**
- The error occurs when GitHub Copilot tries to use a model not available in your plan
- Standard GitHub Copilot access works fine for all repository development tasks
- No code changes are needed in the repository
- See the troubleshooting guide for detailed solutions and workarounds

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details.