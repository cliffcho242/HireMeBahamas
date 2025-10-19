@echo off
REM ============================================
REM  Install Git for Windows
REM ============================================

echo.
echo ============================================
echo   Installing Git for Windows
echo ============================================
echo.
echo Downloading Git installer...
echo.

REM Download Git installer using PowerShell
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile '%TEMP%\GitInstaller.exe'"

echo.
echo Installing Git...
echo.

REM Run installer silently
start /wait %TEMP%\GitInstaller.exe /VERYSILENT /NORESTART

echo.
echo ============================================
echo   Git Installation Complete!
echo ============================================
echo.
echo Please close this window and reopen PowerShell
echo Then run: git --version
echo.
pause
