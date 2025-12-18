@echo off
REM Automated Deployment Script for HireMeBahamas

echo ==========================================
echo   HireMeBahamas Automated Deployment
echo ==========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit - HireMeBahamas"
)

REM Push to GitHub
echo.
echo Pushing to GitHub...
git add .
git commit -m "Deploy: %date% %time%"
git push origin main

echo.
echo ✅ Code pushed to GitHub!
echo.
echo Next steps:
echo 1. Deploy backend to Render: https://render.app
echo 2. Deploy frontend to Vercel: https://vercel.com
echo 3. Update environment variables with production URLs
echo.
echo ==========================================
pause
