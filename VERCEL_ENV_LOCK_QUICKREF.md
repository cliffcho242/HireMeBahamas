# 8️⃣ VERCEL ENV LOCK - Quick Reference

**Status**: 🔴 MANDATORY  
**Last Updated**: December 17, 2025

---

## ✅ DO THIS

```bash
# Vercel Dashboard → Settings → Environment Variables
VITE_API_URL=https://your-backend.onrender.com
```

**Set for**: Production, Preview, Development (all three)

---

## 🚫 NEVER DO THIS

```bash
# ❌ WRONG FRAMEWORK
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com

# ❌ SECURITY RISK - Exposes credentials
VITE_DATABASE_URL=postgresql://...
DATABASE_URL=postgresql://...

# ❌ SECURITY RISK - Exposes secrets
VITE_JWT_SECRET=your-secret
VITE_SECRET_KEY=your-key
VITE_CRON_SECRET=your-cron-secret

# ❌ LOCALHOST IN PRODUCTION
VITE_API_URL=http://localhost:8000
VITE_API_URL=http://127.0.0.1:8000

# ❌ MISSING PREFIX
API_URL=https://your-backend.onrender.com
```

---

## 🎯 The Rules

1. **Use VITE_ prefix** (NOT NEXT_PUBLIC_)
   - This is a Vite/React project
   
2. **No backend secrets with VITE_ prefix**
   - DATABASE_URL, JWT_SECRET, SECRET_KEY → Backend only
   
3. **No DATABASE_URL in frontend**
   - Frontend connects to backend API, not database
   
4. **No localhost in production**
   - Use actual backend URL (https://...)

---

## ✅ Verification

```javascript
// In browser console (F12)
console.log(import.meta.env.VITE_API_URL);
// Should show: "https://your-backend.onrender.com"
// NOT: "undefined"

// These should be undefined (backend only)
console.log(import.meta.env.VITE_DATABASE_URL);  // undefined ✅
console.log(import.meta.env.VITE_JWT_SECRET);    // undefined ✅
```

---

## 📖 Full Documentation

**[VERCEL_ENV_LOCK.md](./VERCEL_ENV_LOCK.md)** - Complete guide with troubleshooting

---

**🔒 MANDATORY LOCK - Violations cause failures or security breaches**
