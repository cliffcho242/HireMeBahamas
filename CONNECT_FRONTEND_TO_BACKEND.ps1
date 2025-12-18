# 🔗 Connect Frontend to Backend

param(
    [string]$BackendURL
)

Write-Host "`n🔗 CONNECTING FRONTEND TO BACKEND`n" -ForegroundColor Cyan -BackgroundColor Black

Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Green

# Get backend URL if not provided
if (-not $BackendURL) {
    Write-Host "📝 Enter your Render backend URL:" -ForegroundColor Yellow
    Write-Host "   Example: https://hiremebahamas-production.up.render.app" -ForegroundColor Gray
    $BackendURL = Read-Host "   Backend URL"
}

# Validate URL
if ($BackendURL -notmatch '^https?://') {
    Write-Host "`n❌ Invalid URL. Must start with http:// or https://`n" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Backend URL: $BackendURL`n" -ForegroundColor Green

# Update Vercel environment variable
Write-Host "📋 Step 1: Update Vercel Environment Variable" -ForegroundColor Yellow
Write-Host "   Opening Vercel dashboard..." -ForegroundColor White
Start-Process "https://vercel.com/dashboard"
Start-Sleep -Seconds 2

Write-Host "`n   Please do the following in Vercel:" -ForegroundColor White
Write-Host "   1. Click on your 'hiremebahamas-backend' project" -ForegroundColor Cyan
Write-Host "   2. Go to Settings → Environment Variables" -ForegroundColor Cyan
Write-Host "   3. Add/Update variable:" -ForegroundColor Cyan
Write-Host "      Key: VITE_API_URL" -ForegroundColor Yellow
Write-Host "      Value: $BackendURL" -ForegroundColor Yellow
Write-Host "      Environment: Production ✓" -ForegroundColor Yellow
Write-Host "   4. Click 'Save'" -ForegroundColor Cyan

Write-Host "`n   Press Enter when done..." -NoNewline -ForegroundColor White
$null = Read-Host

# Redeploy frontend
Write-Host "`n📋 Step 2: Redeploy Frontend" -ForegroundColor Yellow
Write-Host "   Redeploying to apply new backend URL...`n" -ForegroundColor White

try {
    $deployOutput = vercel --prod --yes 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Frontend redeployed successfully!`n" -ForegroundColor Green
        
        # Extract URL from output
        $urlMatch = $deployOutput | Select-String -Pattern 'https://[^\s]+'
        if ($urlMatch) {
            $frontendURL = $urlMatch.Matches[0].Value
            Write-Host "   🌐 Frontend URL: $frontendURL`n" -ForegroundColor Cyan
        }
    } else {
        Write-Host "   ⚠️ Deployment may have failed. Check output above.`n" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error during deployment: $_`n" -ForegroundColor Red
}

# Test backend connection
Write-Host "`n📋 Step 3: Test Backend Connection" -ForegroundColor Yellow
Write-Host "   Testing backend health endpoint...`n" -ForegroundColor White

try {
    $healthURL = "$BackendURL/health"
    $response = Invoke-WebRequest -Uri $healthURL -Method GET -TimeoutSec 10
    
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is responding!" -ForegroundColor Green
        Write-Host "   Status: $($response.StatusCode)" -ForegroundColor White
        Write-Host "   Response: $($response.Content)`n" -ForegroundColor White
    }
} catch {
    Write-Host "   ⚠️ Backend health check failed" -ForegroundColor Yellow
    Write-Host "   This is normal if backend is still deploying" -ForegroundColor Gray
    Write-Host "   Wait a few minutes and visit: $BackendURL/health`n" -ForegroundColor Gray
}

# Test CORS
Write-Host "`n📋 Step 4: Test CORS (Cross-Origin)" -ForegroundColor Yellow
Write-Host "   Testing if frontend can connect to backend...`n" -ForegroundColor White

try {
    $headers = @{
        "Origin" = "https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app"
    }
    $response = Invoke-WebRequest -Uri "$BackendURL/health" -Method GET -Headers $headers -TimeoutSec 10
    
    if ($response.Headers["Access-Control-Allow-Origin"]) {
        Write-Host "   ✅ CORS is properly configured!" -ForegroundColor Green
        Write-Host "   Allowed Origin: $($response.Headers['Access-Control-Allow-Origin'])`n" -ForegroundColor White
    } else {
        Write-Host "   ⚠️ CORS headers not found" -ForegroundColor Yellow
        Write-Host "   You may need to configure CORS in backend`n" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️ CORS test skipped (backend may be deploying)`n" -ForegroundColor Gray
}

# Summary
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Green

Write-Host "🎉 CONNECTION SETUP COMPLETE!`n" -ForegroundColor Cyan -BackgroundColor Black

Write-Host "📊 Your Deployment URLs:`n" -ForegroundColor Yellow
Write-Host "   Frontend: https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app" -ForegroundColor Cyan
Write-Host "   Backend:  $BackendURL" -ForegroundColor Cyan
Write-Host "   Health:   $BackendURL/health`n" -ForegroundColor Cyan

Write-Host "🧪 Test Your Site:" -ForegroundColor Yellow
Write-Host "   1. Visit frontend URL" -ForegroundColor White
Write-Host "   2. Try logging in with:" -ForegroundColor White
Write-Host "      Email: admin@hiremebahamas.com" -ForegroundColor Cyan
Write-Host "      Password: AdminPass123!" -ForegroundColor Cyan
Write-Host "   3. Test job posting" -ForegroundColor White
Write-Host "   4. Test user registration`n" -ForegroundColor White

Write-Host "📱 Next Steps:" -ForegroundColor Yellow
Write-Host "   ✓ Test all features" -ForegroundColor White
Write-Host "   ✓ Share URLs with users" -ForegroundColor White
Write-Host "   ✓ Submit to app stores (use frontend URL)`n" -ForegroundColor White

Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Green

# Save URLs to file
$urlFile = "DEPLOYMENT_URLS.txt"
$urlContent = @"
HireMeBahamas Deployment URLs
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

Frontend (Vercel):
https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app

Backend (Render):
$BackendURL

Health Check:
$BackendURL/health

API Endpoints:
$BackendURL/api/auth/login
$BackendURL/api/auth/register
$BackendURL/api/jobs
$BackendURL/api/posts

Admin Login:
Email: admin@hiremebahamas.com
Password: AdminPass123!

Privacy Policy:
https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app/privacy-policy.html

Terms of Service:
https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app/terms-of-service.html
"@

$urlContent | Out-File -FilePath $urlFile -Encoding UTF8
Write-Host "💾 URLs saved to: $urlFile`n" -ForegroundColor Green

# Open browser to test
Write-Host "🌐 Opening frontend in browser..." -ForegroundColor Cyan
Start-Process "https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app"

Write-Host "`n═══════════════════════════════════════════════════════════════`n" -ForegroundColor Green

# Keep window open
$null = Read-Host "`nPress Enter to close this window"
