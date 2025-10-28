# HireMeBahamas 405 Error Fix and Redeploy
Write-Host "🚀 HireMeBahamas 405 Error Fix" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check if we're in the right directory
if (-not (Test-Path "vercel.json")) {
    Write-Host "❌ vercel.json not found. Please run this from the project root." -ForegroundColor Red
    exit 1
}

Write-Host "📍 Current directory: $(Get-Location)" -ForegroundColor Green

# Step 1: Test backend API
Write-Host "`n🔍 Step 1: Testing backend API..." -ForegroundColor Yellow
try {
    $healthTest = Invoke-RestMethod -Uri "https://hiremebahamas.onrender.com/health" -TimeoutSec 10
    Write-Host "✅ Backend health: $($healthTest.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "⚠️  Continuing anyway..." -ForegroundColor Yellow
}

# Step 2: Check vercel.json configuration
Write-Host "`n📝 Step 2: Checking vercel.json configuration..." -ForegroundColor Yellow
$vercelConfig = Get-Content "vercel.json" | ConvertFrom-Json
$currentApiUrl = $vercelConfig.env.VITE_API_URL

if ($currentApiUrl -eq "https://hiremebahamas.onrender.com") {
    Write-Host "✅ API URL is correct: $currentApiUrl" -ForegroundColor Green
} else {
    Write-Host "❌ API URL needs fixing: $currentApiUrl" -ForegroundColor Red
    Write-Host "🔧 Fixing API URL..." -ForegroundColor Yellow
    
    $vercelConfig.env.VITE_API_URL = "https://hiremebahamas.onrender.com"
    $vercelConfig | ConvertTo-Json -Depth 10 | Set-Content "vercel.json"
    
    Write-Host "✅ API URL fixed!" -ForegroundColor Green
}

# Step 3: Check frontend environment
Write-Host "`n📁 Step 3: Checking frontend environment..." -ForegroundColor Yellow
if (Test-Path "frontend/.env") {
    $envContent = Get-Content "frontend/.env"
    $apiUrlLine = $envContent | Where-Object { $_ -like "VITE_API_URL=*" }
    
    if ($apiUrlLine -eq "VITE_API_URL=https://hiremebahamas.onrender.com") {
        Write-Host "✅ Frontend .env is correct" -ForegroundColor Green
    } else {
        Write-Host "🔧 Fixing frontend .env..." -ForegroundColor Yellow
        
        # Remove old API URL line and add correct one
        $newEnvContent = $envContent | Where-Object { $_ -notlike "VITE_API_URL=*" }
        $newEnvContent += "VITE_API_URL=https://hiremebahamas.onrender.com"
        
        $newEnvContent | Set-Content "frontend/.env"
        Write-Host "✅ Frontend .env fixed!" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Frontend .env not found, creating..." -ForegroundColor Yellow
    @(
        "VITE_API_URL=https://hiremebahamas.onrender.com",
        "VITE_SOCKET_URL=https://hiremebahamas.onrender.com",
        "VITE_CLOUDINARY_CLOUD_NAME=your_cloudinary_name"
    ) | Set-Content "frontend/.env"
    Write-Host "✅ Frontend .env created!" -ForegroundColor Green
}

# Step 4: Rebuild and redeploy
Write-Host "`n🏗️  Step 4: Rebuilding frontend..." -ForegroundColor Yellow
Set-Location frontend

if (Test-Path "package.json") {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Cyan
    npm install
    
    Write-Host "🔨 Building frontend..." -ForegroundColor Cyan
    npm run build
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend build successful!" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend build failed!" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
} else {
    Write-Host "❌ package.json not found in frontend directory!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

# Step 5: Commit and deploy
Write-Host "`n🚀 Step 5: Deploying changes..." -ForegroundColor Yellow

Write-Host "📝 Adding changes to git..." -ForegroundColor Cyan
git add .

Write-Host "💾 Committing changes..." -ForegroundColor Cyan
git commit -m "Fix 405 error: Update API URLs and configuration"

if ($LASTEXITCODE -eq 0) {
    Write-Host "📤 Pushing to repository..." -ForegroundColor Cyan
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Changes pushed successfully!" -ForegroundColor Green
        Write-Host "`n🎉 Deployment initiated!" -ForegroundColor Green
        Write-Host "⏱️  Please wait 2-3 minutes for Vercel to deploy the changes." -ForegroundColor Yellow
        Write-Host "`n🌐 Test the website at: https://hiremebahamas.vercel.app" -ForegroundColor Cyan
        Write-Host "🔍 Use browser DevTools (F12 > Network tab) to check for 405 errors" -ForegroundColor Cyan
        Write-Host "🧪 Or open '405_error_test.html' in your browser for detailed testing" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Git push failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  No changes to commit" -ForegroundColor Yellow
    Write-Host "✅ Configuration is already correct!" -ForegroundColor Green
}

Write-Host "`n🎊 405 Error Fix Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
