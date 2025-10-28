# Railway Deployment Fix Script
# This script helps redeploy the correct backend to Railway

Write-Host "🔧 Railway Backend Deployment Fix" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if Railway CLI is installed
Write-Host "`n🔍 Checking Railway CLI..." -ForegroundColor Yellow
try {
    railway --version | Out-Null
    Write-Host "✅ Railway CLI is installed" -ForegroundColor Green
    
    # Check if logged in
    Write-Host "`n🔐 Checking Railway login status..." -ForegroundColor Yellow
    $loginCheck = railway whoami 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Logged into Railway" -ForegroundColor Green
        
        # Deploy
        Write-Host "`n🚀 Deploying to Railway..." -ForegroundColor Yellow
        railway up
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Deployment successful!" -ForegroundColor Green
            Write-Host "🌐 Testing endpoints..." -ForegroundColor Yellow
            
            # Wait a moment for deployment
            Start-Sleep -Seconds 10
            
            # Test health endpoint
            try {
                $healthResponse = Invoke-WebRequest -Uri "https://hiremebahamas-backend.railway.app/health" -Method GET
                if ($healthResponse.StatusCode -eq 200) {
                    Write-Host "✅ Health endpoint working" -ForegroundColor Green
                } else {
                    Write-Host "❌ Health endpoint failed: $($healthResponse.StatusCode)" -ForegroundColor Red
                }
            } catch {
                Write-Host "❌ Health endpoint test failed: $_" -ForegroundColor Red
            }
            
            # Test auth endpoint
            try {
                $authResponse = Invoke-WebRequest -Uri "https://hiremebahamas-backend.railway.app/api/auth/login" -Method OPTIONS
                if ($authResponse.StatusCode -eq 200) {
                    Write-Host "✅ Auth endpoint working" -ForegroundColor Green
                    Write-Host "`n🎉 DEPLOYMENT SUCCESS!" -ForegroundColor Green
                    Write-Host "The 405 errors should now be resolved." -ForegroundColor Green
                } else {
                    Write-Host "⚠️ Auth endpoint returned: $($authResponse.StatusCode)" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "⚠️ Auth endpoint test: $_" -ForegroundColor Yellow
            }
            
        } else {
            Write-Host "`n❌ Deployment failed" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Not logged into Railway" -ForegroundColor Red
        Write-Host "Please run: railway login" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Railway CLI not found" -ForegroundColor Red
    Write-Host "Install with: npm install -g @railway/cli" -ForegroundColor Yellow
}

Write-Host "`n📋 Manual Alternative:" -ForegroundColor Cyan
Write-Host "1. Go to https://railway.app/dashboard" -ForegroundColor White
Write-Host "2. Find 'hiremebahamas-backend' project" -ForegroundColor White
Write-Host "3. Click Deployments tab" -ForegroundColor White
Write-Host "4. Click 'Deploy Latest Commit'" -ForegroundColor White

Write-Host "`n🔍 After deployment, test at:" -ForegroundColor Cyan
Write-Host "https://hiremebahamas.vercel.app (login should work)" -ForegroundColor White