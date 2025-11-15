@echo off
setlocal

set LOG_FILE=deploy_log.txt
echo Deployment started at %date% %time% > %LOG_FILE%

:: Step 1: Git Push
echo Pushing changes to the repository... >> %LOG_FILE%
git push >> %LOG_FILE% 2>&1
if %ERRORLEVEL% neq 0 (
    echo Git push failed. Check the log for details. >> %LOG_FILE%
    exit /b %ERRORLEVEL%
)
echo Git push completed successfully. >> %LOG_FILE%

:: Step 2: Install dependencies
echo Installing dependencies... >> %LOG_FILE%
npm install >> %LOG_FILE% 2>&1
if %ERRORLEVEL% neq 0 (
    echo Dependency installation failed. Check the log for details. >> %LOG_FILE%
    exit /b %ERRORLEVEL%
)
echo Dependencies installed successfully. >> %LOG_FILE%

:: Step 3: Setup the database
echo Setting up the database... >> %LOG_FILE%
:: Add your command to set up the database here (e.g., migrations)
:: Example: npm run migrate >> %LOG_FILE% 2>&1
if %ERRORLEVEL% neq 0 (
    echo Database setup failed. Check the log for details. >> %LOG_FILE%
    exit /b %ERRORLEVEL%
)
echo Database set up successfully. >> %LOG_FILE%

:: Step 4: Launch the application
echo Launching the application... >> %LOG_FILE%
npm start >> %LOG_FILE% 2>&1
if %ERRORLEVEL% neq 0 (
    echo Application launch failed. Check the log for details. >> %LOG_FILE%
    exit /b %ERRORLEVEL%
)
echo Application launched successfully. >> %LOG_FILE%

echo Deployment completed at %date% %time% >> %LOG_FILE%
endlocal
