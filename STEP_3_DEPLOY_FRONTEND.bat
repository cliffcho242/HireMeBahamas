@echo off
REM ============================================
REM  Step 3: Deploy Frontend to Vercel
REM  Automated Vercel Deployment Guide
REM ============================================

echo.
echo ============================================
echo   Step 3: Deploy Frontend to Vercel
echo ============================================
echo.

echo Vercel is the fastest way to deploy React apps!
echo.
echo COST: 100%% FREE (unlimited bandwidth!)
echo.

REM Read Render URL if exists
if exist RAILWAY_URL.txt (
    set /p RAILWAY_URL=<RAILWAY_URL.txt
) else (
    set /p RAILWAY_URL="Enter your Render backend URL: "
)

echo.
echo ============================================
echo   Follow These Steps:
echo ============================================
echo.

echo 1. SIGN UP / LOGIN
echo    Opening Vercel.com in your browser...
echo.

start https://vercel.com/new

timeout /t 3 >nul

echo 2. IMPORT PROJECT
echo    - Click "Add New..." then "Project"
echo    - Click "Import Git Repository"
echo    - Find your GitHub account and authorize Vercel
echo.
pause

echo 3. SELECT HIREMEBAHAMAS REPOSITORY
echo    - Find "HireMeBahamas" in the list
echo    - Click "Import"
echo.
pause

echo 4. CONFIGURE PROJECT
echo    Important settings:
echo.
echo    Framework Preset: Vite
echo    Root Directory: frontend  (IMPORTANT!)
echo    Build Command: npm run build
echo    Output Directory: dist
echo.
pause

echo 5. ADD ENVIRONMENT VARIABLE
echo    - Click "Environment Variables"
echo    - Add this variable:
echo.
echo    Variable Name:  VITE_API_URL
echo    Variable Value: %RAILWAY_URL%
echo.
echo    (Copy the Render URL above)
echo.
pause

echo 6. DEPLOY!
echo    - Click "Deploy"
echo    - Vercel will build your frontend (1-2 minutes)
echo    - Wait for "Congratulations!" message
echo.
pause

echo 7. GET YOUR WEBSITE URL
echo    - Copy your Vercel URL (e.g., https://hiremebahamas.vercel.app)
echo    - Click "Visit" to see your live site!
echo.
set /p VERCEL_URL="Paste your Vercel frontend URL here: "

if not "%VERCEL_URL%"=="" (
    REM Save Vercel URL to file
    echo %VERCEL_URL% > VERCEL_URL.txt
    echo.
    echo Vercel URL saved!
)

echo.
echo ============================================
echo   Frontend Deployment Complete!
echo ============================================
echo.
echo Your website is now LIVE at:
echo %VERCEL_URL%
echo.

if not "%VERCEL_URL%"=="" (
    echo Opening your live site...
    timeout /t 2 >nul
    start %VERCEL_URL%
)

echo.
echo Next: Run STEP_4_TEST_DEPLOYMENT.bat
echo.
pause
