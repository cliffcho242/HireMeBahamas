@echo off
REM ============================================
REM  Step 1: Initialize Git & Push to GitHub
REM  Automated GitHub Setup
REM ============================================

echo.
echo ============================================
echo   Step 1: GitHub Repository Setup
echo ============================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo.
    echo Installing Git automatically...
    echo Please wait...
    echo.
    
    REM Download Git installer
    powershell -Command "Write-Host 'Downloading Git installer...' -ForegroundColor Cyan; Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile '%TEMP%\GitInstaller.exe'"
    
    REM Install Git silently
    echo Installing Git...
    start /wait %TEMP%\GitInstaller.exe /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /DIR="C:\Program Files\Git"
    
    echo.
    echo Git installed! Please close this window and run the script again.
    pause
    exit
)

echo Git is installed!
echo.

REM Check if already a git repository
if exist .git (
    echo Git repository already initialized.
    echo.
) else (
    echo Initializing Git repository...
    git init
    git branch -M main
    echo.
    echo Git repository initialized!
    echo.
)

REM Create .gitignore if not exists
if not exist .gitignore (
    echo Creating .gitignore...
    python prepare_deployment.py
)

echo.
echo ============================================
echo   IMPORTANT: Create GitHub Repository
echo ============================================
echo.
echo Please follow these steps:
echo.
echo 1. Go to: https://github.com/new
echo 2. Repository name: HireMeBahamas
echo 3. Description: The Bahamas Premier Job Platform
echo 4. Keep it PUBLIC or PRIVATE (your choice)
echo 5. DO NOT initialize with README
echo 6. Click "Create repository"
echo.
echo After creating, copy the repository URL
echo Example: https://github.com/yourusername/HireMeBahamas.git
echo.

REM Open GitHub in browser
start https://github.com/new

echo.
set /p repo_url="Paste your GitHub repository URL here: "

if "%repo_url%"=="" (
    echo ERROR: No URL provided!
    pause
    exit
)

echo.
echo Adding GitHub remote...
git remote remove origin 2>nul
git remote add origin %repo_url%

echo.
echo Staging all files...
git add .

echo.
echo Committing files...
git commit -m "Initial commit - HireMeBahamas deployment ready"

echo.
echo Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo This might be due to authentication. Please try:
    echo 1. Use GitHub Desktop instead
    echo 2. Or configure Git credentials:
    echo    git config --global user.name "Your Name"
    echo    git config --global user.email "your@email.com"
    echo.
    pause
    exit
)

echo.
echo ============================================
echo   SUCCESS! Code pushed to GitHub!
echo ============================================
echo.
echo Your repository: %repo_url%
echo.
echo Next: Run STEP_2_DEPLOY_BACKEND.bat
echo.
pause
