# Profile Picture Gallery - Quick Start Guide

## 🎯 What's New

You can now upload and manage multiple profile pictures! This feature allows you to:
- Upload up to 10 pictures at once
- Create a personal gallery of profile pictures
- Switch between pictures easily
- Delete unwanted pictures

## 🚀 Quick Setup

### 1. Install System Dependencies
```bash
sudo apt-get update
sudo apt-get install -y libpng-dev libjpeg-dev libwebp-dev zlib1g-dev
```

### 2. Install Python Packages
```bash
pip install Pillow aiofiles python-jose passlib python-multipart
```

### 3. Create Database Table
```bash
python3 create_profile_pictures_table.py
```

### 4. Start the Application
```bash
# Start backend
cd backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8005

# In another terminal, start frontend
cd frontend
npm run dev
```

### 5. Use the Feature
1. Navigate to your Profile page
2. Scroll down to "Profile Pictures" section
3. Click "Add Pictures" to upload
4. Hover over any picture to set it as current or delete it

## 📸 Features

### Upload Pictures
- **Single Upload**: Click "Add Pictures" and select one image
- **Multiple Upload**: Select multiple images at once (max 10)
- **Supported Formats**: JPEG, PNG, GIF, WebP
- **Max Size**: 10MB per image

### Manage Gallery
- View all your pictures in a responsive grid
- See which picture is currently active (blue border with "Current" badge)
- Hover over pictures to see available actions

### Set Current Picture
- Click the checkmark icon on any picture
- Your profile picture updates instantly across the platform
- The active picture is used in:
  - Your profile page
  - Posts and comments
  - Messages
  - Notifications

### Delete Pictures
- Click the trash icon on any picture
- Confirm deletion
- Picture is removed from gallery and storage
- If you delete the current picture, the most recent one becomes active

## 🔒 Security

All features are secure and tested:
- ✅ Authentication required (must be logged in)
- ✅ File type validation (images only)
- ✅ Size limits enforced
- ✅ No security vulnerabilities (CodeQL scan passed)

## 📚 Documentation

For detailed information, see:
- **Feature Guide**: `PROFILE_PICTURES_FEATURE.md`
- **Security Summary**: `SECURITY_SUMMARY.md`
- **API Documentation**: Available at `/docs` when backend is running

## ❓ Troubleshooting

### Images won't upload
- Check file size (must be under 10MB)
- Verify file type (JPEG, PNG, GIF, WebP only)
- Ensure you're logged in

### Gallery not showing
- Refresh the page
- Check that backend is running
- Check browser console for errors

### Need Help?
Run the verification test:
```bash
python3 test_profile_pictures_feature.py
```

## 🎉 That's It!

Enjoy managing your profile pictures! Upload your favorite photos and switch between them whenever you want.
