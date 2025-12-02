# Frontend Environment Variable Update - Quick Reference

## 🎯 What Was Changed

### vercel.json Simplification

**Before (Complex):**
- Multiple individual build entries
- `functions` key causing conflicts
- `rewrites` with specific mappings
- Headers and crons configuration

**After (Simplified):**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/"
    }
  ]
}
```

### Key Benefits

✅ **Wildcard builds**: `api/**/*.py` automatically includes all Python files  
✅ **No functions key**: Eliminates Vercel configuration conflicts  
✅ **Simple routing**: Automatically forwards `/api/auth/me` → `api/auth/me.py`  
✅ **Less maintenance**: No need to add new files to config manually  

---

## 🚀 How to Update VITE_API_URL

### Quick Steps

1. **Go to Vercel Dashboard** → Your Project → Settings → Environment Variables
2. **Add Variable:**
   - Key: `VITE_API_URL`
   - Value: `https://your-backend.vercel.app` (or your backend URL)
   - Environments: ✅ Production ✅ Preview ✅ Development
3. **Save** the variable
4. **Redeploy:**
   ```bash
   git commit --allow-empty -m "chore: trigger redeploy"
   git push
   ```

### Detailed Guide
📖 See [VERCEL_ENVIRONMENT_SETUP.md](./VERCEL_ENVIRONMENT_SETUP.md) for complete instructions

---

## 📝 Backend URL Options

Choose based on where your backend is deployed:

| Platform | URL Format | Example |
|----------|------------|---------|
| **Vercel** | `https://[project].vercel.app` | `https://hiremebahamas-backend.vercel.app` |
| **Railway** | `https://[project].railway.app` | `https://hiremebahamas-backend.railway.app` |
| **Render** | `https://[project].onrender.com` | `https://hiremebahamas.onrender.com` |

⚠️ **Important:** No trailing slash, must use `https://`

---

## ✅ Verification

After setting the environment variable and redeploying:

```bash
# 1. Check in browser console
import.meta.env.VITE_API_URL
# Should display: "https://your-backend.vercel.app"

# 2. Test API health
curl https://your-backend.vercel.app/api/health

# 3. Check Network tab
# API requests should go to your configured backend URL
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Variable not found | Ensure exact name: `VITE_API_URL` (case-sensitive) |
| Still using old URL | Clear cache, hard refresh (`Ctrl+Shift+R`) |
| API errors | Check backend URL has no typos or trailing slash |
| Not working after save | Must redeploy after adding environment variables |

---

## 📚 Related Files Changed

- ✅ `vercel.json` - Simplified configuration (removed functions key)
- ✅ `VERCEL_ENVIRONMENT_SETUP.md` - New detailed setup guide
- ✅ `AUTO_DEPLOY_SETUP.md` - Updated with link to new guide

---

## 🎉 Summary

This update makes the Vercel configuration:
- **Simpler**: Fewer lines, clearer intent
- **More flexible**: Automatically picks up new API files
- **Conflict-free**: Removed the problematic `functions` key
- **Better documented**: Clear guide for setting environment variables

**Next Step:** Set `VITE_API_URL` in Vercel dashboard and redeploy! 🚀
