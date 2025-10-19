@echo off
REM ============================================
REM  HireMeBahamas - Complete Launch System
REM  One-Click Launch + Deployment
REM ============================================

:MENU
cls
echo.
echo ============================================
echo     HireMeBahamas - Launch System
echo ============================================
echo.
echo DEVELOPMENT:
echo  1. Start Development Servers (Backend + Frontend)
echo  2. Test Backend API
echo  3. Open Frontend in Browser
echo.
echo DEPLOYMENT (Step by Step):
echo  4. Step 1: Push to GitHub
echo  5. Step 2: Deploy Backend to Railway
echo  6. Step 3: Deploy Frontend to Vercel
echo  7. Step 4: Test Production Deployment
echo  8. Step 5: Share With Users
echo.
echo OTHER:
echo  9. View Deployment Dashboard
echo  0. Exit
echo.
echo ============================================
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto START_DEV
if "%choice%"=="2" goto TEST_API
if "%choice%"=="3" goto OPEN_BROWSER
if "%choice%"=="4" goto STEP1_GITHUB
if "%choice%"=="5" goto STEP2_RAILWAY
if "%choice%"=="6" goto STEP3_VERCEL
if "%choice%"=="7" goto STEP4_TEST
if "%choice%"=="8" goto STEP5_SHARE
if "%choice%"=="9" goto VIEW_DASHBOARD
if "%choice%"=="0" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto MENU

:START_DEV
cls
echo.
echo ============================================
echo   Starting Development Servers
echo ============================================
echo.

REM Start Backend
echo Starting Backend on port 9999...
start "HireMeBahamas Backend" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && python run_backend.py"

timeout /t 5 >nul

REM Start Frontend
echo Starting Frontend on port 3000...
start "HireMeBahamas Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ============================================
echo   Servers Started!
echo ============================================
echo.
echo Backend: http://127.0.0.1:9999
echo Frontend: http://localhost:3000
echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:PREPARE_DEPLOY
cls
echo.
echo ============================================
echo   Preparing Deployment Configuration
echo ============================================
echo.

call .venv\Scripts\activate.bat
python prepare_deployment.py

echo.
echo Press any key to return to menu...
pause >nul
goto MENU

:DEPLOY
cls
echo.
echo ============================================
echo   Deploying to Production
echo ============================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please choose option 4 to install Git first.
    echo.
    pause
    goto MENU
)

REM Initialize Git if needed
if not exist .git (
    echo Initializing Git repository...
    git init
    git add .
    git commit -m "Initial commit - HireMeBahamas"
    echo.
    echo Git repository initialized!
    echo.
    echo Please create a repository on GitHub:
    echo 1. Go to: https://github.com/new
    echo 2. Create repository named: HireMeBahamas
    echo 3. Copy the repository URL
    echo.
    set /p repo_url="Paste your GitHub repository URL: "
    git remote add origin !repo_url!
    git branch -M main
)

echo.
echo Pushing to GitHub...
git add .
git commit -m "Deploy: %date% %time%"
git push -u origin main

echo.
echo ============================================
echo   Code Pushed to GitHub!
echo ============================================
echo.
echo Next Steps:
echo 1. Deploy Backend: https://railway.app
echo 2. Deploy Frontend: https://vercel.com
echo.
echo See DEPLOYMENT_READY.md for instructions
echo.
pause
goto MENU

:INSTALL_GIT
cls
echo.
echo ============================================
echo   Installing Git for Windows
echo ============================================
echo.
echo Downloading and installing Git...
echo This may take a few minutes...
echo.

powershell -Command "Start-Process 'https://git-scm.com/download/win' -Wait"

echo.
echo Please download and install Git from the opened webpage.
echo After installation, restart this script.
echo.
pause
goto MENU

:TEST_API
cls
echo.
echo ============================================
echo   Testing Backend API
echo ============================================
echo.

REM Check if backend is running
powershell -Command "$response = try { Invoke-WebRequest -Uri 'http://127.0.0.1:9999/api/health' -UseBasicParsing -TimeoutSec 5 } catch { $null }; if ($response.StatusCode -eq 200) { Write-Host 'Backend is running!' -ForegroundColor Green; Write-Host 'Status: HEALTHY' -ForegroundColor Green } else { Write-Host 'Backend is NOT running!' -ForegroundColor Red; Write-Host 'Start servers with option 1 first' -ForegroundColor Yellow }"

echo.
echo Testing Admin Login...
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://127.0.0.1:9999/api/auth/login' -Method POST -ContentType 'application/json' -Body '{\"email\":\"admin@hiremebahamas.com\",\"password\":\"AdminPass123!\"}' -TimeoutSec 5; Write-Host 'Admin Login: SUCCESS' -ForegroundColor Green; Write-Host 'Token: ' -NoNewline; Write-Host $response.access_token.Substring(0,40) -ForegroundColor Cyan; Write-Host '...' } catch { Write-Host 'Login test failed' -ForegroundColor Red }"

echo.
pause
goto MENU

:OPEN_BROWSER
cls
echo.
echo ============================================
echo   Opening Frontend in Browser
echo ============================================
echo.

start http://localhost:3000

echo.
echo Frontend opened in default browser!
echo If servers are not running, choose option 1 first.
echo.
pause
goto MENU

:VIEW_DOCS
cls
echo.
echo ============================================
echo   Deployment Documentation
echo ============================================
echo.

if exist DEPLOYMENT_READY.md (
    type DEPLOYMENT_READY.md | more
) else (
    echo Documentation not found!
    echo Run option 2 to generate deployment files.
)

echo.
pause
goto MENU

:EXIT
cls
echo.
echo ============================================
echo   Thank you for using HireMeBahamas!
echo ============================================
echo.
echo To start servers later, run this script again.
echo.
timeout /t 2 >nul
exit

