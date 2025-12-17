# 🚀 VERCEL ENV CHECK - QUICK REFERENCE

## ⚡ 30-Second Setup

### 1️⃣ Go to Vercel Dashboard
```
https://vercel.com/dashboard → Your Project → Settings → Environment Variables
```

### 2️⃣ Add This Variable

```bash
Name:  VITE_API_URL
Value: https://your-backend.onrender.com
```

**⚠️ NOT `NEXT_PUBLIC_API_URL` - This project uses Vite, not Next.js!**

### 3️⃣ Select All Environments
- ✅ Production
- ✅ Preview
- ✅ Development

### 4️⃣ Save & Redeploy
1. Click **Save**
2. Go to **Deployments** tab
3. Click **...** → **Redeploy**

---

## ✅ Verification (30 seconds)

### Open Browser Console (F12):
```javascript
console.log(import.meta.env.VITE_API_URL);
// Should show: "https://your-backend.onrender.com"
// NOT: "undefined"
```

### Test Backend:
```bash
curl https://your-backend.onrender.com/health
# Should return: {"status":"healthy","database":"connected"}
```

---

## 🎯 Visual Guide

```
┌─────────────────────────────────────────────────────────┐
│ Vercel Dashboard → Settings → Environment Variables    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [+ Add New]                                            │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Name:  VITE_API_URL                               │ │
│  │                                                   │ │
│  │ Value: https://hiremebahamas.onrender.com        │ │
│  │                                                   │ │
│  │ Environments:                                     │ │
│  │   ☑ Production                                    │ │
│  │   ☑ Preview                                       │ │
│  │   ☑ Development                                   │ │
│  │                                                   │ │
│  │                    [Cancel]  [Save]               │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ⚠️ Common Mistakes

| ❌ INCORRECT | ✅ CORRECT |
|--------------|------------|
| `NEXT_PUBLIC_API_URL` | `VITE_API_URL` |
| `API_URL` | `VITE_API_URL` |
| `http://backend.com` | `https://backend.com` |
| Only Production checked | All 3 environments checked |
| Added variable but didn't redeploy | Added variable AND redeployed |

---

## 🔗 Backend URL Examples

### Railway
```bash
VITE_API_URL=https://hiremebahamas-production.up.railway.app
```

### Render
```bash
VITE_API_URL=https://hiremebahamas.onrender.com
```

### Local Development
```bash
VITE_API_URL=http://localhost:8000
```

---

## 🆘 Still Not Working?

1. **Check variable name**: Must be exactly `VITE_API_URL` (case-sensitive)
2. **Check you redeployed**: Go to Deployments → Redeploy
3. **Clear browser cache**: Press Ctrl+Shift+R (or Cmd+Shift+R on Mac)
4. **Check backend is up**: Visit your backend URL in browser
5. **Check browser console**: Look for error messages

---

## 📖 Need More Help?

See full guide: [VERCEL_ENV_CHECK.md](./VERCEL_ENV_CHECK.md)

---

**Framework**: Vite (React) - NOT Next.js  
**Required Prefix**: `VITE_` (NOT `NEXT_PUBLIC_`)  
**Last Updated**: December 17, 2025
