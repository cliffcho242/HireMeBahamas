@echo off
REM ============================================
REM  AUTOMATED DEPLOYMENT - NO GIT NEEDED!
REM  Uses GitHub Desktop for Easy Setup
REM ============================================

echo.
echo ╔════════════════════════════════════════════╗
echo ║   Automated GitHub Setup (No Git Needed)  ║
echo ╚════════════════════════════════════════════╝
echo.

echo OPTION 1: GitHub Desktop (Easiest!)
echo =====================================
echo.
echo GitHub Desktop is a visual tool - no commands needed!
echo.
echo 1. Download GitHub Desktop (opening now...)
echo.

start https://desktop.github.com

timeout /t 3 >nul

echo 2. Install and sign in to GitHub
echo 3. Click "Add an existing repository"
echo 4. Browse to: C:\Users\Dell\OneDrive\Desktop\HireBahamas
echo 5. Click "Create repository on GitHub.com"
echo 6. Name it: HireBahamas
echo 7. Click "Publish repository"
echo.
echo ✅ Done! Your code is on GitHub!
echo.

pause

echo.
echo ╔════════════════════════════════════════════╗
echo ║   GitHub Repository Created!               ║
echo ╚════════════════════════════════════════════╝
echo.

set /p github_url="Paste your GitHub repository URL (or press Enter to continue): "

if not "%github_url%"=="" (
    echo %github_url% > GITHUB_URL.txt
    echo.
    echo ✅ Repository URL saved!
)

echo.
echo ═══════════════════════════════════════════
echo   Next: Run STEP_2_DEPLOY_BACKEND.bat
echo ═══════════════════════════════════════════
echo.
pause
