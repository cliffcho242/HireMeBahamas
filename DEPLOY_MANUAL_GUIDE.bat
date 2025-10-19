@echo off
REM ============================================
REM  MANUAL DEPLOYMENT GUIDE - EASIEST PATH
REM  Step-by-Step with Browser Interface
REM ============================================

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║     🎯 SIMPLEST DEPLOYMENT - USE WEB INTERFACE 🎯       ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo This method uses ONLY web browsers - no command line!
echo Perfect for beginners!
echo.
echo Time: 15-20 minutes
echo Cost: 100%% FREE
echo.
pause

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  PART 1: Deploy Backend to Railway (10 minutes)          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo Opening Railway.app...
start https://railway.app/new

timeout /t 2 >nul

echo.
echo FOLLOW THESE STEPS:
echo ═══════════════════════════════════════════════════════════
echo.
echo 1. Click "Login with GitHub"
echo    └─ Sign up if you don't have a GitHub account
echo.
echo 2. Authorize Railway to access GitHub
echo.
echo 3. Click "Deploy from GitHub repo"
echo.
echo 4. Click "Configure GitHub App"
echo.
echo 5. Install Railway on your account
echo.
echo 6. Go back and select "Create New Repository"
echo    └─ Name it: HireMeBahamas
echo    └─ Make it Public or Private (your choice)
echo.
echo 7. Railway will create the repo and start deploying!
echo.
pause

echo.
echo 8. Add Environment Variable:
echo    └─ Click your project
echo    └─ Go to "Variables" tab
echo    └─ Click "New Variable"
echo.

REM Read SECRET_KEY from .env
for /f "tokens=2 delims==" %%a in ('findstr "SECRET_KEY" .env') do set SECRET_KEY=%%a

echo    Variable Name:  SECRET_KEY
echo    Variable Value: %SECRET_KEY%
echo.
echo    (Copy the value above and paste in Railway)
echo.
pause

echo.
echo 9. Wait for deployment (2-3 minutes)
echo    └─ Check "Deployments" tab
echo    └─ Wait for "SUCCESS" status
echo.
pause

echo.
echo 10. Get your Railway URL:
echo     └─ Click "Settings" tab
echo     └─ Find "Domains" section  
echo     └─ Click "Generate Domain"
echo     └─ Copy your URL (e.g., https://hiremebahamas-backend-production.up.railway.app)
echo.

set /p RAILWAY_URL="Paste your Railway backend URL here: "

if not "%RAILWAY_URL%"=="" (
    echo %RAILWAY_URL% > RAILWAY_URL.txt
    echo.
    echo ✅ Railway URL saved!
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ Backend deployed successfully!
echo ═══════════════════════════════════════════════════════════
echo.
echo Testing backend...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%RAILWAY_URL%/api/health' -UseBasicParsing -TimeoutSec 10; Write-Host '✅ Backend is healthy!' -ForegroundColor Green } catch { Write-Host '⏳ Backend still starting... (this is normal)' -ForegroundColor Yellow }"

echo.
pause

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  PART 2: Deploy Frontend to Vercel (10 minutes)          ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo Opening Vercel.com...
start https://vercel.com/new

timeout /t 2 >nul

echo.
echo FOLLOW THESE STEPS:
echo ═══════════════════════════════════════════════════════════
echo.
echo 1. Click "Continue with GitHub"
echo    └─ Sign in with same GitHub account
echo.
echo 2. Find your "HireMeBahamas" repository
echo    └─ Click "Import"
echo.
pause

echo.
echo 3. Configure Project Settings:
echo.
echo    Framework Preset: Vite
echo    Root Directory:   frontend    ⚠️ IMPORTANT!
echo    Build Command:    npm run build
echo    Output Directory: dist
echo.
pause

echo.
echo 4. Add Environment Variable:
echo    └─ Click "Environment Variables"
echo    └─ Add this:
echo.
echo    Name:  VITE_API_URL
echo    Value: %RAILWAY_URL%
echo.
echo    (Copy your Railway URL from above)
echo.
pause

echo.
echo 5. Click "Deploy"!
echo    └─ Vercel will build your site (1-2 minutes)
echo    └─ Wait for "Congratulations!" message
echo.
pause

echo.
echo 6. Get your website URL:
echo    └─ Copy your Vercel URL
echo    └─ Example: https://hiremebahamas.vercel.app
echo.

set /p VERCEL_URL="Paste your Vercel URL here: "

if not "%VERCEL_URL%"=="" (
    echo %VERCEL_URL% > VERCEL_URL.txt
    echo.
    echo ✅ Vercel URL saved!
)

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║           🎉 DEPLOYMENT COMPLETE! 🎉                     ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo ═══════════════════════════════════════════════════════════
echo   YOUR LIVE PLATFORM
echo ═══════════════════════════════════════════════════════════
echo.
echo Website:          %VERCEL_URL%
echo Backend API:      %RAILWAY_URL%
echo Privacy Policy:   %VERCEL_URL%/privacy-policy.html
echo Terms of Service: %VERCEL_URL%/terms-of-service.html
echo.
echo Admin Login:
echo Email:    admin@hiremebahamas.com
echo Password: AdminPass123!
echo.
echo ═══════════════════════════════════════════════════════════
echo   TESTING YOUR DEPLOYMENT
echo ═══════════════════════════════════════════════════════════
echo.

echo Opening your live site...
start %VERCEL_URL%

echo.
echo TEST CHECKLIST:
echo ═══════════════════════════════════════════════════════════
echo.
echo [ ] Website loads correctly
echo [ ] Can create a new account
echo [ ] Can login with admin credentials
echo [ ] Can post a job (as employer)
echo [ ] Can search for jobs
echo [ ] Privacy policy page works
echo [ ] Terms of service page works
echo.
pause

echo.
echo ═══════════════════════════════════════════════════════════
echo   APP STORE SUBMISSION URLS
echo ═══════════════════════════════════════════════════════════
echo.
echo Use these when submitting to app stores:
echo.
echo Website URL:      %VERCEL_URL%
echo Privacy Policy:   %VERCEL_URL%/privacy-policy.html
echo Terms of Service: %VERCEL_URL%/terms-of-service.html
echo Support Email:    support@hiremebahamas.com
echo.
echo ═══════════════════════════════════════════════════════════
echo   NEXT STEPS
echo ═══════════════════════════════════════════════════════════
echo.
echo Week 1:    Share with 5-10 friends/family for testing
echo Week 2-4:  Beta test with Bahamian users
echo Week 5-8:  Build React Native mobile apps
echo Week 9:    Submit to Apple App Store + Google Play
echo.
echo Run: STEP_5_SHARE_WITH_USERS.bat for marketing materials
echo.
echo ═══════════════════════════════════════════════════════════
echo   🇧🇸 HireMeBahamas is LIVE! 🇧🇸
echo ═══════════════════════════════════════════════════════════
echo.
echo Congratulations! The Bahamas' premier job platform
echo is now live and ready for users!
echo.
pause
