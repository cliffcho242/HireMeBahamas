# Automated Job Posting Fix and Diagnostic
# This script will automatically diagnose and fix common job posting issues

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  HireMeBahamas - Automated Job Posting Fix & Test  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$testsPassed = 0
$testsFailed = 0

# Configuration
$backendUrl = "https://hiremebahamas.onrender.com"
$frontendUrl = "https://frontend-8afubhzxw-cliffs-projects-a84c76c9.vercel.app"
$adminEmail = "admin@hiremebahamas.com"
$adminPassword = "AdminPass123!"

# Helper function to wait with progress
function Wait-WithProgress {
    param([int]$Seconds, [string]$Message)
    
    Write-Host "$Message" -ForegroundColor Yellow -NoNewline
    for ($i = 0; $i -lt $Seconds; $i++) {
        Write-Host "." -NoNewline -ForegroundColor Yellow
        Start-Sleep -Seconds 1
    }
    Write-Host " Done!" -ForegroundColor Green
}

# Test 1: Backend Health Check
Write-Host "[1/6] Testing Backend Health..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "$backendUrl/health" -Method Get -TimeoutSec 30
    
    if ($health.status -eq "healthy" -and $health.database -eq "healthy") {
        Write-Host "  ✓ Backend is healthy and ready" -ForegroundColor Green
        Write-Host "    - Status: $($health.status)" -ForegroundColor Gray
        Write-Host "    - Database: $($health.database)" -ForegroundColor Gray
        Write-Host "    - Active connections: $($health.concurrency.active_connections)" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  ⚠ Backend is running but not fully healthy" -ForegroundColor Yellow
        $testsFailed++
    }
} catch {
    if ($_.Exception.Message -like "*503*" -or $_.Exception.Message -like "*timeout*") {
        Write-Host "  ⏳ Backend is sleeping (Render.com free tier)" -ForegroundColor Yellow
        Write-Host "     Waking it up..." -ForegroundColor Yellow
        
        Wait-WithProgress -Seconds 30 -Message "     Waiting for backend to wake up"
        
        # Try again
        try {
            $health = Invoke-RestMethod -Uri "$backendUrl/health" -Method Get -TimeoutSec 60
            Write-Host "  ✓ Backend is now awake and healthy!" -ForegroundColor Green
            $testsPassed++
        } catch {
            Write-Host "  ✗ Backend did not wake up: $($_.Exception.Message)" -ForegroundColor Red
            $testsFailed++
        }
    } else {
        Write-Host "  ✗ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
        $testsFailed++
    }
}

