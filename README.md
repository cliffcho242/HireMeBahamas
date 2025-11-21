# HireMeBahamas - Facebook-Style Professional Social Network 🇧🇸

A modern, Facebook-inspired social platform designed specifically for professionals in the Bahamas to connect, share career opportunities, and build meaningful professional relationships.

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

**One-command installation for all dependencies:**

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

### Prerequisites
- Node.js 18+
- Python 3.8+
- SQLite3 or PostgreSQL
- Redis (optional, for caching)

### Installation Steps

1. **Clone and Setup**
```bash
cd HireMeBahamas
pip install -r requirements.txt
cd frontend && npm install
```

2. **Database Setup**

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

3. **Launch Application**
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
- Image upload
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

## 🚀 Deployment

### Development
```bash
# Backend
python app.py

# Frontend
cd frontend && npm run dev
```

### Production
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

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/hiremebahamas
SECRET_KEY=your_secret_key
CLOUDINARY_NAME=your_cloudinary_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
REDIS_URL=redis://localhost:6379
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000
```

## CI/CD

This repository includes GitHub Actions workflows for continuous integration and deployment:

- **CI Pipeline** (`.github/workflows/ci.yml`): Runs on every push and pull request
  - Lints Python and JavaScript code
  - Checks Python syntax
  - Builds the frontend
  - Uploads build artifacts

- **Deployment** (`.github/workflows/deploy.yml`): Automatically deploys to Render on merge to main
  - Triggers Render deployment via webhook
  - Manual deployment trigger available
  - See [.github/RENDER_DEPLOYMENT.md](.github/RENDER_DEPLOYMENT.md) for setup instructions

### GitHub Copilot Workspace

If you're using GitHub Copilot Workspace, see [.github/COPILOT_WORKSPACE_INFO.md](.github/COPILOT_WORKSPACE_INFO.md) for information about runtime logs and monitoring.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details.