@echo off
REM ============================================
REM  HireMeBahamas - Main Launch Menu
REM  Automated Deployment System
REM ============================================

:MENU
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║   HireMeBahamas - Complete Launch System  ║
echo ╚════════════════════════════════════════════╝
echo.
echo DEVELOPMENT:
echo  [1] Start Dev Servers (Backend + Frontend)
echo  [2] Test Backend API  
echo  [3] Open Frontend Browser
echo.
echo DEPLOYMENT - Follow in Order:
echo  [4] ► Step 1: Push to GitHub
echo  [5] ► Step 2: Deploy Backend (Railway)
echo  [6] ► Step 3: Deploy Frontend (Vercel)
echo  [7] ► Step 4: Test Production
echo  [8] ► Step 5: Marketing & Share
echo.
echo OTHER:
echo  [9] View Deployment Dashboard
echo  [0] Exit
echo.
echo ═══════════════════════════════════════════
set /p choice="Enter choice (0-9): "

if "%choice%"=="1" goto START_DEV
if "%choice%"=="2" goto TEST_API
if "%choice%"=="3" goto OPEN_BROWSER  
if "%choice%"=="4" goto STEP1
if "%choice%"=="5" goto STEP2
if "%choice%"=="6" goto STEP3
if "%choice%"=="7" goto STEP4
if "%choice%"=="8" goto STEP5
if "%choice%"=="9" goto DASHBOARD
if "%choice%"=="0" goto EXIT

echo Invalid choice!
timeout /t 2 >nul
goto MENU

:START_DEV
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║      Starting Development Servers          ║
echo ╚════════════════════════════════════════════╝
echo.

echo [1/2] Starting Backend on port 9999...
start "HireMeBahamas Backend" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && python run_backend.py"

timeout /t 5 >nul

echo [2/2] Starting Frontend on port 3000...
start "HireMeBahamas Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ═══════════════════════════════════════════
echo   ✓ Servers Started!
echo ═══════════════════════════════════════════
echo.
echo Backend:  http://127.0.0.1:9999
echo Frontend: http://localhost:3000
echo.
pause
goto MENU

:TEST_API
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║         Testing Backend API                ║
echo ╚════════════════════════════════════════════╝
echo.

powershell -Command "$response = try { Invoke-WebRequest -Uri 'http://127.0.0.1:9999/api/health' -UseBasicParsing -TimeoutSec 5 } catch { $null }; if ($response.StatusCode -eq 200) { Write-Host '✓ Backend is running!' -ForegroundColor Green; Write-Host 'Status: HEALTHY' -ForegroundColor Cyan } else { Write-Host '✗ Backend NOT running!' -ForegroundColor Red; Write-Host 'Start servers with option 1 first' -ForegroundColor Yellow }"

echo.
echo Testing admin login...
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://127.0.0.1:9999/api/auth/login' -Method POST -ContentType 'application/json' -Body '{\"email\":\"admin@hiremebahamas.com\",\"password\":\"AdminPass123!\"}' -TimeoutSec 5; Write-Host '✓ Admin Login: SUCCESS' -ForegroundColor Green; Write-Host ('Token: ' + $response.access_token.Substring(0,40) + '...') -ForegroundColor Cyan } catch { Write-Host '✗ Login test failed' -ForegroundColor Red }"

echo.
pause
goto MENU

:OPEN_BROWSER
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║       Opening Frontend in Browser          ║
echo ╚════════════════════════════════════════════╝
echo.

start http://localhost:3000

echo.
echo Frontend opened in browser!
echo If servers aren't running, use option 1 first.
echo.
pause
goto MENU

:STEP1
cls
call STEP_1_GITHUB_SETUP.bat
goto MENU

:STEP2
cls
call STEP_2_DEPLOY_BACKEND.bat
goto MENU

:STEP3
cls
call STEP_3_DEPLOY_FRONTEND.bat
goto MENU

:STEP4
cls
call STEP_4_TEST_DEPLOYMENT.bat
goto MENU

:STEP5
cls
call STEP_5_SHARE_WITH_USERS.bat
goto MENU

:DASHBOARD
cls
echo.
echo Opening deployment dashboard...
start deployment_dashboard.html
timeout /t 2 >nul
goto MENU

:EXIT
cls
echo.
echo ╔════════════════════════════════════════════╗
echo ║   Thank you for using HireMeBahamas!       ║
echo ╚════════════════════════════════════════════╝
echo.
echo To deploy: Run this script and choose option 4
echo Documentation: deployment_dashboard.html
echo.
timeout /t 3 >nul
exit
