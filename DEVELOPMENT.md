# 📋 HireBahamas Development Guide

## 🚀 Getting Started

### Prerequisites
- **Node.js 18+** for frontend development
- **Python 3.11+** for backend development
- **PostgreSQL 15+** for database
- **Redis** for caching and sessions
- **Docker & Docker Compose** for containerized development

### Quick Setup

#### Option 1: Docker Compose (Recommended)
```bash
# Clone and navigate to project
git clone <your-repo-url>
cd HireBahamas

# Run setup script
chmod +x setup.sh
./setup.sh

# Or for Windows
./setup.ps1
```

#### Option 2: Manual Setup

**Backend Setup:**
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your database and API keys

# Run migrations (if using Alembic)
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

**Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env
# Edit .env with your API URLs

# Start development server
npm run dev
```

**Database Setup:**
```bash
# Using Docker
docker run --name hirebahamas-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=hirebahamas -p 5432:5432 -d postgres:15

# Using Docker Compose
docker-compose up postgres -d
```

## 🏗️ Project Structure

```
HireBahamas/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   │   ├── auth.py     # Authentication routes
│   │   │   ├── jobs.py     # Job management routes
│   │   │   ├── messages.py # Real-time messaging
│   │   │   ├── reviews.py  # Review system
│   │   │   └── upload.py   # File upload handling
│   │   ├── core/           # Core functionality
│   │   │   ├── security.py # JWT & password hashing
│   │   │   ├── upload.py   # File handling utilities
│   │   │   └── socket_manager.py # Socket.IO management
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── database.py     # Database configuration
│   │   └── main.py         # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Container configuration
│   └── .env.example       # Environment template
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── contexts/       # React contexts (Auth, Socket)
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service functions
│   │   ├── types/          # TypeScript definitions
│   │   └── App.tsx         # Main application
│   ├── package.json        # Node.js dependencies
│   ├── Dockerfile         # Production container
│   ├── Dockerfile.dev     # Development container
│   └── .env.example       # Environment template
├── docker-compose.yml      # Multi-service orchestration
├── vercel.json            # Vercel deployment config
├── setup.sh               # Unix setup script
├── setup.ps1              # Windows setup script
└── README.md              # Project documentation
```

## 🔧 Development Workflow

### API Development
1. **Create Models** in `backend/app/models.py`
2. **Define Schemas** in `backend/app/schemas/`
3. **Implement Routes** in `backend/app/api/`
4. **Test Endpoints** using FastAPI docs at `http://localhost:8000/docs`

### Frontend Development
1. **Create Components** in `frontend/src/components/`
2. **Add Pages** in `frontend/src/pages/`
3. **Update Routes** in `frontend/src/App.tsx`
4. **Style Components** using Tailwind CSS

### Database Changes
```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get current user
- `PUT /api/auth/profile` - Update profile

### Jobs
- `GET /api/jobs` - List jobs with filters
- `POST /api/jobs` - Create job posting
- `GET /api/jobs/{id}` - Get job details
- `POST /api/jobs/{id}/apply` - Apply to job

### Messages
- `GET /api/messages/conversations` - Get conversations
- `POST /api/messages/conversations` - Start conversation
- `GET /api/messages/conversations/{id}/messages` - Get messages
- `POST /api/messages/conversations/{id}/messages` - Send message

### Reviews
- `POST /api/reviews` - Create review
- `GET /api/reviews/user/{id}` - Get user reviews
- `GET /api/reviews/stats/{id}` - Get review statistics

### Upload
- `POST /api/upload/avatar` - Upload profile image
- `POST /api/upload/portfolio` - Upload portfolio images
- `POST /api/upload/document` - Upload documents

## 🔒 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/hirebahamas
SECRET_KEY=your-super-secret-key
CLOUDINARY_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name
```

## 🚀 Deployment

### Frontend (Vercel)
1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables in Vercel dashboard
4. Deploy automatically on push

### Backend (Render/Heroku)
1. Create new web service
2. Connect GitHub repository
3. Set environment variables
4. Configure build and start commands:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Database (Render/Heroku Postgres)
1. Create PostgreSQL instance
2. Copy connection URL to `DATABASE_URL`
3. Run migrations on first deploy

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Tests
```bash
npm run test:e2e
```

## 📱 Features Overview

### ✅ Implemented
- [x] User authentication (JWT)
- [x] Job posting and browsing
- [x] Real-time messaging (Socket.IO)
- [x] File upload (Cloudinary integration)
- [x] Review and rating system
- [x] Responsive design (Tailwind CSS)
- [x] API documentation (FastAPI/Swagger)

### 🚧 In Development
- [ ] Payment integration
- [ ] Advanced search and filters
- [ ] Email notifications
- [ ] Mobile app (React Native)
- [ ] Admin dashboard

### 🔮 Planned Features
- [ ] Video calls integration
- [ ] Skills verification
- [ ] Project templates
- [ ] Analytics dashboard
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Email: support@hirebahamas.com
- Discord: [HireBahamas Community](https://discord.gg/hirebahamas)
- Documentation: [docs.hirebahamas.com](https://docs.hirebahamas.com)

---

**Made with ❤️ in the Bahamas 🇧🇸**