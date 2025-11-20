@echo off
REM One-Click Setup Script for HireMeBahamas (Windows)
REM Installs and activates all dependencies with zero manual intervention

echo ==================================
echo 🚀 HireMeBahamas One-Click Setup
echo ==================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set ROOT_DIR=%SCRIPT_DIR%..
cd /d "%ROOT_DIR%"

echo 📁 Working directory: %ROOT_DIR%
echo.

REM Step 1: Install Python dependencies
echo ==================================
echo 📦 Step 1: Installing Python Dependencies
echo ==================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% EQU 0 (
        echo ✅ Python dependencies installed
    ) else (
        echo ❌ Failed to install Python dependencies
        exit /b 1
    )
) else (
    echo ❌ Python not found. Please install Python 3.8+
    exit /b 1
)

echo.

REM Step 2: Activate all dependencies
echo ==================================
echo ⚙️  Step 2: Activating Dependencies
echo ==================================
echo.

python scripts\activate_all_dependencies.py
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Some optional dependencies could not be activated
    echo    The application will still work with reduced functionality
)

echo.

REM Step 3: Install frontend dependencies
echo ==================================
echo 🎨 Step 3: Installing Frontend Dependencies
echo ==================================
echo.

if exist "frontend\package.json" (
    cd frontend
    
    where npm >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        npm install
        if %ERRORLEVEL% EQU 0 (
            echo ✅ Frontend dependencies installed
        ) else (
            echo ⚠️  Frontend installation had issues
        )
    ) else (
        echo ⚠️  npm not found. Skipping frontend setup.
        echo    Install Node.js to build the frontend
    )
    
    cd ..
) else (
    echo ⚠️  Frontend directory not found
)

echo.

REM Step 4: Run startup initialization
echo ==================================
echo 🔧 Step 4: Running Startup Initialization
echo ==================================
echo.

python scripts\startup_init.py
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Startup checks found some issues
)

echo.

REM Step 5: Verify all dependencies
echo ==================================
echo ✅ Step 5: Verifying Dependencies
echo ==================================
echo.

python scripts\check_dependencies.py
set VERIFY_RESULT=%ERRORLEVEL%

echo.
echo ==================================

if %VERIFY_RESULT% EQU 0 (
    echo ✅ ALL DEPENDENCIES INSTALLED, ACTIVE, AND VERIFIED!
    echo.
    echo 🎉 Setup complete! You can now:
    echo    1. Start the backend: python final_backend_postgresql.py
    echo    2. Start the frontend: cd frontend ^&^& npm run dev
    echo    3. Check health: curl http://localhost:5000/api/health/dependencies
) else (
    echo ⚠️  Setup completed with warnings
    echo.
    echo 💡 The application may work with reduced functionality
    echo    Check the dependency report for details
)

echo ==================================
pause
