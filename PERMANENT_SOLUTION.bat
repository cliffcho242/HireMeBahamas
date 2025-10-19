@echo off
::============================================================================
::
::  HireBahamas - One-Click Permanent Solution
::  This installs auto-start and launches your platform
::
::============================================================================

title HireBahamas - Permanent Solution Installer

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║                                                    ║
echo ║     HireBahamas - Permanent Solution Installer    ║
echo ║                                                    ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo This will:
echo   ✓ Stop any existing servers
echo   ✓ Install auto-start task (runs on login)
echo   ✓ Start both servers
echo   ✓ Open your app in browser
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

:: Run PowerShell script with Install parameter
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0permanent_solution.ps1" -Install

:: Wait for servers to fully start
timeout /t 5 /nobreak >nul

:: Open browser
start http://localhost:3000

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║                                                    ║
echo ║              Installation Complete!                ║
echo ║                                                    ║
echo ║  Your platform is now running and will auto-start  ║
echo ║  every time you log in to Windows.                 ║
echo ║                                                    ║
echo ╚════════════════════════════════════════════════════╝
echo.
echo Useful commands:
echo   - To check status: permanent_solution.ps1 -Status
echo   - To stop servers: permanent_solution.ps1 -Stop
echo   - To uninstall: permanent_solution.ps1 -Uninstall
echo.
pause
