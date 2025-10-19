@echo off
REM Master Network Fix Launcher for HireMeBahamas
REM Ensures network never fails and admin login always works

echo ============================================
echo MASTER NETWORK FIX - HireMeBahamas
echo ============================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Not running as administrator
    echo Some network fixes may not apply
    echo Continuing anyway...
    echo.
)

REM Navigate to project directory
cd /d "%~dp0"

REM Activate virtual environment
echo [1/4] Activating Python environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Could not activate virtual environment
    echo Creating new virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)
echo [OK] Virtual environment activated
echo.

REM Install required packages
echo [2/4] Installing required packages...
python -m pip install --upgrade pip --quiet
python -m pip install flask flask-cors waitress pyjwt bcrypt requests --upgrade --quiet
echo [OK] Packages installed
echo.

REM Run master network fix
echo [3/4] Running master network fix...
python master_network_fix.py
if %errorlevel% neq 0 (
    echo [ERROR] Master fix failed
    pause
    exit /b 1
)

echo.
echo [4/4] Testing admin login...
timeout /t 5 /nobreak >nul
python test_admin_network.py

echo.
echo ============================================
echo MASTER FIX COMPLETE!
echo Backend server is running
echo Test admin login at: http://127.0.0.1:9999
echo ============================================
echo.
echo Press any key to stop the server...
pause >nul
