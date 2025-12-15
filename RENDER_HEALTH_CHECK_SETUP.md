# Render Health Check Setup - Quick Reference

## 🎯 Critical Configuration

This guide shows you exactly how to set up the health check path in Render Dashboard.

## 📍 Where to Configure

**Render Dashboard → Your Backend Service → Settings**

Scroll down to find the **Health Check** section.

## ⚙️ Health Check Configuration

### Step 1: Choose Your Health Check Path

⚠️ **CRITICAL**: The path is **case-sensitive** and must match **exactly**.

Choose **ONE** of these options:

#### Option 1: Simple Path (Recommended) ✅
```
Health Check Path: /health
```
- ✅ Simplest option
- ✅ No prefix
- ✅ Instant response (<5ms)
- ✅ No database dependency

#### Option 2: API Prefix Path
```
Health Check Path: /api/health
```
- ✅ Uses `/api` prefix
- ✅ Instant response (<5ms)
- ✅ No database dependency
- ℹ️ Use if your routing expects `/api` prefix

### Step 2: Configure Additional Settings

```yaml
Grace Period: 60 seconds
Health Check Timeout: 10 seconds
Health Check Interval: 30 seconds
```

## 🔍 All Available Health Endpoints

Your backend provides multiple health check endpoints:

| Endpoint | Purpose | Response Time | Database |
|----------|---------|---------------|----------|
| `/health` | Basic health check | <5ms | ❌ No |
| `/api/health` | Health check with prefix | <5ms | ❌ No |
| `/ready` | Readiness check | ~50ms | ✅ Yes |
| `/live` | Liveness probe | <5ms | ❌ No |

## ✅ Verification

After configuring, verify your health check is working:

### If you chose `/health`:
```bash
curl https://your-app.onrender.com/health
```
Expected response:
```json
{"ok": true}
```

### If you chose `/api/health`:
```bash
curl https://your-app.onrender.com/api/health
```
Expected response:
```json
{"status": "ok"}
```

## ❌ Common Mistakes

### Mistake 1: Wrong Case
```
❌ /Health (wrong - capital H)
❌ /HEALTH (wrong - all caps)
✅ /health (correct - lowercase)
```

### Mistake 2: Missing Slash
```
❌ health (wrong - missing leading slash)
✅ /health (correct - with leading slash)
```

### Mistake 3: Wrong Prefix
```
❌ /api/health when you configured /health
❌ /health when you configured /api/health
✅ Must match your Render Dashboard setting exactly
```

## 🚨 Troubleshooting

### Health Check Failing?

1. **Check the path exactly matches** your Render Dashboard configuration
2. **Verify case-sensitivity** - `/health` ≠ `/Health`
3. **Test manually** with curl to confirm the endpoint works
4. **Check Render logs** for startup errors
5. **Increase Grace Period** if service needs more time to start

### Service Shows as Unhealthy?

1. Go to Render Dashboard → Your Service → Logs
2. Look for errors during startup
3. Verify the health endpoint is accessible
4. Confirm environment variables are set correctly
5. Check if database connection is working (if using `/ready`)

## 📚 Related Documentation

- [DEPLOYMENT_CHECKLIST_FINAL_ARCHITECTURE.md](./DEPLOYMENT_CHECKLIST_FINAL_ARCHITECTURE.md) - Complete deployment guide
- [render.yaml](./render.yaml) - Infrastructure as code configuration
- [FINAL_SPEED_ARCHITECTURE.md](./FINAL_SPEED_ARCHITECTURE.md) - Architecture overview

## 💡 Pro Tips

1. **Use `/health` for Render** - It's the simplest and fastest option
2. **Don't use `/ready` for health checks** - It checks the database and may be slow
3. **Set Grace Period to 60 seconds** - Gives service time to start up properly
4. **Monitor Render logs** during first deployment to catch issues early

## 🎯 Quick Setup Checklist

- [ ] Open Render Dashboard
- [ ] Navigate to your backend service → Settings
- [ ] Find Health Check section
- [ ] Set Path: `/health` (or `/api/health`)
- [ ] Set Grace Period: `60` seconds
- [ ] Set Timeout: `10` seconds
- [ ] Set Interval: `30` seconds
- [ ] Save changes
- [ ] Deploy or redeploy service
- [ ] Verify health check passes in Render logs
- [ ] Test manually with curl

---

**Last Updated**: December 2025  
**Status**: ✅ Current and Tested  
**Platform**: Render.com
