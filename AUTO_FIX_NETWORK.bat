@echo off
REM One-Click Network Fix for HireBahamas
REM Double-click this file to automatically fix network errors

echo.
echo ================================================
echo    HIREBAHAMAS - AUTO FIX NETWORK
echo    One-Click Solution
echo ================================================
echo.

cd /d "%~dp0"

echo [INFO] Starting automated network fix...
echo [INFO] This will take 10-20 seconds...
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0AUTO_FIX_NETWORK.ps1"

echo.
echo ================================================
echo    FIX COMPLETE
echo ================================================
echo.
echo Press any key to close this window...
pause >nul
