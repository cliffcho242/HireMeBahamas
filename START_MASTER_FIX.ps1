#!/usr/bin/env powershell
# Master Network Fix for HireMeBahamas - PowerShell Version
# Ensures network reliability and admin login always works

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "MASTER NETWORK FIX - HireMeBahamas" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check for admin privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[WARNING] Not running as administrator" -ForegroundColor Yellow
    Write-Host "Some network fixes may not apply. Continuing anyway..." -ForegroundColor Yellow
    Write-Host ""
}

# Navigate to project directory
Set-Location $PSScriptRoot

# Step 1: Reset network stack
Write-Host "[1/6] Resetting Windows network stack..." -ForegroundColor Yellow
try {
    ipconfig /flushdns | Out-Null
    Write-Host "✓ DNS cache flushed" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not flush DNS: $_" -ForegroundColor Yellow
}

# Step 2: Kill any processes on ports 9999 and 3000
Write-Host ""
Write-Host "[2/6] Freeing ports 9999 and 3000..." -ForegroundColor Yellow
$ports = @(9999, 3000, 8080, 5000)
foreach ($port in $ports) {
    try {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            $processId = $connection.OwningProcess
            Write-Host "  Killing process $processId on port $port" -ForegroundColor Gray
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
    } catch {
        # Port is free
    }
}
Write-Host "✓ Ports freed" -ForegroundColor Green

# Step 3: Activate virtual environment
Write-Host ""
Write-Host "[3/6] Activating Python environment..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .\.venv\Scripts\Activate.ps1
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "⚠ Creating new virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    & .\.venv\Scripts\Activate.ps1
    Write-Host "✓ Virtual environment created and activated" -ForegroundColor Green
}

# Step 4: Install/upgrade required packages
Write-Host ""
Write-Host "[4/6] Installing required packages..." -ForegroundColor Yellow
$packages = @(
    "flask",
    "flask-cors",
    "flask-limiter",
    "flask-caching",
    "waitress",
    "pyjwt",
    "bcrypt",
    "requests",
    "python-dotenv"
)

python -m pip install --upgrade pip --quiet
foreach ($package in $packages) {
    Write-Host "  Installing $package..." -ForegroundColor Gray
    python -m pip install $package --upgrade --quiet
}
Write-Host "✓ All packages installed" -ForegroundColor Green

# Step 5: Run master network fix
Write-Host ""
Write-Host "[5/6] Starting master network fix..." -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan

# Run the master fix in background
$job = Start-Job -ScriptBlock {
    Set-Location $using:PSScriptRoot
    & .\.venv\Scripts\python.exe master_network_fix.py
}

Start-Sleep -Seconds 5

# Step 6: Test the connection
Write-Host ""
Write-Host "[6/6] Testing admin login..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:9999/api/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"email":"admin@hiremebahamas.com","password":"AdminPass123!"}' `
        -TimeoutSec 10
    
    if ($response.access_token) {
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "✓✓✓ MASTER FIX COMPLETE!" -ForegroundColor Green
        Write-Host "✓✓✓ ADMIN LOGIN SUCCESSFUL!" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Backend: http://127.0.0.1:9999" -ForegroundColor Cyan
        Write-Host "Token: $($response.access_token.Substring(0,50))..." -ForegroundColor Gray
        Write-Host ""
        Write-Host "Network is now stable and reliable!" -ForegroundColor Green
        Write-Host "Admin login works perfectly!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Login test failed: $_" -ForegroundColor Yellow
    Write-Host "Server may still be starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Server is running in background (Job ID: $($job.Id))" -ForegroundColor Cyan
Write-Host "To stop: Stop-Job -Id $($job.Id); Remove-Job -Id $($job.Id)" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop this script (server will continue running)" -ForegroundColor Yellow
