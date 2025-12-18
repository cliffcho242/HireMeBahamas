@echo off
REM ============================================
REM  Step 4: Test Production Deployment
REM  Automated Testing Script
REM ============================================

echo.
echo ============================================
echo   Step 4: Test Your Deployment
echo ============================================
echo.

REM Read URLs
if exist RAILWAY_URL.txt (
    set /p RAILWAY_URL=<RAILWAY_URL.txt
) else (
    echo WARNING: Render URL not found
    set /p RAILWAY_URL="Enter your Render backend URL: "
)

if exist VERCEL_URL.txt (
    set /p VERCEL_URL=<VERCEL_URL.txt
) else (
    echo WARNING: Vercel URL not found
    set /p VERCEL_URL="Enter your Vercel frontend URL: "
)

echo.
echo Testing your deployment...
echo.

echo ============================================
echo   YOUR LIVE URLS
echo ============================================
echo.
echo Backend API:  %RAILWAY_URL%
echo Frontend:     %VERCEL_URL%
echo Privacy:      %VERCEL_URL%/privacy-policy.html
echo Terms:        %VERCEL_URL%/terms-of-service.html
echo.

echo ============================================
echo   TEST 1: Backend Health Check
echo ============================================
echo.

powershell -Command "try { $response = Invoke-RestMethod -Uri '%RAILWAY_URL%/api/health' -TimeoutSec 10; Write-Host 'SUCCESS: Backend is healthy!' -ForegroundColor Green; Write-Host ('Status: ' + $response.status) -ForegroundColor Cyan } catch { Write-Host 'ERROR: Backend not responding!' -ForegroundColor Red; Write-Host $_.Exception.Message -ForegroundColor Yellow }"

echo.
pause

echo ============================================
echo   TEST 2: CORS Configuration
echo ============================================
echo.

powershell -Command "try { $response = Invoke-WebRequest -Uri '%RAILWAY_URL%/api/health' -Method OPTIONS -Headers @{'Origin'='%VERCEL_URL%'} -UseBasicParsing -TimeoutSec 10; $corsHeader = $response.Headers['Access-Control-Allow-Origin']; if ($corsHeader) { Write-Host 'SUCCESS: CORS is configured!' -ForegroundColor Green; Write-Host ('Allow-Origin: ' + $corsHeader) -ForegroundColor Cyan } else { Write-Host 'WARNING: CORS headers not found' -ForegroundColor Yellow } } catch { Write-Host 'ERROR: CORS test failed!' -ForegroundColor Red }"

echo.
pause

echo ============================================
echo   TEST 3: Admin Login
echo ============================================
echo.

powershell -Command "try { $body = @{email='admin@hiremebahamas.com'; password='AdminPass123!'} | ConvertTo-Json; $response = Invoke-RestMethod -Uri '%RAILWAY_URL%/api/auth/login' -Method POST -ContentType 'application/json' -Body $body -TimeoutSec 10; Write-Host 'SUCCESS: Admin login working!' -ForegroundColor Green; Write-Host ('User: ' + $response.user.email) -ForegroundColor Cyan; Write-Host ('Token: ' + $response.access_token.Substring(0,40) + '...') -ForegroundColor Cyan } catch { Write-Host 'ERROR: Login failed!' -ForegroundColor Red; Write-Host $_.Exception.Message -ForegroundColor Yellow }"

echo.
pause

echo ============================================
echo   TEST 4: Frontend Loading
echo ============================================
echo.

powershell -Command "try { $response = Invoke-WebRequest -Uri '%VERCEL_URL%' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'SUCCESS: Frontend is live!' -ForegroundColor Green; Write-Host 'Opening your site...' -ForegroundColor Cyan; Start-Process '%VERCEL_URL%' } else { Write-Host 'ERROR: Frontend not responding!' -ForegroundColor Red } } catch { Write-Host 'ERROR: Frontend test failed!' -ForegroundColor Red }"

echo.
pause

echo ============================================
echo   TEST 5: Privacy Policy & Terms
echo ============================================
echo.

echo Testing privacy policy...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%VERCEL_URL%/privacy-policy.html' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'SUCCESS: Privacy policy accessible!' -ForegroundColor Green } } catch { Write-Host 'WARNING: Privacy policy not found!' -ForegroundColor Yellow }"

echo.
echo Testing terms of service...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%VERCEL_URL%/terms-of-service.html' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { Write-Host 'SUCCESS: Terms of service accessible!' -ForegroundColor Green } } catch { Write-Host 'WARNING: Terms of service not found!' -ForegroundColor Yellow }"

echo.
pause

echo.
echo ============================================
echo   DEPLOYMENT TEST COMPLETE!
echo ============================================
echo.
echo All systems tested! Now you should:
echo.
echo 1. Visit your site: %VERCEL_URL%
echo 2. Create a test account
echo 3. Login with admin: admin@hiremebahamas.com / AdminPass123!
echo 4. Post a test job
echo 5. Search for jobs
echo 6. Test all features!
echo.
echo ============================================
echo   APP STORE READY URLS
echo ============================================
echo.
echo When submitting to app stores, use these:
echo.
echo Website URL:      %VERCEL_URL%
echo Privacy Policy:   %VERCEL_URL%/privacy-policy.html
echo Terms of Service: %VERCEL_URL%/terms-of-service.html
echo Support Email:    support@hiremebahamas.com
echo.
echo ============================================
echo   NEXT STEPS
echo ============================================
echo.
echo Week 1:    Share site with friends/family
echo Week 2-4:  Beta test with Bahamian users
echo Week 5-8:  Build React Native mobile apps
echo Week 9:    Submit to App Stores!
echo.
echo Run STEP_5_SHARE_WITH_USERS.bat for marketing tips
echo.
pause
