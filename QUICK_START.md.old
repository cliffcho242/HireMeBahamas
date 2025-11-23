# 🚀 HireBahamas - Quick Start Guide

## One-Click Launch Options

### Option 1: Windows Batch File (Easiest!)
Double-click: **`START_HIREBAHAMAS.bat`**

This will automatically:
- ✅ Stop any old processes
- ✅ Start backend server
- ✅ Start frontend server  
- ✅ Open browser to http://localhost:3000
- ✅ Show login page

### Option 2: PowerShell Script (Full Setup)
```powershell
# Basic launch (fast)
powershell -ExecutionPolicy Bypass -File .\setup_and_launch.ps1

# Full setup with database seed
powershell -ExecutionPolicy Bypass -File .\setup_and_launch.ps1 -FullSetup
```

### Option 3: Manual Launch
```bash
# Terminal 1 - Backend
python clean_backend.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

## 🔐 Default Login

**Test Account (Admin):**
- Email: `admin@hirebahamas.com`
- Password: `admin123`

**Other Accounts:**
- `john@hirebahamas.com` / `password123` (Job Seeker)
- `sarah@hirebahamas.com` / `password123` (Employer)
- `mike@hirebahamas.com` / `password123` (Job Seeker)
- `emma@hirebahamas.com` / `password123` (Employer)

## 🎯 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:3000 | Facebook-style home page |
| **Login** | http://localhost:3000/login | Enhanced login page |
| **Status** | http://localhost:3000/status.html | System diagnostics |
| **Backend** | http://127.0.0.1:8008 | API server |
| **Health** | http://127.0.0.1:8008/health | API health check |

## 🌟 Facebook-Style Features

### Login Page
- ✨ Modern gradient design
- 🎨 Animated feature highlights
- 📊 Platform statistics
- 🔑 Quick test account button
- 📱 Fully responsive

### Home Page
- 📖 Stories bar (like Facebook)
- ✍️ Create post with modal
- 💬 Posts feed with likes/comments
- 💌 Real-time messaging
- 🔔 Notifications center
- 👥 Friends online sidebar
- 🎨 3-column Facebook layout

### Social Features
- ❤️ Like posts
- 💬 Comment on posts
- 📤 Share functionality
- 👋 Friend requests
- 💼 Job postings
- 📸 Photo uploads
- 🎬 Video support (ready)

## 🛠 Tech Stack

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS
- Framer Motion (animations)
- Heroicons (icons)
- React Hot Toast (notifications)

**Backend:**
- Python Flask
- SQLite database
- JWT authentication
- CORS enabled

## 📱 Responsive Design

Works perfectly on:
- 🖥️ Desktop (1920px+)
- 💻 Laptop (1024px+)
- 📱 Tablet (768px+)
- 📱 Mobile (320px+)

## 🔧 Troubleshooting

### Port Already in Use
```powershell
# Stop all processes
Get-Process | Where-Object { $_.ProcessName -like "*node*" -or $_.ProcessName -like "*python*" } | Stop-Process -Force
```

### Database Issues
```bash
# Reset and seed database
python seed_data.py
```

### Browser Not Opening
Manually navigate to: http://localhost:3000

### API Connection Failed
1. Check backend is running: http://127.0.0.1:8008/health
2. Check browser console for errors
3. Try diagnostic page: http://localhost:3000/status.html

## 🎨 Customization

### Change Colors
Edit `frontend/tailwind.config.js` or component classes

### Modify Layout
Edit components in `frontend/src/components/`:
- `Stories.tsx` - Stories bar
- `PostFeed.tsx` - Main feed
- `CreatePostModal.tsx` - Post creation
- `Messages.tsx` - Chat interface
- `Notifications.tsx` - Notification center
- `FriendsOnline.tsx` - Friends sidebar

### Add Features
1. Create new component in `frontend/src/components/`
2. Import into `Home.tsx`
3. Add API endpoint in `clean_backend.py`

## 📚 Project Structure

```
HireBahamas/
├── START_HIREBAHAMAS.bat      # One-click launcher
├── setup_and_launch.ps1        # PowerShell automation
├── clean_backend.py            # Backend server
├── seed_data.py                # Database seeder
├── hirebahamas.db             # SQLite database
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.tsx      # Enhanced login
│   │   │   ├── Home.tsx       # Facebook-style home
│   │   │   └── ...
│   │   ├── components/
│   │   │   ├── Stories.tsx    # Stories feature
│   │   │   ├── PostFeed.tsx   # Posts feed
│   │   │   ├── CreatePostModal.tsx
│   │   │   ├── Messages.tsx   # Chat
│   │   │   ├── Notifications.tsx
│   │   │   └── FriendsOnline.tsx
│   │   └── services/
│   │       └── api.ts         # API client
│   │
│   └── public/
│       ├── status.html        # Diagnostic page
│       └── ...
```

## 🚀 Next Steps

1. **Launch the app** using any method above
2. **Login** with test credentials
3. **Explore** Facebook-style features:
   - Create posts
   - Like and comment
   - Send messages
   - View notifications
   - Browse jobs
4. **Customize** to your needs
5. **Deploy** when ready

## 💡 Pro Tips

- Use "Test Account" button on login for quick access
- Check status page for system health
- Press Ctrl+C in terminals to stop servers
- Use diagnostic tools for debugging

## 📞 Support

If you encounter issues:
1. Check status page: http://localhost:3000/status.html
2. Review browser console (F12)
3. Check terminal output
4. Restart using launcher script

---

**Built for the Bahamas professional community** 🇧🇸

*Connect. Share. Grow.* 🌴
