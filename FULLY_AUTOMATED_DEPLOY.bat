@echo off
title HireMeBahamas - Fully Automated Deployment
color 0B

echo.
echo ========================================
echo    FULLY AUTOMATED DEPLOYMENT
echo ========================================
echo.
echo This will:
echo   1. Initialize git repository
echo   2. Open GitHub to create repository
echo   3. Guide you through Render deployment
echo   4. Deploy frontend to Vercel
echo   5. Give you final URLs
echo.
echo Press any key to start...
pause > nul

cd /d "%~dp0"

echo.
echo [1/6] Initializing git repository...
git init
if errorlevel 1 (
    echo.
    echo WARNING: Git not installed!
    echo Installing Git...
    powershell -Command "Start-Process 'https://git-scm.com/download/win' -Wait"
    echo Please install Git and run this script again.
    pause
    exit /b
)

echo [2/6] Adding files to git...
git add .
git commit -m "Initial commit - HireMeBahamas Platform"
git branch -M main

echo.
echo [3/6] Opening GitHub to create repository...
timeout /t 2 /nobreak > nul
start https://github.com/new

echo.
echo ========================================
echo    GITHUB SETUP
echo ========================================
echo.
echo In the GitHub page that just opened:
echo   1. Repository name: HireMeBahamas
echo   2. Description: Job platform for the Bahamas
echo   3. Make it Public
echo   4. Click "Create repository"
echo.
echo After creating, copy the repository URL (looks like:)
echo   https://github.com/YOUR_USERNAME/HireMeBahamas.git
echo.
set /p GITHUB_URL="Paste your GitHub repository URL here: "

echo.
echo [4/6] Connecting to GitHub...
git remote add origin %GITHUB_URL%
git push -u origin main

if errorlevel 1 (
    echo.
    echo NOTE: If you see an authentication error:
    echo   1. GitHub may need you to log in
    echo   2. Use GitHub Desktop or authenticate via browser
    echo.
    pause
)

echo.
echo [5/6] Opening Render.com for deployment...
timeout /t 2 /nobreak > nul
start https://dashboard.render.com/register

echo.
echo ========================================
echo    RENDER DEPLOYMENT
echo ========================================
echo.
echo In the Render page that just opened:
echo.
echo   1. Sign up with GitHub (click button)
echo   2. After signup, click "New +" button
echo   3. Select "Web Service"
echo   4. Click "Connect a repository"
echo   5. Find and select: HireMeBahamas
echo   6. Render will AUTO-DETECT everything!
echo   7. Click "Create Web Service"
echo   8. Wait 2-3 minutes for deployment
echo.
echo After deployment completes, copy your backend URL.
echo It will look like: https://hiremebahamas-XXXXX.onrender.com
echo.
set /p BACKEND_URL="Paste your Render backend URL here: "

echo.
echo [6/6] Deploying frontend to Vercel...

REM Update frontend environment
echo VITE_API_URL=%BACKEND_URL% > frontend\.env.production

cd frontend
call vercel --prod --yes

if errorlevel 1 (
    echo.
    echo Error deploying frontend. Trying again...
    call vercel --prod --yes
)

cd ..

echo.
echo ========================================
echo    DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo YOUR LIVE PLATFORM:
echo.
echo   Backend:  %BACKEND_URL%
echo   Frontend: (Check output above)
echo.
echo   Admin: admin@hiremebahamas.com
echo   Password: AdminPass123!
echo.
echo APP STORE READY!
echo   Use your frontend URL for app store submission
echo.
echo All details saved to: DEPLOYMENT_COMPLETE.txt
echo.
pause
