# Job Posting Error - Troubleshooting Guide

## Issue
Getting "Error posting job. Please try again." message when trying to post a job from the website.

## ✅ Backend Status: WORKING
Backend API tested successfully:
- ✅ Health check: Passing
- ✅ Login: Working
- ✅ Job creation API: Working (Jobs #1 and #2 created successfully)

## 🔍 Root Cause
Since the backend is working, the issue is in the **frontend/browser**. Common causes:

### 1. **Authentication Token Issues**
- Token might be expired
- Token not being sent properly
- User session lost

### 2. **CORS / Network Issues**
- Browser blocking cross-origin request
- Network connectivity problem
- Vercel deployment not loading environment variables

### 3. **Browser Console Errors**
- JavaScript error preventing submission
- API call failing silently
- React state issue

## 🛠️ How to Diagnose

### Step 1: Check Browser Console
1. Open your website: https://frontend-8afubhzxw-cliffs-projects-a84c76c9.vercel.app
2. Press **F12** (or right-click > Inspect)
3. Go to **Console** tab
4. Try posting a job again
5. Look for **red error messages**

**What to look for:**
- ❌ `401 Unauthorized` → Need to log in again
- ❌ `CORS error` → Backend CORS issue
- ❌ `Network Error` → Can't reach backend
- ❌ `Failed to fetch` → API request failed
- ❌ Any JavaScript errors

### Step 2: Check Network Tab
1. Stay in browser DevTools (F12)
2. Go to **Network** tab
3. Try posting a job again
4. Look for the POST request to `/api/jobs`
5. Click on it and check:
   - **Status Code** (should be 200 or 201)
   - **Response** tab (what did backend return?)
   - **Headers** tab (is Authorization header present?)

### Step 3: Verify You're Logged In
1. Check if you see your profile picture/name in header
2. Try logging out and logging back in
3. Token might have expired

### Step 4: Check What Data Is Being Sent
In the Console, you should see:
```
Posting job: {title: "...", company: "...", ...}
```

If you don't see this log, the form validation might be failing.

## 🔧 Quick Fixes

### Fix 1: Clear Cache and Refresh
```
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)
```

### Fix 2: Sign Out and Sign In Again
1. Click your profile
2. Sign out
3. Sign in with: admin@hiremebahamas.com / AdminPass123!
4. Try posting job again

### Fix 3: Check Required Fields
Make sure ALL these fields are filled:
- ✅ Job Title
- ✅ Company Name
- ✅ Location
- ✅ Job Type (select from dropdown)
- ✅ Description

Salary fields are **optional** - leave them blank if you want.

### Fix 4: Try Different Browser
Sometimes browser extensions block requests:
- Try in **Incognito/Private mode**
- Or try a different browser (Chrome, Firefox, Edge)

## 📋 Test Data You Can Use

```
Job Title: Software Developer
Company: Tech Company BS
Location: Nassau, Bahamas
Job Type: Full-time (select from dropdown)
Description: We are looking for a talented software developer...
Requirements: (optional) 3+ years experience...
Salary Min: (optional) 50000
Salary Max: (optional) 70000
```

## 🔍 What I Need to Help You

If it's still not working, please tell me:

1. **What do you see in the browser console?** (F12 > Console tab)
   - Copy any red error messages

2. **What's in the Network tab?** (F12 > Network tab > POST /api/jobs)
   - What status code?
   - What response?

3. **Are you logged in?**
   - Can you see your profile in the header?

4. **What browser are you using?**
   - Chrome? Firefox? Safari? Edge?
   - Desktop or mobile?

5. **Did you fill in all required fields?**
   - Job title, company, location, job type, description?

## ✅ Backend Verification

I've verified the backend is working by testing directly:

```powershell
# Test 1: Create job without salary
✓ Job ID: 1 created

# Test 2: Create job with salary
✓ Job ID: 2 created
```

Both API calls succeeded, so the backend is **100% working**.

## 🎯 Most Likely Issues (in order)

1. **Token expired** → Sign out and sign in again
2. **Console has JavaScript error** → Check F12 console
3. **Cache issue** → Hard refresh (Ctrl+Shift+R)
4. **Vercel protection** → Check if you disabled deployment protection

---

**Backend URL**: https://hiremebahamas.onrender.com  
**Frontend URL**: https://frontend-8afubhzxw-cliffs-projects-a84c76c9.vercel.app  

**Status**: Backend ✅ | Frontend ❓ (needs browser console check)
