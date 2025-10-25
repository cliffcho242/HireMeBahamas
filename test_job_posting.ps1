# Quick Job Posting Diagnostic and Test
Write-Host "`n=== HireMeBahamas Job Posting Test ===" -ForegroundColor Cyan
Write-Host "Testing backend API functionality...`n" -ForegroundColor White

$backendUrl = "https://hiremebahamas.onrender.com"
$passed = 0
$failed = 0

# Test 1: Health Check
Write-Host "[1/4] Backend Health..." -NoNewline
try {
    $health = Invoke-RestMethod -Uri "$backendUrl/health" -Method Get -TimeoutSec 30
    if ($health.status -eq "healthy") {
        Write-Host " PASSED" -ForegroundColor Green
        $passed++
    }
} catch {
    Write-Host " FAILED: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

# Test 2: Login
Write-Host "[2/4] Authentication..." -NoNewline
try {
    $loginBody = '{"email":"admin@hiremebahamas.com","password":"AdminPass123!"}'
    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json" -TimeoutSec 30
    $token = $loginResponse.access_token
    if ($token) {
        Write-Host " PASSED" -ForegroundColor Green
        $passed++
    }
} catch {
    Write-Host " FAILED: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
    exit 1
}

# Test 3: Get Jobs
Write-Host "[3/4] Get Jobs API..." -NoNewline
try {
    $jobs = Invoke-RestMethod -Uri "$backendUrl/api/jobs" -Method Get -Headers @{Authorization="Bearer $token"} -TimeoutSec 30
    Write-Host " PASSED ($($jobs.Count) jobs)" -ForegroundColor Green
    $passed++
} catch {
    Write-Host " FAILED: $($_.Exception.Message)" -ForegroundColor Red
    $failed++
}

# Test 4: Create Job
Write-Host "[4/4] Create Job API..." -NoNewline
try {
    $jobData = '{"title":"Test Job","company":"Test Co","location":"Nassau","job_type":"full-time","description":"Test","salary_range":"$50,000"}'
    $result = Invoke-RestMethod -Uri "$backendUrl/api/jobs" -Method Post -Body $jobData -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -TimeoutSec 30
    Write-Host " PASSED (Job ID: $($result.job_id))" -ForegroundColor Green
    $passed++
} catch {
    Write-Host " FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Error: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    $failed++
}

# Summary
Write-Host "`n=== Results ===" -ForegroundColor Cyan
Write-Host "Passed: $passed / 4" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "Failed: $failed / 4" -ForegroundColor Red
}

if ($passed -eq 4) {
    Write-Host "`nBACKEND IS WORKING PERFECTLY!" -ForegroundColor Green
    Write-Host "`nIf browser still shows error, check:" -ForegroundColor Yellow
    Write-Host "1. Press F12 in browser" -ForegroundColor Gray
    Write-Host "2. Check Console tab for errors" -ForegroundColor Gray
    Write-Host "3. Sign out and sign in again" -ForegroundColor Gray
    Write-Host "4. Try posting job with ALL required fields filled" -ForegroundColor Gray
} else {
    Write-Host "`nSome tests failed. Backend might still be starting up." -ForegroundColor Yellow
    Write-Host "Wait 30 seconds and run this script again." -ForegroundColor Gray
}

Write-Host "`nFrontend: https://frontend-p3e568zly-cliffs-projects-a84c76c9.vercel.app" -ForegroundColor Cyan
Write-Host ""
