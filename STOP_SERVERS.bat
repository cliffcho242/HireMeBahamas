@echo off
::============================================================================
::  HireBahamas - Stop All Servers
::  Run this to cleanly stop all running services
::============================================================================

title HireBahamas - Stopping Servers

echo.
echo ================================================
echo   HireBahamas - Stopping All Servers
echo ================================================
echo.

:: Stop all Python and Node processes
echo [1/3] Stopping Python processes...
powershell -Command "Get-Process | Where-Object { $_.ProcessName -like '*python*' } | Stop-Process -Force" 2>nul

echo [2/3] Stopping Node.js processes...
powershell -Command "Get-Process | Where-Object { $_.ProcessName -like '*node*' } | Stop-Process -Force" 2>nul

:: Stop any PowerShell processes running our scripts
echo [3/3] Stopping PowerShell monitors...
powershell -Command "Get-Process | Where-Object { $_.MainWindowTitle -like '*powershell*' -and ($_.CommandLine -like '*service_monitor*' -or $_.CommandLine -like '*complete_launcher*') } | Stop-Process -Force" 2>nul

timeout /t 2 /nobreak >nul

echo.
echo ================================================
echo   SUCCESS! All servers stopped
echo ================================================
echo.
echo   To restart: Run QUICK_START.bat
echo.
pause
