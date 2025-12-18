@echo off
REM ============================================
REM  HireMeBahamas - Automated Deployment
REM  One-Click Deployment Preparation
REM ============================================

echo.
echo ============================================
echo   HireMeBahamas Deployment Automation
echo ============================================
echo.
echo This script will:
echo  1. Create all deployment configuration files
echo  2. Generate environment variables
echo  3. Create privacy policy and terms pages
echo  4. Prepare for Render and Vercel deployment
echo.
echo Press any key to start...
pause > nul

echo.
echo Starting automated deployment preparation...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run deployment preparation script
python prepare_deployment.py

echo.
echo ============================================
echo   Deployment Preparation Complete!
echo ============================================
echo.
echo Next steps:
echo  1. Review the generated files
echo  2. Update .env with your settings
echo  3. Run DEPLOY.bat to push to GitHub
echo  4. Deploy to Render and Vercel
echo.
echo Read DEPLOYMENT_READY.md for full instructions
echo.
pause
