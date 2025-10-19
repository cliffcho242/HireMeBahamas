@echo off
REM ============================================
REM  ONE-CLICK COMPLETE DEPLOYMENT
REM  Fastest Method - Vercel Handles Everything
REM ============================================

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║        🚀 ONE-CLICK DEPLOYMENT - FASTEST METHOD! 🚀      ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo This is the FASTEST way to get HireMeBahamas live!
echo Vercel handles BOTH backend and frontend!
echo.
echo Time: 10 minutes
echo Cost: 100%% FREE
echo.
pause

echo.
echo ═══════════════════════════════════════════════════════════
echo   Step 1: Install Vercel CLI
echo ═══════════════════════════════════════════════════════════
echo.

echo Checking for Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo.
    echo Opening Node.js download...
    start https://nodejs.org
    echo.
    echo Please install Node.js and run this script again.
    pause
    exit
)

echo ✅ Node.js installed!
echo.

echo Installing Vercel CLI...
call npm install -g vercel

echo.
echo ✅ Vercel CLI installed!
echo.

echo ═══════════════════════════════════════════════════════════
echo   Step 2: Login to Vercel
echo ═══════════════════════════════════════════════════════════
echo.

vercel login

echo.
echo ═══════════════════════════════════════════════════════════
echo   Step 3: Deploy Backend
echo ═══════════════════════════════════════════════════════════
echo.

echo Deploying backend to Vercel...
echo.

REM Create vercel.json for backend
(
echo {
echo   "version": 2,
echo   "builds": [
echo     {
echo       "src": "final_backend.py",
echo       "use": "@vercel/python"
echo     }
echo   ],
echo   "routes": [
echo     {
echo       "src": "/(.*)",
echo       "dest": "final_backend.py"
echo     }
echo   ]
echo }
) > vercel_backend.json

vercel --prod --yes

echo.
echo ✅ Backend deployed!
echo.

echo Vercel will show your backend URL above.
set /p BACKEND_URL="Paste your backend URL: "
echo %BACKEND_URL% > BACKEND_URL.txt

echo.
echo ═══════════════════════════════════════════════════════════
echo   Step 4: Deploy Frontend
echo ═══════════════════════════════════════════════════════════
echo.

cd frontend

echo.
echo Updating frontend to use production backend...
(
echo VITE_API_URL=%BACKEND_URL%
echo VITE_SOCKET_URL=%BACKEND_URL%
) > .env.production

echo.
echo Deploying frontend to Vercel...
vercel --prod --yes

echo.
echo ✅ Frontend deployed!
echo.

cd ..

echo.
echo ═══════════════════════════════════════════════════════════
echo   DEPLOYMENT COMPLETE!
echo ═══════════════════════════════════════════════════════════
echo.
echo Your HireMeBahamas platform is LIVE!
echo.
echo Backend:  %BACKEND_URL%
echo Frontend: (Vercel showed the URL above)
echo.
echo Copy your frontend URL:
set /p FRONTEND_URL="Paste your frontend URL: "
echo %FRONTEND_URL% > FRONTEND_URL.txt

echo.
echo ═══════════════════════════════════════════════════════════
echo   YOUR LIVE PLATFORM
echo ═══════════════════════════════════════════════════════════
echo.
echo Website:          %FRONTEND_URL%
echo Backend API:      %BACKEND_URL%
echo Privacy Policy:   %FRONTEND_URL%/privacy-policy.html
echo Terms of Service: %FRONTEND_URL%/terms-of-service.html
echo.
echo Opening your live site...
start %FRONTEND_URL%

echo.
echo ═══════════════════════════════════════════════════════════
echo   🎉 CONGRATULATIONS! 🎉
echo ═══════════════════════════════════════════════════════════
echo.
echo HireMeBahamas is now live and ready for users!
echo.
echo Next steps:
echo 1. Test your site thoroughly
echo 2. Create a test account
echo 3. Login as admin: admin@hiremebahamas.com / AdminPass123!
echo 4. Share with friends and family
echo 5. Gather feedback
echo.
echo Run STEP_5_SHARE_WITH_USERS.bat for marketing materials!
echo.
pause
