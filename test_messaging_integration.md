# Messaging Integration Test Guide

## Overview
This guide provides step-by-step instructions to test the messaging functionality after installing all dependencies and fixing the API endpoints.

## Prerequisites
✅ All frontend dependencies installed (804 packages)
✅ All backend dependencies installed (50+ packages)
✅ Messages.tsx using correct messagesAPI endpoints
✅ SocketContext properly configured

## Test Scenarios

### 1. Load Conversations Test
**Purpose**: Verify conversations load without "Failed to load message" error

**Steps**:
1. Log in as a user
2. Navigate to `/messages`
3. Wait for conversations to load

**Expected Result**:
- ✅ No "Failed to load message" error
- ✅ Conversations list loads (or shows "No conversations" message)
- ✅ No console errors about missing dependencies or wrong endpoints

**API Call Verified**: `GET /api/messages/conversations`

### 2. Create Conversation Test
**Purpose**: Verify users can start new conversations

**Steps**:
1. From user profile page, click "Message" button
2. Or navigate to `/messages?user={userId}`

**Expected Result**:
- ✅ Conversation is created successfully
- ✅ Chat interface opens
- ✅ Toast notification: "Chat opened"

**API Call Verified**: `POST /api/messages/conversations`

### 3. Send Message Test
**Purpose**: Verify messages can be sent and received

**Steps**:
1. Open a conversation
2. Type a message in the input field
3. Click send button or press Enter

**Expected Result**:
- ✅ Message appears in the chat
- ✅ Input field is cleared
- ✅ No error alert
- ✅ Message timestamp is shown

**API Call Verified**: `POST /api/messages/conversations/{id}/messages`

### 4. Real-time Updates Test
**Purpose**: Verify Socket.IO connection for real-time messaging

**Steps**:
1. Open same conversation in two browser windows/tabs
2. Send message from one window
3. Check if it appears in the other window

**Expected Result**:
- ✅ Message appears in both windows without refresh
- ✅ Socket connection indicator shows "connected"
- ✅ Console shows: "Connected to server"

**Socket Events Verified**: 
- `connect`
- `new_message`

### 5. Conversation Selection Test
**Purpose**: Verify switching between conversations works

**Steps**:
1. Have multiple conversations
2. Click on different conversations in the sidebar

**Expected Result**:
- ✅ Messages for selected conversation load
- ✅ Chat header shows correct user name
- ✅ No errors in console

### 6. Search Conversations Test
**Purpose**: Verify conversation search works

**Steps**:
1. Have multiple conversations
2. Type in the search box

**Expected Result**:
- ✅ Conversations filter based on participant name
- ✅ Search is case-insensitive
- ✅ UI updates smoothly

## API Endpoints Checklist

### Messages API
- [ ] `GET /api/messages/conversations` - Get all conversations
- [ ] `POST /api/messages/conversations` - Create conversation
- [ ] `GET /api/messages/conversations/{id}/messages` - Get messages
- [ ] `POST /api/messages/conversations/{id}/messages` - Send message
- [ ] `PUT /api/messages/messages/{id}/read` - Mark as read
- [ ] `GET /api/messages/unread-count` - Get unread count

### Socket.IO Events
- [ ] `connect` - Connection established
- [ ] `disconnect` - Connection lost
- [ ] `new_message` - New message received
- [ ] `typing` - Typing indicator
- [ ] `join_conversation` - Join conversation room
- [ ] `leave_conversation` - Leave conversation room

## Common Issues and Solutions

### Issue 1: "Failed to load message" Error
**Cause**: Missing dependencies or wrong API endpoints
**Solution**: ✅ FIXED - All dependencies installed and API endpoints corrected

### Issue 2: Messages don't appear
**Cause**: API endpoint returning wrong data structure
**Solution**: ✅ FIXED - Using messagesAPI helper functions

### Issue 3: Real-time updates not working
**Cause**: Socket.IO not connected
**Check**: 
- Backend running with Socket.IO support
- SocketProvider wrapped around app components
- VITE_SOCKET_URL environment variable set

### Issue 4: Console errors about missing modules
**Cause**: Dependencies not installed
**Solution**: ✅ FIXED - All 804 frontend packages installed

## Developer Testing Commands

### Check Frontend Dependencies
```bash
cd frontend
npm list socket.io-client axios react
```

### Check Backend Dependencies
```bash
cd backend
python3 -c "import fastapi, socketio, uvicorn, sqlalchemy, aiosqlite; print('All packages OK')"
```

### Build Frontend
```bash
cd frontend
npm run build
# Should complete without errors
```

### Run Frontend Dev Server
```bash
cd frontend
npm run dev
# Access at http://localhost:5173
```

### Run Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API docs at http://localhost:8000/docs
```

## Verification Checklist

### Dependencies
- [x] 804 frontend npm packages installed
- [x] 50+ backend Python packages installed
- [x] socket.io-client@^4.8.1 installed
- [x] axios@^1.6.5 installed
- [x] python-socketio==5.11.0 installed
- [x] aiosqlite==0.21.0 installed

### Code Changes
- [x] Messages.tsx using messagesAPI.getConversations()
- [x] Messages.tsx using messagesAPI.sendMessage()
- [x] Unused api import removed from Messages.tsx
- [x] SocketProvider integrated in App.tsx
- [x] SocketContext properly configured

### Build & Tests
- [x] Frontend builds successfully (755KB bundle)
- [x] No TypeScript errors
- [x] No console warnings about missing dependencies
- [x] Backend imports work correctly

## Success Criteria
✅ Users can view their conversations without "Failed to load message" error
✅ Users can send messages successfully
✅ Messages appear in real-time with Socket.IO
✅ Conversation search works correctly
✅ No dependency-related errors in console
✅ Frontend builds without errors
✅ Backend imports all required modules

## Next Steps After Testing
If all tests pass:
1. ✅ Mark the issue as resolved
2. ✅ Document the fix in MESSAGE_FIX_COMPLETE.md
3. ✅ Commit all changes to the repository
4. ✅ Deploy to production

If any tests fail:
1. Check console for specific error messages
2. Verify environment variables are set correctly
3. Ensure both frontend and backend are running
4. Check network tab for failed API requests
5. Review Socket.IO connection status
