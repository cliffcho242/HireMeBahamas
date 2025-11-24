# Quick Reference - Registration & Dependencies

## Problem Fixed
✅ "Sudo Registration failed" error
✅ Missing dependencies for frontend and backend
✅ All automated and documented

## Quick Commands

### Fix Dependencies Automatically
```bash
# Check and auto-install all dependencies
python3 scripts/check-dependencies.py --install

# Check only
python3 scripts/check-dependencies.py
```

### Test Registration
```bash
# Run all registration tests
python test_registration_fastapi.py

# Expected output: "✓ ALL TESTS PASSED!"
```

### Manual Installation
```bash
# Install all (requires sudo)
sudo ./scripts/install-dependencies.sh

# Backend only
sudo ./scripts/install-dependencies.sh --backend-only

# Frontend only (no sudo)
./scripts/install-dependencies.sh --frontend-only
```

## Status Check

### Everything Working When:
✅ `python3 scripts/check-dependencies.py` shows "All dependencies satisfied"
✅ `python test_registration_fastapi.py` passes all tests
✅ Registration works in UI
✅ No errors in browser console

## Common Issues

### "ImportError: No module named ..."
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### "npm ERR! ERESOLVE"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### OAuth not working
Check `.env` files:
- Backend: `GOOGLE_CLIENT_ID=...`
- Frontend: `VITE_GOOGLE_CLIENT_ID=...`

## Documentation

- **Dependency Management:** `docs/DEPENDENCY_MANAGEMENT.md`
- **Troubleshooting:** `docs/REGISTRATION_TROUBLESHOOTING.md`
- **Implementation Details:** `docs/AUTOMATED_DEPENDENCY_FIX_SUMMARY.md`
- **Security:** `docs/SECURITY_SUMMARY_REGISTRATION.md`

## Test Results

### All Passing ✅
- 17 Flask backend tests
- FastAPI registration tests
- Dependency verification
- OAuth endpoint checks
- CodeQL security scan (0 alerts)

## Security Status

**CodeQL:** 0 alerts
**Status:** All clear ✅
**Dependencies:** All verified ✅

## Need Help?

1. Run diagnostics: `python3 scripts/check-dependencies.py`
2. Check docs: `docs/REGISTRATION_TROUBLESHOOTING.md`
3. Test system: `python test_registration_fastapi.py`

---

**Last Updated:** 2025-11-24
**Status:** ✅ All systems operational
