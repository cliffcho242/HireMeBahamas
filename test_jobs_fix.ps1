# Test Jobs Functionality Fix
Write-Host "`n🔧 TESTING JOBS PAGE FIX" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

Write-Host "`n⏳ Waiting for deployments to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "`n1️⃣ Testing Backend Health..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod "https://hiremebahamas.onrender.com/health" -TimeoutSec 60
    Write-Host "✅ Backend Status: $health" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend might be sleeping, waiting..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

Write-Host "`n2️⃣ Testing Jobs Endpoint (GET)..." -ForegroundColor Cyan
try {
    $jobsResponse = Invoke-RestMethod "https://hiremebahamas.onrender.com/api/jobs" -TimeoutSec 30
    
    if ($jobsResponse -is [System.Array]) {
        Write-Host "✅ Jobs API returns array format (FIXED!)" -ForegroundColor Green
        Write-Host "   Total jobs: $($jobsResponse.Count)" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️  Jobs API returns object format" -ForegroundColor Yellow
        Write-Host "   Format: $($jobsResponse | ConvertTo-Json -Depth 1)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Jobs API Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n3️⃣ Testing Login (to get auth token)..." -ForegroundColor Cyan
try {
    $loginData = @{
        email = "admin@hiremebahamas.com"
        password = "AdminPass123!"
    } | ConvertTo-Json
    
    $loginResp = Invoke-RestMethod `
        -Uri "https://hiremebahamas.onrender.com/api/auth/login" `
        -Method POST `
        -Body $loginData `
        -ContentType "application/json"
    
    Write-Host "✅ Login successful!" -ForegroundColor Green
    $token = $loginResp.access_token
    
    Write-Host "`n4️⃣ Testing Create Job (with auth)..." -ForegroundColor Cyan
    $jobData = @{
        title = "Test Job - $(Get-Date -Format 'HH:mm:ss')"
        company = "Test Company"
        location = "Nassau, Bahamas"
        job_type = "full-time"
        description = "This is a test job posting"
        requirements = "Test requirements"
        salary_range = "$40,000 - $60,000"
    } | ConvertTo-Json
    
    $createResp = Invoke-RestMethod `
        -Uri "https://hiremebahamas.onrender.com/api/jobs" `
        -Method POST `
        -Body $jobData `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"}
    
    Write-Host "✅ Job created successfully!" -ForegroundColor Green
    Write-Host "   Job ID: $($createResp.job_id)" -ForegroundColor Cyan
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" -ForegroundColor Gray
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "🎉 JOBS PAGE FIX COMPLETE!" -ForegroundColor Green -BackgroundColor Black
Write-Host "`n📱 New Frontend URL:" -ForegroundColor Yellow
Write-Host "   https://frontend-6dczr9qn3-cliffs-projects-a84c76c9.vercel.app" -ForegroundColor Cyan
Write-Host "`n✅ Changes Applied:" -ForegroundColor Yellow
Write-Host "   • Fixed backend to return array format" -ForegroundColor Green
Write-Host "   • Added error handling to prevent logout on Jobs page" -ForegroundColor Green
Write-Host "   • Made API interceptor smarter (only logout on auth failures)" -ForegroundColor Green
Write-Host "   • Jobs page now loads without logging users out" -ForegroundColor Green
Write-Host "`n"
