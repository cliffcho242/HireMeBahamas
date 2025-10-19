@echo off
COLOR 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo         🚀 HIREMEBAHAMAS DEPLOYMENT MASTER CONTROL 🚀
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

echo 📊 CURRENT STATUS:
echo.
echo    ✅ Frontend: DEPLOYED
echo       URL: https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app
echo.
echo    ⏳ Backend:  PENDING
echo       Platform: Railway.app
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 📋 DEPLOYMENT MENU:
echo.
echo    [1] Deploy Backend to Railway (Guided)
echo    [2] Connect Frontend to Backend
echo    [3] Test Deployment (Health Checks)
echo    [4] View Deployment Status
echo    [5] Open Frontend in Browser
echo    [6] Open Backend Dashboard (Railway)
echo    [7] View All URLs
echo    [0] Exit
echo.
echo ═══════════════════════════════════════════════════════════════
echo.

set /p choice="Enter your choice (0-7): "

if "%choice%"=="1" goto deploy_backend
if "%choice%"=="2" goto connect_frontend
if "%choice%"=="3" goto test_deployment
if "%choice%"=="4" goto view_status
if "%choice%"=="5" goto open_frontend
if "%choice%"=="6" goto open_railway
if "%choice%"=="7" goto view_urls
if "%choice%"=="0" goto end

echo.
echo ❌ Invalid choice. Please try again.
timeout /t 2 >nul
goto start

:deploy_backend
cls
echo.
echo 🚂 Deploying Backend to Railway...
echo.
powershell.exe -ExecutionPolicy Bypass -File "DEPLOY_BACKEND_RAILWAY.ps1"
pause
goto start

:connect_frontend
cls
echo.
echo 🔗 Connecting Frontend to Backend...
echo.
powershell.exe -ExecutionPolicy Bypass -File "CONNECT_FRONTEND_TO_BACKEND.ps1"
pause
goto start

:test_deployment
cls
echo.
echo 🧪 Testing Deployment...
echo.
echo Testing Frontend...
curl -I https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app
echo.
echo.
echo If you've deployed backend, enter the URL to test it:
set /p backend_url="Backend URL (or press Enter to skip): "
if not "%backend_url%"=="" (
    echo.
    echo Testing Backend Health...
    curl -X GET "%backend_url%/health"
    echo.
)
echo.
pause
goto start

:view_status
cls
echo.
echo 📄 Opening Deployment Status...
echo.
notepad DEPLOYMENT_STATUS.md
goto start

:open_frontend
echo.
echo 🌐 Opening Frontend...
start https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app
goto start

:open_railway
echo.
echo 🚂 Opening Railway Dashboard...
start https://railway.app/dashboard
goto start

:view_urls
cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🔗 HIREMEBAHAMAS DEPLOYMENT URLS
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo 🌐 FRONTEND (Vercel):
echo    https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app
echo.
echo 🔧 BACKEND (Railway):
echo    [Deploy using Option 1 in menu]
echo.
echo 📄 LEGAL PAGES:
echo    Privacy: https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app/privacy-policy.html
echo    Terms:   https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app/terms-of-service.html
echo.
echo 🔐 ADMIN LOGIN:
echo    Email:    admin@hiremebahamas.com
echo    Password: AdminPass123!
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
goto start

:end
echo.
echo 👋 Goodbye! Your app is live at:
echo    https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app
echo.
timeout /t 3 >nul
exit

:start
goto :eof
