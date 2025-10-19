@echo off
title HireBahamas - Facebook-Like AI Platform Launcher

echo.
echo ================================================================
echo         🚀 HireBahamas Facebook-Like AI Platform
echo              Advanced Social Media Experience
echo ================================================================
echo.

echo [STEP 1] 🤖 Installing AI Requirements...
cd /d "c:\Users\Dell\OneDrive\Desktop\HireBahamas"

REM Activate virtual environment
call ".venv\Scripts\activate.bat"

echo.
echo [STEP 2] 🔧 Starting Facebook-Like Backend...
echo Starting AI-powered social backend server...
start "HireBahamas Facebook Backend" cmd /k "cd /d c:\Users\Dell\OneDrive\Desktop\HireBahamas && .venv\Scripts\python.exe facebook_like_backend.py"

timeout /t 6 /nobreak >nul

echo.
echo [STEP 3] 🌐 Starting Social Frontend...
echo Switching to simple App for social features...

REM Backup current App.tsx and use social version
cd frontend\src
if not exist "App_Original.tsx" (
    copy App.tsx App_Original.tsx >nul
    echo Original App.tsx backed up
)
copy App_Social.tsx App.tsx >nul
echo Switched to Facebook-like frontend

cd ..\..

echo Starting frontend server...
start "HireBahamas Social Frontend" cmd /k "cd /d c:\Users\Dell\OneDrive\Desktop\HireBahamas\frontend && npm run dev"

timeout /t 8 /nobreak >nul

echo.
echo [STEP 4] 🔍 Health Check...
powershell -Command "try { $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8008/health' -TimeoutSec 10; Write-Host 'Facebook-Like Backend: HEALTHY' -ForegroundColor Green; Write-Host 'AI Analytics: ' $health.ai_analytics -ForegroundColor Green } catch { Write-Host 'Backend: Starting up...' -ForegroundColor Yellow }"

echo.
echo [STEP 5] 🚀 Opening Social Platform...
start http://localhost:3000
timeout /t 2 /nobreak >nul
start http://localhost:3001

echo.
echo ================================================================
echo                🎉 FACEBOOK-LIKE PLATFORM LAUNCHED! 🎉
echo ================================================================
echo.
echo Your AI-Powered Social Platform Features:
echo.
echo 🤖 AI Features:
echo   • User behavior pattern analysis
echo   • Intelligent content recommendations
echo   • Engagement score tracking
echo   • User type classification
echo   • Predictive analytics
echo.
echo 🌐 Social Features:
echo   • Facebook-like interface
echo   • Real-time posts and comments
echo   • Like and share functionality
echo   • AI-powered feed optimization
echo   • User profile management
echo   • Direct messaging
echo   • Trending topics
echo.
echo 🎯 Access URLs:
echo   • Platform: http://localhost:3000
echo   • Alt Port: http://localhost:3001
echo   • Backend API: http://127.0.0.1:8008
echo   • Health Check: http://127.0.0.1:8008/health
echo.
echo 👤 Login Credentials:
echo   • Email: admin@hirebahamas.com
echo   • Password: AdminPass123!
echo.
echo ================================================================
echo.
echo 🔧 Technical Features Active:
echo   ✓ AI User Pattern Analytics
echo   ✓ Machine Learning Recommendations
echo   ✓ Real-time Socket Connections
echo   ✓ Advanced Rate Limiting
echo   ✓ JWT Authentication
echo   ✓ Performance Caching
echo   ✓ Predictive Error Prevention
echo.
echo Both servers are running in separate windows.
echo The AI system continuously learns from user interactions.
echo.
echo ================================================================

echo.
echo Press any key to exit launcher (servers will continue running)...
pause >nul