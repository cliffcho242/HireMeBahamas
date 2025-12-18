@echo off
REM ============================================
REM  Step 2: Deploy Backend to Render
REM  Automated Render Deployment Guide
REM ============================================

echo.
echo ============================================
echo   Step 2: Deploy Backend to Render
echo ============================================
echo.

echo Render is a modern platform that makes deployment easy!
echo.
echo COST: 100%% FREE to start (500 hours/month = always on)
echo.

echo ============================================
echo   Follow These Steps:
echo ============================================
echo.

echo 1. SIGN UP / LOGIN
echo    Opening Render.app in your browser...
echo.

start https://render.app

timeout /t 3 >nul

echo 2. CLICK "Start a New Project"
echo    - Click the "New Project" button
echo.
pause

echo 3. SELECT "Deploy from GitHub repo"
echo    - Choose "Deploy from GitHub repo"
echo    - Render will ask to connect to GitHub
echo    - Authorize Render to access your repositories
echo.
pause

echo 4. SELECT YOUR REPOSITORY
echo    - Find and select: HireMeBahamas
echo    - Render will automatically detect your configuration!
echo.
pause

echo 5. ADD ENVIRONMENT VARIABLE
echo    - Click on your project
echo    - Go to "Variables" tab
echo    - Click "New Variable"
echo    - Add this:
echo.

REM Read SECRET_KEY from .env
for /f "tokens=2 delims==" %%a in ('findstr "SECRET_KEY" .env') do set SECRET_KEY=%%a

echo    Variable Name:  SECRET_KEY
echo    Variable Value: %SECRET_KEY%
echo.
echo    (Copy the value above)
echo.
pause

echo 6. WAIT FOR DEPLOYMENT
echo    - Render will build and deploy automatically
echo    - Wait 2-3 minutes
echo    - Check the "Deployments" tab for status
echo.
pause

echo 7. GET YOUR BACKEND URL
echo    - Click "Settings" tab
echo    - Find "Domains" section
echo    - Click "Generate Domain"
echo    - Copy your Render URL (e.g., https://hiremebahamas-backend-production.up.render.app)
echo.
set /p RAILWAY_URL="Paste your Render backend URL here: "

if "%RAILWAY_URL%"=="" (
    echo No URL provided. You can add it later.
) else (
    REM Save Render URL to file
    echo %RAILWAY_URL% > RAILWAY_URL.txt
    echo.
    echo Render URL saved!
)

echo.
echo ============================================
echo   Backend Deployment Complete!
echo ============================================
echo.
echo Your backend is now live at:
echo %RAILWAY_URL%
echo.
echo Test it: %RAILWAY_URL%/api/health
echo.

if not "%RAILWAY_URL%"=="" (
    echo Opening health check...
    timeout /t 2 >nul
    start %RAILWAY_URL%/api/health
)

echo.
echo Next: Run STEP_3_DEPLOY_FRONTEND.bat
echo.
pause
