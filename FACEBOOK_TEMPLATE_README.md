# 🌴 HireBahamas Facebook-Style Platform

A modern, Facebook-inspired job platform specifically designed for the Bahamas job market. This template provides an intuitive, social media-like experience for job seekers and employers.

## ✨ Features

### 🎨 Facebook-Like Interface
- **Modern Design**: Clean, familiar interface inspired by Facebook's layout
- **Animated Components**: Smooth animations using Framer Motion
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Intuitive Navigation**: Easy-to-use sidebar, top navigation, and quick actions

### 🔐 Authentication System
- **Secure Login/Signup**: JWT-based authentication with bcrypt password hashing
- **User Types**: Support for Job Seekers, Employers, and Recruiters
- **Demo Account**: Quick demo login functionality
- **Password Recovery**: Built-in password reset workflow

### 💼 Job Management
- **Job Feed**: Facebook-style feed showing job opportunities
- **Interactive Cards**: Like, comment, save, and share job posts
- **Application Tracking**: Track applications, saved jobs, and profile views
- **Smart Filtering**: Filter by location, salary, job type, and skills

### 📱 Social Features
- **Activity Dashboard**: Track your job search activity
- **Trending Topics**: See what's trending in the Bahamas job market
- **Suggestions**: Get personalized recommendations
- **Quick Actions**: One-click access to common tasks

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- Python 3.8+
- Git

### 1. Clone & Setup
```bash
git clone <repository>
cd HireBahamas
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install flask flask-cors pyjwt bcrypt

# Start the backend server
python clean_backend.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. One-Click Launch (Windows)
Simply double-click `launch_facebook_style.bat` to start both backend and frontend automatically!

## 🎯 Default Login Credentials

```
Email: admin@hirebahamas.com
Password: admin123
```

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Lucide React** for icons
- **React Router** for navigation

### Backend
- **Flask** with Python
- **SQLite** database
- **JWT** for authentication
- **bcrypt** for password hashing
- **CORS** enabled for frontend communication

## 📁 Project Structure

```
HireBahamas/
├── 📱 frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FacebookLikeAuth.tsx      # Modern login/signup
│   │   │   └── FacebookLikeDashboard.tsx # Main dashboard
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx           # Authentication state
│   │   ├── AppFacebook.tsx               # Main app component
│   │   └── main.tsx                      # Entry point
│   └── package.json
├── 🔧 backend/
│   └── clean_backend.py                  # Flask API server
├── 🗄️ hirebahamas.db                    # SQLite database
└── 🚀 launch_facebook_style.bat         # Quick launcher
```

## 🎨 UI Components

### Authentication (`FacebookLikeAuth.tsx`)
- Modern login/signup forms with smooth transitions
- User type selection (Job Seeker, Employer, Recruiter)
- Form validation and error handling
- Demo account quick access
- Mobile-responsive design

### Dashboard (`FacebookLikeDashboard.tsx`)
- Facebook-style top navigation
- Three-column layout (sidebar, feed, widgets)
- Job cards with interaction buttons
- Activity tracking
- Trending topics
- Quick actions panel

## 🌟 Key Features Explained

### 🎯 Job Feed
The main feed displays job opportunities in a familiar, social media format:
- **Job Cards**: Rich job information with company logos
- **Interactions**: Like, comment, save, and share buttons
- **Application Tracking**: See how many people applied
- **Real-time Updates**: Live job posting feed

### 📊 Activity Dashboard
Track your job search progress:
- **Profile Views**: See who's viewing your profile
- **Applications Sent**: Track your job applications
- **Saved Jobs**: Quick access to bookmarked positions
- **Network Growth**: Monitor your professional connections

### 🔍 Smart Search
Advanced search functionality:
- **Global Search**: Search jobs, companies, and people
- **Smart Filters**: Filter by location, salary, type
- **Saved Searches**: Save your favorite search queries
- **Search Suggestions**: Get intelligent search recommendations

## 🎨 Customization

### Themes & Colors
The platform uses a modern color scheme that can be easily customized:
- **Primary**: Blue (#3B82F6)
- **Secondary**: Gray (#6B7280)
- **Success**: Green (#10B981)
- **Warning**: Orange (#F59E0B)
- **Error**: Red (#EF4444)

### Layout Options
- **Sidebar**: Toggle left sidebar visibility
- **Feed Width**: Customize main content width
- **Card Layout**: Switch between grid and list views
- **Mobile Layout**: Responsive design for all devices

## 🔧 Configuration

### Environment Variables
Create a `.env` file for custom configuration:
```env
REACT_APP_API_URL=http://localhost:8008
REACT_APP_APP_NAME=HireBahamas
REACT_APP_VERSION=1.0.0
```

### Backend Configuration
Modify `clean_backend.py` for:
- Database settings
- JWT secret keys
- CORS policies
- API endpoints

## 📱 Mobile Experience

The platform is fully responsive with:
- **Touch-Friendly**: Large buttons and touch targets
- **Mobile Navigation**: Collapsible sidebar and bottom navigation
- **Optimized Performance**: Fast loading on mobile networks
- **Native Feel**: Smooth animations and transitions

## 🚀 Deployment

### Development
- Backend: `python clean_backend.py` (runs on port 8008)
- Frontend: `npm run dev` (runs on port 3000+)

### Production
- Backend: Deploy Flask app to Heroku, AWS, or similar
- Frontend: Build with `npm run build` and deploy to Netlify, Vercel
- Database: Upgrade to PostgreSQL or MySQL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

Need help? Here are some resources:
- **Documentation**: Check this README and code comments
- **Issues**: Report bugs via GitHub Issues
- **Community**: Join our Discord community
- **Email**: Contact support@hirebahamas.com

## 🎉 Success Stories

> "This Facebook-like interface made job searching in the Bahamas so much easier! The familiar layout helped me find my dream job in hospitality." - Sarah M., Hotel Manager

> "As an employer, I love how easy it is to post jobs and see candidate interactions. The platform feels modern and professional." - Michael R., HR Director

---

**Made with ❤️ for the Bahamas job market**

*Transform your job search experience with our modern, social-inspired platform designed specifically for Bahamian professionals and employers.*