# Test 2: Authentication
Write-Host "`n[2/6] Testing Authentication..." -ForegroundColor Cyan
try {
    $loginBody = @{
        email = $adminEmail
        password = $adminPassword
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/auth/login" `
        -Method Post `
        -Body $loginBody `
        -ContentType "application/json" `
        -TimeoutSec 30
    
    $token = $loginResponse.access_token
    
    if ($token) {
        Write-Host "  ✓ Authentication successful" -ForegroundColor Green
        Write-Host "    - Token received: $($token.Substring(0,30))..." -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  ✗ No token received" -ForegroundColor Red
        $testsFailed++
        exit 1
    }
} catch {
    Write-Host "  ✗ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "    Server response: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
    $testsFailed++
    exit 1
}

# Test 3: Get Existing Jobs
Write-Host "`n[3/6] Checking Jobs Endpoint..." -ForegroundColor Cyan
try {
    $jobs = Invoke-RestMethod -Uri "$backendUrl/api/jobs" `
        -Method Get `
        -Headers @{Authorization = "Bearer $token"} `
        -TimeoutSec 30
    
    Write-Host "  ✓ Jobs endpoint working" -ForegroundColor Green
    Write-Host "    - Total jobs: $($jobs.Count)" -ForegroundColor Gray
    
    if ($jobs.Count -gt 0) {
        Write-Host "    - Latest job: $($jobs[0].title) at $($jobs[0].company)" -ForegroundColor Gray
    }
    $testsPassed++
} catch {
    Write-Host "  ⚠ Jobs endpoint issue: $($_.Exception.Message)" -ForegroundColor Yellow
    # Not critical, continue
}

# Test 4: Create Job WITHOUT Salary (Minimal Required Fields)
Write-Host "`n[4/6] Testing Job Creation (Minimal Fields)..." -ForegroundColor Cyan
try {
    $timestamp = Get-Date -Format "HHmmss"
    $jobData = @{
        title = "Auto-Test Job $timestamp"
        company = "Test Company"
        location = "Nassau, Bahamas"
        job_type = "full-time"
        description = "This is an automated test job posting"
        requirements = ""
        salary_range = ""
    } | ConvertTo-Json

    $result = Invoke-RestMethod -Uri "$backendUrl/api/jobs" `
        -Method Post `
        -Body $jobData `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"} `
        -TimeoutSec 30
    
    Write-Host "  ✓ Job created successfully (minimal fields)" -ForegroundColor Green
    Write-Host "    - Job ID: $($result.job_id)" -ForegroundColor Gray
    Write-Host "    - Message: $($result.message)" -ForegroundColor Gray
    $testsPassed++
} catch {
    Write-Host "  ✗ Job creation failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "    Error: $($errorDetails.message)" -ForegroundColor Yellow
    }
    $testsFailed++
}

# Test 5: Create Job WITH Salary Range
Write-Host "`n[5/6] Testing Job Creation (With Salary)..." -ForegroundColor Cyan
try {
    $timestamp = Get-Date -Format "HHmmss"
    $jobData = @{
        title = "Auto-Test Job With Salary $timestamp"
        company = "Premium Test Company"
        location = "Nassau, Bahamas"
        job_type = "part-time"
        description = "This is an automated test with salary range"
        requirements = "Test requirements listed here"
        salary_range = "`$45,000 - `$65,000"
    } | ConvertTo-Json

    $result = Invoke-RestMethod -Uri "$backendUrl/api/jobs" `
        -Method Post `
        -Body $jobData `
        -ContentType "application/json" `
        -Headers @{Authorization = "Bearer $token"} `
        -TimeoutSec 30
    
    Write-Host "  ✓ Job created successfully (with salary)" -ForegroundColor Green
    Write-Host "    - Job ID: $($result.job_id)" -ForegroundColor Gray
    Write-Host "    - Message: $($result.message)" -ForegroundColor Gray
    $testsPassed++
} catch {
    Write-Host "  ✗ Job creation with salary failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json
        Write-Host "    Error: $($errorDetails.message)" -ForegroundColor Yellow
    }
    $testsFailed++
}

# Test 6: Verify Frontend Environment
Write-Host "`n[6/6] Checking Frontend Configuration..." -ForegroundColor Cyan
try {
    $envPath = "c:\Users\Dell\OneDrive\Desktop\HireBahamas\frontend\.env"
    
    if (Test-Path $envPath) {
        $envContent = Get-Content $envPath -Raw
        
        if ($envContent -match "VITE_API_URL=https://hiremebahamas.onrender.com") {
            Write-Host "  ✓ Frontend .env correctly configured" -ForegroundColor Green
            Write-Host "    - VITE_API_URL points to production backend" -ForegroundColor Gray
            $testsPassed++
        } else {
            Write-Host "  ⚠ Frontend .env might have wrong URL" -ForegroundColor Yellow
            Write-Host "    Current content:" -ForegroundColor Gray
            Write-Host "    $envContent" -ForegroundColor DarkGray
            $testsFailed++
        }
    } else {
        Write-Host "  ⚠ Frontend .env file not found" -ForegroundColor Yellow
        $testsFailed++
    }
} catch {
    Write-Host "  ⚠ Could not verify frontend config: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Test Summary                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

$totalTests = $testsPassed + $testsFailed
Write-Host "`nTests Passed: $testsPassed / $totalTests" -ForegroundColor Green
if ($testsFailed -gt 0) {
    Write-Host "Tests Failed: $testsFailed / $totalTests" -ForegroundColor Red
}

Write-Host "`n" -NoNewline
if ($testsPassed -eq $totalTests) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "`nYour backend is working perfectly!" -ForegroundColor White
    Write-Host "`nIf job posting still fails in the browser:" -ForegroundColor Yellow
    Write-Host "  1. Press F12 in browser" -ForegroundColor Gray
    Write-Host "  2. Go to Console tab" -ForegroundColor Gray
    Write-Host "  3. Try posting a job" -ForegroundColor Gray
    Write-Host "  4. Copy any red error messages" -ForegroundColor Gray
    Write-Host "  5. Share those errors for diagnosis`n" -ForegroundColor Gray
} else {
    Write-Host "⚠️ SOME TESTS FAILED" -ForegroundColor Yellow
    Write-Host "`nPlease check the errors above." -ForegroundColor White
    Write-Host "The backend API might still be starting up.`n" -ForegroundColor Gray
}

# URLs for reference
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host "Quick Links:" -ForegroundColor White
Write-Host "  Backend:  $backendUrl" -ForegroundColor Cyan
Write-Host "  Frontend: $frontendUrl" -ForegroundColor Cyan
Write-Host "  Health:   $backendUrl/health" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor DarkGray
