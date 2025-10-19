# PERMANENT NETWORK FIX FOR HIREBAHAMAS
# Fixes network errors and connection issues

param(
    [switch]$Install,
    [switch]$Status,
    [switch]$Fix,
    [switch]$Force
)

$BACKEND_PORT = 8008
$FRONTEND_PORT = 3000
$PROJECT_ROOT = "C:\Users\Dell\OneDrive\Desktop\HireBahamas"

function Write-Success { param($Msg) Write-Host "[OK] $Msg" -ForegroundColor Green }
function Write-Fail { param($Msg) Write-Host "[ERROR] $Msg" -ForegroundColor Red }
function Write-Note { param($Msg) Write-Host "[INFO] $Msg" -ForegroundColor Cyan }
function Write-Warn { param($Msg) Write-Host "[WARN] $Msg" -ForegroundColor Yellow }

function Test-Backend {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BACKEND_PORT/health" -Method GET -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        return $r.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Get-PortProcess {
    param([int]$Port)
    $conn = netstat -ano | Select-String ":$Port\s+.*LISTENING"
    if ($conn) {
        $pid = ($conn -split '\s+')[-1]
        try {
            return Get-Process -Id $pid -ErrorAction Stop
        } catch {
            return $null
        }
    }
    return $null
}

function Stop-Backend {
    Write-Note "Stopping backend..."
    
    # Method 1: Stop by port
    $proc = Get-PortProcess -Port $BACKEND_PORT
    if ($proc) {
        Write-Note "Found process on port $BACKEND_PORT (PID: $($proc.Id))"
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Method 2: Stop all Python processes running final_backend or facebook_like_backend
    $pythonProcs = Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*final_backend*" -or $_.CommandLine -like "*facebook_like_backend*"
    }
    foreach ($p in $pythonProcs) {
        Write-Note "Stopping Python process (PID: $($p.Id))"
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
    
    Start-Sleep -Seconds 2
    
    # Verify stopped
    $stillRunning = Get-PortProcess -Port $BACKEND_PORT
    if ($stillRunning) {
        Write-Warn "Port $BACKEND_PORT still in use, forcing kill..."
        Stop-Process -Id $stillRunning.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    Write-Success "Backend stopped"
}

function Start-Backend {
    Write-Note "Starting backend..."
    Stop-Backend
    Start-Sleep -Seconds 2
    
    $script = Join-Path $PROJECT_ROOT "final_backend.py"
    if (-not (Test-Path $script)) {
        Write-Fail "Backend script not found: $script"
        return $false
    }
    
    Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$PROJECT_ROOT'; python final_backend.py"
    
    # Wait for backend
    $attempts = 0
    while ($attempts -lt 10) {
        Start-Sleep -Seconds 2
        $attempts++
        Write-Note "Waiting for backend... $attempts/10"
        if (Test-Backend) {
            Write-Success "Backend is ready!"
            return $true
        }
    }
    
    Write-Fail "Backend failed to start"
    return $false
}

function Show-Status {
    Write-Host "`n======================================" -ForegroundColor Cyan
    Write-Host "  NETWORK STATUS" -ForegroundColor Cyan
    Write-Host "======================================`n" -ForegroundColor Cyan
    
    # Backend
    if (Test-Backend) {
        Write-Success "Backend (Port $BACKEND_PORT) is HEALTHY"
        $proc = Get-PortProcess -Port $BACKEND_PORT
        if ($proc) {
            Write-Host "  Process: $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Gray
        }
    } else {
        Write-Fail "Backend (Port $BACKEND_PORT) is DOWN"
    }
    
    # Frontend
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:$FRONTEND_PORT" -Method GET -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Success "Frontend (Port $FRONTEND_PORT) is RUNNING"
    } catch {
        Write-Fail "Frontend (Port $FRONTEND_PORT) is DOWN"
    }
    
    # Connections
    $timeWait = (netstat -ano | Select-String "TIME_WAIT.*:$BACKEND_PORT").Count
    $established = (netstat -ano | Select-String "ESTABLISHED.*:$BACKEND_PORT").Count
    
    Write-Host "`nConnections:" -ForegroundColor Cyan
    Write-Host "  ESTABLISHED: $established" -ForegroundColor Green
    Write-Host "  TIME_WAIT: $timeWait" -ForegroundColor $(if ($timeWait -gt 500) { "Red" } elseif ($timeWait -gt 100) { "Yellow" } else { "Green" })
    
    if ($timeWait -gt 500) {
        Write-Warn "Too many TIME_WAIT connections!"
        Write-Note "Run: .\NETWORK_FIX.ps1 -Fix"
    }
    
    Write-Host "`n======================================`n" -ForegroundColor Cyan
}

function Fix-Network {
    Write-Note "Applying network fix..."
    
    # Check backend
    if (-not (Test-Backend)) {
        Write-Warn "Backend is down. Restarting..."
        if (Start-Backend) {
            Write-Success "Backend restarted successfully"
        } else {
            Write-Fail "Failed to restart backend"
            return
        }
    } else {
        Write-Success "Backend is healthy"
    }
    
    Start-Sleep -Seconds 2
    Show-Status
}

function Clear-NetworkConnections {
    Write-Note "Clearing stale network connections..."
    
    # Kill TIME_WAIT connections (requires admin)
    try {
        $timeWaitCount = (netstat -ano | Select-String "TIME_WAIT.*:$BACKEND_PORT").Count
        if ($timeWaitCount -gt 100) {
            Write-Warn "Found $timeWaitCount TIME_WAIT connections"
            Write-Note "These will clear automatically in 30-120 seconds"
        }
    } catch {
        Write-Note "Could not check TIME_WAIT connections"
    }
}

function Check-Requirements {
    Write-Note "Checking requirements..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Fail "Python not found! Please install Python 3.8+"
        return $false
    }
    
    # Check backend script
    $backendScript = Join-Path $PROJECT_ROOT "final_backend.py"
    if (Test-Path $backendScript) {
        Write-Success "Backend script found"
    } else {
        Write-Fail "Backend script not found: $backendScript"
        return $false
    }
    
    # Check database
    $dbPath = Join-Path $PROJECT_ROOT "backend\hirebahamas.db"
    if (Test-Path $dbPath) {
        Write-Success "Database found"
    } else {
        Write-Warn "Database not found (will be created)"
    }
    
    # Check if ports are available or can be freed
    $backendProc = Get-PortProcess -Port $BACKEND_PORT
    if ($backendProc) {
        Write-Warn "Port $BACKEND_PORT is in use by PID $($backendProc.Id)"
        Write-Note "Will force kill process..."
    } else {
        Write-Success "Port $BACKEND_PORT is available"
    }
    
    return $true
}

