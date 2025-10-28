# Simple Railway Fix Script
Write-Host "Railway Backend Fix" -ForegroundColor Cyan

# Check Railway CLI
Write-Host "Checking Railway CLI..." -ForegroundColor Yellow
$railwayExists = Get-Command railway -ErrorAction SilentlyContinue

if ($railwayExists) {
    Write-Host "Railway CLI found" -ForegroundColor Green
    
    # Try to deploy
    Write-Host "Deploying to Railway..." -ForegroundColor Yellow
    railway up
    
    # Test endpoints
    Write-Host "Testing deployment..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    try {
        $response = Invoke-WebRequest -Uri "https://hiremebahamas-backend.railway.app/health"
        Write-Host "Health check: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "Health check failed" -ForegroundColor Red
    }
    
} else {
    Write-Host "Railway CLI not found" -ForegroundColor Red
    Write-Host "Install with: npm install -g @railway/cli" -ForegroundColor Yellow
    Write-Host "Or use Railway dashboard manually" -ForegroundColor Yellow
}

Write-Host "Manual option: https://railway.app/dashboard" -ForegroundColor Cyan