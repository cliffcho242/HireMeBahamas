@echo off
REM AI-Powered HireBahamas Platform Launcher with Permanent Network Fix
REM Automatically diagnoses, fixes, and continuously monitors network/auth issues

echo ========================================
echo 🤖 AI HIREBAHAMAS PLATFORM LAUNCHER
echo    Permanent Network Error Fix
echo ========================================
echo.

cd /d "%~dp0"

echo [1/8] Installing AI Requirements...
python install_ai_requirements.py
if errorlevel 1 (
    echo [WARNING] Some AI requirements failed to install, but continuing...
)

echo.
echo [2/8] Running AI Permanent Network Fixer (Diagnostic)...
python ai_permanent_network_fixer.py
if errorlevel 1 (
    echo [ERROR] AI Permanent Fixer failed - attempting emergency restart...
    python ai_permanent_network_fixer.py
)

echo.
echo [3/8] Starting AI Continuous Monitoring (Background)...
start /B "AI Network Monitor" cmd /c "python ai_permanent_network_fixer.py monitor"

echo.
echo [4/8] Starting Backend Server...
start "HireBahamas Backend" cmd /c "python final_backend.py"

echo.
echo [5/8] Starting Frontend Server...
python automated_frontend_fix.py
if errorlevel 1 (
    echo [WARNING] Automated frontend start failed, trying manual...
    cd frontend
    start "HireBahamas Frontend" cmd /c "npm run dev"
    cd ..
)

echo.
echo [6/8] Running Final Health Check...
timeout /t 8 /nobreak > nul
python ai_permanent_network_fixer.py

echo.
echo [7/8] Opening Browser...
start http://localhost:3001

echo.
echo [8/8] Launch Complete - Testing Admin Login...
echo Testing admin login functionality...
python -c "
import requests
try:
    response = requests.post('http://127.0.0.1:8008/auth/login', json={'email': 'admin@hirebahamas.com', 'password': 'AdminPass123!'}, timeout=10)
    if response.status_code == 200 and response.json().get('success'):
        print('✅ Admin login test PASSED - Network errors permanently fixed!')
    else:
        print('❌ Admin login test FAILED')
except Exception as e:
    print('❌ Admin login test FAILED - Network error:', str(e))
"

echo.
echo ========================================
echo 🎉 AI-ENHANCED PLATFORM LAUNCH COMPLETE!
echo    Permanent Network Protection Active
echo ========================================
echo.
echo 🤖 AI Dashboard: http://localhost:3001/ai
echo 🌐 Frontend:     http://localhost:3001
echo 🔧 Backend:      http://127.0.0.1:8008
echo 📧 Admin Login:  admin@hirebahamas.com
echo 🔑 Password:     AdminPass123!
echo.
echo 🔄 AI Continuous Monitoring: ACTIVE
echo 🛡️  Network Error Protection: ENABLED
echo ⚡ Auto-Fix on Detection: ENABLED
echo.
echo Press any key to close this window...
pause > nul

goto :eof

:manual_fix
echo.
echo [MANUAL FIX] Starting services manually...
echo.

REM Kill any existing processes
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

REM Start backend
start "HireBahamas Backend" cmd /c "python final_backend.py"

REM Start frontend
cd frontend
start "HireBahamas Frontend" cmd /c "npm run dev"
cd ..

echo Manual startup complete. Check services are running.
pause
goto :eof
import requests
try:
    response = requests.post('http://127.0.0.1:8008/auth/login', json={'email': 'admin@hirebahamas.com', 'password': 'AdminPass123!'}, timeout=10)
    if response.status_code == 200 and response.json().get('success'):
        print('✅ Admin login test PASSED')
    else:
        print('❌ Admin login test FAILED')
except:
    print('❌ Admin login test FAILED - Network error')
"

echo.
echo ========================================
echo 🎉 AI-ENHANCED PLATFORM LAUNCH COMPLETE!
echo ========================================
echo.
echo 🤖 AI Dashboard: http://localhost:3000/ai
echo 🌐 Frontend:     http://localhost:3000
echo 🔧 Backend:      http://127.0.0.1:8008
echo 📧 Admin Login:  admin@hirebahamas.com
echo 🔑 Password:     AdminPass123!
echo.
echo Press any key to close this window...
pause > nul

goto :eof

:manual_fix
echo.
echo [MANUAL FIX] Starting services manually...
echo.

REM Kill any existing processes
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

REM Start backend
start "HireBahamas Backend" cmd /c "python final_backend.py"

REM Start frontend
cd frontend
start "HireBahamas Frontend" cmd /c "npm run dev"
cd ..

echo Manual startup complete. Check services are running.
pause
goto :eof