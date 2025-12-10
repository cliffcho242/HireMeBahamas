# Vercel Diagnostic Tool - Quick Reference

## Installation
```bash
pip install -r diagnostic/requirements.txt
```

## Basic Commands

### Test Production
```bash
python diagnostic/check_vercel_connection.py --url https://hiremebahamas.vercel.app
```

### Test with Details
```bash
python diagnostic/check_vercel_connection.py --url https://hiremebahamas.vercel.app --verbose
```

### Save Report
```bash
python diagnostic/check_vercel_connection.py --url https://hiremebahamas.vercel.app --output report.txt
```

## Common Issues

### Frontend Not Accessible (404)
**Check**:
- Vercel build logs
- `vercel.json` outputDirectory setting
- Frontend build success

### API Endpoints Not Working (404/500)
**Check**:
- DATABASE_URL in Vercel env vars
- `api/index.py` deployed
- Python dependencies in requirements.txt
- Vercel function logs

### Database Connection Failed
**Check**:
- DATABASE_URL environment variable set
- Database credentials correct
- Database accepts Vercel IPs
- SSL mode set (sslmode=require)

### JWT Using Default Values
**Check**:
- JWT_SECRET_KEY environment variable
- SECRET_KEY environment variable
- Redeploy after setting variables

## Exit Codes
- `0` = All checks passed
- `1` = One or more checks failed
- `130` = Interrupted by user

## Output Symbols
- ✅ = Check passed
- ❌ = Check failed
- ⚠️ = Warning (not critical)
- 💡 = Suggestion
- 📚 = Documentation link

## Quick Diagnostics

### Is my frontend working?
Look for: `✅ Frontend accessible at:`

### Is my backend API working?
Look for: `✅ /api/health: Status 200`

### Is my database connected?
Look for: `✅ Connection: Successful`

### Are my secrets configured?
Look for: `✅ JWT_SECRET_KEY: Set (not default)`

## Response Time Guidelines
- **< 1s**: Excellent
- **1-5s**: Good
- **> 5s**: Slow (warning shown)

## Full Documentation
See `diagnostic/README.md` for complete documentation.
