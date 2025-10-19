# HireBahamas Application Launcher
param([switch]$Force = $false)

$ErrorActionPreference = "Continue"
Write-Host "HireBahamas Application Launcher" -ForegroundColor Cyan

# Kill existing processes if -Force is specified
if ($Force) {
    Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
    Get-Process | Where-Object { $_.ProcessName -like "*node*" -or $_.ProcessName -like "*python*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

# Navigate to project directory
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "Project Directory: $projectRoot" -ForegroundColor Green

# Start Backend
Write-Host "`nStarting Backend Server..." -ForegroundColor Cyan
$backendScript = Join-Path $projectRoot "clean_backend.py"
$backendJob = Start-Process python -ArgumentList $backendScript -WindowStyle Normal -PassThru
Write-Host "Backend process started (PID: $($backendJob.Id))" -ForegroundColor Green

# Wait for backend
Write-Host "Waiting for backend..." -ForegroundColor Yellow
$backendReady = $false
for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8008/health" -Method GET -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "Backend is ready!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "." -NoNewline
    }
}

if (-not $backendReady) {
    Write-Host "`nBackend failed to start" -ForegroundColor Red
    exit 1
}

# Start Frontend
Write-Host "`nStarting Frontend Server..." -ForegroundColor Cyan
$frontendDir = Join-Path $projectRoot "frontend"
Set-Location $frontendDir

$frontendJob = Start-Process cmd -ArgumentList "/c npm run dev" -WindowStyle Normal -PassThru
Write-Host "Frontend process started (PID: $($frontendJob.Id))" -ForegroundColor Green

# Wait for frontend
Write-Host "Waiting for frontend..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "Frontend is ready!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "." -NoNewline
    }
}

# Status
Write-Host "`n`nAPPLICATION STATUS:" -ForegroundColor Cyan
Write-Host "Backend:  http://127.0.0.1:8008 (PID: $($backendJob.Id))" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000 (PID: $($frontendJob.Id))" -ForegroundColor Green

Write-Host "`nOpening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host "`nApplication is ready!" -ForegroundColor Green
Write-Host "Press Ctrl+C to exit`n" -ForegroundColor Gray

try {
    while ($true) { Start-Sleep -Seconds 10 }
} catch {
    Write-Host "Shutting down..." -ForegroundColor Yellow
}
