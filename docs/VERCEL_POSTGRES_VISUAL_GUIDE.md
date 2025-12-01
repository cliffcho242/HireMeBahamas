# Vercel Postgres Setup - Visual Step-by-Step Guide

Complete visual walkthrough for setting up Vercel Postgres with screenshots and UI navigation.

---

## 📋 Prerequisites

Before you begin:
- ✅ Vercel account ([sign up](https://vercel.com/signup))
- ✅ HireMeBahamas project deployed on Vercel
- ✅ 5 minutes of time

---

## 🎯 Step 1: Navigate to Storage

### 1.1 Open Vercel Dashboard
```
URL: https://vercel.com/dashboard
```

### 1.2 Select Your Project
- Find and click: **"HireMeBahamas"** project
- Or navigate to: `https://vercel.com/[your-team]/hiremebahamas`

### 1.3 Access Storage Tab
- Click the **"Storage"** tab in the top navigation
- Or go directly to: `https://vercel.com/[your-team]/hiremebahamas/stores`

**What you'll see:**
```
┌─────────────────────────────────────────────┐
│  Storage                                     │
│  ┌─────────────────────────────────────┐    │
│  │  Create Database                     │    │
│  │  Choose from the following options:  │    │
│  │                                       │    │
│  │  [KV]  [Postgres]  [Blob]  [Edge]   │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

---

## 🎯 Step 2: Create Postgres Database

### 2.1 Click "Create Database" Button
- Large button in the center of the Storage page

### 2.2 Select "Postgres"
- Click the **"Postgres"** card
- Icon shows: 🐘 (elephant)
- Description: "Serverless Postgres powered by Neon"

### 2.3 Click "Continue"

**What you'll see next:**
```
┌─────────────────────────────────────────────┐
│  Create Postgres Database                   │
│                                              │
│  Database Name                               │
│  [hiremebahamas-db     ] (auto-generated)   │
│                                              │
│  Region                                      │
│  [▼ US East (N. Virginia)]                  │
│                                              │
│  Plan                                        │
│  ○ Hobby (Free)                             │
│     • 0.5 GB storage                        │
│     • 60 compute hours/month                │
│                                              │
│  ○ Pro ($0.10/GB)                           │
│     • Pay per GB                             │
│     • Unlimited compute                      │
│     • Database branches                      │
│                                              │
│  [Cancel]  [Create Database]                │
└─────────────────────────────────────────────┘
```

---

## 🎯 Step 3: Configure Database Settings

### 3.1 Database Name (Optional)
- **Default**: Auto-generated (e.g., `hiremebahamas-db`)
- **Custom**: Can rename to anything (e.g., `hiremebahamas-prod`)
- **Recommendation**: Keep default for simplicity

### 3.2 Select Region
Choose region closest to your users:

| Region | Best For | Latency |
|--------|----------|---------|
| **US East (N. Virginia)** | USA, Caribbean, Bahamas | ~20-50ms |
| **US East (Ohio)** | USA, Caribbean | ~25-55ms |
| **US West (Oregon)** | West Coast USA | ~30-60ms |
| **Europe (Frankfurt)** | Europe | ~15-40ms |
| **Asia Pacific (Singapore)** | Asia | ~20-50ms |

**Recommendation for Bahamas**: **US East (N. Virginia)**

### 3.3 Choose Plan

#### Hobby Plan (Free) ✨
- ✅ **Storage**: 0.5 GB
- ✅ **Compute**: 60 hours/month
- ✅ **Cost**: $0
- ✅ **Best for**: Development, small apps, testing
- ⚠️ **Limitation**: Database hibernates after inactivity

#### Pro Plan ($0.10/GB)
- ✅ **Storage**: Pay per GB used
- ✅ **Compute**: Unlimited
- ✅ **Cost**: ~$1-5/month for small apps
- ✅ **Best for**: Production, always-on apps
- ✅ **Benefits**: Database branches, no hibernation, faster performance

**Recommendation**:
- Start with **Hobby** (free)
- Upgrade to **Pro** when ready for production

### 3.4 Click "Create Database"

**Wait time**: 30-60 seconds

---

## 🎯 Step 4: Copy Connection String

Once created, you'll see the database dashboard:

```
┌─────────────────────────────────────────────────────────────┐
│  hiremebahamas-db                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                              │
│  Database Credentials                                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ POSTGRES_URL                                        │    │
│  │ postgres://default:xxxxxxxxxxx@ep-cool-sound-...   │    │
│  │                                         [Copy] [•••] │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ POSTGRES_URL_NON_POOLING                            │    │
│  │ postgres://default:xxxxxxxxxxx@ep-cool-sound-...   │    │
│  │                                         [Copy] [•••] │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ POSTGRES_PRISMA_URL                                 │    │
│  │ postgres://default:xxxxxxxxxxx@ep-cool-sound-...   │    │
│  │                                         [Copy] [•••] │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 4.1 Which Connection String to Use?

| Variable | Use Case | Recommended |
|----------|----------|-------------|
| `POSTGRES_URL` | **Use this one!** | ✅ Yes |
| `POSTGRES_URL_NON_POOLING` | Direct connections (avoid) | ❌ No |
| `POSTGRES_PRISMA_URL` | Prisma ORM only | ❌ Not needed |

### 4.2 Copy POSTGRES_URL
1. Find **"POSTGRES_URL"** section
2. Click **[Copy]** button
3. Connection string copied to clipboard!

**Example copied string:**
```
postgres://default:AbCdEf123456@ep-cool-sound-12345678.us-east-1.aws.neon.tech/verceldb?sslmode=require
```

⚠️ **IMPORTANT**: This contains your password! Keep it secret.

---

## 🎯 Step 5: Add Environment Variables

### 5.1 Navigate to Environment Variables
- Click **"Settings"** tab (top navigation)
- Click **"Environment Variables"** in left sidebar
- Or go to: `https://vercel.com/[your-team]/hiremebahamas/settings/environment-variables`

### 5.2 Add DATABASE_URL Variable

Click **"Add New"** button, then fill in:

```
┌─────────────────────────────────────────────┐
│  Add New Environment Variable               │
│                                              │
│  Key                                         │
│  [DATABASE_URL                         ]    │
│                                              │
│  Value                                       │
│  [postgresql://default:AbCdEf123@ep-...] ← PASTE HERE
│                                              │
│  ⚠️ Convert postgres:// → postgresql://     │
│                                              │
│  Environment                                 │
│  [✓] Production                             │
│  [✓] Preview                                │
│  [✓] Development                            │
│                                              │
│  [Cancel]  [Save]                           │
└─────────────────────────────────────────────┘
```

**CRITICAL**: Change `postgres://` to `postgresql://`:

❌ **Wrong**: `postgres://default:password@host...`
✅ **Correct**: `postgresql://default:password@host...`

### 5.3 Click "Save"

---

## 🎯 Step 6: Redeploy Application

### 6.1 Navigate to Deployments
- Click **"Deployments"** tab (top navigation)
- You'll see list of recent deployments

### 6.2 Redeploy Latest
1. Find the most recent deployment (top of list)
2. Click **"..."** (three dots menu) on the right
3. Select **"Redeploy"** from dropdown
4. Click **"Redeploy"** in confirmation dialog

**What you'll see:**
```
┌─────────────────────────────────────────────┐
│  Redeploy?                                   │
│                                              │
│  This will create a new deployment using    │
│  the same source code and environment       │
│  variables as this deployment.              │
│                                              │
│  [Cancel]  [Redeploy]                       │
└─────────────────────────────────────────────┘
```

### 6.3 Wait for Deployment
- Status shows: **"Building"** → **"Deploying"** → **"Ready"**
- Time: 2-3 minutes
- You'll see progress bar and live logs

---

## 🎯 Step 7: Verify Connection

### 7.1 Test Health Endpoint

Once deployed, test your database connection:

```bash
# Replace with your actual Vercel URL
curl https://hiremebahamas.vercel.app/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": 1701234567,
  "database": "connected",
  "pool": {
    "pool_size": 2,
    "checked_out": 0
  }
}
```

### 7.2 Test in Browser

1. Visit: `https://your-app.vercel.app/api/health`
2. Should see JSON response with `"database": "connected"`

### 7.3 Test User Registration

1. Open your app: `https://your-app.vercel.app`
2. Click **"Sign Up"**
3. Register a new user
4. Login with credentials
5. Create a test post
6. Verify data persists after page refresh

---

## ✅ Success Checklist

Mark each item as you complete it:

- [ ] Created Vercel Postgres database
- [ ] Copied POSTGRES_URL connection string
- [ ] Converted `postgres://` to `postgresql://`
- [ ] Added DATABASE_URL to Environment Variables
- [ ] Selected all environments (Production, Preview, Development)
- [ ] Saved environment variable
- [ ] Redeployed application
- [ ] Deployment completed successfully
- [ ] Health endpoint returns "connected"
- [ ] Can register and login users
- [ ] Data persists after page refresh

---

## 🎉 You're Done!

Your Vercel Postgres database is now live and connected to your application.

---

## 📖 Additional Resources

- **Full Setup Guide**: [VERCEL_POSTGRES_SETUP.md](../VERCEL_POSTGRES_SETUP.md)
- **Quick Start**: [docs/VERCEL_POSTGRES_QUICK_START.md](./VERCEL_POSTGRES_QUICK_START.md)
- **Migration Guide**: [VERCEL_POSTGRES_MIGRATION.md](../VERCEL_POSTGRES_MIGRATION.md)
- **Troubleshooting**: See full setup guide

---

## 🆘 Common UI Issues

### Can't find Storage tab?
- Make sure you're in the correct project
- Storage tab is in the top navigation bar
- Try refreshing the page

### "Create Database" button disabled?
- You may have reached the limit for your plan
- Hobby plan: 1 database per project
- Delete existing database or upgrade plan

### Connection string not showing?
- Database may still be creating (wait 60 seconds)
- Refresh the page
- Click on database name to view details

### Save button disabled in Environment Variables?
- Check that Key and Value are both filled
- Check that at least one environment is selected
- Try refreshing the page

---

*Last Updated: December 2025*
