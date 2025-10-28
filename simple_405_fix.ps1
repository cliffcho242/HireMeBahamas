# Simple 405 Error Fix
Write-Host "🚀 Fixing HireMeBahamas 405 Error" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Test backend
Write-Host "🔍 Testing backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "https://hiremebahamas.onrender.com/health"
    Write-Host "✅ Backend is healthy: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check current directory
if (-not (Test-Path "vercel.json")) {
    Write-Host "❌ Not in project root directory" -ForegroundColor Red
    exit 1
}

# Fix vercel.json
Write-Host "📝 Fixing vercel.json..." -ForegroundColor Yellow
$config = Get-Content "vercel.json" | ConvertFrom-Json
$config.env.VITE_API_URL = "https://hiremebahamas.onrender.com"
$config | ConvertTo-Json -Depth 10 | Set-Content "vercel.json"
Write-Host "✅ vercel.json updated" -ForegroundColor Green

# Fix frontend/.env if it exists
if (Test-Path "frontend/.env") {
    Write-Host "📁 Fixing frontend/.env..." -ForegroundColor Yellow
    $envLines = Get-Content "frontend/.env"
    $newLines = @()
    
    foreach ($line in $envLines) {
        if ($line -notlike "VITE_API_URL=*") {
            $newLines += $line
        }
    }
    $newLines += "VITE_API_URL=https://hiremebahamas.onrender.com"
    
    $newLines | Set-Content "frontend/.env"
    Write-Host "✅ frontend/.env updated" -ForegroundColor Green
}

# Rebuild frontend
Write-Host "🏗️ Rebuilding frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
npm run build
Set-Location ..

# Deploy
Write-Host "🚀 Deploying..." -ForegroundColor Yellow
git add .
git commit -m "Fix 405 error: Update API URL to Render"
git push origin main

Write-Host "🎉 Fix deployed! Check https://hiremebahamas.vercel.app in 2-3 minutes" -ForegroundColor Green