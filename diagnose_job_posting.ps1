# Job Posting Diagnostic Script
# This will test the complete job posting flow

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Job Posting Diagnostic Test" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Backend Health
Write-Host "[1/5] Testing backend health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "https://hiremebahamas.onrender.com/health" -Method Get
    Write-Host "✓ Backend is healthy" -ForegroundColor Green
    Write-Host "  Status: $($health.status)" -ForegroundColor Gray
    Write-Host "  Database: $($health.database)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Login
Write-Host "`n[2/5] Testing login..." -ForegroundColor Yellow
try {
    $loginBody = @{
        email = "admin@hiremebahamas.com"
        password = "AdminPass123!"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "https://hiremebahamas.onrender.com/api/auth/login" `
        -Method Post `
        -Body $loginBody `
        -ContentType "application/json"
    
    $token = $loginResponse.access_token
    Write-Host "✓ Login successful" -ForegroundColor Green
    Write-Host "  Token: $($token.Substring(0,20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: Check existing jobs
Write-Host "`n[3/5] Checking existing jobs..." -ForegroundColor Yellow
try {
    $jobs = Invoke-RestMethod -Uri "https://hiremebahamas.onrender.com/api/jobs" `
        -Method Get `
        -Headers @{Authorization = "Bearer $token"}
    
    Write-Host "✓ Retrieved jobs list" -ForegroundColor Green
    Write-Host "  Total jobs: $($jobs.Count)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Failed to get jobs: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Create a test job (without salary range)
Write-Host "`n[4/5] Testing job creation (without salary)..." -ForegroundColor Yellow
try {
    $jobData = @{
        title = "Mobile Test Job"
        company = "Test Company"
        location = "Nassau, Bahamas"
        job_type = "full-time"
        description = "This is a test job posting from diagnostic script"
        requirements = "Test requirements"
        salary_range = ""
    } | ConvertTo-Json

    Write-Host "  Sending data:" -ForegroundColor Gray
    Write-Host "  $jobData" -ForegroundColor DarkGray

    $result = Invoke-RestMethod -Uri "https://hiremebahamas.onrender.com/api/jobs" `
        -Method Post `
        -Body $jobData `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"}
    
    Write-Host "✓ Job created successfully (no salary)" -ForegroundColor Green
    Write-Host "  Job ID: $($result.job_id)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "  Backend error: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
}

# Test 5: Create a test job (with salary range)
Write-Host "`n[5/5] Testing job creation (with salary)..." -ForegroundColor Yellow
try {
    $jobData = @{
        title = "Mobile Test Job With Salary"
        company = "Test Company Ltd"
        location = "Nassau, Bahamas"
        job_type = "part-time"
        description = "This is a test job posting with salary range"
        requirements = "Test requirements here"
        salary_range = "`$40,000 - `$60,000"
    } | ConvertTo-Json

    Write-Host "  Sending data:" -ForegroundColor Gray
    Write-Host "  $jobData" -ForegroundColor DarkGray

    $result = Invoke-RestMethod -Uri "https://hiremebahamas.onrender.com/api/jobs" `
        -Method Post `
        -Body $jobData `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"}
    
    Write-Host "✓ Job created successfully (with salary)" -ForegroundColor Green
    Write-Host "  Job ID: $($result.job_id)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "  Backend error: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Diagnostic Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nIf all tests passed, the backend is working correctly." -ForegroundColor White
Write-Host "The issue is likely in the frontend (browser console)." -ForegroundColor White
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Open https://frontend-8afubhzxw-cliffs-projects-a84c76c9.vercel.app" -ForegroundColor Gray
Write-Host "2. Press F12 to open browser console" -ForegroundColor Gray
Write-Host "3. Try posting a job and check console for errors" -ForegroundColor Gray
Write-Host "4. Look for CORS, network, or authentication errors" -ForegroundColor Gray
Write-Host ""
