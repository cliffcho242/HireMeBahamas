# HireBahamas - Automated Facebook-Style Setup
# This script will automatically configure and launch the platform

param(
    [switch]$FullSetup = $false,
    [switch]$QuickStart = $false
)

$ErrorActionPreference = "Continue"

# Color functions
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }

# Banner
Clear-Host
Write-Host @"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║          🌴 HIREBAHAMAS SETUP 🌴                     ║
║     Facebook-Style Professional Social Platform      ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

Start-Sleep -Seconds 1

# Navigate to project root
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot
Write-Info "Project Directory: $projectRoot"

# Step 1: Clean up old processes
Write-Host "`n[1/7] Cleaning up old processes..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -like "*node*" -or $_.ProcessName -like "*python*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Success "Cleaned up existing processes"

# Step 2: Check dependencies
Write-Host "`n[2/7] Checking dependencies..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Python installed: $pythonVersion"
} catch {
    Write-Error "Python not found! Please install Python 3.8+"
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version 2>&1
    Write-Success "Node.js installed: $nodeVersion"
} catch {
    Write-Error "Node.js not found! Please install Node.js 18+"
    exit 1
}

# Step 3: Setup database
Write-Host "`n[3/7] Setting up database..." -ForegroundColor Yellow
if ($FullSetup) {
    Write-Info "Running database seed script..."
    python seed_data.py
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Database seeded with sample data"
    } else {
        Write-Warning "Database seed had warnings (this is usually okay)"
    }
} else {
    Write-Info "Skipping database seed (use -FullSetup to seed data)"
}

# Step 4: Install frontend dependencies
Write-Host "`n[4/7] Checking frontend dependencies..." -ForegroundColor Yellow
$frontendDir = Join-Path $projectRoot "frontend"
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Info "Installing frontend dependencies..."
    Set-Location $frontendDir
    npm install --silent
    Set-Location $projectRoot
    Write-Success "Frontend dependencies installed"
} else {
    Write-Success "Frontend dependencies already installed"
}

# Step 5: Start Backend
Write-Host "`n[5/7] Starting Backend Server..." -ForegroundColor Yellow
$backendScript = Join-Path $projectRoot "clean_backend.py"
$backendJob = Start-Process python -ArgumentList $backendScript -WindowStyle Normal -PassThru
Write-Success "Backend server starting (PID: $($backendJob.Id))"

# Wait for backend
Write-Info "Waiting for backend to be ready..."
$backendReady = $false
for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8008/health" -Method GET -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Success "Backend is ready on http://127.0.0.1:8008"
            break
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

if (-not $backendReady) {
    Write-Error "Backend failed to start properly"
    exit 1
}

# Step 6: Start Frontend
Write-Host "`n`n[6/7] Starting Frontend Server..." -ForegroundColor Yellow
Set-Location $frontendDir
$frontendJob = Start-Process npm -ArgumentList "run", "dev" -WindowStyle Normal -PassThru
Set-Location $projectRoot
Write-Success "Frontend server starting (PID: $($frontendJob.Id))"

# Wait for frontend
Write-Info "Waiting for frontend to be ready..."
$frontendReady = $false
for ($i = 1; $i -le 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $frontendReady = $true
            Write-Success "Frontend is ready on http://localhost:3000"
            break
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
    }
}

if (-not $frontendReady) {
    Write-Error "Frontend failed to start properly"
    exit 1
}

# Step 7: Launch Browser
Write-Host "`n`n[7/7] Opening HireBahamas in browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"
Write-Success "Browser opened!"

# Summary
Write-Host @"

╔═══════════════════════════════════════════════════════╗
║                                                       ║
║           🎉 HIREBAHAMAS IS READY! 🎉                ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

📱 FRONTEND: http://localhost:3000
🔧 BACKEND:  http://127.0.0.1:8008
📊 STATUS:   http://localhost:3000/status.html

🔐 DEFAULT LOGIN:
   Email:    admin@hirebahamas.com
   Password: admin123

🌟 FEATURES:
   ✓ Facebook-style login page
   ✓ Stories and posts
   ✓ Real-time messaging
   ✓ Notifications system
   ✓ Friend connections
   ✓ Job postings
   ✓ Professional networking

📋 RUNNING PROCESSES:
   Backend:  PID $($backendJob.Id)
   Frontend: PID $($frontendJob.Id)

💡 TIP: Press Ctrl+C in the terminal windows to stop servers

"@ -ForegroundColor Cyan

Write-Host "Happy networking! 🚀" -ForegroundColor Green
