@echo off
REM HireBahamas Frontend Quick Start
REM This script can be run from anywhere to start the frontend

echo Starting HireBahamas Frontend...
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "FRONTEND_DIR=%PROJECT_DIR%\frontend"

echo Project directory: %PROJECT_DIR%
echo Frontend directory: %FRONTEND_DIR%

REM Check if frontend directory exists
if not exist "%FRONTEND_DIR%" (
    echo ERROR: Frontend directory not found at %FRONTEND_DIR%
    echo Please ensure you're running this from the HireBahamas project folder.
    pause
    exit /b 1
)

REM Check if package.json exists
if not exist "%FRONTEND_DIR%\package.json" (
    echo ERROR: package.json not found in frontend directory
    echo Please ensure Node.js dependencies are installed.
    pause
    exit /b 1
)

REM Navigate to frontend directory and start
cd /d "%FRONTEND_DIR%"
echo Starting npm run dev from: %CD%
echo.

REM Kill any existing node processes
taskkill /F /IM node.exe >nul 2>&1

REM Start the development server
start "HireBahamas Frontend" cmd /c "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo HireBahamas Frontend is starting...
echo It will be available at: http://localhost:3000
echo.
echo Keep this window open to keep the server running.
echo Press Ctrl+C to stop the server.
echo.

REM Keep the window open
pause