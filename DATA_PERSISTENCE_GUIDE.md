# Data Persistence & Session Management Guide

## Overview
This guide explains how HireMeBahamas ensures user data and posts are persisted across sessions and prevents data loss.

## Fixed Issues

### 1. ✅ Secret Key Persistence
**Problem**: App was using a default SECRET_KEY that could change between restarts, invalidating all user sessions.

**Solution**: 
- Created permanent `.env` file with fixed SECRET_KEY
- Set `SECRET_KEY=hiremebahamas-secure-secret-key-2024-production-do-not-change`
- **CRITICAL**: Never change this SECRET_KEY in production as it will invalidate all user sessions

### 2. ✅ Token Refresh Endpoint
**Problem**: Frontend was trying to refresh expired tokens, but the backend endpoint didn't exist.

**Solution**: 
- Added `/api/auth/refresh` endpoint to refresh tokens
- Added `/api/auth/verify` endpoint to validate sessions
- Added `/api/auth/profile` endpoint to fetch user profile
- Tokens now automatically refresh before expiring

### 3. ✅ Session Management
**Problem**: User sessions were not being properly maintained across page reloads.

**Solution**:
- Enhanced `sessionManager.ts` with proper session persistence
- Session data is encrypted and stored in localStorage
- Sessions automatically restore on page reload
- Activity tracking prevents premature timeout

### 4. ✅ Database Persistence
**Problem**: Database might reset if not properly configured.

**Solution**:
- Database files (*.db) are excluded from git (in .gitignore) - this is correct
- For **Development**: SQLite database (`hiremebahamas.db`) persists in the project root
- For **Production**: PostgreSQL database configured via `DATABASE_URL` environment variable
- Database initialization checks for existing tables before creating new ones

## How Data Persistence Works

### Local Development (SQLite)
1. Database file: `hiremebahamas.db` (in project root)
2. File persists between app restarts
3. All user data, posts, jobs stored in this file
4. File is excluded from git to prevent conflicts

### Production (PostgreSQL)
1. Database URL set via `DATABASE_URL` environment variable
2. Hosted on Render/Render with persistent storage
3. Data survives deployments and restarts
4. Automatic backups (depends on hosting provider)

## Environment Variables

Required environment variables in `.env`:

```bash
# CRITICAL: Do not change after production deployment
SECRET_KEY=hiremebahamas-secure-secret-key-2024-production-do-not-change
JWT_SECRET_KEY=hiremebahamas-jwt-secret-key-2024-production-do-not-change

# Database (optional for local dev, required for production)
# DATABASE_URL=postgresql://user:password@host:port/database

# Server
PORT=8080

# Frontend URL for CORS
FRONTEND_URL=https://hiremebahamas.vercel.app
```

## Session Flow

### Login Process
1. User enters credentials
2. Backend validates and generates JWT token (valid for 7 days)
3. Token and user data saved to:
   - localStorage (for backward compatibility)
   - sessionManager (encrypted)
4. User remains logged in across page reloads

### Session Persistence
1. On page load, app checks for existing session
2. If found, restores user state
3. If token near expiration, automatically refreshes
4. Session tracks user activity to prevent timeout

### Logout Process
1. User clicks logout
2. Token removed from localStorage
3. Session cleared from sessionManager
4. User redirected to login page

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh token (NEW)
- `GET /api/auth/verify` - Verify session (NEW)
- `GET /api/auth/profile` - Get user profile (NEW)

### Health Check
- `GET /health` - Basic health check
- `GET /api/health` - Detailed health check with DB status

## Troubleshooting

### Problem: Users get logged out randomly
**Cause**: Token expired or SECRET_KEY changed
**Solution**: 
- Check that .env file exists with fixed SECRET_KEY
- Verify token refresh is working (check browser console)

### Problem: Posts disappear after restart
**Cause**: Database file missing or not persisting
**Solution**:
- For local dev: Check that `hiremebahamas.db` file exists in project root
- For production: Verify DATABASE_URL is set correctly
- Check database initialization logs on startup

### Problem: "Token has expired" errors
**Cause**: Token refresh not working
**Solution**:
- Check browser console for refresh errors
- Verify `/api/auth/refresh` endpoint is responding
- Clear localStorage and login again

### Problem: Database resets on deployment
**Cause**: Using SQLite in production or database not configured
**Solution**:
- Set DATABASE_URL to PostgreSQL connection string
- Use Render/Render's database services
- Enable persistent storage on hosting platform

## Best Practices

### Development
1. **Keep .env file**: Don't delete it
2. **Backup database**: Periodically backup `hiremebahamas.db`
3. **Test persistence**: Restart app and verify data remains

### Production
1. **Use PostgreSQL**: Don't use SQLite in production
2. **Enable backups**: Configure automatic database backups
3. **Monitor SECRET_KEY**: Never change it after deployment
4. **Check logs**: Monitor for database connection errors

### Security
1. **Never commit .env**: Already in .gitignore
2. **Rotate JWT secrets**: Only if necessary, coordinate with users
3. **Use HTTPS**: Always use secure connections in production
4. **Validate tokens**: Backend validates all tokens

## Testing Data Persistence

### Test 1: User Session Persistence
1. Register or login as a user
2. Create a post
3. Refresh the page
4. ✅ User should still be logged in
5. ✅ Post should still be visible

### Test 2: Database Persistence
1. Create a user and post
2. Stop the backend server
3. Restart the backend server
4. Login again
5. ✅ User account should exist
6. ✅ Post should still be there

### Test 3: Token Refresh
1. Login and wait for token to approach expiration
2. Continue using the app
3. ✅ Token should refresh automatically
4. ✅ No logout or interruption

## Deployment Checklist

- [ ] .env file created with fixed SECRET_KEY
- [ ] DATABASE_URL set for production (PostgreSQL)
- [ ] All authentication endpoints tested
- [ ] Token refresh working
- [ ] Session persistence verified
- [ ] Database backups configured
- [ ] Monitoring and logging enabled

## Support

If you encounter issues with data persistence:
1. Check the logs for database errors
2. Verify environment variables are set
3. Test with the provided test scripts
4. Review this guide for troubleshooting steps

---

**Last Updated**: 2024-11-22
**Backend**: `final_backend_postgresql.py`
**Frontend**: React with session management
