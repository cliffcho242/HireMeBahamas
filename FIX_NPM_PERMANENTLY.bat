@echo off
REM Permanent Node.js/npm Fix for HireBahamas
REM This script ensures Node.js and npm are properly installed and configured

echo ========================================
echo PERMANENT NODE.JS/NPM FIX
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Node.js installation...
python automate_nodejs_fix.py

if errorlevel 1 (
    echo.
    echo FAILED: Could not install Node.js
    echo Please run this script as Administrator or install manually
    echo.
    pause
    exit /b 1
)

echo.
echo SUCCESS: Node.js and npm are now permanently installed!
echo.
echo You can now run:
echo - npm install
echo - npm run dev
echo - python automated_frontend_fix.py
echo.
echo Press any key to continue...
pause > nul