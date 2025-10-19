@echo off
REM HireBahamas Ultimate Automation Launcher
REM Fixes freezing issues, installs requirements, enables HireMe automation

echo ========================================
echo 🚀 HIREBAHAMAS ULTIMATE AUTOMATION
echo ========================================
echo.

REM Set error handling
setlocal enabledelayedexpansion
set "ERROR_FLAG=0"

REM Change to project directory
cd /d "%~dp0"

echo [1/8] Checking Python Environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+
    echo Download from: https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo [2/8] Installing Python Requirements...
echo Attempting to install Python packages (this may take a few minutes)...
pip install --upgrade pip --quiet
pip install -r requirements.txt --timeout 300
if %errorlevel% neq 0 (
    echo [WARNING] Some Python packages may have failed to install due to network issues
    echo You can try installing them manually later with: pip install -r requirements.txt
    echo Continuing with setup...
) else (
    echo ✅ Python requirements installed
)

echo.
echo [3/8] Checking Node.js Environment...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found! Please install Node.js 18+
    echo Download from: https://nodejs.org
    pause
    exit /b 1
)
echo ✅ Node.js found

echo.
echo [4/8] Installing Frontend Dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages...
    npm install --silent
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install npm packages
        cd ..
        pause
        exit /b 1
    )
) else (
    echo Node modules already installed
)
cd ..
echo ✅ Frontend dependencies ready

echo.
echo [5/8] Setting up HireMe Availability Automation...
echo Creating automated HireMe availability manager...

REM Create the HireMe automation script
(
echo @echo off
echo REM HireMe Availability Automation Manager
echo REM Automatically manages user availability for HireMe feature
echo.
echo echo Starting HireMe Availability Automation...
echo python hireme_automation.py
echo.
echo pause
) > hireme_automation.bat

echo ✅ HireMe automation script created

echo.
echo [6/8] Starting Backend Service...
echo Starting Flask backend on port 8008...
start "HireBahamas Backend" cmd /c "python ULTIMATE_BACKEND_FIXED.py"
timeout /t 5 /nobreak > nul

echo.
echo [7/8] Starting Frontend Service...
echo Starting React frontend on port 3000...
cd frontend
start "HireBahamas Frontend" cmd /c "npm run dev"
cd ..
timeout /t 10 /nobreak > nul

echo.
echo [8/8] Running Comprehensive Health Checks...
call run_health_check.bat

echo.
echo ========================================
echo 🎯 AUTOMATION COMPLETE!
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://127.0.0.1:8008
echo 📧 Admin:    admin@hirebahamas.com
echo 🔑 Password: AdminPass123!
echo.
echo 🚀 HireMe Features:
echo   • Browse available talent
echo   • Toggle availability status
echo   • Real-time updates
echo.
echo 📋 Automation Scripts:
echo   • hireme_automation.bat - Auto-updates availability
echo.
echo Press any key to open browser and start HireMe automation...
pause > nul

echo.
echo 🚀 Starting HireMe Availability Automation...
start "HireMe Automation" cmd /c "hireme_automation.bat"

echo.
echo 🌐 Opening browser...
start http://localhost:3000

echo.
echo ✅ Setup complete! HireMe automation is running in background.
echo    Close this window to stop automation.
echo.
pause