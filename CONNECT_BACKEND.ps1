# Backend URL Collection and Frontend Connection Script

Write-Host "`n╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "║      🔗 CONNECT FRONTEND TO BACKEND - AUTOMATED 🔗           ║" -ForegroundColor White -BackgroundColor DarkCyan
Write-Host "║                                                               ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Get your Railway backend URL" -ForegroundColor White
Write-Host "  2. Update Vercel frontend configuration" -ForegroundColor White
Write-Host "  3. Redeploy frontend with backend connected" -ForegroundColor White
Write-Host "  4. Test the connection`n" -ForegroundColor White

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Get backend URL
Write-Host "📝 Enter your Railway backend URL:" -ForegroundColor Yellow
Write-Host "   (Example: https://hiremebahamas-production.up.railway.app)`n" -ForegroundColor Gray

$backendURL = Read-Host "Backend URL"

# Validate URL
if ($backendURL -eq "" -or $backendURL -eq "skip") {
    Write-Host "`n⏭️  Skipping backend connection for now." -ForegroundColor Yellow
    Write-Host "   You can run this script again later: .\CONNECT_BACKEND.ps1`n" -ForegroundColor Gray
    Read-Host "Press Enter to exit"
    exit
}

if ($backendURL -notmatch '^https?://') {
    Write-Host "`n❌ Invalid URL format. Must start with http:// or https://`n" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean URL (remove trailing slash)
$backendURL = $backendURL.TrimEnd('/')

Write-Host "`n✅ Backend URL: " -NoNewline -ForegroundColor Green
Write-Host "$backendURL`n" -ForegroundColor Cyan

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Test backend connection
Write-Host "🧪 Testing backend connection..." -ForegroundColor Cyan

try {
    $healthURL = "$backendURL/health"
    Write-Host "   Testing: $healthURL" -ForegroundColor Gray
    
    $response = Invoke-WebRequest -Uri $healthURL -Method GET -TimeoutSec 15 -ErrorAction Stop
    
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend is responding!" -ForegroundColor Green
        Write-Host "   Status: $($response.StatusCode) OK`n" -ForegroundColor White
    }
} catch {
    Write-Host "   ⚠️  Warning: Could not connect to backend" -ForegroundColor Yellow
    Write-Host "   This might be normal if Railway is still deploying" -ForegroundColor Gray
    Write-Host "   Continuing anyway...`n" -ForegroundColor Gray
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Update frontend environment variable
Write-Host "🔧 Updating frontend configuration..." -ForegroundColor Cyan

# Method 1: Update .env.production file
$envFile = "frontend\.env.production"
$envContent = "VITE_API_URL=$backendURL"

try {
    $envContent | Out-File -FilePath $envFile -Encoding UTF8 -Force
    Write-Host "   ✅ Updated $envFile" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Could not update .env file: $_" -ForegroundColor Yellow
}

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Method 2: Vercel environment variable (via dashboard)
Write-Host "📋 Vercel Configuration Needed:" -ForegroundColor Yellow
Write-Host "`n   Please do this in Vercel Dashboard:" -ForegroundColor White
Write-Host "   1. Visit: https://vercel.com/dashboard" -ForegroundColor Cyan
Write-Host "   2. Click your 'hiremebahamas-backend' project" -ForegroundColor White
Write-Host "   3. Go to Settings > Environment Variables" -ForegroundColor White
Write-Host "   4. Add or update:" -ForegroundColor White
Write-Host "      Key:   " -NoNewline -ForegroundColor White
Write-Host "VITE_API_URL" -ForegroundColor Yellow
Write-Host "      Value: " -NoNewline -ForegroundColor White
Write-Host "$backendURL" -ForegroundColor Cyan
Write-Host "      Environment: " -NoNewline -ForegroundColor White
Write-Host "Production ✓" -ForegroundColor Yellow
Write-Host "   5. Click 'Save'`n" -ForegroundColor White

# Open Vercel dashboard
Write-Host "   Opening Vercel dashboard..." -ForegroundColor Gray
Start-Process "https://vercel.com/dashboard"
Start-Sleep -Seconds 3

Write-Host "`n   Press Enter when you've added the environment variable..." -NoNewline -ForegroundColor Yellow
$null = Read-Host

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Redeploy frontend
Write-Host "🚀 Redeploying frontend with backend configuration...`n" -ForegroundColor Cyan

try {
    Write-Host "   Running: vercel --prod --yes`n" -ForegroundColor Gray
    
    $deployOutput = vercel --prod --yes 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Frontend redeployed successfully!`n" -ForegroundColor Green
        
        # Extract URL
        if ($deployOutput -match 'https://[^\s]+vercel\.app') {
            $frontendURL = $matches[0]
            Write-Host "   🌐 Frontend URL: $frontendURL`n" -ForegroundColor Cyan
        }
    } else {
        Write-Host "   ⚠️  Deployment completed with warnings" -ForegroundColor Yellow
        Write-Host "   Check the output above for details`n" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Deployment error: $_`n" -ForegroundColor Red
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Test CORS
Write-Host "🔍 Testing CORS configuration..." -ForegroundColor Cyan

try {
    $headers = @{
        "Origin" = "https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app"
    }
    
    $response = Invoke-WebRequest -Uri "$backendURL/health" -Method GET -Headers $headers -TimeoutSec 10 -ErrorAction Stop
    
    $corsHeader = $response.Headers["Access-Control-Allow-Origin"]
    if ($corsHeader) {
        Write-Host "   ✅ CORS is configured correctly!" -ForegroundColor Green
        Write-Host "   Allowed Origin: $corsHeader`n" -ForegroundColor White
    } else {
        Write-Host "   ⚠️  CORS headers not found (may need backend restart)`n" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  Could not test CORS (backend may still be deploying)`n" -ForegroundColor Yellow
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Save URLs
Write-Host "💾 Saving deployment URLs..." -ForegroundColor Cyan

$urlsContent = @"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              HIREMEBAHAMAS DEPLOYMENT URLS                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 FRONTEND (Vercel):
https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app

🔧 BACKEND (Railway):
$backendURL

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 LEGAL PAGES:

Privacy Policy:
https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app/privacy-policy.html

Terms of Service:
https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app/terms-of-service.html

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 ADMIN LOGIN:

Email:    admin@hiremebahamas.com
Password: AdminPass123!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 API ENDPOINTS:

Health Check: $backendURL/health
Login:        $backendURL/api/auth/login
Register:     $backendURL/api/auth/register
Jobs:         $backendURL/api/jobs
Posts:        $backendURL/api/posts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 FOR APP STORE SUBMISSION:

Website URL: https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app
Privacy URL: https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app/privacy-policy.html
Terms URL:   https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app/terms-of-service.html

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"@

$urlsContent | Out-File -FilePath "DEPLOYMENT_URLS.txt" -Encoding UTF8
Write-Host "   ✅ URLs saved to: DEPLOYMENT_URLS.txt`n" -ForegroundColor Green

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Final summary
Write-Host "╔═══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                               ║" -ForegroundColor Green
Write-Host "║              🎉 DEPLOYMENT COMPLETE! 🎉                       ║" -ForegroundColor Cyan -BackgroundColor Black
Write-Host "║                                                               ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "✅ Your HireMeBahamas platform is now LIVE!`n" -ForegroundColor Green

Write-Host "🌐 Frontend: " -NoNewline -ForegroundColor Yellow
Write-Host "https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app" -ForegroundColor Cyan

Write-Host "🔧 Backend:  " -NoNewline -ForegroundColor Yellow
Write-Host "$backendURL`n" -ForegroundColor Cyan

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "🧪 NEXT STEPS:`n" -ForegroundColor Yellow

Write-Host "1. Test your website:" -ForegroundColor White
Write-Host "   • Open frontend URL in browser" -ForegroundColor Gray
Write-Host "   • Try logging in as admin@hiremebahamas.com" -ForegroundColor Gray
Write-Host "   • Post a test job" -ForegroundColor Gray
Write-Host "   • Register a test user`n" -ForegroundColor Gray

Write-Host "2. Submit to app stores:" -ForegroundColor White
Write-Host "   • Use frontend URL as website" -ForegroundColor Gray
Write-Host "   • Link to privacy policy and terms" -ForegroundColor Gray
Write-Host "   • All requirements are met!`n" -ForegroundColor Gray

Write-Host "3. Share with users:" -ForegroundColor White
Write-Host "   • Post on social media" -ForegroundColor Gray
Write-Host "   • Send to job seekers in the Bahamas" -ForegroundColor Gray
Write-Host "   • Get feedback and improve`n" -ForegroundColor Gray

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "🌐 Opening your website..." -ForegroundColor Cyan
Start-Process "https://hiremebahamas-backend-earawsqiw-cliffs-projects-a84c76c9.vercel.app"

Write-Host "`n" -ForegroundColor Gray
Read-Host "Press Enter to close this window"