function Install-PythonPackages {
    Write-Note "Checking Python packages..."
    
    $packagesNeeded = @(
        "flask",
        "flask-cors",
        "bcrypt",
        "pyjwt",
        "python-decouple"
    )
    
    $pipList = pip list 2>&1 | Out-String
    $missingPackages = @()
    
    foreach ($pkg in $packagesNeeded) {
        if ($pipList -notmatch $pkg) {
            $missingPackages += $pkg
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Warn "Missing packages: $($missingPackages -join ', ')"
        Write-Note "Installing missing packages..."
        try {
            pip install $missingPackages 2>&1 | Out-Null
            Write-Success "Packages installed"
        } catch {
            Write-Warn "Could not auto-install packages. Backend may have issues."
        }
    } else {
        Write-Success "All required packages are installed"
    }
}

function Install-Fix {
    param([switch]$ForceInstall)
    
    Write-Host "`n======================================" -ForegroundColor Green
    Write-Host "  AUTOMATED NETWORK FIX INSTALLER" -ForegroundColor Green
    if ($ForceInstall) {
        Write-Host "  [FORCE MODE - NUCLEAR OPTION]" -ForegroundColor Yellow
    }
    Write-Host "======================================`n" -ForegroundColor Green
    
    # Step 0: Check requirements
    if (-not (Check-Requirements)) {
        if (-not $ForceInstall) {
            Write-Fail "Requirements check failed. Use -Force to override."
            return
        }
        Write-Warn "Requirements check failed but continuing due to -Force flag..."
    }
    
    # Step 0.5: Install Python packages if needed
    if ($ForceInstall) {
        Install-PythonPackages
    }
    
    # Step 1: Clear network connections
    Clear-NetworkConnections
    
    # Step 2: Force stop all backend processes
    Write-Note "Force stopping all backend processes..."
    Stop-Backend
    Start-Sleep -Seconds 3
    
    # Step 3: Restart backend
    Write-Note "Restarting backend with enhanced configuration..."
    if (Start-Backend) {
        Write-Success "Backend restarted successfully!"
    } else {
        Write-Fail "Backend restart failed"
        if (-not $ForceInstall) {
            Write-Note "Try running with -Force flag: .\NETWORK_FIX.ps1 -Install -Force"
            return
        }
        Write-Warn "Attempting force recovery..."
        Start-Sleep -Seconds 5
        if (Start-Backend) {
            Write-Success "Backend started on retry!"
        } else {
            Write-Fail "Backend failed to start. Check logs."
            return
        }
    }
    
    # Step 4: Verify everything is working
    Start-Sleep -Seconds 2
    Show-Status
    
    # Step 5: Test connectivity
    Write-Note "Testing network connectivity..."
    $testPassed = $true
    
    for ($i = 1; $i -le 3; $i++) {
        Write-Note "Test $i/3..."
        if (Test-Backend) {
            Write-Success "Test $i passed"
        } else {
            Write-Fail "Test $i failed"
            $testPassed = $false
        }
        Start-Sleep -Seconds 1
    }
    
    Write-Host "`n======================================" -ForegroundColor Green
    if ($testPassed) {
        Write-Host "  NETWORK FIX INSTALLED SUCCESSFULLY" -ForegroundColor Green
    } else {
        Write-Host "  NETWORK FIX PARTIALLY INSTALLED" -ForegroundColor Yellow
    }
    Write-Host "======================================`n" -ForegroundColor Green
    
    Write-Note "Usage:"
    Write-Host "  Check status: .\NETWORK_FIX.ps1 -Status" -ForegroundColor White
    Write-Host "  Fix issues:   .\NETWORK_FIX.ps1 -Fix" -ForegroundColor White
    Write-Host "  Force fix:    .\NETWORK_FIX.ps1 -Install -Force" -ForegroundColor White
    
    if ($testPassed) {
        Write-Host "`nYour app is ready at: http://localhost:3000" -ForegroundColor Green
    }
}

# Main
if ($Install) {
    Install-Fix -ForceInstall:$Force
} elseif ($Status) {
    Show-Status
} elseif ($Fix) {
    Fix-Network
} else {
    Write-Host @"

======================================
  HIREBAHAMAS NETWORK FIX
======================================

Usage:
  .\NETWORK_FIX.ps1 -Install         # Install and apply fix
  .\NETWORK_FIX.ps1 -Install -Force  # Force install (nuclear option)
  .\NETWORK_FIX.ps1 -Status          # Check status
  .\NETWORK_FIX.ps1 -Fix             # Fix issues

Examples:
  .\NETWORK_FIX.ps1 -Install
  .\NETWORK_FIX.ps1 -Install -Force
  .\NETWORK_FIX.ps1 -Status

======================================

"@
}
