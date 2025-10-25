Write-Host "`n=== MONITORING BACKEND DEPLOYMENT ===" -ForegroundColor Cyan
Write-Host "Waiting for Render to finish deploying..." -ForegroundColor Yellow
Write-Host "This usually takes 2-3 minutes after git push`n" -ForegroundColor Gray

$maxAttempts = 15
$attempt = 0
$success = $false

while ($attempt -lt $maxAttempts -and -not $success) {
    $attempt++
    $elapsed = $attempt * 20
    Write-Host "[$elapsed seconds] Attempt $attempt/$maxAttempts..." -ForegroundColor Cyan
    
    try {
        # Test health first
        $health = Invoke-RestMethod "https://hiremebahamas.onrender.com/health" -TimeoutSec 30
        Write-Host "  Backend Status: $($health.status)" -ForegroundColor Green
        
        # Test login
        $loginData = @{
            email = "admin@hiremebahamas.com"
            password = "AdminPass123!"
        } | ConvertTo-Json
        
        $loginResponse = Invoke-RestMethod `
            -Uri "https://hiremebahamas.onrender.com/api/auth/login" `
            -Method POST `
            -Body $loginData `
            -ContentType "application/json" `
            -TimeoutSec 30
        
        Write-Host "`n=== SUCCESS! ===" -ForegroundColor Green -BackgroundColor Black
        Write-Host "Backend is READY and WORKING!" -ForegroundColor Green
        Write-Host "`nLogin Test Results:" -ForegroundColor Yellow
        Write-Host "  Token received: YES" -ForegroundColor Green
        Write-Host "  User: $($loginResponse.user.email)" -ForegroundColor Cyan
        Write-Host "`nFrontend URLs:" -ForegroundColor Yellow
        Write-Host "  Latest: https://frontend-wwuxd8hx9-cliffs-projects-a84c76c9.vercel.app" -ForegroundColor Cyan
        Write-Host "  Stable: https://frontend-6dczr9qn3-cliffs-projects-a84c76c9.vercel.app" -ForegroundColor Cyan
        Write-Host "`nBackend: https://hiremebahamas.onrender.com" -ForegroundColor Cyan
        Write-Host "`nYou can now sign in from the website!" -ForegroundColor Green -BackgroundColor Black
        $success = $true
    }
    catch {
        $errorMsg = $_.Exception.Message
        $statusCode = $_.Exception.Response.StatusCode.Value__
        
        if ($statusCode -eq 405) {
            Write-Host "  Status: 405 (Method Not Allowed) - Backend still deploying" -ForegroundColor Yellow
        }
        elseif ($errorMsg -like "*timeout*" -or $errorMsg -like "*unable to connect*") {
            Write-Host "  Status: Timeout - Backend restarting" -ForegroundColor Yellow
        }
        elseif ($statusCode -eq 500) {
            Write-Host "  Status: 500 (Server Error) - Backend starting up" -ForegroundColor Yellow
        }
        else {
            Write-Host "  Status: $statusCode - $errorMsg" -ForegroundColor Yellow
        }
        
        if ($attempt -lt $maxAttempts) {
            Write-Host "  Waiting 20 seconds...`n" -ForegroundColor Gray
            Start-Sleep -Seconds 20
        }
    }
}

if (-not $success) {
    Write-Host "`n=== TIMEOUT ===" -ForegroundColor Yellow
    Write-Host "Backend is taking longer than expected." -ForegroundColor Yellow
    Write-Host "`nCheck deployment status at:" -ForegroundColor Yellow
    Write-Host "https://dashboard.render.com/" -ForegroundColor Cyan
    Write-Host "`nOr wait a few more minutes and try again." -ForegroundColor Gray
}

Write-Host ""
