# Quick Start Guide - Notification System

## What Was Fixed

### Problem
- Profile page features weren't showing up
- Notifications always showed red badge even with no notifications
- No automatic notifications for follow and job actions

### Solution
Complete notification system with automated creation and real-time display.

## How to Use

### For Users

#### Viewing Notifications
1. Click the bell icon in the header
2. See all your notifications with unread count
3. Click on a notification to mark it as read
4. Click "Mark all read" to clear all notifications

#### Profile Page
1. Navigate to your profile
2. See your follower and following counts
3. Toggle "Available for Hire" to show up on HireMe board
4. Update your profile information

### For Developers

#### Starting the Backend
```bash
cd backend
python -m uvicorn app.main:socket_app --host 127.0.0.1 --port 9999
```

#### Starting the Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Database Setup
```bash
cd backend
# Create all tables
python create_all_tables.py

# Or just notifications table
python create_notifications_table.py

# Or add hireme column to existing database
python add_hireme_column.py
```

## API Endpoints

### Notifications
- `GET /api/notifications/list` - List all notifications
- `GET /api/notifications/unread-count` - Get unread count
- `PUT /api/notifications/{id}/read` - Mark one as read
- `PUT /api/notifications/mark-all-read` - Mark all as read

### HireMe
- `GET /api/hireme/available` - Get available users
- `POST /api/hireme/toggle` - Toggle availability

### Users (Enhanced)
- `POST /api/users/follow/{user_id}` - Now creates notification
- `POST /api/users/unfollow/{user_id}` - Unfollow user
- `GET /api/users/followers/list` - Get followers
- `GET /api/users/following/list` - Get following

### Jobs (Enhanced)
- `POST /api/jobs/{job_id}/apply` - Now creates notification for employer

## Notification Types

| Type | Icon | Color | Triggered By |
|------|------|-------|--------------|
| follow | 👤 | Teal | User follows you |
| friend_request | 👤 | Green | Friend request received |
| job_application | 💼 | Purple | Someone applies to your job |
| job_post | 💼 | Blue | New job posted |
| like | ❤️ | Red | Someone likes your post |
| comment | 💬 | Blue | Someone comments on your post |
| mention | @ | Purple | Someone mentions you |

## Testing

### Manual Testing
1. Create two test accounts
2. Have one account follow the other
3. Check notifications on the followed account
4. Post a job with one account
5. Apply to the job with another account
6. Check notifications on the employer account

### Automated Testing
```bash
cd backend
pytest test_notifications.py  # (when created)

cd frontend
npm run test  # (when tests exist)
```

## Troubleshooting

### Notifications not showing?
- Check backend is running
- Verify frontend can connect to backend
- Check browser console for errors
- Ensure you're logged in

### Profile features missing?
- Run database migrations
- Check is_available_for_hire column exists
- Verify API endpoints are registered

### Build errors?
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Next Steps

1. Add real-time notifications using Socket.IO
2. Add email notifications
3. Add notification preferences
4. Add notification grouping
5. Add push notifications for PWA

## Support

For issues or questions, check:
- `IMPLEMENTATION_SUMMARY.md` - Detailed technical docs
- Backend logs for API errors
- Browser console for frontend errors
