@echo off
REM HireBahamas Platform Auto-Launcher with AI System
REM Automatically configures API keys and starts the 100x enhanced AI platform

echo ========================================
echo 🤖 HIREBAHAMAS AI PLATFORM LAUNCHER
echo ========================================
echo.

REM Change to the project root directory
cd /d "%~dp0"

echo [0/8] Checking Node.js Installation...
python automate_nodejs_fix.py
if errorlevel 1 (
    echo [ERROR] Node.js installation failed
    echo Please install Node.js manually from https://nodejs.org
    pause
    exit /b 1
) else (
    echo ✅ Node.js and npm ready
)

echo.
echo [1/8] Checking AI API Key Configuration...
python configure_api_keys.py --auto --no-validate >nul 2>&1
if errorlevel 1 (
    echo No API keys found in environment. Running setup...
    call setup_api_keys.bat
    if errorlevel 1 (
        echo [ERROR] API key setup failed
        pause
        exit /b 1
    )
) else (
    echo ✅ API keys configured
)

echo.
echo [2/8] Starting Advanced AI System...
echo Running: python advanced_ai_launcher.py
start "AI System" cmd /c "python advanced_ai_launcher.py"
timeout /t 10 /nobreak > nul

echo.
echo [2/8] Setting up Database Tables...
python create_posts_table.py
python add_trade_field.py
if errorlevel 1 (
    echo [WARNING] Database setup had issues, but continuing...
)

echo.
echo [3/8] Setting up Frontend Environment (Automated)...
echo Running: python automated_frontend_fix.py AUTOMATE
python automated_frontend_fix.py AUTOMATE
if errorlevel 1 (
    echo [ERROR] Automated frontend setup failed
    echo Please check the automated_frontend_fix.py script
    pause
    exit /b 1
)

echo.
echo [4/8] Running Health Checks...
cd /d "%~dp0"
python comprehensive_health_check.py
timeout /t 3 /nobreak > nul

echo.
echo [5/8] Opening Browser...
start http://localhost:3000

echo.
echo ========================================
echo 🎉 AI-ENHANCED PLATFORM LAUNCH COMPLETE!
echo ========================================
echo.
echo 🤖 AI Dashboard: http://localhost:3000/ai
echo 🌐 Frontend:     http://localhost:3000
echo 🔧 Backend:      http://127.0.0.1:8008
echo 🎯 AI API:       http://localhost:8009
echo 📧 Admin:        admin@hirebahamas.com
echo 🔑 Password:     AdminPass123!
echo.
echo Press any key to close this window...
pause > nul