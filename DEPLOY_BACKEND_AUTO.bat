@echo off
REM ============================================
REM  COMPLETE AUTOMATED DEPLOYMENT
REM  Render CLI Method (No Git/GitHub Needed!)
REM ============================================

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║      🚀 AUTOMATED DEPLOYMENT - SIMPLEST METHOD! 🚀       ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo This method uses Render CLI to deploy directly!
echo No Git or GitHub account needed!
echo.

echo ═══════════════════════════════════════════════════════════
echo   Step 1: Install Render CLI
echo ═══════════════════════════════════════════════════════════
echo.

echo Installing Render CLI...
powershell -Command "iwr https://render.app/install.ps1 -useb | iex"

if errorlevel 1 (
    echo.
    echo ERROR: Render CLI installation failed
    echo.
    echo ALTERNATIVE: Use Render Web Interface
    echo Opening Render.app...
    start https://render.app
    echo.
    echo Follow these steps:
    echo 1. Sign up / Login
    echo 2. Click "New Project"
    echo 3. Click "Empty Project"
    echo 4. Upload your code manually
    echo.
    pause
    exit
)

echo.
echo ✅ Render CLI installed!
echo.

echo ═══════════════════════════════════════════════════════════
echo   Step 2: Login to Render
echo ═══════════════════════════════════════════════════════════
echo.

render login

echo.
echo ═══════════════════════════════════════════════════════════
echo   Step 3: Create New Render Project
echo ═══════════════════════════════════════════════════════════
echo.

render init

echo.
echo ═══════════════════════════════════════════════════════════
echo   Step 4: Add Environment Variables
echo ═══════════════════════════════════════════════════════════
echo.

REM Read SECRET_KEY from .env
for /f "tokens=2 delims==" %%a in ('findstr "SECRET_KEY" .env') do set SECRET_KEY=%%a

echo Adding SECRET_KEY...
render variables set SECRET_KEY=%SECRET_KEY%

echo.
echo ═══════════════════════════════════════════════════════════
echo   Step 5: Deploy Backend
echo ═══════════════════════════════════════════════════════════
echo.

echo Deploying to Render...
render up

echo.
echo ═══════════════════════════════════════════════════════════
echo   Step 6: Get Your Backend URL
echo ═══════════════════════════════════════════════════════════
echo.

render domain

echo.
echo Copy your Render URL from above
echo.
set /p RAILWAY_URL="Paste your Render URL here: "

if not "%RAILWAY_URL%"=="" (
    echo %RAILWAY_URL% > RAILWAY_URL.txt
    echo.
    echo ✅ Render URL saved!
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   Backend Deployed Successfully!
echo ═══════════════════════════════════════════════════════════
echo.
echo Your backend is live at: %RAILWAY_URL%
echo.
echo Next: Run STEP_3_DEPLOY_FRONTEND.bat
echo.
pause
